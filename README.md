# PM Skill Distiller

PM Skill Distiller is a Codex skill for distilling a PM's PRD habits, source-reading workflow, review preferences, historical decisions, and recurring corrections into a reusable personalized PRD copilot skill.

中文名：PM 蒸馏器。

## Repository Structure

```text
pm-skill-distiller/
├── skills/
│   └── pm-distiller/
└── examples/
    └── pm-jalen/
```

## Skills

### `pm-distiller`

The main skill.

Use it to create or refresh a personalized `pm-xxx` PRD copilot from read-only Confluence context and local PRD materials.

It helps distill:

- PRD writing habits
- source discovery workflow
- product/module boundaries
- review preferences
- recurring corrections
- reusable author-specific rules

### `pm-jalen`

An example personalized PRD copilot skill.

It demonstrates the expected output structure of a generated PM skill, including:

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- continuous learning rules
- source routing and PRD workflow references

Before making this repository public, review and remove any private company context, internal links, personal data, or business-specific details from the example skill.

## Install

Copy the skill folder into your local Codex skills directory:

```bash
cp -R skills/pm-distiller ~/.codex/skills/
```

Optionally install the example skill:

```bash
cp -R examples/pm-jalen ~/.codex/skills/
```

Then restart Codex or reload skills.

## Usage

Use the main skill with a prompt like:

```text
Use $pm-distiller to distill a personalized PRD copilot from this Confluence page, user name, and local folder.
```

Example inputs:

- PM name or handle
- one or more read-only Confluence pages
- a local folder containing PRDs, BRDs, FRFs, PDFs, exports, or frontend code

## Design Principles

- Treat Confluence and Google Sheets as read-only sources.
- Do not invent APIs, configs, product facts, or file paths.
- Distill durable PM habits, not one-off PRD facts.
- Keep generated skills lightweight and source-grounded.
- Use local files as the editable working surface.

## Safety

Do not publish secrets, credentials, internal URLs, private Jira/Confluence links, customer data, or company-confidential product details.

If using `examples/pm-jalen` as a public example, sanitize it first.

## License

Add a license only after confirming the repository can be published.
