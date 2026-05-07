# PRD Skill Patterns

Use these patterns when designing a personalized PRD copilot.

The distiller's main job is author distillation. Use generic PRD skills as ingredients, but the generated `pm-xxx` skill should primarily encode the author's repeated habits, judgment, historical logic, and anti-patterns.

## Patterns to Adopt

- Discovery before drafting: read source materials, understand current behavior, then draft.
- Author distillation before generation: extract confirmed habits, inferred habits, historical logic modules, review preferences, recurring corrections, and anti-patterns before writing the target skill.
- Writing-style preservation: preserve the PM's voice, structure, omissions, table style, and level of detail; improve clarity without making the output generic or corporate.
- Knowledge delta: encode PM-specific decision rules and anti-patterns, not generic "how to write a PRD" content the model already knows.
- Profile scoring: use quality scoring as a distiller gate. If author evidence is weak, ask targeted questions or output profile gaps instead of pretending the PM model is complete.
- Scoping before details: define problem, goals, non-goals, source of truth, and product boundary.
- Outline confirmation before full drafting: propose the PRD structure and wait for confirmation before writing a complete initial draft.
- Detail clarification after outline confirmation: batch P0/P1 gaps in one numbered table.
- Draft readiness before writing: confirm scope dimensions, table-first Feature Detail, and optional late sections.
- Structured PRD sections: Problem, Goals, Non-goals, Users/Scenarios, P0/P1/P2 scope, Functional Requirements, NFR, Metrics, Rollout, Open Questions.
- Success criteria: each major requirement should have acceptance criteria or measurable behavior.
- Evaluation/rollout: include rollout, monitoring, and quality gates when the feature changes user-facing workflows or model behavior.
- Traceability: connect requirements back to BRD/FRF/local PRD/source code evidence.
- Confluence publishing: final drafts should use reader-openable links and include Jira/request traceability in the top metadata table when available.
- Review checklist: check source grounding, missing edge cases, state handling, metrics, dependencies, and unresolved questions.
- Mandatory planning: every new PRD/full draft confirms plan, Feature List, and outline before drafting; use `planning-with-files-zh` for new PRDs, multi-source Confluence tasks, source-heavy, browser-heavy, or multi-turn work.
- Decision-layer PRDs: for pre-check, gating, or suppression changes, describe current/target behavior only inside the relevant Feature Detail row/subsection.
- Table-first Feature Detail: use compact `Feature | Detail | UI/Diagram` tables by default.
- Requirement Brief fallback: when problem, target user, source of truth, or core flow is unclear after discovery, output a requirement brief instead of a fake complete PRD.
- Auto Enrich: fill gaps by writing them into Feature Details, Data Tracking, NFR, Success Metrics, or Open Questions; do not spawn unnecessary late chapters.
- Review Board: when preparing for requirement review, use Product/Engineering/QA/Ops roles by default and classify issues as Blocker/Major/Minor with a Pass/Conditional Pass/Fail verdict.
- Confluence discovery: when the user's PRD library is in Confluence, read/search relevant Confluence pages before inferring style or drafting. For new PRDs and full drafts, use "No Confluence source map, no full draft" when historical logic matters.
- Metadata precision: do not create both `Request Info` and `Epic`; use one traceability row such as `Jira / Epic`, unless the target Confluence page already uses a different label.
- Lightweight Scope: default to `Markets`, `Tenant`, and `Channel` when channel scope matters; put module, role, permission, and system-boundary details in Feature List or Feature Details only when relevant.
- Feature List first: use `Index | Feature | Description | Remark` as the confirmed outline before writing Feature Details.
- Scope boundary: do not add standalone `In Scope` by default; add `Out of Scope` only for real exclusions.
- Compact Feature Detail: default to `Feature | Detail | UI/Diagram`; add nested tables only for real product dimensions.
- Bilingual long details: keep headings/background/terms English when suitable, but use Chinese first plus `English Version:` for long Feature Detail blocks.
- Mandatory confirmation: new PRDs/full drafts must confirm plan, Feature List, and outline before drafting.

## Patterns to Avoid

- One fixed "full PRD" flow for every request.
- Heavy project-management templates when the task is only section rewrite or requirement clarification.
- Asking many questions before reading available sources.
- Skipping Confluence search when the provided Confluence entry page is empty or only an index.
- Treating an unread Confluence link as evidence.
- Treating PM's manual workflow as the optimal agent workflow.
- Copying generic PRD templates without adapting to local product modules and existing document style.
- Treating external PRD skills as authoritative over the target PM's actual Confluence history.
- Distilling one-off page quirks as durable author habits.
- Adding generic "professional" wording that erases the PM's established PRD voice.
- Putting local-only relative links into a PRD meant for Confluence readers.
- Expanding Background into a detailed evidence dump when the PM expects a short initial context.
- Creating planning files for every PRD by default.
- Auto-generating Rollout, standalone Acceptance Criteria, and standalone Dependencies when they do not materially help review.
- Over-specifying Scope with role/module/system rows when the PM's Confluence style only needs Markets/Tenant/Channel.
- Adding product-irrelevant engineering narration, code paths, database internals, owner routing, or prompt internals to Feature Details.

## Recommended Agent Modes

- Context: source map and problem understanding.
- Outline: PRD structure and missing inputs.
- Interview: targeted questions ordered by blocking impact.
- Section Rewrite: rewrite only selected parts and identify dependent sections.
- Review: issue-first PRD critique.
- Consistency: align scope, triggers, states, metrics, and open questions after edits.
- Draft: full PRD only when sources and assumptions are explicit.
