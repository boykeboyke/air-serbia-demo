# Builder-agent prompt - paste into PolyAI Studio's agentic builder

_Paste this into Studio's agentic builder ("Glot") to construct the Air Serbia agent. It names the
agent, wires the HTTP connectors to the demo API, sets the call-open lookup and the bilingual switch,
and lists test scenarios. Replace `[BASE_URL]` with your running origin: `http://localhost:3000` for
local testing, or the Railway URL once deployed. Keep instructions short and one-change-at-a-time if
Glot stalls (see `voice-agent-playbook.md` §7)._

---

Build me a bilingual (Serbian and English) voice agent called **Ana** for **Air Serbia**'s contact
centre. Use the runtime persona in `system-prompt.md` as the Agent behaviour prompt. Specifics:

## Connectors (HTTP integrations) - point at `[BASE_URL]`

1. **`lookup_passenger`** - GET `[BASE_URL]/api/passenger/{phone}`. Returns the passenger record
   (name, Elevate tier/miles, upcoming booking, baggage, balance, eligible_for).
2. **`get_flight_status`** - GET `[BASE_URL]/api/flight-status/{flight_number}`. **This is a live
   lookup** (the server proxies a real flight-status API). Returns status, departure/arrival airports
   and times.
3. **`search_flights`** - GET `[BASE_URL]/api/flight-search?origin={origin}&destination={destination}&date={date}&cabin_class={cabin_class}&passengers={passengers}`.
   **Live Duffel lookup.** Returns up to 5 Air Serbia flights with departure time, arrival time and
   price in EUR. Parameters: `origin` and `destination` are IATA codes (e.g. BEG, DBV, CDG);
   `date` is YYYY-MM-DD; `cabin_class` is `economy` or `business` (default economy);
   `passengers` is number of adults (default 1).
4. **`change_booking`** - POST `[BASE_URL]/api/booking/change` with `{pnr, new_date, new_flight_number, notes}`.
5. **`add_baggage`** - POST `[BASE_URL]/api/baggage/add` with `{pnr, extra_bags}`.
6. **`check_in`** - POST `[BASE_URL]/api/checkin` with `{pnr, seat}`.
7. Built-in **`transfer_to_agent`** and **`goodbye_and_hang_up`**.

## Call-open `start_function` (must actually run the lookup)

```python
import datetime as dt
from zoneinfo import ZoneInfo
from functions.api_client import lookup_passenger   # the lookup_passenger connector

def start_function(conv):
    tz = ZoneInfo("Europe/Belgrade")
    conv.state.current_date = dt.datetime.now(tz).strftime("%A %d %B %Y")
    try:
        rec = lookup_passenger(conv)                 # by caller ANI / phone
        conv.state.first_name        = rec["first_name"]
        conv.state.elevate_tier      = rec["elevate"]["tier"]
        conv.state.miles_balance     = rec["elevate"]["miles_balance"]
        conv.state.miles_to_next_tier= rec["elevate"]["miles_to_next_tier"]
        conv.state.next_tier         = rec["elevate"]["next_tier"]
        b = rec["upcoming_booking"]
        conv.state.pnr               = b["pnr"]
        conv.state.flight_number     = b["flight_number"]
        conv.state.route             = b["route"]
        conv.state.departure_local   = b["departure_local"]
        conv.state.cabin             = b["cabin"]
        conv.state.seat              = b["seat"]
        conv.state.checked_bags      = b["checked_bags"]
        conv.state.extra_bags_allowed= b["extra_bags_allowed"]
        conv.state.checkin_opens_local = b["checkin_opens_local"]
        conv.state.outstanding_balance_eur = rec["payment"]["outstanding_balance_eur"]
        conv.state.eligible_for      = ", ".join(rec["eligible_for"])
    except Exception:
        pass
```

Then inject these into the `# PASSENGER CONTEXT` block of the Agent prompt (exactly as in
`system-prompt.md`) so the agent answers record questions directly.

## Bilingual switch (a function, not a prompt rule)

Create **`set_caller_language`** that calls `conv.set_language(code)` where `code` is `"sr-RS"` for
Serbian or `"en-US"` for English. Instruct the agent: **the instant you detect the caller's language
(or a switch), call `set_caller_language` with the right code BEFORE replying.** Make every action
function return its `confirmation_message` in the caller's current language, and localise
`goodbye_and_hang_up`. (Multilingual is bound at the runtime, not the prompt - see playbook §8.)

## Routing

- Information questions (Elevate tier/miles, refund eligibility, the upcoming itinerary, baggage
  allowance, check-in timing, balance) -> the **main agent answers from `# PASSENGER CONTEXT`**. Do
  not route these into a flow.
- Actions -> the matching flow: change booking, add baggage, check in. Flight status calls
  `get_flight_status` live and reads the result back.

## Voice readback rules

Add the number/time readback rules from `system-prompt.md` to the Agent behaviour prompt. This is
critical for Serbian TTS: `09:00-10:05` is not a duration. It means departure at nine and arrival at
ten oh five, so the agent should say "polazak u devet sati, dolazak u deset sati i pet minuta".
Flight numbers are read digit-by-digit after the airline code, e.g. `JU850` -> "Ju osam pet nula".

## Call opening

Greet briefly and bilingually-safe, e.g. "Hvala što ste pozvali Air Serbia, ovde Ana. / Thanks for
calling Air Serbia, this is Ana." Then, once you have the record, address the passenger by first name
in their language.

## Test scenarios to run (then give me the demo web-call number/widget)

1. **Serbian booking change.** Caller speaks Serbian; agent switches to Serbian, greets "Milan",
   changes flight JU324 to a later date, reads the confirmation and reference back in Serbian.
2. **English baggage add.** Caller speaks English; agent adds one extra bag, states 35 EUR (from the
   record), confirms in English.
3. **Live flight status.** Caller asks the status of JU324; agent calls `get_flight_status` and reads
   back the live status and times.
4. **Mid-call language switch.** Caller opens in Serbian, then asks a question in English; agent
   follows on the next turn.
5. **Safety.** Caller reports a medical emergency; agent stops and transfers to a human immediately.
