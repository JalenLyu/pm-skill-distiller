#!/usr/bin/env python3
"""Generate a stable V0.1 personalized PRD copilot skill."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from datetime import date
from pathlib import Path


REFERENCE_FILES = [
    "source-router.md",
    "confluence-discovery.md",
    "continuous-learning.md",
    "user-prd-profile.md",
    "work-map.md",
    "prd-copilot-modes.md",
    "new-prd-template.md",
    "confluence-draft-workflow.md",
    "checklist-gates.md",
    "outline-patterns.md",
    "question-playbook.md",
    "quality-checklist.md",
    "frontend-code-discovery.md",
]


def normalize_skill_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    name = re.sub(r"-{2,}", "-", name)
    if not name:
        raise SystemExit("Skill name is empty after normalization.")
    if len(name) > 64:
        raise SystemExit("Skill name must be 64 characters or fewer.")
    return name


def safe_name(value: str) -> str:
    return value.replace('"', "'").strip()


def detect_handles(user_name: str) -> list[str]:
    parts = [p for p in re.split(r"\s+", user_name.strip()) if p]
    handles = []
    if parts:
        handles.append(".".join(p.lower() for p in parts))
        handles.append(parts[0].lower())
    return sorted(set(handles))


def collect_local_docs(root: Path, max_files: int = 80) -> list[dict[str, object]]:
    if not root.exists():
        return []
    doc_exts = {".md", ".txt", ".csv", ".pdf", ".ppt", ".pptx", ".doc", ".docx"}
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", "dist", "build", ".next"}]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() not in doc_exts:
                continue
            rel = path.relative_to(root)
            item: dict[str, object] = {
                "path": str(rel),
                "ext": path.suffix.lower(),
                "size": path.stat().st_size if path.exists() else None,
            }
            if path.suffix.lower() in {".md", ".txt"}:
                headings = []
                try:
                    with path.open("r", encoding="utf-8", errors="ignore") as fh:
                        for line in fh:
                            if heading_re.match(line):
                                headings.append(line.strip())
                            if len(headings) >= 8:
                                break
                except OSError:
                    headings = []
                item["headings"] = headings
            results.append(item)
            if len(results) >= max_files:
                return results
    return results


def infer_clusters(docs: list[dict[str, object]]) -> list[str]:
    clusters = []
    seen = set()
    for doc in docs:
        path = str(doc["path"])
        first = path.split("/", 1)[0]
        if "/" not in path:
            first = "root"
        if first not in seen:
            seen.add(first)
            clusters.append(first)
    return clusters[:12]


def md_list(values: list[str]) -> str:
    if not values:
        return "- TBD"
    return "\n".join(f"- {v}" for v in values)


def source_rows(urls: list[str], local_folder: str) -> str:
    rows = [f"| Local folder | {local_folder} | Editable local source material |"]
    for idx, url in enumerate(urls, 1):
        rows.append(f"| Confluence {idx} | {url} | Read-only reference |")
    return "\n".join(rows)


def render_files(args: argparse.Namespace, docs: list[dict[str, object]]) -> dict[str, str]:
    skill_name = normalize_skill_name(args.skill_name)
    user_name = safe_name(args.user_name)
    handles = detect_handles(user_name)
    confluence_urls = args.confluence_url or []
    local_folder = str(Path(args.local_folder).expanduser()) if args.local_folder else "TBD"
    clusters = infer_clusters(docs)
    today = date.today().isoformat()
    display_name = args.display_name or user_name
    short_desc_name = display_name.split()[0] if display_name else skill_name

    doc_lines = []
    for doc in docs[:24]:
        doc_lines.append(f"- `{doc['path']}` ({doc['ext']})")
    representative_docs = "\n".join(doc_lines) if doc_lines else "- TBD after discovery"

    files: dict[str, str] = {}

    files["SKILL.md"] = f"""---
name: {skill_name}
description: Personalized PRD copilot for {user_name}, distilled from this PM's PRD habits, writing style, historical decisions, product knowledge modules, review preferences, and recurring corrections. Use when this PM asks to prepare, outline, write, rewrite, review, or iterate product requirement documents from local PRD materials and read-only Confluence context, especially for PM discovery, scoping, question-driven drafting, section-level rewrites, new PRD templates, and consistency checks.
---

# {display_name} PRD Copilot

Use this skill as {user_name}'s personal PRD copilot. It should act from the distilled author model in `references/author-model.md`: read the right sources, ask the right questions, use the PM's usual PRD structure, preserve repeated omissions, and review against the PM's known concerns. It should not blindly generate a full PRD unless explicitly asked and the outline has been confirmed.

## Default Stance

- Default language: {args.default_language}.
- Prefer local files for working drafts and intermediate edits. Treat Confluence as the final publishing surface and Google Sheets, Google Docs, Figma, Jira, dashboards, and chat links as read-only references unless explicitly told otherwise.
- Keep outputs compact and scannable, but not cryptic.
- Separate issue/problem, expected outcome, actions/solution, next steps, and open questions.
- Do not invent APIs, configs, timelines, field names, owner names, or metrics. If unsure, search local materials first.

## Mode Selection

Pick the smallest useful mode instead of forcing a fixed flow.

| User intent | Mode | Output |
|---|---|---|
| "先了解/查资料/我现在做什么" | Context | source map, work understanding, known facts, gaps |
| "帮我搭大纲/PRD结构" | Outline | recommended outline, section purpose, missing inputs |
| "需求不清楚/帮我问问题" | Interview | blocking questions first, optional questions second |
| "信息太少/还没想清楚" | Requirement Brief | current understanding, key questions, options, next step |
| "新建PRD/给我模板/填Confluence模板" | New PRD Template | Confluence-ready skeleton plus batch missing-info table |
| "补漏/完善异常/埋点/NFR" | Auto Enrich | section-targeted additions without creating unnecessary chapters |
| "改这一段/优化这个章节" | Section Rewrite | revised section plus impacted sections |
| "帮我review PRD" | Review | findings, risks, missing decisions, checklist result |
| "过会前检查/多角色评审" | Review Board | Blocker/Major/Minor risks, verdict, re-review list |
| "改完帮我检查一致性" | Consistency | scope/trigger/state/data/metrics/open-question alignment |
| "这个偏好以后记住/优化skill/为什么又跑偏" | Learning Check | durable preference extraction and proposed skill patch |
| "直接写完整PRD" | Draft | only after source map and assumptions are explicit |

See `references/prd-copilot-modes.md`, `references/new-prd-template.md`, `references/checklist-gates.md`, and `references/continuous-learning.md` for detailed mode behavior.

## New PRD Critical Path

For a new PRD, use this path unless the user explicitly asks for a narrow section only:

1. Discovery Summary: briefly state what was read, source authority, current understanding, and unresolved gaps.
2. Mandatory Confluence Historical Logic Check: before scoping or drafting, use `skill-confluence` / `skynet-base confluence read/search` to read the provided page and search historical PRD/BRD/FRF pages by user handle, product/module keywords, feature keywords, and `PRD`.
3. Mandatory Planning Gate: propose a source-grounded plan, Feature List draft, and Confluence-ready outline; wait for user confirmation before writing the full draft.
4. Preflight: ask once for missing Confluence PRD link, Jira/Epic links, PRD title, people involved, and related docs.
5. Detail Clarification Gate: batch P0/P1 detail gaps after the plan/outline is confirmed, before filling Feature Details.
6. Draft Readiness Check: confirm scope shape, feature-detail structure, and optional late sections before drafting.
7. Draft/Paste-ready: write Confluence-ready content without local-only markdown links unless the user asks to maintain a local draft.

