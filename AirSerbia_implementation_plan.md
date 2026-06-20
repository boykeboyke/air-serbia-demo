# Air Serbia x PolyAI — Implementation Plan

_Last updated: 2026-06-20. Track this alongside the GitHub repo: https://github.com/boykeboyke/air-serbia-demo_

---

## Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Done and working |
| 🔶 | Mock / placeholder — needs real wiring for production |
| 🔲 | Not started |
| 🔑 | Needs an API key / credential |

---

## Phase 1 — Local demo (COMPLETE)

| Task | Status | Notes |
|---|---|---|
| Branded 8-tab microsite (Air Serbia brand) | ✅ | Navy `#0E2040` + red `#C8102E`, Archivo/Inter |
| Air Serbia logo (official from website) | ✅ | SVG from logo.wine (airserbia.com blocks direct fetch) |
| EN / SR bilingual toggle | ✅ | 126 i18n strings, all translated |
| Marquee / copy corrected to 24/7 | ✅ | Removed "06:00–23:00"; emphasise zero hold times + no retraining |
| Metric strip: 24/7/365, zero hold, no retraining | ✅ | Live |
| Express mock API (server.js) | ✅ | Running on port 3000 |
| Passenger lookup `GET /api/passenger/:phone` | ✅ | Returns demo passenger: Milan Petrović, Silver Elevate, JU324 BEG→CDG |
| Booking change `POST /api/booking/change` | 🔶 | Mock — never writes to a real GDS |
| Baggage add `POST /api/baggage/add` | 🔶 | Mock — returns 35 EUR per bag |
| Check-in `POST /api/checkin` | 🔶 | Mock — returns boarding pass "issued" |
| Flight status `GET /api/flight-status/:fn` | 🔶 | Falls back to sample data; see Phase 2 below |
| `/healthz` endpoint | ✅ | Returns `{"status":"ok"}` |
| Node.js installed via nvm | ✅ | v24.17.0 at `~/.nvm/versions/node/v24.17.0/bin/node` |
| GitHub repo created | ✅ | https://github.com/boykeboyke/air-serbia-demo |
| README | ✅ | `README.md` |
| CLAUDE.md | ✅ | Navigation and context for AI assistants |

---

## Phase 2 — Live flight-status integration

| Task | Status | Notes |
|---|---|---|
| AeroDataBox integration (server.js) | ✅ | Code written; env var `AERODATABOX_KEY` needed |
| AviationStack fallback (server.js) | ✅ | Code written; env var `AVIATIONSTACK_KEY` needed |
| **Get a free API key** (AeroDataBox via RapidAPI) | 🔑 | Sign up at https://rapidapi.com, subscribe to AeroDataBox. Free tier = 500 req/month. Copy key → `.env` as `AERODATABOX_KEY=…` |
| Add `.env` file locally | 🔲 | `cp .env.example .env` then fill in key |
| Verify live source label in hero flight-status card | 🔲 | Should show `"source":"live: AeroDataBox"` not "sample data" |

---

## Phase 3 — PolyAI Studio voice agent

