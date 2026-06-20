# Air Serbia x PolyAI - prospect demo

A PolyAI prospect demo for **Air Serbia (JU)**: a branded microsite + a mock contact-centre API a
live **bilingual (Serbian / English)** PolyAI Studio voice agent calls during a meeting. One
flight-status action is a **genuinely live external call**; everything else is a faithful mock.

Built with the `prospect-demo` skill. The page is the prop; the agent is the show.

## What's here

```
air-serbia-demo/
  server.js                 # Express: static site + mock API + LIVE flight-status proxy + /healthz
  package.json              # express; "start": "node server.js"; node >= 18
  public/
    index.html              # 8-tab Air Serbia-branded site, with EN/SR toggle + live flight lookup
    assets/air-serbia-logo.svg
  docs/
    system-prompt.md        # the agent's runtime persona + bilingual + flows + rules
    builder-agent-prompt.md # paste into Studio's agentic builder to construct the agent
    mock-api-payload.json   # sample API responses
    demo-script.md          # the 45-min meeting running order
  .env.example              # flight-status API key config (optional)
  .gitignore
```

## Run locally

```bash
npm install
npm start                 # -> http://localhost:3000
```

If `node` is missing, this repo was set up with nvm:
```bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"   # then npm install && npm start
```

Check it:
```bash
curl localhost:3000/healthz
curl localhost:3000/api/passenger/+381641234567
curl localhost:3000/api/flight-status/JU324
curl -X POST localhost:3000/api/baggage/add -H 'content-type: application/json' -d '{"pnr":"JU8K2P","extra_bags":1}'
```

## Live flight-status integration

`GET /api/flight-status/:flightNumber` makes a **real** external call when an API key is set, and
falls back to deterministic sample data otherwise (so it always works on stage).

1. Copy `.env.example` to `.env`.
2. Set **one** key:
   - `AERODATABOX_KEY` - AeroDataBox via [RapidAPI](https://rapidapi.com) (HTTPS, free tier). Recommended.
   - or `AVIATIONSTACK_KEY` - [AviationStack](https://aviationstack.com) free key (HTTP only on free tier).
3. Restart. The lookup now reports `source: "live: ..."`.

Reads can be live; **all writes (booking change, baggage, check-in) are mock** and never touch a real
reservation system.

## Build the voice agent

Follow `docs/builder-agent-prompt.md` in PolyAI Studio. The agent is bilingual: it switches between
Serbian and English at runtime via a `set_caller_language` function (not a prompt rule). It greets the
passenger by name and answers from the record on call-open.

## Deploy (later)

Railway autodetects Node (`npm install` + `npm start`, sets `$PORT`). A mock-data demo is fine public.
See the `prospect-demo` skill's `adk-and-deploy.md`.

## Honesty

The passenger record (Milan Petrović, PNR JU8K2P) is illustrative sample data. Brand colours and the
wordmark are matched from public Air Serbia assets and are not an official brand handover. Case-study
metrics are quoted from published PolyAI customer stories.