If the user already provides a Confluence PRD link, treat that page as the target publishing context. Do not ask whether to create a page.
If discovery leaves the problem, target user, or core flow unclear, enter Requirement Brief mode instead of writing a full PRD.
No Confluence source map, no full draft: if the PRD depends on Confluence history and Confluence cannot be searched, report the failure and ask whether to continue from local/user-provided sources only.

## Planning Default

- New PRD, full draft, or Confluence-source PRD work must use a planning/confirmation gate before drafting: Discovery Summary -> Proposed Plan -> Feature List -> Outline Gate -> Detail Clarification Gate -> Draft Readiness Check.
- Use in-chat planning for narrow edits and short one-source PRDs.
- Use `planning-with-files-zh` for new PRDs, multi-source Confluence tasks, browser/code-heavy discovery, or any task likely to span multiple turns. Create planning files only for those cases, then wait for user confirmation before drafting.

## Source Routing

1. Before new PRD/full draft work, run a Confluence historical logic check when the source library is Confluence: search by user handle/name plus product/module/feature keywords, read the relevant pages, and include the result in the source map.
2. Use local Markdown PRDs in the current folder or user-provided path as editable working material and style examples.
3. Record but do not read external Google/Figma/Jira links in V0 unless another explicitly invoked skill handles them.
4. If a frontend repo or local web code path is provided, inspect code to understand existing B-side UI behavior before writing requirements.
5. For new Confluence PRDs, assume the PM creates the Confluence page and provides the link; do not ask whether to create a page.
6. If materials conflict, state which source is newer or more authoritative and ask only if the decision changes the PRD.

Use `skill-confluence` / `skynet-base confluence read/search` when available. Read `references/source-router.md`, `references/confluence-discovery.md`, and `references/confluence-draft-workflow.md` before multi-source or Confluence-ready PRD work.

## PRD Style

This PM's PRD style should be inferred from `references/author-model.md` and `references/user-prd-profile.md`, then refined over time. Default to:

- Background should usually be short English product context for initial drafts; keep detailed evidence in Current Logic, Problem, or Feature Details.
- Objective that maps to specific system behavior.
- Scope should stay lightweight and usually include `Markets`, `Tenant`, and `Channel` when channel scope matters, such as Chat Channel. Put module/role/system details in Feature List or Feature Details only when needed.
- Do not add a standalone `In Scope` section by default; it usually duplicates Feature List. Add `Out of Scope` only for explicit exclusions that prevent reviewer misunderstanding.
- Add a Feature List before Feature Details for new PRDs: `Index | Feature | Description | Remark`.
- Feature Detail should be structured and compact, usually `Feature | Detail | UI/Diagram`. Avoid product-irrelevant engineering narration.
- For existing-flow optimization, decision-layer, pre-check, gating, or suppression PRDs, describe Current/Target behavior only where it helps the selected feature row; do not force a long row template.
- Functional details that distinguish user-facing UI, system logic, model behavior, data tracking, metrics, rollout, and open questions.
- For long requirement descriptions, use Chinese and English as two separate paragraphs/blocks. Headings, product names, terms, and short Background can stay English only.
- Section-level iteration: update the selected section and then check dependent tables, diagrams, acceptance criteria, and metrics.

Read `references/author-model.md`, `references/user-prd-profile.md`, `references/outline-patterns.md`, `references/quality-checklist.md`, and `references/continuous-learning.md` when writing, reviewing, or updating the skill from user feedback.

## Checklist Gates

Do not ask checklist items one by one. Batch them at the right trigger point with a numbered table:

| # | 缺口 | 为什么影响 | 默认假设 | 需要你确认 |
|---|---|---|---|---|

Use P0 rows for blockers, P1 rows for quality improvements, and continue with explicit assumptions when the gap is not blocking.

## Continuous Learning

When the user corrects a PRD output, asks why the skill repeated a mistake, or says a preference should be remembered, run a Learning Check before editing the skill:

1. Separate one-off PRD facts from durable PM preferences.
2. Classify durable feedback as Template Preference, Writing Style, Workflow Preference, Domain Knowledge, or Review Preference.
3. Propose the exact skill file(s) to update in a compact table.
4. Update the skill only after explicit confirmation such as "可以", "继续", "以后默认这样", or "优化skill".
5. Validate the changed skill with `quick_validate.py`.

Do not store Jira IDs, private local draft links, one-time feature decisions, or source facts as preferences. Store only the reusable rule or anti-pattern. Use `references/continuous-learning.md` for the full write-location map and update threshold.

## Local Discovery Helpers

- Use `rg --files`, `rg`, and targeted `sed` reads first.
- Optionally run `scripts/local_prd_inventory.py <path>` to summarize local PRD files and headings.
- For frontend code, use `references/frontend-code-discovery.md` and inspect routes, components, labels, i18n keys, API clients, state machines, and existing interaction behavior.

## Domain Routing

If one product/domain dominates the task and has many modules or terms, prefer a dedicated domain skill when available. If no domain skill exists yet, use `references/work-map.md` as the local domain map.
"""

    files["agents/openai.yaml"] = f"""interface:
  display_name: "{display_name} PRD"
  short_description: "{short_desc_name}'s personal PRD copilot."
  default_prompt: "Use ${skill_name} to help me prepare, outline, review, or improve a PRD from my local materials."
policy:
  allow_implicit_invocation: true
"""

    files["references/source-router.md"] = f"""# Source Router

Generated: {today}

## Known Sources

| Source | Value | Role |
|---|---|---|
{source_rows(confluence_urls, local_folder)}

## Priority

1. Confluence PRD library/root/page when provided, or when the user's PRD source library is known to live in Confluence.
2. Local Markdown PRDs in the current task folder or explicitly provided folder.
3. Local exports and material files: CSV, TXT, extracted docs, PDFs by filename or extracted content when requested.
4. Local frontend code when the task depends on existing B-side web behavior.
5. External links to Google Docs/Sheets, Figma, Jira, dashboards, and chat tools are dependency references in V0 unless another skill/tool is explicitly invoked.

## Confluence Discovery

- If the user provides a Confluence URL, read it before proposing scope or outline.
- If the Confluence page body is empty, only an index, or only a target draft shell, search Confluence with user handle plus product/module keywords.
- For new PRDs and full drafts, search Confluence with feature keywords from the request before scoping. No Confluence source map, no full draft when historical logic matters.
- Read the top relevant PRD/BRD/FRF/TD pages, then stop when there is enough evidence for the requested mode.
- Use `skill-confluence` or:

```bash
skynet-base confluence read "<PAGE_URL_OR_ID>" --body-format markdown --raw
skynet-base confluence search "<product/module>" "{handles[0] if handles else user_name}" --space SCPM --limit 10
```

- Record page title, page ID/URL, last modified date, and evidence status in the Discovery Summary.
- Do not directly edit Confluence.

## Editable Destination

- Prefer local files.
- Do not directly edit Confluence or Google Sheets.
- For a new Confluence PRD, assume the PM creates the page and sends the link. Do not ask whether to create a Confluence page.
- Use the provided Confluence link as the target location/reference and prepare Confluence-ready content locally or in chat, following workspace rules.
- Do not include local-only relative links in Confluence-ready content. Convert them to Confluence/external links when available, or keep them as private working notes.
- If the local editable destination is unclear, ask before writing local files.

## Conflict Handling