| Task | Status | Notes |
|---|---|---|
| `docs/system-prompt.md` | ✅ | Bilingual (EN/SR), call-open personalization, 4 flows, escalation rules |
| `docs/builder-agent-prompt.md` | ✅ | Paste into Studio's agentic builder; wires all 5 HTTP connectors |
| `docs/mock-api-payload.json` | ✅ | Sample payloads for Studio connector tests |
| **Get a PolyAI ADK key** (`POLY_ADK_KEY`) | 🔑 | studio.us.poly.ai → account icon → Personal Access Tokens → create, save to `~/.config/claude/secrets.env` |
| Create empty Studio project | 🔲 | studio.us.poly.ai → New project → blank. Note the project ID. |
| Paste `builder-agent-prompt.md` into agentic builder | 🔲 | Replace `[BASE_URL]` with running server URL first |
| Wire `lookup_passenger` HTTP connector | 🔲 | `GET [BASE_URL]/api/passenger/{phone}` |
| Wire `get_flight_status` HTTP connector | 🔲 | `GET [BASE_URL]/api/flight-status/{flight_number}` — LIVE |
| Wire `change_booking` HTTP connector | 🔲 | `POST [BASE_URL]/api/booking/change` |
| Wire `add_baggage` HTTP connector | 🔲 | `POST [BASE_URL]/api/baggage/add` |
| Wire `check_in` HTTP connector | 🔲 | `POST [BASE_URL]/api/checkin` |
| Build `set_caller_language` function | 🔲 | `conv.set_language("sr-RS"/"en-US")` — bilingual switch |
| Build `start_function` (call-open lookup) | 🔲 | Must store all fields on `conv.state`; inject into `# PASSENGER CONTEXT` |
| Test scenario 1: Serbian booking change | 🔲 | Greet Milan, switch to SR, change JU324 date, confirm reference |
| Test scenario 2: English baggage add | 🔲 | EN caller, add 1 bag, state 35 EUR, confirm |
| Test scenario 3: Live flight status | 🔲 | Ask for JU324 status; agent calls live lookup, reads back |
| Test scenario 4: Mid-call language switch | 🔲 | Open SR, switch to EN mid-call, agent follows |
| Test scenario 5: Safety / emergency | 🔲 | Must transfer to human immediately, 100% of the time |
| Tune voice (speed 1.2, stability 10-30, clarity 90) | 🔲 | Studio: Channels → Agent voice → gear icon |

---

## Phase 4 — Railway deployment

| Task | Status | Notes |
|---|---|---|
| Install Railway CLI | 🔲 | `npm install -g @railway/cli` |
| Get `RAILWAY_API_TOKEN` | 🔑 | railway.app → account settings → tokens |
| Confirm public vs gated | 🔲 | Mock-only demo is fine public |
| `railway init && railway up && railway domain` | 🔲 | From inside `air-serbia-demo/` |
| Set `AERODATABOX_KEY` as Railway env var | 🔲 | `railway variables --set "AERODATABOX_KEY=…"` |
| Verify `GET https://[domain]/healthz` returns 200 | 🔲 | After deploy |
| Update `[BASE_URL]` in `builder-agent-prompt.md` | 🔲 | Replace localhost with Railway domain |

---

## Phase 5 — Widget + adversarial iteration

| Task | Status | Notes |
|---|---|---|
| Publish PolyAI web-call widget | 🔲 | Studio: Channels → Widgets → + Widget → Web calling. Website URL must match Railway domain exactly. |
| Deploy agent to Sandbox env first | 🔲 | Token won't mint until agent is deployed to an environment |
| Wire widget `<script>` into `public/index.html` | 🔲 | Replace the `<!-- POLYAI_WIDGET_PLACEHOLDER -->` comment in the "Your Agent" tab |
| Run adversarial critic loop | 🔲 | See `reference/adversarial-iteration.md` — red-team agent on commercial value |
| Agent reaches L3+ on growth-engine ladder | 🔲 | L0 answers → L1 knows caller → L2 acts → L3 grows revenue |

---

## Known mocks (honest list)

| What's mocked | Why | What replaces it in a real pilot |
|---|---|---|
| Passenger record (Milan Petrović, JU8K2P) | Can't connect to Air Serbia's Amadeus/CRM without a contract | Air Serbia's actual GDS/CRM connector via PolyAI's pre-built Amadeus or custom connector |
| Booking change / cancel | No live GDS writes in a demo | Amadeus NDC or Air Serbia's booking API |
| Baggage add | No live ancillary API | Air Serbia's ancillary/extras API |
| Check-in | No live DCS access | Departure control system connector |
| Flight status (no key) | AeroDataBox key not yet set | Add `AERODATABOX_KEY` to `.env` — then it's a real live call |
| Elevate miles redemption | No loyalty API | Air Serbia's new Elevate program API |

---

## Quick commands reference

```bash
# Run locally
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
cd air-serbia-demo && npm start

# Test APIs
curl localhost:3000/healthz
curl localhost:3000/api/passenger/any
curl localhost:3000/api/flight-status/JU324
curl -X POST localhost:3000/api/baggage/add -H 'content-type: application/json' -d '{"pnr":"JU8K2P","extra_bags":1}'

# Push changes to GitHub
git add -A && git commit -m "your message" && git push

# GitHub CLI (installed at ~/bin/gh)
export PATH="$HOME/bin:$PATH"
gh repo view boykeboyke/air-serbia-demo
```
