# Air Serbia x PolyAI — Implementation Plan

_Last updated: 2026-06-21_
_GitHub: https://github.com/boykeboyke/air-serbia-demo_
_Railway: https://air-serbia-demo-production.up.railway.app_
_Studio: https://studio.eu.poly.ai/poly-srpski-euw/PROJECT-LEQWVUHR_

---

## How the system works (summary)

Two chat modes controlled by `CHAT_MODE` env var:

**`polyai_full`** — PolyAI voice widget handles everything (speech-to-speech). Widget dropped into the "The Agent" tab once Studio agent is published.

**`elevenlabs_hybrid`** (currently active) — Browser mic → ElevenLabs STT → PolyAI Chat API (text-to-text, `tts_lang_code: sr-RS` forces Serbian) → ElevenLabs TTS → audio playback. Transcript shown in UI. Session managed server-side with 1-hour TTL.

The Railway server also hosts the branded microsite and proxies live flight data (AviationStack).

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

## Phase 4 — ElevenLabs hybrid voice chat ✅ COMPLETE

| Task | Status | Notes |
|---|---|---|
| `CHAT_MODE` feature flag | ✅ | `polyai_full` (default) vs `elevenlabs_hybrid` |
| ElevenLabs STT (Scribe v1) | ✅ | Multipart audio upload, `ELEVENLABS_STT_LANG=sr` |
| PolyAI Chat API integration | ✅ | `tts_lang_code: sr-RS` forces Serbian text responses |
| ElevenLabs TTS | ✅ | Voice `peXmQaCErbfrWCM5FqjH`, eleven_multilingual_v2 |
| Server-side session store | ✅ | In-memory Map, 1-hour TTL |
| Greeting spoken aloud on start | ✅ | `/api/chat/tts` endpoint, plays before mic unlocks |
| Voice chat UI (mic button) | ✅ | Push-to-talk, transcript panel, end call button |
| UTF-8 / Cyrillic transcript fix | ✅ | `b64utf8()` via TextDecoder — no more garbled chars |
| `vcPlaying` state reset fix | ✅ | Mic re-enables after greeting finishes |
| All Studio function steps in Serbian | ✅ | No English strings fed to LLM (eliminates language drift) |
| Deployed to Railway (hybrid mode) | ✅ | `CHAT_MODE=elevenlabs_hybrid` set as Railway env var |
| All secrets set on Railway | ✅ | `POLY_ADK_KEY`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` |

### New API routes (server.js)

| Route | Purpose |
|---|---|
| `GET /api/chat/mode` | Returns current `CHAT_MODE` |
| `POST /api/chat/session` | Creates PolyAI session, returns greeting |
| `POST /api/chat/message` | Text in → Serbian text reply |
| `POST /api/chat/tts` | Text → MP3 (speaks greeting) |
| `POST /api/chat/speak` | Audio in → ElevenLabs STT → PolyAI → ElevenLabs TTS → MP3 out |
| `POST /api/chat/end` | Closes PolyAI session |

---

## Phase 5 — PolyAI Studio agent (ADK) ✅ MOSTLY COMPLETE

| Task | Status | Notes |
|---|---|---|
| Studio project created | ✅ | PROJECT-LEQWVUHR, euw-1 cluster |
| Flows built in Studio UI | ✅ | 8 flows: flight status, booking lookup, new booking, cancel, baggage, check-in, loyalty, complaint |
| ADK CLI access | ✅ | `~/.polyai-venv/bin/adk`, key in `~/.config/claude/secrets.env` |
| ADK project pulled & tracked in Git | ✅ | `poly-srpski-euw/PROJECT-LEQWVUHR/` |
| Serbian rules + personality | ✅ | `rules.txt`, `personality.yaml` — all in Serbian |
| `default_language: sr-RS` | ✅ | `agent_settings/languages.yaml` |
| All function steps in Serbian | ✅ | State vars and return strings — no English LLM context |
| ADK branch pushed | ✅ | Branch `ADK-49236-af16` — **merge in Studio UI to activate** |
| **Wire HTTP connectors in Studio UI** | 🔲 | 5 endpoints — see table below |
| Test: live flight status via connector | 🔲 | After connectors wired |
| Merge ADK branch in Studio | 🔲 | Studio → Branches → merge `ADK-49236-af16` into main |

### HTTP connectors to wire in Studio UI (⚠️ UI-only — ADK cannot do this)

| Connector name | Method | URL |
|---|---|---|
| `lookup_passenger` | GET | `https://air-serbia-demo-production.up.railway.app/api/passenger/{phone}` |
| `get_flight_status` | GET | `https://air-serbia-demo-production.up.railway.app/api/flight-status/{flight_number}` |
| `change_booking` | POST | `https://air-serbia-demo-production.up.railway.app/api/booking/change` |
| `add_baggage` | POST | `https://air-serbia-demo-production.up.railway.app/api/baggage/add` |
| `check_in` | POST | `https://air-serbia-demo-production.up.railway.app/api/checkin` |

---

## Phase 6 — PolyAI widget (polyai_full mode) 🔲

| Task | Status | Notes |
|---|---|---|
| Merge ADK branch in Studio | 🔲 | Prerequisite for everything below |
| Wire HTTP connectors (5 endpoints) | 🔲 | Studio UI only |
| Deploy agent to Sandbox environment | 🔲 | Required before widget token can be minted |
| Publish web-call widget | 🔲 | Studio: Channels → Widgets → + Widget → Web calling |
| Wire widget `<script>` into `public/index.html` | 🔲 | Replace placeholder in "The Agent" tab |
| Redeploy Railway with widget script | 🔲 | `railway up --service air-serbia-demo --detach` |
| Set `CHAT_MODE=polyai_full` on Railway | 🔲 | Switches from hybrid to PolyAI full speech |
| Run adversarial critic loop | 🔲 | See `reference/adversarial-iteration.md` |

---

## What's mocked vs live (honest list)

| Component | Status | What replaces it in a real pilot |
|---|---|---|
| Passenger record (Milan Petrović) | 🔶 Mock | Air Serbia's GDS/CRM via Amadeus or custom connector |
| Booking change / cancel | 🔶 Mock | Amadeus NDC or Air Serbia's booking API |
| Baggage add | 🔶 Mock | Air Serbia's ancillary/extras API |
| Check-in | 🔶 Mock | Departure control system (DCS) connector |
| Flight status | ✅ Live | AviationStack (wired in both local + Railway) |
| Elevate miles / tier | 🔶 Mock | Air Serbia's Elevate program API |

---

## Quick commands

```bash
# Run locally
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
cd air-serbia-demo && npm start          # → http://localhost:3000

# Redeploy to Railway
railway up --service air-serbia-demo --detach

# Test production endpoints
curl https://air-serbia-demo-production.up.railway.app/healthz
curl https://air-serbia-demo-production.up.railway.app/api/chat/mode
curl https://air-serbia-demo-production.up.railway.app/api/flight-status/JU500

# Push to GitHub
export PATH="$HOME/bin:$PATH"
git add -A && git -c commit.gpgsign=false commit -m "your message" && git push

# Push to PolyAI Studio (from project subfolder)
cd poly-srpski-euw/PROJECT-LEQWVUHR
source ~/.config/claude/secrets.env && export POLY_ADK_KEY
~/.polyai-venv/bin/adk push
```