- Prefer newer version history in local PRD when it is the active working doc.
- Prefer BRD/FRF for business background and scope intent.
- Prefer TD/code for implementation constraints and current behavior.
- If two sources disagree on product intent, state the conflict and ask.

## Search Patterns

```bash
rg --files
rg -n "PRD|BRD|FRF|Background|Objective|Scope|Out of Scope|Feature Detail|Data Tracking|Metrics|Open Questions" -g "*.md"
rg -n "{user_name}|{'|'.join(handles) if handles else user_name}|Issue|Summary|SOP|Order|Case|Prompt|loading" -g "*.md" -g "*.csv"
skynet-base confluence search "<product/module>" "{handles[0] if handles else user_name}" --space SCPM --limit 10
skynet-base confluence search "<module keyword>" "PRD" "{handles[0] if handles else user_name}" --space SCPM --limit 10
```
"""

    files["references/confluence-discovery.md"] = CONFLUENCE_DISCOVERY
    files["references/continuous-learning.md"] = CONTINUOUS_LEARNING

    files["references/user-prd-profile.md"] = f"""# User PRD Profile

## User

- Name: {user_name}.
- Handles: {", ".join(handles) if handles else "TBD"}.
- Default explanation language: {args.default_language}.
- Product writing language: preserve product/system names, field names, events, buttons, and metrics as written in source materials. Use English headings/background/terms by default; use Chinese first plus `English Version:` for long Feature Detail blocks when needed.

## Source Environment

- Local folder: `{local_folder}`.
- Confluence roots:
{md_list(confluence_urls)}
- Unsupported V0 live reads: Google Docs/Sheets, Figma, Jira, dashboards, and chat links unless another skill/tool is explicitly invoked.

## Working Style

- Source-grounded outputs first; broad drafting second.
- Use local files as working artifacts, but prepare PRDs for Confluence readers when the task is a new PRD.
- Prefer small, reviewable document changes.
- Use existing local PRDs and actively read/search Confluence context before asking broad questions.
- Ask batched blocking questions instead of one-by-one checklist questions.
- For new PRDs/full drafts, first establish context, then propose and confirm a plan, Feature List, and outline before writing.
- Use `planning-with-files-zh` for new PRDs, multi-source Confluence tasks, source-heavy, browser-heavy, or multi-turn work.

## PRD Style Defaults

- New PRD pages commonly start with a compact top metadata table: `Jira / Epic`, `Related Document`, and `People Involved`.
- Do not create both `Request Info` and `Epic`; if the target page already uses `Request Info`, treat it as the Jira/Epic traceability row.
- Initial-draft Background should usually be short English product context. Move detailed analysis, experiment evidence, and metric findings into Current Logic, Problem, Feature Details, Data Tracking, or Open Questions.
- Objective maps to user/system behavior.
- Scope is lightweight and usually includes `Markets`, `Tenant`, and `Channel` when channel scope matters.
- Do not add standalone `In Scope` by default because it usually duplicates Feature List. Use `Out of Scope` only for explicit exclusions.
- Feature details are module-level and scenario-based.
- Add Feature List before Feature Details for new PRDs: `Index | Feature | Description | Remark`.
- Tables are preferred for Feature List, Feature Details, transify, metrics, and open questions.
- Feature Detail should be table-first and compact, usually `Feature | Detail | UI/Diagram`.
- Current/target behavior, Before/After, state handling, and edge cases should appear only when useful for that feature.
- Edge cases, loading/empty/fail/retry states, data tracking, success metrics, rollout, and open questions should be checked.
- Rollout, standalone Acceptance Criteria, and standalone Dependencies are optional late sections; include them only when they materially help review or launch.

## To Refine

- Product/domain-specific terminology.
- Preferred PRD section order.
- Reviewer expectations.
- Common metrics and rollout style.
"""

    files["references/author-model.md"] = f"""# Author Model

This is the distilled author model for {user_name}. Treat it as V0 until more same-author Confluence PRDs, local drafts, and user corrections are reviewed.

## Evidence Basis

- User name: `{user_name}`.
- Detected handles: {", ".join(handles) if handles else "TBD"}.
- Local folder: `{local_folder}`.
- Confluence roots:
{md_list(confluence_urls)}

Evidence priority:

1. Explicit user correction in the current thread.
2. Same-author, recent Confluence PRD in the same product area.
3. Same-author Confluence PRD in adjacent product areas.
4. Local active draft with recent edits.
5. Historical local/exported PRD.
6. External PRD or PM skills.

## Confirmed Habits

- Discovery before drafting; do not jump into a full PRD from a thin prompt.
- Confluence context is read-only and final drafts should be Confluence-ready.
- Use a source map before outline or draft when Confluence history matters.
- Confirm plan, Feature List, and outline before full drafting.
- Batch missing information in numbered tables instead of asking one-by-one.
- When a PRD correction is reusable, turn it into a Learning Check and update the skill only after confirmation.

## Inferred Habits

- Prefer compact Background and table-first Feature Details.
- Prefer section-level iteration and consistency checks after edits.
- Prefer explicit assumptions over hidden invention.

## PRD Style Model

- Top metadata table should use one traceability row such as `Jira / Epic`; do not duplicate `Request Info` and `Epic`.
- Scope should stay lightweight: `Markets`, `Tenant`, and `Channel` when channel scope matters.
- Do not add standalone `In Scope` by default; use `Out of Scope` only for real exclusions.
- Add Feature List before Feature Details for new PRDs.
- Default Feature Detail shape: `Feature | Detail | UI/Diagram`.
- Use Chinese first plus `English Version:` only for long requirement blocks.

## Historical Logic Modules

Initial local evidence suggests these possible modules. Treat them as routing hints, not confirmed requirements:

{md_list(clusters)}

## Review Preferences

- Source grounding and historical logic checked before drafting.
- Scope does not drift into role/module/system details unless useful.
- Feature Details are structured and not overloaded with product-irrelevant engineering narration.
- Late sections such as Rollout, standalone Acceptance Criteria, and Dependencies are included only when review risk requires them.
- Review Board mode should return Blocker/Major/Minor findings, verdict, and re-review list.

## Recurring Corrections To Preserve

- Do not put local-only links into Confluence-ready PRDs.
- Do not over-expand Background.
- Do not skip Confluence search when historical logic is needed.
- Do not proceed to full draft without outline confirmation for new/full PRDs.
- Do not let generic PRD templates override the PM's observed Confluence format.
- Do not silently absorb one-off PRD facts into the skill; only durable preferences, recurring corrections, and confirmed style rules should be learned.

## Profile Gaps

- Product/domain terminology should be refined after reading more same-author Confluence pages.
- Module-specific historical logic should be refined per PRD task.
- Reviewer expectations, metrics style, and rollout style should remain explicit assumptions until source evidence confirms them.
"""

    files["references/work-map.md"] = f"""# Work Map

Generated from initial local folder inventory and provided source links. Treat this as V0 and refine after reading more source materials.

## Source Clusters

{md_list(clusters)}

## Representative Local Materials

{representative_docs}

## Confluence Roots

{md_list(confluence_urls)}

## Domain Skill Route

If one domain repeatedly appears across many PRDs, split that material into a companion domain skill rather than bloating this personal PM skill.
"""

    files["references/prd-copilot-modes.md"] = PM_MODES
    files["references/new-prd-template.md"] = NEW_PRD_TEMPLATE
    files["references/confluence-draft-workflow.md"] = CONFLUENCE_WORKFLOW
    files["references/checklist-gates.md"] = CHECKLIST_GATES
    files["references/outline-patterns.md"] = OUTLINE_PATTERNS
    files["references/question-playbook.md"] = QUESTION_PLAYBOOK
    files["references/quality-checklist.md"] = QUALITY_CHECKLIST
    files["references/frontend-code-discovery.md"] = FRONTEND_DISCOVERY
    files["scripts/local_prd_inventory.py"] = LOCAL_PRD_INVENTORY_SCRIPT
    return files


CONFLUENCE_DISCOVERY = """# Confluence Discovery

