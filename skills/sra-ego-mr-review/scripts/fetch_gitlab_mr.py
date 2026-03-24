#!/usr/bin/env python3
"""
Fetch a GitLab merge request into temporary files and stream the result.

The script stores:
1. Raw MR metadata / changes / discussions as JSON.
2. A normalized JSON document that links changed snippets with discussions.
3. A markdown summary for humans or downstream agents.

Authentication:
- Prefer `--token`
- Or `GITLAB_TOKEN`
- Or `PRIVATE_TOKEN`
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import json
import os
import re
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from urllib import error, parse, request


@dataclass
class ParsedMrUrl:
    base_url: str
    project_path: str
    mr_iid: str


@dataclass
class BasicAuthCredential:
    username: str
    password: str


class CredentialRequiredError(RuntimeError):
    """Raised when the MR cannot be accessed without additional credentials."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a GitLab MR into temporary files and print structured output."
    )
    parser.add_argument("mr_url", help="GitLab merge request URL")
    parser.add_argument(
        "--token",
        default=os.environ.get("GITLAB_TOKEN") or os.environ.get("PRIVATE_TOKEN"),
        help="GitLab private token. Falls back to GITLAB_TOKEN / PRIVATE_TOKEN.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--stdout",
        choices=("summary", "normalized"),
        default="normalized",
        help="Write summary markdown or normalized JSON to stdout (default: normalized).",
    )
    parser.add_argument(
        "--report-path",
        help=(
            "Persistent path for the final review conclusion. Defaults to "
            "./mr-<iid>-review.md in the current directory."
        ),
    )
    return parser.parse_args()


