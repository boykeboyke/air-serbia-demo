# Air Serbia x PolyAI — Implementation Plan

_Last updated: 2026-06-20_
_GitHub: https://github.com/boykeboyke/air-serbia-demo_
_Railway: https://air-serbia-demo-production.up.railway.app_
_Studio: https://studio.eu.poly.ai/poly-srpski-euw/PROJECT-LEQWVUHR_

---

## How the system works (summary)

A passenger calls in → PolyAI Studio's voice agent answers in Serbian or English → the agent calls the Railway server via HTTP connectors to look up the passenger and perform actions → the Railway server proxies live data (flight status via AviationStack) or returns mock data for everything else. The same Railway server also hosts the branded microsite a prospect views in a browser.

See `architecture diagram` in the README or the diagram in the conversation.

---

## Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Done and working |
| 🔶 | Mock — works in demo, replaced by real systems in a pilot |
| 🔲 | Not yet done |
| 🔑 | Needs a credential |

---

## Phase 1 — Local demo ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Branded 8-tab microsite | ✅ | Air Serbia navy + red, Archivo/Inter |
| Air Serbia logo (official SVG) | ✅ | CSS filter recolours in nav/footer |
| EN / SR bilingual toggle | ✅ | 126 strings, all translated |
| 24/7 + zero hold + no retraining copy | ✅ | Removed "06:00–23:00" messaging |
| Express mock API (server.js) | ✅ | passenger, booking, baggage, check-in |
| Live flight status proxy | ✅ | AviationStack, graceful mock fallback |
| Auto-load .env on npm start | ✅ | No manual key export needed |
| Node.js v24.17.0 via nvm | ✅ | `~/.nvm/versions/node/v24.17.0/bin/node` |
| GitHub repo | ✅ | https://github.com/boykeboyke/air-serbia-demo |

---

## Phase 2 — Live flight status ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| AviationStack integration | ✅ | `AVIATIONSTACK_KEY` in `.env` |
| Status normalisation | ✅ | `active` → En route, `landed` → Landed, etc. |
| Full airport names | ✅ | "Belgrade Nikola Tesla (BEG)" |
| CEST timezone offset | ✅ | UTC+2 applied to departure/arrival times |
| Graceful fallback | ✅ | Non-operating flights fall back to sample data |

---

## Phase 3 — Railway deployment ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| Railway CLI installed | ✅ | v5.20.0 via npm |
| Railway login (boykeboyke) | ✅ | lukacarb@gmail.com |
| Project created | ✅ | air-serbia-demo on boykeboyke's Projects |
| Deployed to Railway | ✅ | https://air-serbia-demo-production.up.railway.app |
| AVIATIONSTACK_KEY set on Railway | ✅ | Live flight status works in production |
| Public domain minted | ✅ | `air-serbia-demo-production.up.railway.app` |
| /healthz verified | ✅ | Returns `{"status":"ok"}` |

---

## Phase 4 — Studio voice agent 🔲 IN PROGRESS

| Task | Status | Notes |
|---|---|---|
| Studio project created | ✅ | PROJECT-LEQWVUHR, euw-1 cluster |
| Flows built in Studio UI | ✅ | User built manually |
| `system-prompt.md` written | ✅ | Bilingual, call-open personalization, 4 flows |
| `builder-agent-prompt.md` written | ✅ | Reference doc (not needed since flows built manually) |
| **Wire HTTP connectors in Studio UI** | 🔲 | 5 endpoints — see table below |
| Build `start_function` | 🔲 | Call-open passenger lookup → `conv.state` |
| Build `set_caller_language()` | 🔲 | `conv.set_language("sr-RS"/"en-US")` |
| Populate `# PASSENGER CONTEXT` in agent prompt | 🔲 | Inject `conv.state` fields so agent answers from record |
| Test: Serbian greeting by name | 🔲 | Agent greets "Milan" in Serbian on call-open |
| Test: live flight status lookup | 🔲 | Agent calls `/api/flight-status/JU500`, reads back live data |
| Test: bilingual switch mid-call | 🔲 | Open in SR, switch to EN, agent follows |
| Test: safety/emergency routing | 🔲 | Must transfer to human, 100% of the time |
| Tune voice (speed 1.2, stability low) | 🔲 | Studio: Channels → Agent voice → gear |

### HTTP connectors to wire in Studio UI (⚠️ UI-only — ADK cannot do this)

| Connector name | Method | URL |
|---|---|---|
| `lookup_passenger` | GET | `https://air-serbia-demo-production.up.railway.app/api/passenger/{phone}` |
| `get_flight_status` | GET | `https://air-serbia-demo-production.up.railway.app/api/flight-status/{flight_number}` |
| `change_booking` | POST | `https://air-serbia-demo-production.up.railway.app/api/booking/change` |
| `add_baggage` | POST | `https://air-serbia-demo-production.up.railway.app/api/baggage/add` |
| `check_in` | POST | `https://air-serbia-demo-production.up.railway.app/api/checkin` |

---

## Phase 5 — Widget + adversarial iteration 🔲

| Task | Status | Notes |
|---|---|---|
| Deploy agent to Sandbox environment | 🔲 | Required before widget token can be minted |
| Publish web-call widget | 🔲 | Studio: Channels → Widgets → + Widget → Web calling. Website URL = `https://air-serbia-demo-production.up.railway.app` |
| Wire widget `<script>` into `public/index.html` | 🔲 | Replace the placeholder comment in "Your Agent" tab |
| Redeploy Railway with widget script | 🔲 | `railway up --detach` from `air-serbia-demo/` |
| Verify bubble renders on live site | 🔲 | `window.PolyphoneAPI` should be defined on page load |
| Run adversarial critic loop | 🔲 | See `reference/adversarial-iteration.md` |
| Agent reaches L3+ (grows revenue, not just answers) | 🔲 | Upsell ancillaries, proactive Elevate upgrade nudge |

---

## What's mocked vs live (honest list)

| Component | Status | What replaces it in a real pilot |
|---|---|---|
| Passenger record (Milan Petrović) | 🔶 Mock | Air Serbia's GDS/CRM via Amadeus or custom connector |
| Booking change / cancel | 🔶 Mock | Amadeus NDC or Air Serbia's booking API |
| Baggage add | 🔶 Mock | Air Serbia's ancillary/extras API |
| Check-in | 🔶 Mock | Departure control system (DCS) connector |
| Flight status | ✅ Live | AviationStack (already wired) |
| Elevate miles / tier | 🔶 Mock | Air Serbia's new Elevate program API |

---

## Quick commands

```bash
# Run locally
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
cd air-serbia-demo && npm start          # → http://localhost:3000

# Redeploy to Railway
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
cd air-serbia-demo && railway up --detach

# Test production endpoints
curl https://air-serbia-demo-production.up.railway.app/healthz
curl https://air-serbia-demo-production.up.railway.app/api/flight-status/JU500
curl https://air-serbia-demo-production.up.railway.app/api/passenger/any

# Push to GitHub
export PATH="$HOME/bin:$PATH"
cd air-serbia-demo
git add -A && git -c commit.gpgsign=false commit -m "your message" && git push
```