Use this before PRD scoping when the user provides a Confluence page/root, when the relevant PRD library is in Confluence, or when local files are only working drafts. For new PRDs and full drafts, this is a mandatory historical logic check.

## Rules

- Read-only only. Do not create, update, or delete Confluence pages.
- Prefer `skill-confluence` or `skynet-base confluence` when available.
- Treat unread links as references, not evidence.
- Cite page title, page ID or URL, authorName/FPM signal, and last modified date in the working source map.
- No Confluence source map, no full draft when the requirement depends on historical Confluence logic.
- If Confluence access fails, report the exact failure and continue with local sources only if the user accepts that limitation or the task is narrow enough.

## Discovery Protocol

1. Read the provided Confluence URL or page ID.
   - If the body has PRD content, classify it as active PRD, BRD/FRF, TD, source index, or target draft page.
   - If the body is empty or only a container, search instead of treating it as the source of truth.
2. Search Confluence with batched keywords and record the actual query terms:
   - user handles and name
   - product/module keywords
   - feature keywords from the user's request
   - document type: `PRD`, `BRD`, `FRF`, `requirement`
3. Read only the top relevant pages needed for the current PRD task.
4. Build a source map:
   - source type
   - title / page ID / URL
   - authorName / FPM / owner signal
   - last modified date
   - relevance to Background, Scope, Current Logic, Feature Detail, Metrics, or Open Questions
5. Use Confluence docs to infer PRD style only after separating style examples from factual requirement sources.

## Commands

```bash
skynet-base confluence read "<PAGE_URL_OR_ID>" --body-format markdown --raw
skynet-base confluence search "<product/module>" "<user handle>" --space SCPM --limit 10
skynet-base confluence search "<module keyword>" "PRD" "<user handle>" --space SCPM --limit 10
```

If `read` reports that full content was saved to a local cache file, read only the relevant segments from that cache and keep the Confluence page as the cited source.

## Discovery Summary Shape

```markdown
## Discovery Summary

| Source | Type | Why it matters | Evidence status |
|---|---|---|---|
| <Confluence title / pageId> | PRD / BRD / FRF / index / target draft | <use> | Read / unread / failed |

### Search Keywords
- <keywords actually searched>

### Current Understanding
- <confirmed facts>

### Gaps
| # | 缺口 | 为什么影响 | 默认假设 | 需要你确认 |
|---|---|---|---|---|
```
"""


CONTINUOUS_LEARNING = """# Continuous Learning

Use this when user feedback on a PRD output may need to become a durable rule for this PM copilot.

## Trigger

Run a Learning Check when:

- The user says "以后", "默认", "记住", "不要再", "为什么又跑偏", or "优化 skill".
- The same correction appears in two or more PRD tasks.
- A review finds a repeated failure pattern that is not already captured in the skill.
- Same-author Confluence evidence confirms a recurring PRD format or writing habit.

Do not run it for one-off content facts such as a specific Jira link, owner, title, metric target, or launch scope unless the user explicitly says that fact represents a reusable rule.

## Learning Check Output

Before editing the skill, produce a compact table:

| # | 用户反馈 | 判断 | 更新位置 | 是否写入 skill |
|---|---|---|---|---|
| 1 | <feedback> | <durable preference / one-off fact / unclear> | <file> | <yes/no/confirm> |

If the user already said "可以", "继续", "以后默认这样", or directly asked to optimize the skill, that counts as confirmation for the proposed durable updates. Otherwise ask for confirmation before editing.

## Classification

| Type | Meaning | Primary target |
|---|---|---|
| Template Preference | Metadata table, section order, Scope shape, Feature List, Feature Detail table | `user-prd-profile.md`, `outline-patterns.md`, `new-prd-template.md` |
| Writing Style | Language, density, bilingual rule, Background length, wording style | `author-model.md`, `user-prd-profile.md` |
| Workflow Preference | Confluence search, planning gate, outline confirmation, detail clarification timing | `SKILL.md`, `checklist-gates.md`, `confluence-discovery.md` |
| Domain Knowledge | Product/module boundary, historical logic, known systems | `author-model.md`, `work-map.md` |
| Review Preference | Review Board severity, checklist items, recurring review risks | `quality-checklist.md`, `prd-copilot-modes.md` |

## Update Threshold

Write into the skill when at least one is true:

- The user explicitly says it is a default or future preference.
- The user approves a proposed skill patch.
- The same correction appears at least twice.
- Same-author Confluence PRDs show the same pattern and the current output violated it.

Keep it out of the skill when:

- It only applies to the current PRD.
- It is a source fact that belongs in the PRD, not in the author model.
- It would expose secrets, credentials, private links, or local-only draft references.
- It conflicts with stronger evidence and needs user confirmation.

## Write Rules

- Store the abstract reusable rule, not the full PRD text.
- Preserve the reason when the rule prevents a known failure.
- Mark weak rules as inferred until confirmed by user correction or repeated source evidence.
- Prefer updating reference files over expanding `SKILL.md`; keep `SKILL.md` limited to trigger and routing behavior.
- If a generated `pm-xxx` should inherit the rule, update `pm-distiller` and `scripts/create_pm_copilot.py` as well.

## Validation

After editing, run the skill-creator `quick_validate.py` against the changed skill.

Then run a narrow read-only check against the failed PRD scenario:

- Does the skill now detect the original mistake?
- Does it update the right PRD section instead of over-expanding the template?
- Does it avoid storing one-off PRD facts as durable preferences?
"""


PM_MODES = """# PRD Copilot Modes

Pick one primary mode per response. Combine modes only when the user clearly asks for it.

## Context Mode

Use when the user asks to understand a feature or current work.

Output:

- Source map.
- Current understanding.
- Confirmed facts.
- Inferred assumptions.
- Gaps that block PRD writing.
- For new drafts, a short Discovery Summary that can precede outline confirmation.

## Outline Mode

Use when the user wants a PRD structure.

Output:

- Proposed plan.
- Feature List draft: `Index | Feature | Description | Remark`.
- Recommended outline.
- Purpose of each section.
- Required source or decision for each section.
- Sections that can be deferred.
- Whether late sections such as Rollout, Acceptance Criteria, and Dependencies should be included or collapsed.
- A clear confirmation request before drafting: "请确认这个 plan / Feature List / 大纲是否可以作为初稿结构".

## New PRD Template Mode

Use when the user wants to start a new PRD or fill a newly created Confluence page.

Output:

- Discovery Summary and preflight table for missing Confluence PRD link, Jira/Epic/SPCPM links, title, people, and related docs.
- Proposed plan, Feature List, and Confluence-ready outline for confirmation.
- Detail clarification table after outline confirmation.
- Draft Readiness Check before full drafting.
- Confluence-ready PRD skeleton only after plan/outline confirmation or explicit user instruction to draft with assumptions.
- Related docs and Jira/Epic/SPCPM links inserted if provided.
- Batch missing-info table with numbered P0/P1 gaps.
- Assumptions and Open Questions.

Do not ask whether to create a Confluence page. The PM usually creates it and provides the link.
Do not use local-only Markdown links in the final Confluence draft.