def parse_mr_url(mr_url: str) -> ParsedMrUrl:
    parsed = parse.urlparse(mr_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid MR URL: {mr_url}")

    match = re.search(r"^(?P<project>.+)/-/merge_requests/(?P<iid>\d+)/?$", parsed.path)
    if not match:
        raise ValueError(
            "Unsupported GitLab MR URL format. Expected .../<project>/-/merge_requests/<iid>"
        )

    base_url = f"{parsed.scheme}://{parsed.netloc}"
    return ParsedMrUrl(
        base_url=base_url,
        project_path=match.group("project").lstrip("/"),
        mr_iid=match.group("iid"),
    )


class GitLabClient:
    def __init__(
        self,
        base_url: str,
        token: Optional[str],
        timeout: int,
        basic_auth: Optional[BasicAuthCredential] = None,
    ) -> None:
        self.base_api = f"{base_url}/api/v4"
        self.token = token
        self.timeout = timeout
        self.basic_auth = basic_auth

    def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_api}{path}"
        if params:
            query = parse.urlencode(params)
            url = f"{url}?{query}"
        req = request.Request(url, headers=self._headers())
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code in (401, 403):
                raise CredentialRequiredError(
                    self._credential_message(
                        f"GitLab API authorization failed ({exc.code}).",
                        detail=detail,
                    )
                ) from None
            if exc.code == 404:
                raise self._handle_not_found(url, detail) from None
            raise RuntimeError(
                f"GitLab API request failed ({exc.code}) for {url}: {detail}"
            ) from None
        except error.URLError as exc:
            raise RuntimeError(f"Network error while requesting {url}: {exc}") from None

    def get_paginated_json(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        merged: List[Any] = []
        page = 1
        while True:
            page_params = dict(params or {})
            page_params.update({"per_page": 100, "page": page})
            url = f"{self.base_api}{path}?{parse.urlencode(page_params)}"
            req = request.Request(url, headers=self._headers())
            try:
                with request.urlopen(req, timeout=self.timeout) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                    merged.extend(payload)
                    next_page = resp.headers.get("X-Next-Page")
            except error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if exc.code in (401, 403):
                    raise CredentialRequiredError(
                        self._credential_message(
                            f"GitLab API authorization failed ({exc.code}).",
                            detail=detail,
                        )
                    ) from None
                if exc.code == 404:
                    raise self._handle_not_found(url, detail) from None
                raise RuntimeError(
                    f"GitLab API request failed ({exc.code}) for {url}: {detail}"
                ) from None
            except error.URLError as exc:
                raise RuntimeError(f"Network error while requesting {url}: {exc}") from None

            if not next_page:
                return merged
            page = int(next_page)

    def get_optional_json(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        try:
            return self.get_json(path, params=params)
        except CredentialRequiredError:
            raise
        except RuntimeError as exc:
            if "GitLab API request failed (404)" in str(exc):
                return None
            raise

    def get_binary(self, path: str, params: Optional[Dict[str, Any]] = None) -> bytes:
        url = f"{self.base_api}{path}"
        if params:
            query = parse.urlencode(params)
            url = f"{url}?{query}"
        req = request.Request(url, headers=self._headers())
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code in (401, 403):
                raise CredentialRequiredError(
                    self._credential_message(
                        f"GitLab API authorization failed ({exc.code}).",
                        detail=detail,
                    )
                ) from None
            if exc.code == 404:
                raise self._handle_not_found(url, detail) from None
            raise RuntimeError(
                f"GitLab API request failed ({exc.code}) for {url}: {detail}"
            ) from None
        except error.URLError as exc:
            raise RuntimeError(f"Network error while requesting {url}: {exc}") from None

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token
        elif self.basic_auth:
            raw = f"{self.basic_auth.username}:{self.basic_auth.password}".encode("utf-8")
            headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
        return headers

    def _credential_message(self, prefix: str, detail: str = "") -> str:
        lines = [
            prefix,
            "Blocked: this MR cannot be fetched with the current credentials.",
            "Please provide a GitLab access token, or ensure ~/.git-credentials contains a valid credential for this GitLab host, then rerun the script.",
            "Example:",
            '  export GITLAB_TOKEN="your_token"',
            '  python3 scripts/fetch_gitlab_mr.py "<mr_url>"',
        ]
        if detail:
            lines.append(f"GitLab detail: {detail}")
        return "\n".join(lines)

    def _handle_not_found(self, url: str, detail: str) -> CredentialRequiredError:
        message = (
            f"GitLab API returned 404 for {url}.\n"
            "Blocked: this usually means the project/MR is private or invisible to the current credentials.\n"
            "Please provide a valid GitLab access token, or ensure ~/.git-credentials contains a valid credential for this GitLab host, then rerun the script.\n"
            "Example:\n"
            '  export GITLAB_TOKEN="your_token"\n'
            '  python3 scripts/fetch_gitlab_mr.py "<mr_url>"\n'
            f"GitLab detail: {detail}"
        )
        return CredentialRequiredError(message)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-") or "mr"


def load_basic_auth_from_git_credentials(base_url: str) -> Optional[BasicAuthCredential]:
    credentials_path = Path.home() / ".git-credentials"
    if not credentials_path.exists():
        return None

    target_host = parse.urlparse(base_url).netloc
    try:
        lines = credentials_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parsed = parse.urlparse(line)
        if parsed.netloc != target_host:
            continue
        if parsed.username is None or parsed.password is None:
            continue
        return BasicAuthCredential(
            username=parse.unquote(parsed.username),
            password=parse.unquote(parsed.password),
        )
    return None


def load_mr_data(client: GitLabClient, parsed_url: ParsedMrUrl) -> Dict[str, Any]:
    project_id = parse.quote(parsed_url.project_path, safe="")
    mr_base = f"/projects/{project_id}/merge_requests/{parsed_url.mr_iid}"

    mr = client.get_json(mr_base)
    changes = client.get_json(f"{mr_base}/changes")
    discussions = client.get_paginated_json(f"{mr_base}/discussions")
    commits = client.get_paginated_json(f"{mr_base}/commits")
    approval_state = client.get_optional_json(f"{mr_base}/approval_state")
    approvals = client.get_optional_json(f"{mr_base}/approvals")

    return {
        "mr": mr,
        "changes": changes,
        "discussions": discussions,
        "commits": commits,
        "approval_state": approval_state,
        "approvals": approvals,
    }


def count_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file())


def extract_repository_archive(
    client: GitLabClient,
    project_path: str,
    ref: str,
    destination_root: Path,
    label: str,
) -> Dict[str, Any]:
    project_id = parse.quote(project_path, safe="")
    archive_bytes = client.get_binary(
        f"/projects/{project_id}/repository/archive.tar.gz",
        params={"sha": ref},
    )

    extract_root = destination_root / label
    extract_root.mkdir(parents=True, exist_ok=True)

    with tarfile.open(fileobj=BytesIO(archive_bytes), mode="r:gz") as tar:
        tar.extractall(extract_root)

    top_level_dirs = [path for path in extract_root.iterdir() if path.is_dir()]
    repo_root = top_level_dirs[0] if len(top_level_dirs) == 1 else extract_root
    return {
        "ref": ref,
        "path": str(repo_root),
        "file_count": count_files(repo_root),
    }


def summarize_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not user:
        return None
    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "username": user.get("username"),
        "state": user.get("state"),
        "web_url": user.get("web_url"),
    }


