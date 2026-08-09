# BlackHawk

BlackHawk, yetkili kamu kaynaklarından kaynaklı gözlemleri toplayıp Türkçe
raporlayan güvenli bir Python TUI ve OSINT çalışma temelidir.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pip install blackhawk` — install the published BlackHawk CLI
- `blackhawk --demo` — launch the offline demo TUI
- `cd blackhawk && python -m pytest -q` — run BlackHawk tests
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `blackhawk/blackhawk/` — Python package: CLI, TUI, monitoring, safety,
  correlation, reporting, legal guidance
- `blackhawk/tests/` — package tests
- `blackhawk/README.md` — package usage and security boundary
- `blackhawk/SECURITY.md` — security policy and CVE-ready advisory template
- `blackhawk/assets/` — terminal reference and seven generated gallery images
- `README.md` — GitHub-facing project overview

## Architecture decisions

- Public targets are restricted to `http`/`https` URLs or non-network username
  labels; credentials and secret-bearing URLs are rejected.
- Demo mode never performs network calls and clearly marks demo observations.
- Reports are generated locally as escaped HTML, JSON, and TXT.
- Confidence labels never imply certainty without independent source evidence.
- No real CVE number is claimed; the security policy contains a ready-to-fill
  advisory template.

## Product

The published 0.1.1 package provides a Turkish Textual terminal interface,
single/multi-target session models, safe public URL observation, demo/offline
mode, audit logs, confidence classification, local HTML/JSON/TXT reports,
keyboard help, and a TCK/ethical-use screen.

## User preferences

- User wants the BlackHawk terminal to visually follow the supplied
  black/red reference image and to ship with Turkish documentation.

## Gotchas

- Run BlackHawk tests from `blackhawk/`; running root-level pytest can resolve
  the outer folder as a namespace and hide the package modules.
- Use `python -m build` from `blackhawk/` and check with `twine check`.
- For a fresh PyPI release, use the official PyPI index explicitly because
  package mirrors and metadata caches may lag.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
