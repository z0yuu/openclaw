---
name: update-ego-agent-alpha-shopee
description: >
  ego-agent-alpha-shopee updater (ego-agent-alpha-shopee 更新器) — refresh the package to the latest version and reinstall bundled skills and agents.
  TRIGGER when: the user asks to update `ego-agent-alpha-shopee`, reinstall the latest bundled skills or agents, or says `请更新ego-agent-alpha-shopee到最新版`.
  DO NOT TRIGGER when: the user is only troubleshooting one skill, editing local skill files, or asking for a package status check without requesting an update.
block_until_ms: 600000
---

# Update ego-agent-alpha-shopee

## Skill Scope

This skill performs a full refresh of `ego-agent-alpha-shopee` package and synced skills/agents.

## Trigger

Use this skill when user asks for package update, for example:

- `update ego-agent-alpha-shopee to the latest version`
- `update ego-agent-alpha-shopee`
- `reinstall the latest ego-agent-alpha-shopee and bundled skills`

## Execution

Run exactly this script from repo root:

```bash
bash skills/update-ego-agent-alpha-shopee/scripts/update_ego_agent_alpha_shopee_latest.sh
```

## Behavior Contract

1. Do not ask user for extra inputs.
2. Do not split into manual ad-hoc commands if script is available.
3. Return step-by-step command output summary and final status.
4. If any step fails, stop immediately and return explicit failing step + stderr.
