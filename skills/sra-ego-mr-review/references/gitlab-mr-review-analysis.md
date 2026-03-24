# GitLab MR Review Analysis Reference

Read this file only after MR artifacts have been fetched successfully.

## Required Inputs

Prefer these inputs in order:

1. `normalized.json`
2. `summary.md`
3. source branch snapshot
4. target branch snapshot

If `normalized.json` is available, use it as the primary machine-readable source.

## Review Checklist

1. Read MR metadata and changed-file diffs first.
2. Identify the main changed modules, critical paths, and likely design intent.
3. Read reviewer comments, replies, approvals, and commit timeline.
4. Inspect the source-branch snapshot for surrounding implementation and hidden dependencies.
5. Inspect the target-branch snapshot when you need a pre-change baseline.
6. Mark which findings are already well supported by in-repo evidence and which findings depend on missing context.
7. If a key judgment depends on rollout assumptions, hidden protocol contracts, or out-of-repo consumers, ask the user for clarification before finalizing.
8. Verify the user's explanation against code, documented contracts, or other reliable evidence when possible.
9. Update the finding status after clarification and verification, then produce findings first, followed by design summary and optimization suggestions.

## Must-Check Areas

### Naming

Check whether changed identifiers are readable, consistent, and aligned with Google-style C++ expectations where relevant.

Focus on:

- class, struct, function, method, and variable names
- constants, macros, enums, and file names when relevant

For each meaningful naming issue, include:

- file path
- identifier
- why the name is weak or misleading
- 1 to 3 replacement names

### Correctness and Crash Risk

Check for:

- null dereference
- out-of-bounds access
- use-after-free
- lifetime or ownership bugs
- memory leak or double free
- unchecked container access
- integer overflow or truncation
- race condition, deadlock, or thread-safety issues
- unchecked error handling
- inconsistent state updates across modules

When uncertain, label the conclusion as:

- likely bug
- plausible risk
- low-confidence suspicion

### Design and Maintainability

Summarize:

- inferred design intent
- key implementation strategy
- strengths
- weaknesses
- coupling or blast radius
- maintainability and extensibility impact
- testability impact
- simpler or safer alternatives

Tie claims back to files, call paths, or module interactions.

## Extra Checks

Also inspect these areas unless the user explicitly narrows scope:

- reviewer comment follow-up status
- commit timeline coherence
- cross-module impact
- invariant or contract preservation
- observability and debuggability
- backward compatibility
- rollout or config risk
- duplicated logic in nearby modules

## Output Rules

Present results in this order:

1. Findings
2. Open questions or low-confidence risks
3. Design summary
4. Optimization suggestions

For each finding include:

- severity: `high`, `medium`, or `low`
- status: `confirmed`, `needs clarification`, `dismissed after verification`, or `user claim conflicts with code`
- file path
- concise problem statement
- reasoning
- recommended fix

Default language:

- write the final review conclusion in Chinese unless the user explicitly asks for English or another language
- keep technical identifiers, APIs, enum values, and file paths unchanged when translating

## Review Principles

- Findings first. Keep summary prose shorter than findings.
- Prefer code evidence over speculation.
- Use reviewer comments and commit history as supporting evidence, not as substitutes for code inspection.
- Cross-check claims against source snapshots when diffs are insufficient.
- Ask the user for clarification when a suspected issue may depend on hidden design context, phased rollout, or out-of-repo consumers.
- Treat user clarification as new evidence, not as ground truth by default.
- After clarification, verify the explanation against code or a reliable contract when possible.
- If the user's explanation conflicts with the code, state that conflict explicitly instead of silently accepting the claim.
- If no concrete bug is found, say so explicitly and still report justified maintainability or design risks.
- Avoid style-only nitpicks unless they materially affect readability, correctness, or maintenance.
- Keep the final write-up concise and readable in Chinese by default.
