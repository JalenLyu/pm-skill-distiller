# Generation Workflow

Use this when turning discovery results into a stable `pm-xxx` skill. Treat generation as an author-distillation task: the output should preserve the PM's habits, style, historical logic, knowledge modules, review preferences, and recurring failure modes.

## Minimum Inputs

- `--skill-name`: lower-case skill name, usually `pm-<name>`.
- `--user-name`: PM name.
- `--local-folder`: local PRD or product-materials folder.
- `--confluence-url`: one or more read-only Confluence entry points.

## Recommended Flow

1. Read the provided Confluence link and local files.
   - If the Confluence link is an empty root/index, search by user handle plus product/module keywords and read relevant PRD/BRD/FRF pages.
2. Produce a short profile preview:
   - user name and handles
   - likely work modules
   - source priority
   - author model: confirmed habits, inferred habits, historical logic modules, review preferences, anti-patterns, and profile gaps
   - profile completeness score using `author-distillation.md`
   - PRD style assumptions
   - expected Confluence metadata fields
   - outline-confirmation and clarification gates
   - mandatory planning/confirmation default
   - metadata row naming: `Jira / Epic` vs target-page-specific labels
   - Scope shape: usually `Markets`, `Tenant`, and `Channel` when channel scope matters
   - Feature List and compact Feature Detail shape
   - whether `Out of Scope` is needed; standalone `In Scope` should not be a default section
   - bilingual rule for long Feature Detail blocks
   - Decision Layer / pre-check / suppression outline needs
   - table-first Feature Detail preference
   - domain skill candidates
   - Requirement Brief / Auto Enrich / Review Board mode support
3. Run `create_pm_copilot.py --dry-run`.
4. If the preview is acceptable, run without `--dry-run`.
5. Validate with `quick_validate.py`.

## Command

```bash
python3 scripts/create_pm_copilot.py \
  --skill-name pm-example \
  --user-name "Example PM" \
  --local-folder "/path/to/prd/folder" \
  --confluence-url "https://confluence.shopee.io/display/SPACE/Page" \
  --path "${CODEX_HOME:-$HOME/.codex}/skills"
```

## Safety

- The script does not call Confluence or external URLs.
- The script records provided URLs as source references. Confluence read/search must happen before running the script, and the results should shape the generated profile.
- For Confluence-backed PRD copilots, the generated skill should enforce "No Confluence source map, no full draft" for new PRDs/full drafts when historical logic matters.
- If the author model is below the completeness threshold in `author-distillation.md`, generate a V0 with explicit profile gaps instead of pretending the author's style is fully known.
- The script refuses to overwrite an existing skill unless `--force` is provided.
- Use local files and explicit user input to refine the generated profile after creation.
