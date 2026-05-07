# Author Distillation

Use this when distilling or refreshing a `pm-xxx` PRD copilot. The distiller's core output is not a template; it is a compact author model that helps the generated skill think, ask, draft, and review like the target PM.

## External Skill Lessons

`find-skills` searches surfaced useful reference patterns:

| Reference skill | Useful lesson | How to adapt |
|---|---|---|
| `incept5/eve-skillpacks@eve-skill-distillation` | Distill repeated workflows and recurring failure modes, not one-off events. Teach why, not just steps. | Capture repeated PRD decisions, repeated user corrections, and recurring anti-patterns as the PM copilot's durable rules. |
| `different-ai/agent-bank@writing-style` | Preserve the writer's voice; improve clarity without making it sound generic or corporate. | Preserve the PM's section order, wording style, table preference, and omissions. Do not "upgrade" into a generic consulting PRD. |
| `davila7/claude-code-templates@skill-judge` | A good skill is compressed expert knowledge, not a tutorial. Keep knowledge delta high and add explicit anti-patterns. | Encode only PM-specific judgment, source routing, and non-obvious PRD rules. Avoid generic "how to write a PRD" filler. |
| `cexll/myclaude@product-requirements` | Use quality scoring and targeted clarification before generation. | Score profile completeness and ask only for the weakest evidence areas before generating a personal copilot. |
| `zephyrwang6/pm-skills@space-review-board` | Multi-role review works when findings are grouped by severity with a verdict and re-review list. | Keep Review Board mode issue-first and concise: Blocker/Major/Minor, verdict, and fix list. |
| `pmprompt/claude-plugin-product-management@prd-writer` | A broad PRD ingredient list is useful for coverage. | Treat generic PRD sections as fallback ingredients, not the author's default structure. |

## Distillation Targets

Capture these dimensions explicitly:

| Dimension | What to extract | Evidence examples |
|---|---|---|
| Publishing format | Metadata table, Confluence-ready link policy, version history, section order | same-author Confluence PRDs |
| Scope model | How the PM defines scope and what they omit | `Markets`, `Tenant`, `Channel`, explicit exclusions |
| Feature structure | Feature List shape, Feature Detail table shape, nesting depth | `Index | Feature | Description | Remark`, `Feature | Detail | UI/Diagram` |
| Writing style | Background length, language split, bilingual triggers, wording density | short English Background, Chinese + `English Version:` long details |
| Work modules | Product areas, modules, known systems, channels, dependencies | AA, Chaser, Issue Summary, SOP, SmartKB, Case, Channel |
| Historical logic | Current behavior, old decisions, system boundaries, known constraints | Confluence PRD/BRD/FRF pages and local drafts |
| Review lens | What the PM usually worries about before review | source grounding, scope drift, missing states, metrics, Confluence readability |
| Collaboration behavior | When to ask, when to draft, how to batch gaps | outline gate, detail clarification table, no one-by-one checklist |
| Anti-patterns | Things the PM repeatedly rejects | local-only links in Confluence PRD, over-detailed Background, over-heavy late chapters |
| Learning loop | Which user corrections should update the skill later | explicit "以后/default" feedback, repeated corrections, Confluence-confirmed patterns |

## Evidence Weight

Use this priority when sources conflict:

1. Explicit user correction in the current thread.
2. Same-author, recent Confluence PRD in the same product area.
3. Same-author Confluence PRD in adjacent product areas.
4. Local active draft with recent edits.
5. Historical local/exported PRD.
6. External PRD or PM skills.

Mark any inferred rule as inferred unless it appears in at least two independent samples or was confirmed by the user.

## Distillation Process

1. Build a source map with author, page ID/path, date/version, product area, and evidence status.
2. Extract repeated patterns by dimension, not by page: format, scope, feature details, language, review lens, and anti-patterns.
3. Separate durable habits from one-off page quirks.
4. Produce an author model with:
   - confirmed habits
   - inferred habits
   - historical logic modules
   - review preferences
   - anti-patterns
   - open profile gaps
5. Generate or update the PM skill from the author model.
6. Add a controlled continuous-learning loop so future PRD corrections become proposed skill patches instead of silent drift.
7. Validate the generated skill against realistic prompts and a source-grounding checklist.

## Profile Completeness Score

Use this as a distiller gate, not as user-facing roleplay:

| Dimension | Weight | Pass signal |
|---|---:|---|
| Source grounding | 30 | Confluence/local sources are read and cited; unread links are not treated as evidence. |
| Author style fidelity | 25 | Generated rules preserve repeated author format, wording density, table patterns, and omissions. |
| Workflow fit | 20 | Generated copilot supports discovery, outline confirmation, detail clarification, draft, review, and consistency modes. |
| Domain knowledge map | 15 | Work modules and historical logic are mapped enough to search the right sources. |
| Anti-pattern coverage | 10 | Known failure modes and "do not do" rules are explicit. |

If score is below 80, produce a profile preview plus missing evidence table instead of claiming a complete personal copilot.

## Do Not Distill

- One-off formatting from a single page unless the target Confluence page already uses it.
- Obsolete historical sections that the PM has explicitly rejected.
- Generic PM templates as defaults.
- Local-only file links into Confluence-ready output.
- Exact phrasing from confidential docs when a compact behavioral rule is enough.
- Tool-specific mechanics that belong in source routing, not the PM author's style.
