# CLAUDE.md — Navigation guide for AI assistants

This file is for AI assistants (Claude, cloud agents, etc.) picking up work on this project.

---

## What this project is

A **PolyAI prospect demo for Air Serbia (JU)** — a sales-ready microsite + bilingual contact-centre API + voice agent docs, built with the `prospect-demo` skill. The goal is a live PolyAI demo for an Air Serbia sales meeting. The agent is bilingual (Serbian / English).

**GitHub:** https://github.com/boykeboyke/air-serbia-demo  
**Skill reference:** `/Users/lukabojovic/Documents/call_centre_agents/.claude/skills/prospect-demo/`

---

## File map

```
air-serbia-demo/
├── server.js                    ← Express API (start here for backend changes)
├── package.json                 ← dep: express only; engines: node >=18
├── public/
│   ├── index.html               ← The entire frontend (8-tab SPA, ~800 lines)
│   └── assets/
│       ├── air-serbia-logo-official.svg   ← real Air Serbia wordmark (navy #0f2d53, recolourable via CSS filter)
│       └── air-serbia-logo.svg            ← logotyp.us version (older, same wordmark)
├── docs/
│   ├── system-prompt.md         ← PolyAI Studio agent persona + bilingual wiring notes
│   ├── builder-agent-prompt.md  ← paste into Studio's agentic builder (replace [BASE_URL] first)
│   ├── mock-api-payload.json    ← sample API responses for Studio connector tests
│   └── demo-script.md           ← 45-min meeting running order
├── AirSerbia_implementation_plan.md  ← TODO list with status per task (read this first)
├── README.md                    ← How to run locally + Railway deploy
├── CLAUDE.md                    ← This file
├── .env.example                 ← Copy to .env; add AERODATABOX_KEY for live flight status
└── .gitignore                   ← excludes node_modules/, .env
```

---

## How to run the server

Node is installed via nvm. Always load nvm before running node/npm:

```bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
cd /Users/lukabojovic/Documents/call_centre_agents/air-serbia-demo
npm install    # first time only
npm start      # → http://localhost:3000
```

The preview tool launch config is at:
`/Users/lukabojovic/Documents/call_centre_agents/.claude/launch.json`
It uses the absolute node path: `/Users/lukabojovic/.nvm/versions/node/v24.17.0/bin/node`

---

## Key design decisions

### Bilingual (Serbian / English)
- The language toggle in the nav switches all 126 `data-i18n` nodes in `index.html` via a JS dict (`DICT.sr`).
- The voice agent switches language at the **runtime** via `conv.set_language("sr-RS")` — NOT a prompt rule. See `docs/system-prompt.md` wiring notes and `reference/voice-agent-playbook.md` §8.

### Live flight-status integration
- `GET /api/flight-status/:flightNumber` in `server.js` tries AeroDataBox (via `AERODATABOX_KEY` env var), then AviationStack (`AVIATIONSTACK_KEY`), then falls back to a deterministic mock.
- The `source` field in the response tells you which path ran: `"live: AeroDataBox"` vs `"sample data (no live flight API key configured)"`.
- To activate: add `AERODATABOX_KEY=your_key` to a `.env` file (see `.env.example`).

### All writes are mock
- `POST /api/booking/change`, `POST /api/baggage/add`, `POST /api/checkin` are always mock. They return believable confirmations but never touch a real GDS. This is intentional and disclosed in the Demo Assumptions tab.

### Branding rules
- Air Serbia brand: navy `#0E2040` / `#0f2d53`, red `#C8102E`.
- Logo: `public/assets/air-serbia-logo-official.svg` (single-color `#0f2d53`). In the nav, a CSS `filter` recolours it to navy. In the footer, `filter: brightness(0) invert(1)` makes it white on dark.
- PolyAI macaw `#D9EE50` used sparingly: pulse dot on the live integration card only.
- Fonts: Archivo (headings) + Inter (body) from Google Fonts.

### Demo passenger
- **Milan Petrović**, phone `+381641234567`, PNR `JU8K2P`, flight JU324 BEG→CDG 3 July 2026.
- All `/api/passenger/:phone` calls return this same record regardless of the phone number — this makes the personalization wow reproducible on stage.
- Elevate Silver tier, 18,450 miles, 6,550 to Gold.

---

## What's NOT built yet

See `AirSerbia_implementation_plan.md` for the full status table. Short version:

1. **Flight API key** — add `AERODATABOX_KEY` to `.env` to make flight status genuinely live.
2. **PolyAI Studio agent** — all docs are ready in `docs/`; needs a `POLY_ADK_KEY` and a Studio project.
3. **Railway deploy** — code is ready; needs `RAILWAY_API_TOKEN` and `railway` CLI.
4. **Widget** — the web-call widget placeholder is in the "Your Agent" tab; needs the Studio agent published first.

---

## Skill reference (for building the Studio agent)

The full `prospect-demo` skill lives at:
```
/Users/lukabojovic/Documents/call_centre_agents/.claude/skills/prospect-demo/
```

Key refs for the agent build:
- `reference/voice-agent-playbook.md` — build/test/iterate (read before touching Studio)
- `reference/adk-and-deploy.md` — ADK CLI and Railway deploy
- `reference/adversarial-iteration.md` — commercial value red-team loop

---

## GitHub / git

```bash
export PATH="$HOME/bin:$PATH"   # gh CLI installed here
git add -A && git -c commit.gpgsign=false commit -m "…" && git push
gh repo view boykeboyke/air-serbia-demo
```

Credential stored in keychain under account `boykeboyke`. If auth expires: `~/bin/gh auth login`.

---

## Things to watch out for

- **nvm not on default PATH**: always prefix with `export NVM_DIR=...` or use the absolute path `/Users/lukabojovic/.nvm/versions/node/v24.17.0/bin/node`.
- **Air Serbia's website blocks curl** (403 on all paths including assets). Use the local SVG assets; don't try to hotlink.
- **Bilingual in Studio is `conv.set_language()`, not a prompt rule** — see playbook §8. Failing to call the function means the agent ignores the prompt instruction and stays in `en-US`.
- **Flows are isolated** — don't route information questions into flows; answer from `# PASSENGER CONTEXT` in the main agent.
- **Never commit `.env`** — it contains the AeroDataBox key. `.gitignore` already excludes it.