def safe_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def summarize_discussion(discussion: Dict[str, Any]) -> Dict[str, Any]:
    notes = discussion.get("notes", [])
    first_note = notes[0] if notes else {}
    position = first_note.get("position") or {}

    author_username = ((first_note.get("author") or {}).get("username")) or "unknown"
    participants = []
    for note in notes:
        author = (note.get("author") or {}).get("username")
        if author and author not in participants:
            participants.append(author)

    return {
        "id": discussion.get("id"),
        "individual_note": discussion.get("individual_note"),
        "resolved": discussion.get("resolved"),
        "resolved_by": ((discussion.get("resolved_by") or {}).get("username")),
        "resolvable": discussion.get("resolvable"),
        "created_at": first_note.get("created_at"),
        "updated_at": notes[-1].get("updated_at") if notes else None,
        "anchor": {
            "file_path": position.get("new_path") or position.get("old_path"),
            "new_line": position.get("new_line"),
            "old_line": position.get("old_line"),
            "line_range": position.get("line_range"),
            "position_type": position.get("position_type"),
        },
        "author": author_username,
        "participants": participants,
        "notes": [
            {
                "id": note.get("id"),
                "type": note.get("type"),
                "body": note.get("body"),
                "system": note.get("system"),
                "created_at": note.get("created_at"),
                "updated_at": note.get("updated_at"),
                "resolvable": note.get("resolvable"),
                "resolved": note.get("resolved"),
                "author": {
                    "name": (note.get("author") or {}).get("name"),
                    "username": (note.get("author") or {}).get("username"),
                },
                "position": note.get("position"),
            }
            for note in notes
        ],
    }


