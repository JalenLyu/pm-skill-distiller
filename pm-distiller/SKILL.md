---
name: pm-distiller
description: Use when the user wants to distill a PM's PRD habits, source-reading workflow, review preferences, historical decisions, and recurring corrections into a personalized PRD copilot skill such as pm-jalen, or refresh an existing pm-xxx skill from read-only Confluence and local materials.
---

# PM Skill Distiller

Use this skill as a **PM Skill Distiller**. It does not write product PRDs directly. Its core job is to distill source materials into a personalized PRD copilot: discover sources, extract the PRD author's habits, style, historical logic, product modules, and review preferences, then produce or update a user-specific skill such as `pm-jalen`.

## Inputs

Require or infer:

- User name or handle, such as `Jialun Lv` / `jialun.lv`.
- One or more Confluence root/page links.
- One local folder containing PRDs, BRDs, FRFs, PDFs, exports, or frontend code.

If a blocking input is missing, ask one concise question. Otherwise proceed and state assumptions.

## Source Rules

- Treat Confluence as read-only.
- If the user's PRD library is in Confluence, `skill-confluence` discovery is a required source step, not a passive reference.
- Before inferring author style or generating a `pm-xxx` skill, explicitly invoke `skill-confluence` or run `skynet-base confluence read/search` to find same-author PRD/BRD/FRF pages.
- Do not claim the distiller has learned a PM's Confluence style unless same-author Confluence pages were read or the user explicitly accepts a local-only V0.
- Treat Google Docs, Google Sheets, Figma, Jira, dashboards, and SeaTalk links as references to record, not sources to read in V0.
- Local Markdown and exported text files are source material; PDFs can be indexed by filename unless the user asks for extraction.
- If the user provides frontend code, inspect it as local files. Do not assume APIs, routes, labels, or field names without code or document evidence.
- Do not add telemetry, external network calls, or credentials.

## Workflow

1. **Discover sources**
   - Load `skill-confluence` when available.
   - Read the Confluence entry page with `skynet-base confluence read "<PAGE_URL_OR_ID>" --body-format markdown --raw`.
   - Search same-author PRDs with `skynet-base confluence search "<user handle>" "PRD" --space SCPM --limit 10`.
   - Search product/module PRDs with `skynet-base confluence search "<product/module>" "<user handle>" --space SCPM --limit 10`.
   - Search feature/history docs with `skynet-base confluence search "<module keyword>" "PRD" "<user handle>" --space SCPM --limit 10`.
   - If the entry page is empty or only a container, do not infer style from it; search Confluence and read the relevant PRD/BRD/FRF pages first.
   - Inventory local files with `scripts/local_context_inventory.py` or `rg --files`.
   - Identify source types: PRD, BRD, FRF, TD, design link, data sheet link, dashboard link, frontend code.

2. **Build a source map**
   - Group materials by product area, module, date, and owner.
   - Mark likely source of truth and stale/secondary materials.
   - Include Confluence search keywords, pages read, page IDs/URLs, authorName/FPM signal, last modified date, and evidence status.
   - Capture unreadable external links as dependency references.

3. **Infer the PM profile**
   - Current work modules and recurring product boundaries.
   - PRD writing style, language pattern, expected level of detail, and common section structure.
   - Review preferences: scope, metrics, rollout, acceptance criteria, edge cases, open questions.
   - Collaboration style: how much the agent should ask before drafting.
   - Author model: repeated decisions, preferred omissions, recurring corrections, anti-patterns, and historical logic habits that make the generated copilot think more like the PM.
   - Continuous learning model: how future user corrections should be classified, confirmed, written into references, and validated without turning the skill into a PRD archive.
   - Evidence weight: same-author current Confluence PRDs beat local drafts; repeated patterns beat one-off page quirks; user corrections beat generic PM skill templates.

