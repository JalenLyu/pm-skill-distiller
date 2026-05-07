# Skill Blueprint

Generated PM copilot skills should follow this structure:

```text
pm-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── source-router.md
│   ├── confluence-discovery.md
│   ├── author-model.md
│   ├── continuous-learning.md
│   ├── user-prd-profile.md
│   ├── work-map.md
│   ├── prd-copilot-modes.md
│   ├── new-prd-template.md
│   ├── confluence-draft-workflow.md
│   ├── checklist-gates.md
│   ├── outline-patterns.md
│   ├── question-playbook.md
│   ├── quality-checklist.md
│   └── frontend-code-discovery.md
└── scripts/
    └── local_prd_inventory.py
```

## SKILL.md Responsibilities

- Trigger description.
- Default stance and safety rules.
- Mode selection table.
- Source routing summary.
- Pointers to references.

## Reference Responsibilities

- `source-router.md`: source priority and read-only boundaries.
- `confluence-discovery.md`: direct Confluence read/search protocol for PRD libraries, root pages, and target draft pages.
- `author-model.md`: distilled author habits, confirmed/inferred style rules, historical logic modules, review preferences, anti-patterns, and profile gaps.
- `continuous-learning.md`: controlled loop for turning future user PRD corrections into confirmed preference updates.
- `user-prd-profile.md`: personal PM style and preferences.
- `work-map.md`: current products/modules and representative docs.
- `prd-copilot-modes.md`: detailed behavior for context, outline, interview, rewrite, review, consistency, and draft modes.
- `new-prd-template.md`: generic Confluence-ready PRD template, excluding target release and PRD status by default.
- `confluence-draft-workflow.md`: PM-created Confluence page flow; agent fills paste-ready content, not page creation.
- `checklist-gates.md`: batched numbered gap tables, outline confirmation, detail clarification, and trigger timing.
- `outline-patterns.md`: PRD skeletons by requirement type.
- `question-playbook.md`: targeted confirmation questions.
- `quality-checklist.md`: review and consistency checklist.
- `frontend-code-discovery.md`: optional local frontend code inspection guidance.

## Design Rule

Separate personal workflow from domain knowledge. If a domain is large or reusable, create a companion domain skill rather than bloating the PM skill.

## Stable V0.1 Contract

A generated `pm-xxx` skill is considered equivalent to `pm-jalen` V0.1 when it has:

- A concise `SKILL.md` with Default Stance, Mode Selection, Source Routing, PRD Style, Local Discovery Helpers, and Domain Routing.
- An `author-model.md` reference that makes the generated copilot an author-style/knowledge distillation product, not a generic PRD writer.
- A `continuous-learning.md` reference and Learning Check mode that classify feedback before proposing skill updates.
- Distillation rules that separate confirmed author habits from inferred habits and generic PRD best practices.
- A Confluence discovery rule that reads/searches Confluence before scope/outline when the user's PRD library or provided source link is in Confluence.
- A hard gate for Confluence-backed PRDs: no Confluence source map, no full draft when historical logic matters.
- Mode-based behavior rather than a full-PRD-only workflow.
- Requirement Brief fallback, Auto Enrich section-targeted gap filling, and Review Board severity mode.
- New PRD template mode that assumes the PM provides the Confluence page link.
- New PRD flow that proposes an outline and waits for confirmation before full drafting.
- New PRD flow that confirms a plan, Feature List, and outline before full drafting.
- Detail clarification gate that batches questions after outline confirmation.
- Mandatory planning default: every new PRD/full draft confirms plan, Feature List, and outline; use `planning-with-files-zh` for new PRDs, multi-source Confluence tasks, source-heavy, browser-heavy, or multi-turn work.
- Initial draft validation flow: Discovery Summary, Proposed Outline, outline confirmation, detail clarification table, and Draft Readiness Check.
- A Confluence-ready template that uses one Jira/Epic traceability row instead of duplicating `Request Info` and `Epic`.
- Lightweight Scope default: `Markets`, `Tenant`, and `Channel` when channel scope matters.
- No standalone `In Scope` by default; optional `Out of Scope` only for real exclusions.
- Feature List before Feature Details: `Index | Feature | Description | Remark`.
- Compact Feature Details: `Feature | Detail | UI/Diagram`, with nested tables only when useful.
- Bilingual rule for long Feature Detail blocks: Chinese first, then `English Version:`.
- A rule that final Confluence drafts should not contain local-only relative links.
- A default that initial-draft Background is short English context, with detailed evidence moved into later sections.
- A Decision Layer / Pre-check / Suppression outline pattern for Chaser-style PRDs.
- Table-first Feature Detail guidance, using current/target behavior only when useful for the selected feature row.
- Optional late sections rule: Rollout, standalone Acceptance Criteria, and standalone Dependencies are included only when materially useful.
- Checklist gates using a numbered table: `# | 缺口 | 为什么影响 | 默认假设 | 需要你确认`.
- Local-only frontend/code discovery guidance.
- A local inventory helper script.
- A controlled iteration rule: learn durable preferences from user corrections, avoid storing one-off PRD facts, and validate after every skill update.
