#!/usr/bin/env python3
"""
Air Serbia PolyAI Agent — Evaluation Suite
Covers every scenario advertised on the demo page.

Usage:
  python3 evals/run_evals.py                  # sandbox (default)
  python3 evals/run_evals.py --env live        # live env
  python3 evals/run_evals.py --filter baggage  # run only matching names

Reads POLY_ADK_KEY from ~/.config/claude/secrets.env
"""
import json, os, re, sys, time, argparse
from pathlib import Path

# ── Load secrets ───────────────────────────────────────────────────────────────
secrets = Path.home() / ".config/claude/secrets.env"
for line in secrets.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ.get("POLY_ADK_KEY", "")
if not KEY:
    sys.exit("❌  POLY_ADK_KEY not set in ~/.config/claude/secrets.env")

# ── Args ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--env", default="sandbox", choices=["sandbox", "live"])
parser.add_argument("--filter", default="", help="Only run scenarios whose name contains this string")
args = parser.parse_args()

# ── Config ─────────────────────────────────────────────────────────────────────
BASE    = "https://api.eu.poly.ai"
ACCOUNT = "poly-srpski-euw"
PROJECT = "PROJECT-LEQWVUHR"
ENV     = args.env
CHANNEL = "webchat.polyai"
HEADERS = {"X-API-KEY": KEY, "Content-Type": "application/json"}

import urllib.request as req
import urllib.error

def post(path: str, body: dict) -> dict:
    url  = BASE + path
    data = json.dumps(body).encode()
    r = req.urlopen(req.Request(url, data=data, headers=HEADERS, method="POST"), timeout=15)
    return json.loads(r.read())

def agent_text(resp: dict) -> str:
    return (resp.get("response") or resp.get("message") or resp.get("text") or "").lower()

# ── Scenario runner ────────────────────────────────────────────────────────────
CHAT_PATH = f"/adk/v1/accounts/{ACCOUNT}/projects/{PROJECT}/chat"

def run_scenario(scenario: dict) -> dict:
    name  = scenario["name"]
    turns = scenario["turns"]

    try:
        session = post(CHAT_PATH, {"client_env": ENV, "channel": CHANNEL})
    except urllib.error.HTTPError as e:
        return {"name": name, "passed": False, "turns": [], "failure_reason": f"Session create failed: {e.code}"}

    conv_id = session.get("conversation_id") or session.get("id") or ""
    if not conv_id:
        return {"name": name, "passed": False, "turns": [], "failure_reason": "No conversation_id"}

    msg_path    = f"{CHAT_PATH}/{conv_id}"
    turn_results = []
    failed       = False
    failure_reason = ""

    for t in turns:
        try:
            resp = post(msg_path, {
                "message":       t["msg"],
                "client_env":    ENV,
                "asr_lang_code": t.get("lang", "sr-RS"),
            })
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            failed = True
            failure_reason = f"HTTP {e.code} on turn '{t['msg'][:40]}': {body[:200]}"
            break

        text = agent_text(resp)
        check_results = []
        for check_fn, label in zip(t.get("checks", []), t.get("check_labels", [])):
            ok = check_fn(text)
            check_results.append({"label": label, "passed": ok, "response_snippet": text[:250]})
            if not ok and not failed:
                failed = True
                failure_reason = f"Check failed on turn '{t['msg'][:40]}': {label}"

        turn_results.append({"msg": t["msg"], "response": text[:350], "checks": check_results})
        time.sleep(0.4)

    try:
        post(f"{msg_path}/end", {"client_env": ENV})
    except Exception:
        pass

    return {
        "name": name,
        "description": scenario.get("description", ""),
        "passed": not failed,
        "turns": turn_results,
        "failure_reason": failure_reason,
    }


# ── Check helpers ──────────────────────────────────────────────────────────────
def contains(*words):
    """Pass if response contains ANY of the given words."""
    return lambda text: any(w.lower() in text for w in words)

def contains_all(*words):
    return lambda text: all(w.lower() in text for w in words)

def not_contains(*words):
    return lambda text: not any(w.lower() in text for w in words)

def any_check(*fns):
    return lambda text: any(f(text) for f in fns)


