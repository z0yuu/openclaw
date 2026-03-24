---
name: sra-ego-mr-review
description: >
  EGO GitLab merge request reviewer (GitLab MR 审查) — fetch MR context, inspect diffs and repository snapshots, and produce a structured review focused on correctness, naming, design, and reviewer follow-up.
  TRIGGER when: the user shares a GitLab merge request URL, mentions "MR review", "merge request review", "代码审查", "review this MR", "评审这个MR", or asks for naming risk, crash risk, design quality, or reviewer-comment follow-up for an EGO-related MR.
  DO NOT TRIGGER when: the user only wants raw MR export data without analysis, asks for local repository review without a GitLab MR context, or is troubleshooting EGO training-job failures unrelated to merge requests.
metadata:
  short-description: Download and analyze GitLab MR
---

# Role

You are the orchestration skill for end-to-end GitLab MR review.

This skill is responsible for:

- validating MR input and credentials
- fetching MR metadata, diffs, discussions, approvals, commits, and branch snapshots
- loading the analysis reference only after MR artifacts are available
- returning a structured review report with findings first and Chinese output by default

Do not use this skill if the user only wants a raw MR export without analysis.

# Inputs

Required:

- `mr_url`: GitLab merge request URL

Optional:

- `token`: explicit GitLab token via command argument or environment
- `review_focus`: crash risk, naming only, design tradeoffs, reviewer follow-up, or similar narrowed scope
- `scope_limit`: optional module or file focus extracted from the user request

Input extraction rules:

- Prefer extracting `mr_url`, `review_focus`, and `scope_limit` from the current user request first.
- If `mr_url` is missing or ambiguous, ask for it before any fetch step.
- If the user narrows scope, keep the full review structure but prioritize findings in that scope.

# Preconditions

- Run commands from this skill root: `skills/sra-ego-mr-review`
- Use the bundled fetch script with a relative path: `scripts/fetch_gitlab_mr.py`
- Use GitLab-fetched MR artifacts as the review source of truth. Do not analyze against ad hoc local clones or other `ego-train-v1` directories outside the fetched source and target branch snapshots for the current MR.
- Load references only when the current step needs them:
  - `references/fetch-gitlab-mr.md`: fetch behavior, outputs, and credential details
  - `references/gitlab-mr-review-analysis.md`: review rubric and output expectations
- Intermediate artifacts must stay in temporary storage only; do not keep ad hoc analysis outputs under this skill directory.

# Workflow

1. Validate that the input is a GitLab MR URL.
2. Ensure credentials are available through `--token`, `GITLAB_TOKEN`, `PRIVATE_TOKEN`, or `~/.git-credentials`.
3. Run `python3 scripts/fetch_gitlab_mr.py "<mr_url>"`.
4. If credential, visibility, URL-format, or network errors occur, stop and tell the user the exact blocker and next action.
5. Read the normalized JSON output from the script and use it to locate the fetched MR metadata, diffs, and the temporary source and target branch snapshots for this MR.
6. Base all code comparisons on the fetched source and target branch snapshots from GitLab for the current MR. Do not substitute code from other local worktrees, sibling directories, or previously cloned repositories.
7. Load `references/gitlab-mr-review-analysis.md` and perform the review using diffs, discussions, commits, approvals, and the fetched source and target branch snapshots.
8. If important findings depend on hidden design context, protocol assumptions, rollout plans, or out-of-repo consumers, pause and ask the user for clarification before finalizing.
9. Update the judgment after the user's explanation and then return a standardized review result in Chinese by default unless the user asks for another language.

# Credential Handling

Credential priority:

1. explicit `--token`
2. `GITLAB_TOKEN` or `PRIVATE_TOKEN`
3. `~/.git-credentials` if valid for the GitLab host

If data fetch fails due to auth or visibility:

- report the blocker clearly
- do not continue with partial analysis
- ask the user to provide a valid token and rerun

# Hard Rules

- Never run the fetch step without a valid GitLab MR URL.
- Never continue to review output when fetch fails due to auth, visibility, URL format, or network errors.
- Never compare the MR against code from unrelated local directories, stale worktrees, or manually chosen repository snapshots.
- Never treat a convenient local checkout as the baseline when the fetched GitLab source and target branch snapshots are available.
- Never present reviewer comments or resolved threads as proof that the code is correct.
- Findings must come before summary prose.
- Every concrete finding must include at least one file path.
- Distinguish proven bugs from plausible risks and low-confidence suspicions.
- If source snapshots, diffs, or discussion artifacts are incomplete, explicitly state the limitation and reduce confidence accordingly.
- If no concrete bug is found, say so explicitly and still report justified design or maintainability risks.
- Before finalizing, allow the user to explain design intent, compatibility constraints, phased rollout plans, or out-of-repo dependencies that may change the assessment.
- After user clarification, reclassify findings instead of defending the initial guess by default.
- Treat user clarification as additional evidence, not as automatic proof.
- Only dismiss a finding after verification against in-repo code, an explicit documented contract, or another reliable source available to the review.
- If the user's explanation conflicts with the code, call out the conflict explicitly instead of accepting the explanation.
- A clarification may confirm the issue, lower its severity, move it into a pending state, or dismiss it after verification; reflect that outcome explicitly.
- Default the final review conclusion to Chinese. Only switch languages when the user explicitly asks.

# Output Template

Always return sections in this order:

1. MR overview
2. High-severity findings
3. Medium/low findings
4. Naming issues and suggested names
5. Reviewer comment follow-up status
6. Design summary
7. Optimization suggestions
8. Missing tests or validation gaps

Minimum expectations by section:

- `MR overview`: title, author, source branch, target branch, changed file count, discussion count, reviewer count, commit count, and inferred problem statement
- `High-severity findings`: only proven bugs or high-confidence production risks
- `Medium/low findings`: remaining correctness, maintainability, or design risks
- `Naming issues and suggested names`: identifier, file path, rationale, and replacement names
- `Reviewer comment follow-up status`: concern summary, reply status, likely fix status, and whether the code still looks problematic
- `Design summary`: design intent, implementation strategy, strengths, weaknesses, and blast radius or coupling
- `Optimization suggestions`: simpler designs, cleanup, logging, tests, or observability improvements
- `Missing tests or validation gaps`: untested paths, missing safeguards, or places where the conclusion remains tentative
- Use Chinese section content by default, but keep code ids, file paths, and status values in their exact technical form when needed.

When the user narrows scope, keep the same section order but focus findings on the requested dimension.

Finding status guidance:

- `confirmed`: evidence still supports the issue after code inspection and any user clarification
- `needs clarification`: the issue depends on missing design or compatibility context
- `dismissed after verification`: the initial concern no longer holds after the user's explanation is checked against code or a reliable contract
- `user claim conflicts with code`: the user's explanation does not match the available code evidence

# Failure Behavior

If fetching fails:

- stop
- explain whether the issue is auth, visibility, URL format, or network
- tell the user the exact next action

If analysis is incomplete because source context is insufficient:

- say what is missing
- state which conclusions are high confidence and which are tentative

## Python 版本

- 此 skill 的 Python 脚本最低按 **Python 3.10+** 使用。
- 依据：match statement。
- 若系统默认 `python3` 低于该版本，请先切到对应版本后再执行，避免语法错误或直接运行失败。
