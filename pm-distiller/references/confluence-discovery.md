# Confluence Discovery

Generated PM copilot skills must treat Confluence as an active read-only source when the user's PRD library lives there.

For new PRDs and full drafts, generated skills should enforce: no Confluence source map, no full draft when historical logic matters.

## Required Behavior

- Read a provided Confluence page/root before proposing source priority or PRD style.
- If the page is empty, an index, or a target draft shell, search Confluence with user handle plus product/module keywords.
- Search should also include feature keywords from the user's request and `PRD` / `BRD` / `FRF` terms.
- Read only relevant PRD/BRD/FRF/TD pages needed for the current task.
- Record title, page ID/URL, last modified date, and evidence status.
- Do not write to Confluence.

## Generated Skill Rule

Generated `pm-xxx` skills should include a one-level reference named `references/confluence-discovery.md` and link to it from `SKILL.md` and `source-router.md`.

## Search Seeds

- user name and handles
- product area
- module names
- `PRD`, `BRD`, `FRF`, `requirement`, `scope`, `Feature Detail`

## Failure Handling

If auth, permission, or parsing fails, the generated skill should report the exact failure and ask whether to continue from local sources only.
