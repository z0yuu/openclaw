# GitLab MR Fetch Reference

Read this file only when you need fetch behavior, output artifacts, or auth troubleshooting for `scripts/fetch_gitlab_mr.py`.

## Entry Point

Run:

```bash
python3 scripts/fetch_gitlab_mr.py "<mr_url>"
```

Default behavior:

- prints normalized JSON to stdout
- materializes temporary artifacts during execution
- the export directory stays available while the script process remains alive
- the agent can read snapshots, diffs, and discussions during analysis
- all intermediate artifacts stay in a temporary directory only
- the only expected persistent file is the final review report
- cleanup happens when stdin closes, or after the agent sends `FINALIZE` and the final report file exists locally
- do not copy raw MR artifacts into the skill directory as long-term files

## Final Report Path

- Use `--report-path <abs_path>` to explicitly set the persistent review report path
- If `--report-path` is omitted, the default path is `./mr-<iid>-review.md` in the current directory
- `FINALIZE` checks that this final report path already exists before cleaning up temporary artifacts
- if the user does not request another language, the final review report should be written in Chinese

## Main Artifacts

The script may create:

- `mr.json`
- `changes.json`
- `discussions.json`
- `commits.json`
- `approval_state.json`
- `approvals.json`
- `normalized.json`
- `summary.md`
- `repository_snapshots/source_branch/...`
- `repository_snapshots/target_branch/...`

Prefer `normalized.json` as the primary machine-readable input for downstream review.

## Auth Priority

Use credentials in this order:

1. `--token`
2. `GITLAB_TOKEN`
3. `PRIVATE_TOKEN`
4. `~/.git-credentials` for the matching GitLab host

## Common Failure Types

- auth failure: token missing, invalid, or insufficient
- visibility failure: project or MR is private to the current credential
- URL format failure: input is not a supported GitLab MR URL
- network failure: GitLab API cannot be reached

## Fetch Rules

- If the script returns an auth or visibility blocker, stop and ask for valid credentials.
- If the script returns a URL-format blocker, stop and ask for a valid MR URL.
- Do not continue with partial review when normalized artifacts are unavailable.
- Do not assume a GitLab 404 means the MR does not exist; private MRs may surface as visibility failures.
