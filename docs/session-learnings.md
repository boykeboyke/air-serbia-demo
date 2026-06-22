# Session learnings — Air Serbia demo

_Last updated: 2026-06-22_

## What this demo is optimised for

This is a sales-ready Air Serbia prospect demo, not a production airline system. The strongest story is:

- Aries AI can build a branded, bilingual PolyAI voice-agent demo in days.
- The user can call the agent from the microsite and hear Serbian-first behaviour.
- Flight status is live where credentials are configured; booking, baggage, check-in and passenger profile are honest mocks.
- The demo should always disclose what is real and what is modelled.

## Current architecture

- `public/index.html` is the whole microsite SPA and includes the Serbian dictionary in `DICT.sr`.
- `server.js` serves the site, mock contact-centre APIs, flight status, hybrid web voice chat and Duffel flight search.
- Hybrid web voice is the current practical mode: browser mic -> speech recognition -> PolyAI Chat API -> speech playback.
- `CHAT_MODE=polyai_full` is reserved for the published PolyAI web-call widget.
- ADK project lives in `poly-srpski-euw/PROJECT-LEQWVUHR/` and is tracked in Git.

## Copy and language notes

Serbian copy should sound like regional business Serbian, not a literal translation from English. Useful choices:

- Keep normal industry English where it sounds better: `live`, `lookup`, `widget`, `flow`, `sandbox`, `security review`, `sample`, `case study`, `customer story`, `containment`.
- Avoid awkward literal Serbian such as `šavovi`, `živa pretraga`, `zadržani pozivi`, `zadržane namere`, `od strane`, `nula čekanja`, `deluje`, `smetnje`.
- Prefer direct phrasing: `bez čekanja u redu`, `live provera leta`, `rešen poziv`, `zahtev`, `profil putnika`, `napravio je Aries AI`.
- For a sales meeting, Serbian can be polished but not over-formal. It should feel like someone who actually sells enterprise software in the region.

## Demo passenger and repeatability

- Demo passenger: Milan Petrović, phone `+381641234567`, PNR `JU8K2P`.
- The passenger endpoint intentionally returns the same record for any phone number so stage demos are reproducible.
- Use JU324, JU500 and JU200 as safe flight-status examples on the site.

## Voice and language behaviour

- PolyAI Studio language switching must happen at runtime with `conv.set_language("sr-RS")`, not only through prompt instructions.
- Hybrid web voice mode forces Serbian replies with `tts_lang_code: sr-RS` when needed.
- Serbian speech playback needs text normalization. `server.js` now includes number-to-word handling so numbers are read naturally.
- English strings in function-step returns can cause the LLM to drift back to English; keep Studio function-step outputs Serbian.

## Integration lessons

- Flight status has a graceful fallback. The response `source` field matters for demo honesty.
- Duffel flight search is added behind `DUFFEL_KEY`; without the key it should fail clearly rather than pretend.
- Studio HTTP connectors are UI-only in the current workflow and still need wiring/verification after ADK changes.
- Keep `.env` out of Git. Railway env vars are the production source of truth.

## Deployment and Git state

- Production URL from the implementation plan: `https://air-serbia-demo-production.up.railway.app`.
- Local `main` currently matches `origin/main`, but there are many uncommitted local changes.
- Because those changes are uncommitted, they have not been pushed to GitHub from this worktree.
- Treat Railway production as still representing the last deployed code unless `railway up` is run after committing/pushing or directly from this worktree.

## Reusable pattern for the next company demo

1. Start with a branded one-page microsite that lets the prospect hear the agent quickly.
2. Use one fixed demo customer record so the live call is deterministic.
3. Make one integration genuinely live if possible, usually flight/order/account status.
4. Mock write operations honestly and label them as demo-only.
5. Build a bilingual or local-language path early; language quality is often the difference between impressive and obviously generated.
6. Keep the implementation notes in `AGENTS.md` plus a session-learning file like this one so future agents can continue without rediscovery.
