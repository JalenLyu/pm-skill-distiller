# Continuous Learning

Use this when generating or refreshing a personalized `pm-xxx` PRD copilot. The generated skill should keep improving from user corrections, but only through controlled preference distillation.

## Generated Skill Contract

Every generated `pm-xxx` should include:

- A Learning Check mode in `SKILL.md`.
- `references/continuous-learning.md`.
- A rule that user corrections are classified before any skill edit.
- A rule that explicit user confirmation is required unless the user already says "可以", "继续", "以后默认这样", or directly asks to optimize the skill.
- A validation step with skill-creator `quick_validate.py`.

## What To Learn

Learn durable preferences:

- Template Preference: section order, metadata table, Scope rows, Feature List, Feature Detail shape.
- Writing Style: language split, density, Background length, terminology preservation.
- Workflow Preference: source discovery, Confluence search, planning gate, outline confirmation, clarification timing.
- Domain Knowledge: repeated module boundaries, product/system constraints, historical logic search keywords.
- Review Preference: checklist gates, severity model, recurring review risks.

Do not learn one-off PRD facts:

- Jira/Epic IDs.
- Page-specific owner names.
- Temporary launch scope.
- Local draft links.
- Exact source content that belongs in the PRD, not the skill.
- Secrets, credentials, or private values.

## Update Routing

| Feedback type | Generated file to update |
|---|---|
| Default workflow or trigger rule | `SKILL.md`, `checklist-gates.md` |
| Author writing habit | `author-model.md`, `user-prd-profile.md` |
| Confluence format evidence | `user-prd-profile.md`, `new-prd-template.md`, optional author-style reference if present |
| Requirement type outline | `outline-patterns.md` |
| Review failure or checklist rule | `quality-checklist.md`, `prd-copilot-modes.md` |
| Product/domain routing hint | `author-model.md`, `work-map.md` |

## Distiller Behavior

When refreshing a skill from feedback:

1. Read the current generated skill and the PRD/user correction.
2. Produce a Learning Check table with `# | 用户反馈 | 判断 | 更新位置 | 是否写入 skill`.
3. Apply only confirmed durable rules.
4. Keep `SKILL.md` lean; move detailed preference rules into references.
5. Validate the refreshed skill.
6. If the rule should apply to future generated skills, update `create_pm_copilot.py` and `skill-blueprint.md` too.