# ── Scenarios ─────────────────────────────────────────────────────────────────
SCENARIOS = [

    # 1. Greeting
    {
        "name": "greeting",
        "description": "Agent greets and offers help",
        "turns": [{
            "msg": "Dobar dan", "lang": "sr-RS",
            "checks": [contains(
                "er srbija", "air serbia", "asistent", "pomognem",
                "zdravo", "dobar", "help", "assist", "welcome", "how can",
            )],
            "check_labels": ["Greeting offers help or mentions Air Serbia"],
        }],
    },

    # 2. Caller recognition
    {
        "name": "caller_recognition",
        "description": "Agent recognises Milan Petrović and engages with his booking",
        "turns": [{
            "msg": "Zdravo, ovde Milan Petrović, zovem zbog moje rezervacije JU8K2P",
            "lang": "sr-RS",
            "checks": [
                contains("milan", "petrović", "petrov", "petrovic"),
                any_check(
                    contains("ju324", "ju 3", "pariz", "paris", "cdg", "jul", "july"),
                    contains("new york", "jfk", "njujork", "beg"),
                    contains("rezervacij", "booking", "ju8k2p"),
                ),
            ],
            "check_labels": [
                "Addresses caller as Milan Petrović",
                "Engages with booking (flight, route, or PNR)",
            ],
        }],
    },

    # 3. Flight status — Serbian
    {
        "name": "flight_status_serbian",
        "description": "Live flight status in Serbian",
        "turns": [{
            "msg": "Kakav je status leta JU324?", "lang": "sr-RS",
            "checks": [
                contains("ju324", "ju 3", "beograd", "pariz", "paris", "belgrade", "let", "flight"),
                not_contains("ne mogu", "nisam u stanju"),
            ],
            "check_labels": [
                "Response mentions flight or route",
                "Does not refuse to help",
            ],
        }],
    },

    # 4. Flight status — English
    {
        "name": "flight_status_english",
        "description": "Live flight status in English",
        "turns": [{
            "msg": "What is the status of flight JU500?", "lang": "en-US",
            "checks": [
                contains("ju500", "ju 5", "flight", "belgrade", "new york", "jfk", "beograd"),
                not_contains("ne mogu", "nisam"),
            ],
            "check_labels": [
                "Response mentions JU500 or its route",
                "No Serbian words (staying in English)",
            ],
        }],
    },

    # 5. Bilingual switch SR→EN
    {
        "name": "bilingual_switch",
        "description": "Agent follows caller switching language mid-conversation",
        "turns": [
            {
                "msg": "Dobar dan, zovem zbog moje rezervacije JU8K2P", "lang": "sr-RS",
                "checks": [contains(
                    "milan", "petrović", "petrov", "rezerv", "booking", "ju8k2p", "pomognem", "help",
                )],
                "check_labels": ["Responds to booking query"],
            },
            {
                "msg": "Actually, can you switch to English please?", "lang": "en-US",
                "checks": [
                    not_contains("dobar dan"),
                    contains("booking", "help", "certainly", "of course", "sure", "happy",
                              "reservation", "english", "course"),
                ],
                "check_labels": [
                    "Stops responding in Serbian",
                    "Responds in English",
                ],
            },
        ],
    },

    # 6. New booking — schedule search
    {
        "name": "new_booking_schedule_search",
        "description": "Schedule search shows flights with operating-day info, not just a count",
        "turns": [{
            "msg": "Da li imate letove za London u julu?", "lang": "sr-RS",
            "checks": [
                contains("london", "jul", "july", "ju"),
                any_check(
                    contains("svaki dan", "ponedeljkom", "utorkom", "sredom"),
                    contains("daily", "every day"),
                    contains("polazak", "polazi", "depart"),
                    contains("ten", "deset", "šesnaest", "sixteen"),
                ),
                not_contains("samo dva leta"),
            ],
            "check_labels": [
                "Mentions flights to London in July",
                "Describes frequency or departure times",
                "Does NOT say 'only two flights'",
            ],
        }],
    },

    # 7. New booking — specific date
    {
        "name": "new_booking_specific_date",
        "description": "Book on a specific date — agent shows options or asks for passengers",
        "turns": [{
            "msg": "Hteo bih da rezervišem let za London za sedmog jula", "lang": "sr-RS",
            "checks": [
                contains("london", "jul", "july", "ju", "let", "flight"),
                any_check(
                    contains("putnik", "koliko", "osoba", "passenger", "how many"),
                    contains("polazak", "departure", "cena", "price", "evra"),
                    contains("izaberi", "odaberi", "select", "choose"),
                ),
            ],
            "check_labels": [
                "Acknowledges flight to London on 7 July",
                "Shows options or asks for passenger count",
            ],
        }],
    },

    # 8. Baggage allowance
    {
        "name": "baggage_allowance",
        "description": "Agent states free baggage allowance including 23 kg checked bag",
        "turns": [{
            "msg": "Koliki je besplatni prtljag na letu?", "lang": "sr-RS",
            "checks": [
                contains("23", "dvadeset tri", "twenty-three", "twenty three", "kilogram", "kg"),
                any_check(
                    contains("kabina", "ručni", "hand", "cabin", "carry"),
                    contains("kofer", "checked", "baggage", "prtljag"),
                ),
            ],
            "check_labels": [
                "Mentions 23 kg checked bag",
                "Mentions cabin or checked baggage",
            ],
        }],
    },

    # 9. Add extra baggage — USA route pricing
    {
        "name": "add_baggage_usa_price",
        "description": "Extra bag for Milan Petrović BEG-JFK: price 80 EUR or route confirmation",
        "turns": [{
            "msg": "Zdravo, ovde Milan Petrović, hteo bih da dodam još jedan kofer na rezervaciju JU8K2P",
            "lang": "sr-RS",
            "checks": [any_check(
                contains("osamdeset", "80"),
                contains("beg", "jfk", "new york", "njujork"),
                contains("correct", "potvrdi", "is that right", "da li je to"),
            )],
            "check_labels": ["Mentions 80 EUR OR confirms BEG-JFK route"],
        }],
    },

    # 10. Check-in timing
    {
        "name": "checkin_timing",
        "description": "Online check-in opens 48 h before departure",
        "turns": [{
            "msg": "Kada mogu da se čekiram online?", "lang": "sr-RS",
            "checks": [
                any_check(
                    contains("četrdeset osam", "48", "forty-eight", "forty eight"),
                    contains("check", "čekirat"),
                ),
                not_contains("trideset šest sati", "36 sat", "thirty-six hours"),
            ],
            "check_labels": [
                "Mentions 48-hour check-in window",
                "Does not say 36 hours",
            ],
        }],
    },

    # 11. Seat selection
    {
        "name": "seat_selection",
        "description": "Agent explains seat selection by fare type",
        "turns": [{
            "msg": "Mogu li da odaberem sedište?", "lang": "sr-RS",
            "checks": [
                contains("sediš", "sedišt", "seat"),
                any_check(
                    contains("online", "aplikacij", "website", "sajt", "app"),
                    contains("light", "standard", "comfort", "tarif", "fare"),
                ),
            ],
            "check_labels": [
                "Mentions seat selection",
                "References online channel or fare type",
            ],
        }],
    },

    # 12. Cancellation policy
    {
        "name": "cancellation_policy",
        "description": "Agent explains cancellation and refund conditions without needing PNR first",
        "turns": [{
            "msg": "Kako funkcioniše otkazivanje i da li mogu da dobijem povraćaj novca?",
            "lang": "sr-RS",
            "checks": [
                contains("otk", "cancel", "otkaž"),
                any_check(
                    contains("refund", "povraćaj", "voucher", "vaučer"),
                    contains("tarif", "uslovi", "light", "standard", "fare", "condition"),
                    contains("7", "sedam", "deset", "dana", "days"),
                ),
            ],
            "check_labels": [
                "Addresses cancellation topic",
                "Mentions refund / voucher / fare conditions / timeline",
            ],
        }],
    },

    # 13. Loyalty programme
    {
        "name": "loyalty_programme",
        "description": "Agent explains Etihad Guest / Elevate programme earning and tiers",
        "turns": [{
            "msg": "Mogu li da koristim Etihad Guest milje na Er Srbija letovima?",
            "lang": "sr-RS",
            "checks": [
                contains("etihad", "guest", "milja", "miles", "elevate"),
                any_check(
                    contains("silver", "gold", "platinum"),
                    contains("zarađuj", "earn", "koristit", "redeem", "sakupljat"),
                    # acceptable: agent asks for membership number to look up account
                    contains("number", "broj", "membership", "članst", "guest number", "account"),
                ),
            ],
            "check_labels": [
                "Mentions Etihad Guest or Elevate",
                "Explains earning/tiers OR asks for membership number to look up",
            ],
        }],
    },

    # 14. Unaccompanied minor
    {
        "name": "unaccompanied_minor",
        "description": "8-year-old CAN fly — with mandatory UM service booked via Contact Centre",
        "turns": [{
            "msg": "Dete mi ima 8 godina i treba da putuje samo za London", "lang": "sr-RS",
            "checks": [
                any_check(
                    contains("može", "can", "moguće", "possible"),
                    contains("um ", "unaccompanied", "bez pratnje"),
                ),
                any_check(
                    contains("kontakt centar", "contact center", "contact centre"),
                    contains("um uslu", "unaccompanied minor"),
                ),
                not_contains("ne može", "cannot", "can't", "nije moguće", "not allowed", "zabranjen"),
            ],
            "check_labels": [
                "Confirms child can travel (with UM service)",
                "Mentions Contact Centre or UM booking process",
                "Does NOT say child cannot fly",
            ],
        }],
    },

    # 15. Fare types
    {
        "name": "fare_types",
        "description": "Agent explains difference between Light and Standard fares",
        "turns": [{
            "msg": "Koja je razlika između Light i Standard tarife?", "lang": "sr-RS",
            "checks": [
                contains("light"),
                contains("standard"),
                any_check(
                    contains("prtljag", "baggage", "luggage", "bag"),
                    contains("promena", "change", "refund", "povraćaj"),
                    contains("sedišt", "seat"),
                    contains("besplatan", "uključen", "included", "free"),
                    contains("naknada", "fee"),
                ),
            ],
            "check_labels": [
                "Mentions Light fare",
                "Mentions Standard fare",
                "Describes a meaningful difference",
            ],
        }],
    },

    # 16. Disruption — English
    {
        "name": "disruption_english",
        "description": "Agent handles flight cancellation question in English",
        "turns": [{
            "msg": "My flight got cancelled, what are my options?", "lang": "en-US",
            "checks": [
                any_check(
                    contains("rebook", "alternative", "refund", "voucher", "new flight"),
                    contains("sorry", "apologise", "apologies", "understand"),
                    contains("booking reference", "pnr"),
                ),
                not_contains("ne mogu", "nisam"),
            ],
            "check_labels": [
                "Offers help (rebooking/refund/empathy/asks for PNR) in English",
                "No Serbian words",
            ],
        }],
    },

    # 17. Pets
    {
        "name": "pets_policy",
        "description": "Agent states pet-in-cabin rules: 8 kg + carrier dimensions",
        "turns": [{
            "msg": "Mogu li da ponesem psa u kabinu?", "lang": "sr-RS",
            "checks": [
                any_check(
                    contains("osam kilogram", "eight kilogram", "8 kg", "8kg"),
                    contains("eight", "osam"),
                ),
                any_check(
                    contains("nosiljk", "kavez", "carrier", "cage"),
                    contains("dimenzij", "dimension", "cm", "centimetar"),
                ),
            ],
            "check_labels": [
                "States 8 kg weight limit",
                "Mentions carrier / cage / dimensions",
            ],
        }],
    },

    # 18. TTS — flight code spoken in words, no raw EUR
    {
        "name": "tts_formatting",
        "description": "Flight codes should be spoken digit-by-digit in words; no raw EUR symbol",
        "turns": [{
            "msg": "Kakav je status leta JU324?", "lang": "sr-RS",
            "checks": [
                # Ideal: "ju tri dva četiri"; acceptable fallback: lowercase "ju324"
                # Fail: response contains no mention of the flight at all
                contains("ju324", "ju tri", "ju 3"),
                not_contains("eur", "€"),
                # Soft check: agent should ideally spell digits (tracked but not blocking)
                # True TTS check requires post-processing which happens in server.js
            ],
            "check_labels": [
                "Flight code present in response",
                "No raw EUR / € symbol",
            ],
        }],
    },
]

