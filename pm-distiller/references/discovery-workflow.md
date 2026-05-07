# Discovery Workflow

## Purpose

Create a source-grounded profile for a PM-specific PRD copilot. The goal is not to write a product PRD; it is to distill how the PM works and what a future PRD agent should load, ask, produce, avoid, and review.

## Inputs

- Confluence root/page URL.
- User name, handle, or email prefix.
- Local folder path.

## Steps

1. Read the Confluence root/page.
   - If the page is an empty container, search Confluence with product keywords and user name.
   - Read the top relevant PRD/BRD/FRF/TD pages before inferring the PM profile.
   - Capture page IDs, titles, last modified dates, `authorName`, FPM/Changed by mentions, and obvious ownership signals.

2. Search local files.
   - Use `rg --files`.
   - Prioritize `.md`, `.txt`, `.csv`, and filenames with PRD, BRD, FRF, TD, requirement, feature, design, issue, summary, loading, search, prompt, order, case.
   - Index PDFs by filename unless extraction is explicitly needed.

3. Identify source types.
   - PRD: product requirements and feature details.
   - BRD/FRF: business background and high-level scope.
   - TD/DSTD: implementation constraints and data/model details.
   - Sheet exports: requirements matrix, metric definitions, rollout trackers.
   - Frontend code: routes, components, labels, current behavior.

4. Build a work map.
   - Group documents by product area and module.
   - Note recurring systems, workflows, and user roles.
   - Mark current vs historical material based on dates and version history.

5. Distill the author model.
   - Confirm repeated habits, inferred habits, historical logic modules, review preferences, recurring corrections, and anti-patterns.
   - Use `author-distillation.md` to separate durable author rules from one-off document quirks.
   - Score profile completeness; if evidence is weak, return profile gaps instead of a complete copilot claim.

6. Infer style.
   - Common headings and sequence.
   - Language mix.
   - Table/diagram/checklist usage.
   - Depth of edge cases, metrics, and data tracking.

7. Produce a skill blueprint.
   - Keep `SKILL.md` lean.
   - Move detailed profile, routes, templates, and checklists into references.

## Evidence Rules

- Cite local paths or Confluence page IDs in the working notes.
- Separate confirmed facts from inferred patterns.
- Do not use external links as factual evidence unless read by an appropriate skill/tool.
- If a source is unreadable, record it as a dependency, not as evidence.
- If Confluence access fails, record the exact failure and do not claim Confluence was searched.

## Confluence Commands

Use `skill-confluence` or the CLI:

```bash
skynet-base confluence read "<PAGE_URL_OR_ID>" --body-format markdown --raw
skynet-base confluence search "<product/module>" "<user handle>" --space SCPM --limit 10
skynet-base confluence search "<module keyword>" "PRD" "<user handle>" --space SCPM --limit 10
```

If `read` saves a large page to a local cache file, inspect only relevant segments and cite the Confluence page, not the cache file, in the profile.