For new PRDs or full drafts, the planning/confirmation gate is mandatory. Use in-chat planning for narrow edits and short one-source drafts. Use `planning-with-files-zh` when the work is Confluence-source, source-heavy, or likely to span multiple turns.

## Interview Mode

Use when requirements are unclear.

Output:

- Blocking questions: decisions needed before drafting.
- Optional questions: improve quality but not blocking.
- Suggested confirmation order.
- One numbered table for detail clarification; do not ask one question per message.

## Requirement Brief Mode

Use when discovery is insufficient for a reliable PRD, especially when two or more are unclear: problem, target user, core flow, system boundary, or source of truth.

Output:

- Current understanding.
- Known facts and source evidence.
- Missing decisions ranked P0/P1/P2.
- 2-3 possible solution directions if useful.
- Recommended next step.

Do not output a full PRD in this mode. A structured requirement brief is better than a fake complete PRD.

## Auto Enrich Mode

Use when the user asks to complete missing details or when review finds missing edge cases, tracking, NFR, states, or system integration details.

Output:

- Additions grouped by target PRD section.
- Mark `[待确认]` or `[假设]` when the detail cannot be inferred.
- Keep additions inside existing sections such as Feature Details, Data Tracking, NFR, Success Metrics, or Open Questions.
- Remove unnecessary product-irrelevant implementation narration rather than expanding the PRD.

Do not create standalone chapters for every enrichment category.

## Section Rewrite Mode

Use when the user selects a section or asks to optimize part of a PRD.

Output:

- Revised section.
- Assumptions made.
- Related sections/tables/metrics that may need updates.

## Review Mode

Use when the user asks for review.

If the PRD was written from Confluence history, verify that a Confluence source map exists. If it is missing, make that a Blocker or Major finding depending on whether historical logic affects the requirement.

Output findings first:

- Missing or conflicting scope.
- Unclear user/system behavior.
- Unsupported assumptions.
- Missing states, edge cases, data tracking, metrics, rollout, or open questions.

## Review Board Mode

Use when the user asks whether a PRD can pass review, asks for multi-role review, or is preparing for requirement review.

This mode follows the useful pattern from `pm-review-board`: role-based critique, issue-first output, Blocker/Major/Minor severity, explicit verdict, and a re-review list. Do not turn it into a long meeting simulation.

Default roles:

- Product: problem, goals, non-goals, scope, priority.
- Engineering: system boundary, APIs/data dependencies, feasibility, compatibility.
- QA: acceptance conditions, states, edge cases, testability.
- Ops/Data: tracking, rollout, monitoring, operational fallback.
- Design: only when UI/interaction changes are meaningful.
- Legal/Compliance: only when privacy, personal data, permission, or policy risk exists.

Output findings first, grouped by severity:

| # | Severity | Issue | Role | Section | Recommendation |
|---|---|---|---|---|---|

Severity:

- Blocker: cannot enter development/review until fixed.
- Major: can continue, but must be resolved before launch or test handoff.
- Minor: quality improvement or follow-up.

Verdict:

- Pass: 0 Blocker + 0 Major.
- Conditional Pass: 0 Blocker + one or more Major.
- Fail: one or more Blocker.

End with:

- Verdict.
- Re-review required sections.
- Top 3 fixes before sharing with reviewers.

## Consistency Mode

Use after edits or PRD version changes.

Check:

- Background vs objective.
- Scope vs feature details.
- Trigger rules vs state tables.
- UI text vs localization/data tracking.
- Metrics vs success criteria.
- Open questions vs unresolved dependencies.

## Draft Mode

Use only when the user asks for a full PRD and the outline is confirmed, or when the user explicitly asks to draft with assumptions. Keep source-derived facts separate from proposed wording.

For initial PRDs, prefer short English Background and move detailed analysis into Current Logic, Problem, Feature Details, Data Tracking, or Open Questions.

For existing-flow optimization, decision-layer, pre-check, gating, or suppression PRDs, explain Current/Target behavior only inside the relevant Feature Detail row/subsection and use structured tables as the default shape.

Default Scope is lightweight: `Markets`, `Tenant`, and `Channel` when channel scope matters. Do not add standalone `In Scope` by default. Default Feature Details use `Feature | Detail | UI/Diagram`; add nested tables only for real product dimensions.
"""


NEW_PRD_TEMPLATE = """# New PRD Template

Use this template for a new PRD that will be published on Confluence. The PM usually creates the Confluence page and provides the link; use that link as the target context. Do not include `Target Release` or `PRD Status` by default.

Do not put local-only Markdown links into the final Confluence draft. Local files can be used as working evidence, but final `Related Document` rows should point to Confluence, Jira, request pages, Figma, Sheets, or other links that Confluence readers can open.

## Preflight Inputs

Ask once, in a batch, only for fields that are missing and useful. If the user asks for an initial draft and the Confluence PRD link is missing, ask for it before producing paste-ready content.

| # | 字段 | 用途 | 默认假设 | 需要你提供 |
|---|---|---|---|---|
| 1 | Confluence PRD link | Identify the final publishing page and avoid local-only references | PM has or will create the page | Page link |
| 2 | PRD title | First heading and page title alignment | Use working title from request | Final title |
| 3 | Jira / Epic / SPCPM link | Required traceability in the first PRD metadata table | Leave placeholder if unavailable | Links |
| 4 | People involved | Reviewer and owner context | FPM is requestor | Names/roles |
| 5 | Related docs | Source grounding for Confluence readers | Use discovered Confluence/external docs; local files stay as working notes | Links |

Do not ask whether to create a Confluence page.

## Required Flow

1. Produce a Discovery Summary: sources read, source authority, current understanding, and gaps.
2. If the source library is Confluence, run the mandatory historical logic check: read/search relevant Confluence PRD/BRD/FRF pages before outline drafting and include the source map.
3. If source evidence is too thin, produce a Requirement Brief instead of a full PRD.
4. Produce a proposed plan, Feature List, and outline first.
5. Wait for user confirmation before writing the full PRD draft, unless the user explicitly says to draft with assumptions.
6. After outline confirmation, ask detail clarification questions in one numbered table.
7. Run a Draft Readiness Check: scope dimensions, Feature Detail structure, and optional late sections.
8. Then produce the Confluence-ready draft.

No Confluence source map, no full draft when the requirement depends on historical Confluence logic. If search/read fails, stop before drafting and ask whether to continue from local/user-provided sources only.

## Template

```markdown
# [PRD] <Feature / Module Name>

| Key | Value |
|-----|-------|
| Jira / Epic | <Jira issue / Epic / SPCPM link> |
| Related Document | <Confluence / Figma / Sheet / existing PRD links> |
| People Involved | FPM: <name>; Dev PIC: <name or TBD> |

**Version History:**

| Version | Date | Description | Changed by |
|---------|------|-------------|------------|
| V0.1 | <date> | Initial draft | <author> |

---

## 1. Background

<Short English context. Keep it to 2-4 sentences for the first draft. Put detailed findings in Current Logic / Problem / Feature Details.>

## 2. Objective

<Behavior-oriented goals.>

## 3. Scope

| Dimension | Value |
|---|---|
| Markets | <market scope> |
| Tenant | <tenant> |
| Channel | <channel scope, such as Chat Channel / Email / N/A> |

## 4. Feature List

| Index | Feature | Description | Remark |
|---|---|---|---|
| 1 | <feature name> | <one-sentence summary> | <optional> |

## 5. Feature Details

### 5.1 <Feature>

| Feature | Detail | UI / Diagram |
|---|---|---|
| <feature> | <structured bullets or a nested product table> | <Confluence image / Figma / TBD> |

For long requirement blocks in the Detail cell, write Chinese first and then `English Version:` as a separate paragraph/list.

## 6. Non-Functional Requirements

- Performance:
- Compatibility:
- Permission:
- Localization:

## 7. Transify Key

| Default | Key |
|---|---|
| <copy> | <key> |

## 8. Data Tracking

| Event / Data | Trigger | Parameters | Purpose |
|---|---|---|---|
| <event> | <trigger> | <params> | <purpose> |

## 9. Success Metrics

| Metric | Definition | Target / Monitoring |
|---|---|---|
| <metric> | <definition> | <target> |

## 10. Open Questions

| # | Question | Owner | Status | Decision |
|---|---|---|---|---|
| 1 | <question> | <owner> | Open | - |
```

