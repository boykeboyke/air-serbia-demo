# Air Serbia x PolyAI — prospect demo

A PolyAI prospect demo for **Air Serbia (JU)**: an 8-tab bilingual microsite branded in Air Serbia's navy and red, backed by a mock contact-centre API, with a genuinely live flight-status integration and full PolyAI Studio voice-agent docs.

**GitHub:** https://github.com/boykeboyke/air-serbia-demo  
**Implementation plan + status:** [`AirSerbia_implementation_plan.md`](AirSerbia_implementation_plan.md)

---

## What's in the demo

| | |
|---|---|
| **Site** | 8-tab anchor-scroll page in Air Serbia brand. EN/SR toggle flips all copy to Serbian latin. In-page live flight-status lookup. |
| **Mock API** | Passenger lookup (Milan Petrović, Elevate Silver), booking change, baggage add, check-in. |
| **Live action** | `GET /api/flight-status/:fn` proxies AeroDataBox (or AviationStack), falls back to sample data if no key set. |
| **Agent docs** | Bilingual `system-prompt.md` + `builder-agent-prompt.md` ready to paste into PolyAI Studio. |

---

## Run locally

Node.js is installed via nvm. Use the nvm-sourced path:

```bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
cd air-serbia-demo
npm install       # first time only
npm start         # → http://localhost:3000
```

### Test the API

```bash
curl localhost:3000/healthz
curl localhost:3000/api/passenger/+381641234567
curl localhost:3000/api/flight-status/JU324
curl -X POST localhost:3000/api/booking/change \
  -H 'content-type: application/json' \
  -d '{"pnr":"JU8K2P","new_date":"2026-07-05"}'
curl -X POST localhost:3000/api/baggage/add \
  -H 'content-type: application/json' \
  -d '{"pnr":"JU8K2P","extra_bags":1}'
curl -X POST localhost:3000/api/checkin \
  -H 'content-type: application/json' \
  -d '{"pnr":"JU8K2P","seat":"14C"}'
```

---

## Activate the live flight-status lookup

By default, flight status returns deterministic sample data. To make it a real external call:

1. Sign up at [RapidAPI](https://rapidapi.com) and subscribe to **AeroDataBox** (free tier: 500 req/month).
2. Copy `.env.example` to `.env` and set your key:
   ```
   AERODATABOX_KEY=your_rapidapi_key_here
   ```
3. Restart the server. The `source` field will change to `"live: AeroDataBox"`.

---

## Build the Studio voice agent

1. Make sure the server is running (locally or on Railway) so the agent can hit the API.
2. Open `docs/builder-agent-prompt.md`, replace `[BASE_URL]` with your server URL.
3. Paste the prompt into PolyAI Studio's agentic builder.
4. The agent is bilingual — it switches Serbian/English via `conv.set_language()` at runtime. Read `docs/system-prompt.md` for the full wiring notes.

You'll need a `POLY_ADK_KEY` from [studio.us.poly.ai](https://studio.us.poly.ai) → account icon → Personal Access Tokens.

---

## Deploy to Railway

```bash
npm install -g @railway/cli
export RAILWAY_API_TOKEN=your_token
railway init && railway up && railway domain
# Set the live flight key as an env var:
railway variables --set "AERODATABOX_KEY=your_key"
```

Public deploy is fine — this demo contains only mock data.

---

## Project structure

```
air-serbia-demo/
├── server.js                         # Express: mock API + live flight proxy
├── package.json
├── public/
│   ├── index.html                    # 8-tab bilingual site
│   └── assets/
│       └── air-serbia-logo-official.svg
├── docs/
│   ├── system-prompt.md              # Studio agent persona (bilingual)
│   ├── builder-agent-prompt.md       # Paste into agentic builder
│   ├── mock-api-payload.json         # Sample payloads
│   └── demo-script.md                # 45-min meeting script
├── AirSerbia_implementation_plan.md  # Full task list with status
├── CLAUDE.md                         # Navigation guide for AI assistants
├── .env.example                      # API key config
└── .gitignore
```

---

## Honesty

The passenger record (Milan Petrović, PNR JU8K2P) is illustrative sample data. All writes (booking, baggage, check-in) are mock and never touch a real GDS. Case-study metrics are quoted from published PolyAI customer stories. Brand assets are reproduced from public Air Serbia materials for demo purposes only.