def normalize_payload(raw: Dict[str, Any], mr_url: str, repository_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    mr = raw["mr"]
    changes_payload = raw["changes"]
    discussions_payload = raw["discussions"]
    commits_payload = raw.get("commits") or []
    approval_state_payload = raw.get("approval_state") or {}
    approvals_payload = raw.get("approvals") or {}

    discussions = [summarize_discussion(item) for item in discussions_payload]
    commits = [
        {
            "id": item.get("id"),
            "short_id": item.get("short_id"),
            "title": item.get("title"),
            "message": item.get("message"),
            "created_at": item.get("created_at"),
            "parent_ids": item.get("parent_ids"),
            "author_name": item.get("author_name"),
            "author_email": item.get("author_email"),
            "committer_name": item.get("committer_name"),
            "committer_email": item.get("committer_email"),
            "web_url": item.get("web_url"),
        }
        for item in commits_payload
    ]

    commit_times = [safe_datetime(item.get("created_at")) for item in commits]
    commit_times = [item for item in commit_times if item is not None]
    latest_commit_at = max(commit_times).isoformat() if commit_times else None

    discussions_by_file: Dict[str, List[Dict[str, Any]]] = {}
    for item in discussions:
        file_path = ((item.get("anchor") or {}).get("file_path")) or "general"
        discussions_by_file.setdefault(file_path, []).append(item)

    for item in discussions:
        updated_at = safe_datetime(item.get("updated_at")) or safe_datetime(item.get("created_at"))
        item["has_commit_after_discussion"] = bool(
            updated_at and any(commit_time > updated_at for commit_time in commit_times)
        )

    files = []
    for change in changes_payload.get("changes", []):
        file_path = change.get("new_path") or change.get("old_path")
        files.append(
            {
                "file_path": file_path,
                "old_path": change.get("old_path"),
                "new_path": change.get("new_path"),
                "new_file": change.get("new_file"),
                "renamed_file": change.get("renamed_file"),
                "deleted_file": change.get("deleted_file"),
                "generated_file": change.get("generated_file"),
                "diff": change.get("diff"),
                "discussions": discussions_by_file.get(file_path, []),
            }
        )

    general_discussions = [
        item
        for item in discussions
        if not (item.get("anchor") or {}).get("file_path")
    ]

    approval_rules = []
    for rule in approval_state_payload.get("rules", []):
        approval_rules.append(
            {
                "name": rule.get("name"),
                "rule_type": rule.get("rule_type"),
                "approvals_required": rule.get("approvals_required"),
                "approved": rule.get("approved"),
                "approved_by": [
                    summarize_user((entry or {}).get("user"))
                    for entry in (rule.get("approved_by") or [])
                    if (entry or {}).get("user")
                ],
                "eligible_approvers": [
                    summarize_user(user) for user in (rule.get("eligible_approvers") or [])
                ],
            }
        )

    return {
        "source": {
            "mr_url": mr_url,
            "fetched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
        "repository_snapshot": repository_snapshot,
        "mr": {
            "id": mr.get("id"),
            "iid": mr.get("iid"),
            "project_id": mr.get("project_id"),
            "title": mr.get("title"),
            "description": mr.get("description"),
            "state": mr.get("state"),
            "draft": mr.get("draft"),
            "web_url": mr.get("web_url"),
            "author": {
                "name": (mr.get("author") or {}).get("name"),
                "username": (mr.get("author") or {}).get("username"),
            },
            "source_branch": mr.get("source_branch"),
            "target_branch": mr.get("target_branch"),
            "created_at": mr.get("created_at"),
            "updated_at": mr.get("updated_at"),
            "merged_at": mr.get("merged_at"),
            "merge_status": mr.get("merge_status"),
            "sha": mr.get("sha"),
            "labels": mr.get("labels"),
            "reviewers": [summarize_user(user) for user in (mr.get("reviewers") or [])],
            "assignees": [summarize_user(user) for user in (mr.get("assignees") or [])],
            "milestone": (
                {
                    "id": (mr.get("milestone") or {}).get("id"),
                    "title": (mr.get("milestone") or {}).get("title"),
                }
                if mr.get("milestone")
                else None
            ),
        },
        "stats": {
            "changed_files": len(files),
            "discussions": len(discussions),
            "file_level_discussions": sum(
                1 for item in discussions if (item.get("anchor") or {}).get("file_path")
            ),
            "resolved_discussions": sum(1 for item in discussions if item.get("resolved")),
            "unresolved_discussions": sum(
                1 for item in discussions if item.get("resolvable") and not item.get("resolved")
            ),
            "commits": len(commits),
            "latest_commit_at": latest_commit_at,
        },
        "workflow": {
            "reviewers": [summarize_user(user) for user in (mr.get("reviewers") or [])],
            "assignees": [summarize_user(user) for user in (mr.get("assignees") or [])],
            "approval_summary": {
                "approvals_required": approvals_payload.get("approvals_required"),
                "approvals_left": approvals_payload.get("approvals_left"),
                "approved_by": [
                    summarize_user((entry or {}).get("user"))
                    for entry in (approvals_payload.get("approved_by") or [])
                    if (entry or {}).get("user")
                ],
                "suggested_approvers": [
                    summarize_user(user)
                    for user in (approvals_payload.get("suggested_approvers") or [])
                ],
            },
            "approval_rules": approval_rules,
        },
        "commits": commits,
        "files": files,
        "general_discussions": general_discussions,
    }


def markdown_escape(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").strip()


def render_markdown(normalized: Dict[str, Any]) -> str:
    mr = normalized["mr"]
    stats = normalized["stats"]
    repository_snapshot = normalized.get("repository_snapshot") or {}
    lines: List[str] = []

    lines.append(f"# MR {mr['iid']}: {mr['title']}")
    lines.append("")
    lines.append(f"- URL: {mr['web_url']}")
    lines.append(f"- State: {mr['state']}")
    lines.append(f"- Author: {mr['author']['name']} (@{mr['author']['username']})")
    lines.append(f"- Branch: `{mr['source_branch']}` -> `{mr['target_branch']}`")
    lines.append(f"- Updated At: {mr['updated_at']}")
    lines.append(f"- Changed Files: {stats['changed_files']}")
    lines.append(f"- Discussions: {stats['discussions']}")
    lines.append(f"- Commits: {stats['commits']}")
    lines.append(f"- Resolved Discussions: {stats['resolved_discussions']}")
    lines.append(f"- Unresolved Discussions: {stats['unresolved_discussions']}")
    lines.append("")

    if repository_snapshot:
        lines.append("## Repository Snapshots")
        lines.append("")
        source_snapshot = repository_snapshot.get("source_branch") or {}
        target_snapshot = repository_snapshot.get("target_branch") or {}
        lines.append(
            f"- Source Branch Snapshot: `{source_snapshot.get('ref')}` at `{source_snapshot.get('path')}`, files={source_snapshot.get('file_count')}"
        )
        lines.append(
            f"- Target Branch Snapshot: `{target_snapshot.get('ref')}` at `{target_snapshot.get('path')}`, files={target_snapshot.get('file_count')}"
        )
        lines.append("")

    workflow = normalized.get("workflow") or {}
    reviewers = workflow.get("reviewers") or []
    assignees = workflow.get("assignees") or []
    approval_summary = workflow.get("approval_summary") or {}

    lines.append("## Review Workflow")
    lines.append("")
    lines.append(
        "- Reviewers: "
        + (", ".join(f"@{item['username']}" for item in reviewers if item and item.get("username")) or "none")
    )
    lines.append(
        "- Assignees: "
        + (", ".join(f"@{item['username']}" for item in assignees if item and item.get("username")) or "none")
    )
    if approval_summary:
        lines.append(
            f"- Approvals Required: {approval_summary.get('approvals_required')}"
        )
        lines.append(f"- Approvals Left: {approval_summary.get('approvals_left')}")
        approved_by = ", ".join(
            f"@{item['username']}"
            for item in (approval_summary.get("approved_by") or [])
            if item and item.get("username")
        )
        lines.append(f"- Approved By: {approved_by or 'none'}")
    lines.append("")

    if normalized.get("commits"):
        lines.append("## Commits")
        lines.append("")
        for commit in normalized["commits"]:
            commit_author = commit.get("author_name") or "unknown"
            commit_title = commit.get("title") or ""
            lines.append(
                f"- `{commit.get('short_id') or commit.get('id')}` by {commit_author} at {commit.get('created_at')}: {commit_title}"
            )
        lines.append("")

    if mr.get("description"):
        lines.append("## Description")
        lines.append("")
        lines.append(markdown_escape(mr["description"]))
        lines.append("")

    if normalized.get("general_discussions"):
        lines.append("## General Discussions")
        lines.append("")
        for discussion in normalized["general_discussions"]:
            lines.extend(render_discussion_block(discussion))
        lines.append("")

    lines.append("## File Changes")
    lines.append("")
    for file_item in normalized["files"]:
        lines.append(f"### `{file_item['file_path']}`")
        lines.append("")
        meta = []
        if file_item.get("new_file"):
            meta.append("new file")
        if file_item.get("deleted_file"):
            meta.append("deleted")
        if file_item.get("renamed_file"):
            meta.append("renamed")
        if file_item.get("generated_file"):
            meta.append("generated")
        if meta:
            lines.append(f"- Flags: {', '.join(meta)}")
        lines.append("")
        lines.append("```diff")
        lines.append(file_item.get("diff") or "")
        lines.append("```")
        lines.append("")

        discussions = file_item.get("discussions") or []
        if not discussions:
            lines.append("_No discussions on this file._")
            lines.append("")
            continue

        lines.append("#### Discussions")
        lines.append("")
        for discussion in discussions:
            lines.extend(render_discussion_block(discussion))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_discussion_block(discussion: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    anchor = discussion.get("anchor") or {}
    file_path = anchor.get("file_path")
    new_line = anchor.get("new_line")
    old_line = anchor.get("old_line")
    resolved = "resolved" if discussion.get("resolved") else "open"

    summary = f"- Discussion `{discussion['id']}` [{resolved}]"
    if file_path:
        summary += f" on `{file_path}`"
    if new_line is not None:
        summary += f" new_line={new_line}"
    if old_line is not None:
        summary += f" old_line={old_line}"
    if discussion.get("resolved_by"):
        summary += f", resolved_by=@{discussion['resolved_by']}"
    if discussion.get("has_commit_after_discussion"):
        summary += ", commits_after_discussion=yes"
    lines.append(summary)

    for note in discussion.get("notes", []):
        author = (note.get("author") or {}).get("username") or "unknown"
        created_at = note.get("created_at") or "unknown-time"
        body = markdown_escape(note.get("body"))
        lines.append(f"  - @{author} at {created_at}")
        if body:
            for body_line in body.splitlines():
                lines.append(f"    {body_line}")
        else:
            lines.append("    <empty>")
    return lines


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_report_path(parsed_url: ParsedMrUrl, explicit_path: Optional[str]) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve()
    return (Path.cwd() / f"mr-{parsed_url.mr_iid}-review.md").resolve()


@contextlib.contextmanager
def export_directory(mr_slug: str) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix=f"{mr_slug}-") as tmpdir:
        yield Path(tmpdir)


def wait_for_analysis_finalization(export_dir: Path, report_path: Path) -> int:
    print(
        "Analysis hold is active. Temporary export will be kept until stdin closes, "
        "or a FINALIZE command confirms the final report is written.",
        file=sys.stderr,
    )
    print(
        f"Expected final report path: {report_path}",
        file=sys.stderr,
    )
    print(
        "Finalize command example: FINALIZE",
        file=sys.stderr,
    )

    while True:
        line = sys.stdin.readline()
        if line == "":
            print(
                "Analysis session ended before finalize confirmation. Cleaning up export.",
                file=sys.stderr,
            )
            return 0

        command = line.strip()
        if not command:
            continue

        if command.upper() == "CLEANUP":
            print("Received CLEANUP command. Cleaning up export.", file=sys.stderr)
            return 0

        if command == "FINALIZE":
            if not report_path.exists():
                print(
                    f"Ignoring FINALIZE command because report file does not exist yet: {report_path}",
                    file=sys.stderr,
                )
                continue
            print(
                f"Confirmed final report at {report_path}. Cleaning up export.",
                file=sys.stderr,
            )
            return 0

        if command.startswith("FINALIZE "):
            override_report_path = Path(command[len("FINALIZE ") :].strip()).expanduser()
            if not override_report_path.is_absolute():
                print(
                    "Ignoring FINALIZE override because report path is not absolute: "
                    f"{override_report_path}",
                    file=sys.stderr,
                )
                continue
            if not override_report_path.exists():
                print(
                    "Ignoring FINALIZE override because report file does not exist yet: "
                    f"{override_report_path}",
                    file=sys.stderr,
                )
                continue
            print(
                f"Confirmed final report at {override_report_path}. Cleaning up export.",
                file=sys.stderr,
            )
            return 0

        print(
            "Unknown hold command. Use FINALIZE, FINALIZE <absolute_report_path>, or CLEANUP.",
            file=sys.stderr,
        )


def main() -> int:
    args = parse_args()

    try:
        parsed_url = parse_mr_url(args.mr_url)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    basic_auth = None if args.token else load_basic_auth_from_git_credentials(parsed_url.base_url)
    client = GitLabClient(parsed_url.base_url, args.token, args.timeout, basic_auth=basic_auth)
    report_path = resolve_report_path(parsed_url, args.report_path)

    try:
        raw = load_mr_data(client, parsed_url)
    except CredentialRequiredError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    mr = raw["mr"]
    mr_slug = slugify(f"{parsed_url.project_path}-mr-{parsed_url.mr_iid}")

    with export_directory(mr_slug) as export_dir:
        repository_root = export_dir / "repository_snapshots"
        repository_root.mkdir(parents=True, exist_ok=True)
        repository_snapshot = {
            "source_branch": extract_repository_archive(
                client,
                parsed_url.project_path,
                mr.get("source_branch"),
                repository_root,
                "source_branch",
            ),
            "target_branch": extract_repository_archive(
                client,
                parsed_url.project_path,
                mr.get("target_branch"),
                repository_root,
                "target_branch",
            ),
        }

        normalized = normalize_payload(raw, args.mr_url, repository_snapshot)
        summary_markdown = render_markdown(normalized)

        write_json(export_dir / "mr.json", raw["mr"])
        write_json(export_dir / "changes.json", raw["changes"])
        write_json(export_dir / "discussions.json", raw["discussions"])
        write_json(export_dir / "commits.json", raw["commits"])
        write_json(export_dir / "approval_state.json", raw.get("approval_state"))
        write_json(export_dir / "approvals.json", raw.get("approvals"))
        write_json(export_dir / "normalized.json", normalized)
        (export_dir / "summary.md").write_text(summary_markdown, encoding="utf-8")

        print(f"Saved MR export to: {export_dir}", file=sys.stderr)
        print(f"- Summary: {export_dir / 'summary.md'}", file=sys.stderr)
        print(f"- Normalized JSON: {export_dir / 'normalized.json'}", file=sys.stderr)
        print(f"- Raw MR JSON: {export_dir / 'mr.json'}", file=sys.stderr)
        print(f"- Raw Changes JSON: {export_dir / 'changes.json'}", file=sys.stderr)
        print(f"- Raw Discussions JSON: {export_dir / 'discussions.json'}", file=sys.stderr)
        print(f"- Raw Commits JSON: {export_dir / 'commits.json'}", file=sys.stderr)
        print(f"- Raw Approval State JSON: {export_dir / 'approval_state.json'}", file=sys.stderr)
        print(f"- Raw Approvals JSON: {export_dir / 'approvals.json'}", file=sys.stderr)
        print(f"- Final Review Report: {report_path}", file=sys.stderr)
        print(
            f"- Source Branch Snapshot: {repository_snapshot['source_branch']['path']}",
            file=sys.stderr,
        )
        print(
            f"- Target Branch Snapshot: {repository_snapshot['target_branch']['path']}",
            file=sys.stderr,
        )
        print(
            "Temporary export will stay available during analysis and be removed "
            "when analysis finalizes or the session ends.",
            file=sys.stderr,
        )

        if args.stdout == "summary":
            sys.stdout.write(summary_markdown)
        else:
            sys.stdout.write(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n")
        sys.stdout.flush()

        return wait_for_analysis_finalization(export_dir, report_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