## When to Adjust

- Use a lighter template for small UI-only PRDs.
- For existing-flow optimization, pre-check, gating, or suppression PRDs, explain current/target behavior only inside the relevant Feature Detail row or subsection.
- Do not add a standalone `In Scope` section by default; it usually duplicates Feature List.
- Add `Out of Scope` only when there is a real exclusion to call out, such as excluded markets, tenants, channels, entry points, user groups, or feature behavior.
- Do not force `Affected User`, `Impacted Role`, `System Module`, `Current Logic`, `Current Gap`, `Target Logic`, `System Logic`, `Edge Cases`, or `Tracking` as default rows.
- Keep Rollout only when gray-scale, feature switch, model/API risk, or rollback is meaningful.
- Keep Acceptance Criteria as Feature Detail rows or Review Checklist unless the reviewer needs a standalone section.
- Put dependencies into Open Questions unless many cross-team owners require a dedicated dependency table.
- Use model/LLM sections for prompt, summary, detection, search, and recommendation work.
- Use platform/config sections for admin portals, permissions, versioning, publish, rollback, and audit.
"""


CONFLUENCE_WORKFLOW = """# Confluence Draft Workflow

## Default

The PM creates the Confluence page and sends the link. The agent should not ask whether to create a page.

The agent prepares Confluence-ready Markdown content using the provided link as the target reference. Do not directly edit Confluence unless higher-priority instructions explicitly allow it.

Local files are working evidence only. Do not put local-only relative links such as `[README.md](README.md)` into a Confluence-ready PRD unless the user explicitly asks for a local draft.

## Flow

1. Read source docs and local materials.
2. If the user provides a Confluence root/page or the PRD library is in Confluence, run `confluence-discovery.md` before scoping as the mandatory historical logic check.
3. Produce a Discovery Summary with sources read, source authority, current understanding, and unresolved gaps.
4. If the problem, target user, or core flow is still unclear, output a Requirement Brief instead of a full PRD.
5. Ask for missing preflight inputs in one batch if needed.
6. Propose the PRD plan, Feature List, and outline; wait for confirmation before full drafting.
7. After plan/outline confirmation, ask detail clarification questions in one numbered table if needed.
8. Run a Draft Readiness Check: Scope shape, Feature List, Feature Detail structure, bilingual needs, and optional late sections.
9. Fill `new-prd-template.md` with available evidence and explicit assumptions.
10. Put unresolved items into the numbered checklist table or Open Questions.
11. Provide paste-ready content or update a local draft file, depending on the user's requested destination.

Use a planning/confirmation gate for every new PRD or full draft. Use `planning-with-files-zh` for new PRDs, multi-source Confluence tasks, source-heavy work, browser-heavy work, or explicitly requested planning.

No Confluence source map, no full draft when the requirement depends on historical Confluence logic. If Confluence search/read fails, stop before full drafting and ask whether to continue from local/user-provided sources only.

## Preflight Table

| # | 缺口 | 为什么影响 | 默认假设 | 需要你确认 |
|---|---|---|---|---|
| 1 | <missing field> | <impact> | <assumption> | <what user should provide> |

Do not include:

- Target release
- PRD status
- A question asking whether to create a Confluence page

## Jira and Related Links

The first PRD metadata table should include one Jira/Epic traceability row when available:

| Key | Value |
|-----|-------|
| Jira / Epic | <Jira issue / Epic / SPCPM link> |
| Related Document | <Confluence/Figma/Sheet/source links> |
| People Involved | FPM: <name>; Dev PIC: <name or TBD> |

Do not create both `Request Info` and `Epic` rows. If the target page already uses `Request Info`, treat it as the Jira/Epic traceability row.

If Jira/Epic/SPCPM links are missing, ask for them once in the preflight table. If unavailable, leave one placeholder instead of blocking the whole draft.

## Auto Enrich Rule

When filling gaps found after the draft, write additions into the relevant existing section:

- Exceptions and edge cases -> Feature Details.
- State handling -> Feature Details.
- Events/logs/metrics -> Data Tracking or Success Metrics.
- Permission/performance/localization -> Non-Functional Requirements.
- Cross-team unknowns -> Open Questions.

Do not create new late chapters unless the review risk materially requires them.
Do not add product-irrelevant backend implementation steps, code paths, database internals, owner routing, or prompt internals unless they are part of the product contract.
"""


CHECKLIST_GATES = """# Checklist Gates

Use checklist gates to reduce repeated questions. They should be batched, numbered, and tied to timing.

## Table Format

```markdown
当前有 <N> 个 P0 缺口会影响 PRD：

| # | 缺口 | 为什么影响 | 默认假设 | 需要你确认 |
|---|---|---|---|---|
| 1 | <gap> | <impact> | <default assumption> | <confirmation needed> |
```

## Discovery Gate

Trigger: after reading initial sources.

Check:

- Source of truth.
- Whether the mandatory Confluence historical logic check has been run when the PRD library or provided source link is in Confluence.
- Missing BRD/FRF/old PRD.
- Whether local frontend code or UAT observation is needed.
- Whether Confluence link is a root page, active PRD, or target draft page.
- Whether this task requires `planning-with-files-zh`: new PRD, multi-source Confluence task, source-heavy, browser-heavy, or multi-turn.

Default: every new PRD/full draft requires a planning/confirmation gate. Use in-chat planning only for narrow edits or short one-source drafts.

If Confluence has not been searched and the task depends on historical PRD context, treat it as a P0 discovery gap before outline drafting. No Confluence source map, no full draft unless the user explicitly accepts local/user-provided sources only.

## Scoping Gate

Trigger: before proposing the PRD outline.

Check:

- Scope should usually contain `Markets`, `Tenant`, and `Channel` when channel scope matters.
- Module boundary, role impact, permission, and current/target behavior should move into Feature List or Feature Details unless the source page explicitly uses them in Scope.
- Do not add standalone `In Scope` by default. Add `Out of Scope` only when a real exclusion must be visible to reviewers.

## Outline Confirmation Gate

Trigger: after proposing the PRD outline and before writing a full initial draft.

Check:

- The outline follows the PM's Confluence PRD format.
- The first metadata table uses one traceability row: `Jira / Epic` or the target page's existing `Request Info` label.
- Do not create both `Request Info` and `Epic` rows.
- Scope uses `Markets`, `Tenant`, and `Channel` by default when channel scope is relevant.
- Feature List is present before Feature Details: `Index | Feature | Description | Remark`.
- Existing-flow optimization outlines explain current/target behavior only inside relevant Feature Detail rows/subsections.
- Late sections are intentionally included or collapsed: Rollout, Acceptance Criteria, Dependencies.
- The user has confirmed whether to keep, remove, or reorder sections.
- The draft destination is clear: Confluence-ready content or a local working draft.