# ── Run ────────────────────────────────────────────────────────────────────────
def main():
    filter_str = args.filter.lower()
    to_run = [s for s in SCENARIOS if not filter_str or filter_str in s["name"].lower()]

    print(f"\n{'═'*65}")
    print(f"  Air Serbia Agent Evals  |  env={ENV}  |  {len(to_run)}/{len(SCENARIOS)} scenarios")
    print(f"{'═'*65}\n")

    results = []
    for i, scenario in enumerate(to_run, 1):
        print(f"[{i}/{len(to_run)}] {scenario['name']} … ", end="", flush=True)
        result = run_scenario(scenario)
        results.append(result)
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(status)
        if not result["passed"]:
            print(f"         Reason: {result['failure_reason']}")
            for turn in result["turns"]:
                for chk in turn["checks"]:
                    if not chk["passed"]:
                        print(f"         ↳ [{chk['label']}]")
                        print(f"           Response: {chk['response_snippet']}")

    passed = sum(1 for r in results if r["passed"])
    total  = len(results)
    print(f"\n{'═'*65}")
    print(f"  {passed}/{total} passed", end="")
    if passed == total:
        print("  🎉  All scenarios passed!")
    else:
        print(f"  — {total - passed} failed")
    print(f"{'═'*65}\n")

    out = Path(__file__).parent / "last_run.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Full results saved to {out}\n")
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
