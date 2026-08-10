# BlackHawk

Termux ve minimal Python kurulumlarında, yalnızca yetkili kamuya açık web kaynaklarını
yerel olarak gözlemleyip raporlayan, oturum tokeni gerektirmeyen terminal aracı.

## Run & Operate

- `python -m blackhawk --ui ansi` — Termux uyumluluk arayüzünü çalıştırır
- `python -m blackhawk --target https://example.com` — yetkili bir kamu kaynağı ekler
- `python -m compileall -q blackhawk` — Python sözdizimi kontrolü
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
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
- CLI: Python 3.10+, bağımlılıksız ANSI varsayılanı; Textual isteğe bağlı

## Where things live

- `blackhawk/cli.py` — token istemeyen başlangıç ve arayüz seçimi
- `blackhawk/terminal_ui.py` — Termux/minimal terminal menüsü
- `blackhawk/ui.py` — Textual kuruluysa isteğe bağlı arayüz
- `blackhawk/security.py` — yalnızca kamuya açık URL doğrulaması
- `blackhawk/reports.py` — JSON, TXT ve HTML raporları
- `blackhawk/tests/` — Python davranış kontrolleri

## Architecture decisions

- Başlangıçta oturum tokeni, profil parolası, PyPI tokeni veya GitHub tokeni istenmez.
- Termux'ta varsayılan arayüz bağımlılıksız ANSI'dir; Textual yalnızca açıkça seçilirse kullanılır.
- Ağ erişimi kullanıcı tarafından verilen yetkili HTTP/HTTPS URL'leriyle sınırlıdır.
- Raporlar ek Python kütüphanesi olmadan JSON, TXT ve HTML olarak yazılır.

## Product

BlackHawk, kullanıcı tarafından girilen kamuya açık web URL'lerini yavaşlatılmış
tekil isteklerle okur, başlık ve kısa metin özeti çıkarır, yerel log ve rapor üretir.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Termux'ta `python -m blackhawk` veya kurulum sonrası `blackhawk` çalıştırılmalıdır.
- Textual kurulu değilse bu bir hata değildir; `--ui auto` veya Termux algılaması ANSI'ye düşer.
- Kimlik bilgisi, token, parola veya özel hesap URL'si hedef olarak kabul edilmez.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