Ask for confirmation explicitly. Do not proceed to a full PRD draft unless the user confirms the outline or explicitly asks to draft with assumptions.

## Detail Clarification Gate

Trigger: after outline confirmation and before writing Feature Details.

Check:

- Trigger conditions.
- Feature List completeness.
- Trigger/condition only when it changes product behavior.
- UI/interaction behavior.
- Permission, error, empty, loading, timeout, or retry behavior only when user-visible or review-relevant.
- Data tracking and success metrics only when behavior validation is needed.
- Bilingual requirement blocks for long Feature Detail descriptions.
- Dependencies and owners.

Use one numbered table. Group related questions by section or module rather than asking one by one.

## Draft Readiness Check

Trigger: after detail clarification and before writing a full PRD draft.

Check:

- If discovery is still too thin, switch to Requirement Brief Mode rather than drafting a full PRD.
- Feature List has been confirmed by the user.
- Feature Detail will use compact structured tables, usually `Feature | Detail | UI/Diagram`.
- Scope is lightweight: `Markets`, `Tenant`, and `Channel` when channel scope is relevant, unless source evidence requires more.
- Long Feature Detail requirement blocks use Chinese first and `English Version:` second.
- Rollout is included only for gray-scale, feature switch, model/API risk, or rollback needs.
- Acceptance Criteria is standalone only if reviewers need it; otherwise fold into Feature Detail or Review Checklist.
- Dependencies is standalone only for many cross-team owners; otherwise fold into Open Questions.

## Auto Enrich Gate

Trigger: after a draft/review finds missing details.

Check:

- Exceptions and edge cases are inserted into Feature Details.
- Data tracking additions go into Data Tracking or Success Metrics.
- Permission, performance, localization, and compatibility go into NFR.
- Unconfirmed dependencies go into Open Questions.
- No new late section is created unless it materially improves review or launch control.
- Product-irrelevant implementation steps, code paths, database internals, owner routing, and prompt internals are removed unless they are product contracts.

## Publish/Paste Gate

Trigger: before preparing final Confluence-ready content.

Check:

- Confluence PRD link provided by PM.
- PRD title.
- Jira / Epic / SPCPM link if required.
- People involved.
- Related docs.
- Open Questions table is current.
- No local-only relative links are present in the Confluence-ready draft.

Do not ask whether to create a Confluence page. Do not include Target Release or PRD Status by default.
"""


OUTLINE_PATTERNS = """# Outline Patterns

## Default Confluence PRD

0. Top metadata table:
   - `Jira / Epic`
   - `Related Document`
   - `People Involved`
1. Historic Version / Version History.
2. Background: short English context.
3. Objective & Solution.
4. Scope:
   - `Markets`
   - `Tenant`
   - `Channel` when channel scope matters
5. Feature List:
   - `Index | Feature | Description | Remark`
6. Feature Details:
   - default table: `Feature | Detail | UI / Diagram`
   - use subsections such as `5.1 <Feature>` for complex features
7. Transify Key when UI copy exists.
8. Data Tracking / Metrics when behavior needs validation.
9. Open Questions when decisions are unresolved.

Do not add standalone `In Scope`, Rollout, Acceptance Criteria, or Dependencies unless they materially help review or launch. Add `Out of Scope` only for explicit exclusions.

## Existing Feature Optimization

Use the same default outline. In Feature Details, describe existing and target behavior inside the relevant feature row or subsection.

Preferred Feature Detail table:

| Feature | Detail | UI / Diagram |
|---|---|---|
| <feature> | <structured bullets or nested table> | <Confluence image / Figma / TBD> |

Use nested tables only for real product dimensions:

- Module / Current Status / Required Change
- Trigger Scene / Trigger Method / Update Content
- Field / Source / Description / Display
- State / Behavior
- Permission / Behavior

## Decision Layer / Pre-check / Suppression

Use for changes where an existing flow adds a pre-check, gate, suppression, or send/continue decision.

Keep the outline lean:

1. Background.
2. Objective & Solution.
3. Scope: `Markets`, `Tenant`, and `Channel` when channel scope matters.
4. Feature List.
5. Feature Details.
6. Data Tracking / Metrics.
7. Open Questions.

Feature Details should answer only product-review questions:

- Which feature/flow is changed?
- What condition triggers the decision?
- What behavior changes before vs after?
- What user-visible or operational state changes?
- What data/tracking confirms the behavior?

Avoid product-irrelevant backend implementation steps, code paths, database internals, owner routing, and prompt internals.

## Model / LLM Feature

Use Feature List to separate model-facing and UI-facing work.

Feature Details may include:

- input/output contract when it affects product behavior
- confidence/fallback behavior
- display fields and language behavior
- feedback loop
- evaluation/data tracking

Do not include prompt internals unless the prompt behavior is the requirement.

## UI / Action Button / Console Feature

Use Feature Details with:

- entry point
- display condition
- button or field behavior
- permission behavior
- success/failure state
- transify copy
- UI / diagram reference
"""


QUESTION_PLAYBOOK = """# Question Playbook

Ask only questions that change the next output.

## Blocking Questions

- What is the editable destination: local file, new draft, or review-only?
- If this is a new Confluence PRD, what is the Confluence PRD link where the PM will publish it?
- Which Confluence root/page or historical PRD library should be searched for source context?
- What Jira / Epic / SPCPM link should appear as the single traceability row in the first metadata table?
- Which document is source of truth if local PRD and Confluence disagree?
- What are the target `Markets`, `Tenant`, and `Channel`?
- What Feature List should be confirmed before detail drafting?
- What is the trigger condition, if it changes product behavior?
- For optimization/pre-check/gating/suppression changes, what current/target behavior must be described in Feature Details?
- What should happen in loading, empty, fail, timeout, retry, and stale-response cases if user-visible?
- What is the compatibility requirement with existing behavior?
- What data/event/metric is needed to validate success?
- Should Rollout, standalone Acceptance Criteria, or standalone Dependencies be included, or collapsed into Feature Detail / Open Questions?

## Optional Questions

- Is there a design/Figma reference?
- Is there a TD/code constraint that should shape requirements?
- Are there region, permission, or feature switch gates that should appear in Feature Details?
- Is rollout by user, market, issue category, feature flag, or agent group?
- What open questions should stay in the PRD for reviewers?

## Question Format

Prefer:

```text
当前有 2 个 P0 缺口会影响 PRD：

| # | 缺口 | 为什么影响 | 默认假设 | 需要你确认 |
|---|---|---|---|---|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |
```

Avoid long questionnaires before reading available materials.
"""


QUALITY_CHECKLIST = """# Quality Checklist

Use this as a gate, not as a long questionnaire. Batch missing items in a numbered table:

| # | 缺口 | 为什么影响 | 默认假设 | 需要你确认 |
|---|---|---|---|---|

Only P0 gaps should block drafting. P1/P2 gaps can become explicit assumptions or Open Questions.

## Source Grounding

- Related docs are listed.
- Facts are traceable to local PRD, Confluence, BRD/FRF, TD, code, or explicit user input.
- When the PRD library/source link is Confluence, the mandatory historical logic check has read/searched relevant Confluence pages before outline/draft.
- The Discovery Summary includes a Confluence source map with search keywords, pages read, page IDs/URLs, and how each source affects current/target logic.
- External links not read are not treated as evidence.
- Confluence-ready drafts do not contain local-only relative Markdown links.
- One Jira/Epic/SPCPM traceability row is present in the top metadata table or explicitly listed as missing.
- `Request Info` and `Epic` are not duplicated as separate rows.

