# Frontend Code Discovery

Use this optional layer when the user provides a local frontend repo or says existing B-side web behavior should inform the PRD.

## What to Inspect

- Route definitions and page entry files.
- Components, containers, hooks, stores, reducers, and state machines.
- i18n keys, button labels, tooltips, empty/error/loading text.
- API clients, GraphQL queries, service modules, and mock data.
- Feature flags, permission checks, region/tenant/channel gates.
- Tests, stories, snapshots, and fixture files that reveal expected behavior.

## Fast Commands

Use targeted searches before broad reading:

```bash
rg --files <repo>
rg -n "Agent Assistant|Issue|SOP|Order|Case|Summary|loading|Retry|permission|featureFlag" <repo>
rg -n "route|path|Router|createBrowserRouter|useRoutes|lazy\\(" <repo>
rg -n "i18n|Trans|t\\(|formatMessage|defineMessages" <repo>
```

## Optional Script

Run:

```bash
python3 scripts/local_context_inventory.py <path>
```

This only reads local files and emits a compact JSON inventory. It does not crawl authenticated websites or call remote APIs.

## PRD Use

Use code evidence to:

- Describe current behavior accurately.
- Avoid inventing field names, routes, states, or permissions.
- Find hidden edge cases such as loading, empty, fail, retry, disabled, and permission-denied states.
- Align requirements with existing component and API boundaries.

Do not turn code structure into product requirements automatically. Code explains current behavior; the PRD still needs product intent and business scope.
