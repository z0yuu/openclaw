# Sub-Skill Design and Extension Rules for sra-ego-job-troubleshoot

This file defines the design and implementation rules for all troubleshooting sub-skills under `sra-ego-job-troubleshoot`.
Goal:

- avoid rigid templates
- avoid main-flow bloat
- ensure each new sub-skill is executable and extensible

## 1. Overall principles

1. The main flow handles only standard investigation and keyword-based dispatch.
2. All special investigation flow, additional evidence collection, and dedicated root-cause logic must stay inside sub-skills.
3. A sub-skill must start from failed-pod single-point evidence and expand to other pods only when necessary.
4. All recommendations must be executable by the user. Do not output platform-internal actions the user cannot execute.

## 2. Boundary between the main flow and sub-skills

1. The main flow may contain:

- standard steps such as job or task query, log list fetch, `01/02` extraction, keyword dispatch, and final synthesis
- keyword trigger rules only; these rules trigger sub-skills and must not expand into scenario-specific details

2. The main flow must not contain:

- scenario-specific investigation details for one bad case
- hardcoded root-cause templates for one bad case
- fixed repair-action text for one bad case

3. Each sub-skill must contain:

- special evidence collection such as additional logs, config files, or external documents
- scenario-specific decision branches and fallback branches
- scenario-specific repair-suggestion rules

## 3. Required structure for every sub-skill

Every `sub-skills/*.md` must contain and fully define the following sections:

1. `Role`

- explain exactly which scenario the skill handles

2. `Trigger`

- define explicit trigger keywords or conditions
- define anti-miss logic without conflicting with other sub-skills

3. `Inputs`

- list required and optional inputs

4. `Preconditions`

- list required environment variables and script dependencies
- explain degradation behavior when dependencies are missing

5. `Workflow`

- must contain at least three branches:
  - primary branch for the normal matched path
  - fallback branch for insufficient evidence, API failure, or missing fields
  - last-resort branch for sub-skills that still cannot converge

6. `Hard Rules`

- declare forbidden bad practices for this scenario, such as generic recommendations, skip-step conclusions, or no-evidence conclusions

7. `Output Contract`

- output fields must be structured and stable
- include `artifacts` with the key artifact paths

## 4. Anti-rigidity rules, mandatory

1. Do not hardcode root-cause templates

- for example, do not hardcode that worker not ready is always the cause
- generate root cause dynamically from evidence

2. Do not hardcode a single path

- every sub-skill must provide at least one failure fallback path

3. Do not output only one fixed repair sentence

- recommendations must be derived from evidence plus config or log differences

4. Do not conclude from `fail_reason` alone

- include at least log-level or config-level evidence

5. Do not default to telling the user to contact EGO

- this is allowed only when all executable investigation branches in the sub-skill still cannot converge
- if the root cause is user-fixable, provide user modification guidance instead

## 5. Cross-pod evidence rules

1. First round: inspect the failed pod only.
2. Second round: expand to other pods only when one of the following is true:

- the sub-skill explicitly requires cross-pod chain evidence
- failed-pod evidence already points to a cross-pod dependency
- the failed pod alone cannot converge

3. Do not prefetch all pod logs before the trigger is established.

## 6. External documents and platform-information rules

1. When Confluence is needed, prefer scripted retrieval such as `scripts/get_confluence.py`.
2. If document fetch fails:

- do not interrupt the whole flow
- explain the reason in `limitations`
- continue with actionable recommendations based on the remaining evidence

## 7. Recommendation output rules

1. User-executable recommendation priority:

- model code
- training config
- resource request size

2. Recommendation formatting:

- point to concrete config keys or parameters; do not say only “follow the document”
- when key-value localization is possible, output `<key>: <current> -> <expected>`

3. OOM sub-skills:

- you may hand off to Smart Tune, but you must still keep the failure fallback branch documented

## 8. Pre-submit self-checklist for a new sub-skill

1. Is all special flow placed inside the sub-skill instead of the main flow?
2. Does any root-cause text remain hardcoded?
3. Are failure fallback and last-resort logic defined?
4. Are evidence sources and artifact paths explicit?
5. Are all recommendations user-executable?
6. Do the trigger conditions conflict with any existing sub-skill?
7. Is field-shape variance handled, such as top-level fields versus nested fields?

## 9. Prompt template for future sub-skill extension

> Please design and add a new troubleshooting sub-skill strictly according to `sra-ego-job-troubleshoot/sub-skills/SUB_SKILL_RULES.md`.
> Requirements:
>
> 1. do not add scenario-specific detail to the main flow; add keyword trigger only
> 2. the new sub-skill must include Trigger, Inputs, Preconditions, Workflow, Hard Rules, and Output Contract
> 3. Workflow must contain a primary branch, a fallback branch, and a last-resort branch
> 4. root cause and repair measures must not be hardcoded; generate them dynamically from evidence
> 5. recommendations must be executable by the user and must include artifact paths