## Product Clarity

- Problem is concrete.
- Objective is behavior-oriented.
- Goals and non-goals are separated.
- Scope is not over-specified; it defaults to `Markets`, `Tenant`, and `Channel` when channel scope matters.
- Module, role, permission, current/target behavior, and system boundary are placed in Feature List or Feature Details only when relevant.
- Standalone `In Scope` is absent by default; `Out of Scope` appears only for real exclusions.
- Initial-draft Background is concise; detailed evidence is moved into the appropriate detail section.

## Requirement Completeness

- Feature List exists before Feature Details unless the change is tiny.
- Feature Detail is table-first, compact, and organized by feature/module/scenario.
- Trigger, UI behavior, model behavior, data behavior, state handling, and edge cases are included only when product-relevant.
- Long Feature Detail descriptions use Chinese first and `English Version:` second when needed.
- Product-irrelevant implementation steps, code paths, database internals, owner routing, and prompt internals are absent unless they are part of product contract.
- Loading, empty, fail, retry, timeout, and stale-response cases are covered when user-visible asynchronous behavior exists.
- Backward compatibility and migration are covered when existing data/config is affected.

## Measurement

- Data tracking events or BE records are specified when behavior needs validation.
- Success metrics are measurable and tied to the objective.
- Rollout/gray-scale and monitoring are included for risky or model-facing changes.
- Rollout is not included by default unless gray-scale, feature switch, model/API risk, or rollback is meaningful.

## Review Readiness

- Open questions are real unresolved decisions.
- Dependencies and owners are visible either in Open Questions or a dedicated table when many teams are involved.
- Acceptance criteria are testable; they may live in Feature Detail or Review Checklist instead of a standalone chapter.
- Terminology is consistent across sections.

## Review Board Severity

Use this when the user asks for review readiness:

| Severity | Meaning | Typical examples |
|---|---|---|
| Blocker | Cannot enter development/review until fixed | core flow missing, system boundary unclear, source of truth unread, compliance/security risk, no acceptance basis |
| Major | Can continue, but must be fixed before launch/test handoff | missing state/edge case, incomplete tracking, unclear owner/dependency, ambiguous target logic |
| Minor | Quality improvement or follow-up | wording, table polish, optional metric detail, non-blocking examples |

Verdict:

- Pass: 0 Blocker + 0 Major.
- Conditional Pass: 0 Blocker + one or more Major.
- Fail: one or more Blocker.

## Gate Timing

- Discovery Gate: after reading sources, before proposing scope.
- Scoping Gate: before proposing the PRD outline.
- Planning/Outline Confirmation Gate: after proposing plan, Feature List, and outline, before writing the full draft.
- Detail Clarification Gate: after plan/outline confirmation, before filling Feature Details.
- Draft Readiness Check: before full drafting, confirm Scope shape, Feature List, compact Feature Detail, bilingual needs, and optional late sections.
- Publish/Paste Gate: before preparing final Confluence-ready content.

## External PRD Skill Lessons

- Use Discovery -> Scoping -> Drafting from `write-a-prd` as the backbone.
- Read Confluence/docs/code/current behavior before drafting; do not rely on memory or local filenames alone.
- Use `pm-prd-writer`'s Clarify -> Structure -> Auto Enrich -> Deliver flow, but write enrichment back into the relevant section instead of adding many chapters.
- When information is too thin, use Requirement Brief Mode instead of a fake complete PRD.
- Use `pm-review-board`'s multi-role review pattern when checking review readiness: Product, Engineering, QA, Ops/Data, Design only when UI changes, and Legal/Compliance only when privacy or policy risk exists.
- Review output should start with Blocker/Major/Minor findings, include a Pass/Conditional Pass/Fail verdict, and end with a short re-review list.
- Use Problem / Goals / Non-goals / P0-P2 / Metrics / Open Questions as template ingredients, not a rigid full template.
- Use quality scoring as a gate and checklist, not as roleplay.
- Keep FR/NFR, priority, and traceability available, but avoid heavyweight PM templates unless the task requires them.
"""


FRONTEND_DISCOVERY = """# Frontend Code Discovery

Use when existing B-side web behavior should inform the PRD.

## Local Code Reading

Inspect only local code paths provided by the user or present in the workspace.

Look for:

- Page routes and entry components.
- Existing component boundaries and props.
- Labels, button text, tooltips, empty/error/loading copy.
- Feature flags, permissions, tenant/market/channel gates.
- API client calls and data models.
- State machines, stores, hooks, reducers, and retry logic.
- Tests, stories, mocks, and fixtures.

## Useful Searches

```bash
rg --files <repo>
rg -n "Issue|SOP|Order|Case|Summary|Key Info|loading|Retry" <repo>
rg -n "route|Router|path|permission|featureFlag|i18n|formatMessage|t\\(" <repo>
```

## How to Use in PRD

- Use code to describe current behavior and constraints.
- Use docs/user input to decide desired behavior.
- Do not invent product requirements from implementation details alone.
- If code and PRD conflict, surface the conflict.
"""


LOCAL_PRD_INVENTORY_SCRIPT = r'''#!/usr/bin/env python3
"""Summarize local PRD markdown files and document-like assets."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DOC_EXTS = {".md", ".txt", ".csv", ".pdf", ".ppt", ".pptx", ".doc", ".docx"}


def headings(path: Path, limit: int) -> list[str]:
    if path.suffix.lower() not in {".md", ".txt"}:
        return []
    found: list[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if HEADING_RE.match(line):
                    found.append(line.strip())
                    if len(found) >= limit:
                        break
    except OSError:
        return []
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--max-files", type=int, default=160)
    parser.add_argument("--max-headings", type=int, default=16)
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules"}]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() not in DOC_EXTS:
                continue
            files.append(
                {
                    "path": str(path.relative_to(root)),
                    "ext": path.suffix.lower(),
                    "size": path.stat().st_size,
                    "headings": headings(path, args.max_headings),
                }
            )
            if len(files) >= args.max_files:
                print(json.dumps({"root": str(root), "truncated": True, "files": files}, ensure_ascii=False, indent=2))
                return
    print(json.dumps({"root": str(root), "truncated": False, "files": files}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
'''


def write_generated(target: Path, files: dict[str, str], force: bool) -> None:
    if target.exists():
        if not force:
            raise SystemExit(f"Target already exists: {target}. Use --force to overwrite.")
        shutil.rmtree(target)
    for rel, content in files.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    inventory = target / "scripts" / "local_prd_inventory.py"
    inventory.chmod(0o755)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--user-name", required=True)
    parser.add_argument("--local-folder", required=True)
    parser.add_argument("--confluence-url", action="append", default=[])
    parser.add_argument("--path", default=str(Path.home() / ".codex" / "skills"))
    parser.add_argument("--display-name")
    parser.add_argument("--default-language", default="Chinese")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    skill_name = normalize_skill_name(args.skill_name)
    local_root = Path(args.local_folder).expanduser()
    docs = collect_local_docs(local_root)
    files = render_files(args, docs)
    target = Path(args.path).expanduser() / skill_name

    summary = {
        "target": str(target),
        "skill_name": skill_name,
        "user_name": args.user_name,
        "confluence_urls": args.confluence_url,
        "local_folder": str(local_root),
        "file_count": len(files),
        "files": sorted(files.keys()),
        "local_docs_indexed": len(docs),
        "dry_run": args.dry_run,
    }

    if args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    write_generated(target, files, args.force)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