4. **Choose copilot modes**
   - Do not force one fixed PRD flow. Select modes based on user intent.
   - Learn from proven PRD skills: discovery before drafting, source-grounded outlines, outline confirmation before full drafting, detail clarification gates, goals/non-goals, P0/P1/P2 scope, FR/NFR, success criteria, rollout/evaluation, traceability, and a quality checklist.
   - Add three learned modes: Requirement Brief when information is insufficient, Auto Enrich that writes gaps back into existing sections, and Review Board with Blocker/Major/Minor severity.
   - Preserve Jialun-style Confluence PRD patterns when evidence supports them: single Jira/Epic traceability row, lightweight `Markets`/`Tenant`/`Channel` Scope, Feature List before Feature Details, compact `Feature | Detail | UI/Diagram` details, optional Out of Scope only for real exclusions, and bilingual long requirement blocks.
   - For Confluence PRDs, preserve the PM's publishing format: top metadata table with request/Jira traceability, no local-only links in the final draft, concise Background for initial drafts.
   - Encode mandatory planning/confirmation gates before full PRD drafting. Use `planning-with-files-zh` for new PRDs, multi-source Confluence work, or source-heavy/multi-turn work.
   - Encode "No Confluence source map, no full draft" for Confluence-backed PRDs: generated skills must search historical PRD/BRD/FRF pages by user, module, feature keywords, and PRD before scoping.
   - Include table-first Feature Detail and Decision Layer / Pre-check / Suppression patterns for existing-flow optimization PRDs.
   - Keep the PM copilot lightweight; avoid heavyweight project-management templates unless the source materials require them.

5. **Generate the skill blueprint**
   - Use `references/skill-blueprint.md` for the target file layout.
   - Use `references/author-distillation.md` to produce the author model before writing the generated skill.
   - Use `references/continuous-learning.md` to give generated `pm-xxx` skills a controlled iteration loop from future PRD feedback.
   - Use `references/profile-schema.md` for the user profile.
   - For a stable V0.1 personal copilot, prefer `scripts/create_pm_copilot.py` over hand-written file creation.
   - Write a concise `SKILL.md` and route detailed material into `references/`.

6. **Validate**
   - Run the skill-creator `quick_validate.py` against generated skills.
   - Spot-check that the target skill does not accidentally claim unsupported sources.

## Output Contract

When only drafting the architecture, output:

- Proposed skill name.
- Source map summary.
- User/work profile summary.
- Reference file plan.
- Distilled author model summary.
- Continuous learning / preference update rules.
- Open design decisions.

When creating the skill, edit files directly and report:

- Files created or changed.
- Validation command and result.
- Whether generated `pm-xxx` includes `continuous-learning.md` and a Learning Check mode.
- Known gaps for the next iteration.

## Quick Generator

After discovery, run the deterministic generator:

```bash
python3 /Users/jialun.lv/.codex/skills/pm-distiller/scripts/create_pm_copilot.py \
  --skill-name pm-example \
  --user-name "Example PM" \
  --confluence-url "https://confluence.shopee.io/display/SPACE/Page" \
  --local-folder "/path/to/prd/folder" \
  --path /Users/jialun.lv/.codex/skills
```

Use `--dry-run` first when the user has not confirmed the generated profile. Use `--force` only when intentionally refreshing an existing skill.

## References

- `references/discovery-workflow.md`: source discovery and evidence rules.
- `references/confluence-discovery.md`: direct Confluence read/search protocol.
- `references/author-distillation.md`: how to distill author habits, style, knowledge modules, and recurring failure modes.
- `references/continuous-learning.md`: how generated PRD copilots should turn future PRD corrections into controlled skill updates.
- `references/generation-workflow.md`: deterministic PM copilot generation flow.
- `references/prd-skill-patterns.md`: patterns adapted from PRD writer and PM skills.
- `references/profile-schema.md`: target PM profile schema.
- `references/skill-blueprint.md`: recommended generated skill structure.
- `references/frontend-code-discovery.md`: optional local frontend/code inspection layer.
- `references/validation-checklist.md`: distiller and generated-skill checks.
