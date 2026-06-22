from _gen import *  # <AUTO GENERATED>
import datetime
import calendar
from functions.api_client import search_flights


# ── Date-range helpers ────────────────────────────────────────────────────────

_MONTHS_SR = {
    "januar": 1, "januara": 1, "january": 1,
    "februar": 2, "februara": 2, "february": 2,
    "mart": 3, "marta": 3, "march": 3,
    "april": 4, "aprila": 4,
    "maj": 5, "maja": 5, "may": 5,
    "jun": 6, "juna": 6, "june": 6,
    "jul": 7, "jula": 7, "july": 7,
    "avgust": 8, "avgusta": 8, "august": 8,
    "septembar": 9, "septembra": 9, "september": 9,
    "oktobar": 10, "oktobra": 10, "october": 10,
    "novembar": 11, "novembra": 11, "november": 11,
    "decembar": 12, "decembra": 12, "december": 12,
}

_DAY_NAMES = {
    0: "ponedeljak", 1: "utorak", 2: "sreda",
    3: "četvrtak", 4: "petak", 5: "subota", 6: "nedelja",
}


def _dates_in_range(start: datetime.date, end: datetime.date, weekends_only: bool):
    dates = []
    cur = start
    while cur <= end:
        if not weekends_only or cur.weekday() >= 5:
            dates.append(cur)
        cur += datetime.timedelta(days=1)
    return dates


def _parse_period(travel_period: str, ref_iso: str):
    """Return (dates, weekends_only) from a free-text period string."""
    text = travel_period.lower() if travel_period else ""
    ref = datetime.date.fromisoformat(ref_iso) if ref_iso else datetime.date.today()
    year = ref.year

    month = None
    for name, num in _MONTHS_SR.items():
        if name in text:
            month = num
            break
    if month is None:
        month = ref.month
    if month < ref.month:
        year += 1

    wants_weekends = any(w in text for w in ("vikend", "weekend", "subota", "nedelja", "subote", "nedeljom"))
    is_second_half = any(w in text for w in ("druga", "second", "drugoj", "drugu", "drugom", "krajem", "kraj", "kasni", "kasno", "later", "end of", "late"))
    is_first_half = any(w in text for w in ("prva", "first", "prvoj", "prvu", "početak", "pocetak", "početkom", "pocetkom", "early", "start of"))

    last_day = calendar.monthrange(year, month)[1]
    if is_second_half:
        start = datetime.date(year, month, 16)
        end = datetime.date(year, month, last_day)
    elif is_first_half:
        start = datetime.date(year, month, 1)
        end = datetime.date(year, month, 15)
    else:
        start = datetime.date(year, month, 1)
        end = datetime.date(year, month, last_day)

    return _dates_in_range(start, end, wants_weekends), wants_weekends


# ── Main function ─────────────────────────────────────────────────────────────

def check_availability(conv: Conversation, flow: Flow):
    origin      = (conv.entities.origin_city.value if conv.entities.origin_city else None) or "Beograd"
    destination = conv.entities.destination_city.value if conv.entities.destination_city else None
    date        = conv.entities.travel_date.value    if conv.entities.travel_date    else None
    period_text = conv.entities.travel_period.value  if conv.entities.travel_period  else None
    passengers  = conv.entities.num_passengers.value if conv.entities.num_passengers else 1
    fare        = conv.entities.fare_preference.value if conv.entities.fare_preference else "economy"

    if not destination:
        flow.goto_step("Collect Booking Details", "nedostaje destinacija")
        return "Nije navedena destinacija. Pitaj pozivaoca za grad dolaska."

    # ── SCHEDULE MODE: caller wants to see availability across a date range ──
    if period_text and not date:
        ref_iso = getattr(conv.state, "current_iso_date", None) or datetime.date.today().isoformat()
        dates_to_search, _ = _parse_period(period_text, ref_iso)

        if not dates_to_search:
            return conv.functions.handoff(reason="NO_AVAILABILITY")

        # Search each date; dedupe by date keeping cheapest result
        schedule = {}  # date_str → flight dict
        for d in dates_to_search:
            date_str = d.strftime("%Y-%m-%d")
            result = search_flights(origin, destination, date_str, 1, fare, conv=conv)
            for f in result.get("flights", []):
                if date_str not in schedule or f["price_eur"] < schedule[date_str]["price_eur"]:
                    schedule[date_str] = {**f, "date": date_str, "weekday": _DAY_NAMES.get(d.weekday(), "")}

        if not schedule:
            return conv.functions.handoff(reason="NO_AVAILABILITY")

        # Store up to 8 schedule slots
        # Register schedule slot variables explicitly so the ADK validator sees them
        conv.state.sched_date_1 = conv.state.sched_date_2 = conv.state.sched_date_3 = ""
        conv.state.sched_date_4 = conv.state.sched_date_5 = conv.state.sched_date_6 = ""
        conv.state.sched_date_7 = conv.state.sched_date_8 = ""
        conv.state.sched_code_1 = conv.state.sched_code_2 = conv.state.sched_code_3 = ""
        conv.state.sched_code_4 = conv.state.sched_code_5 = conv.state.sched_code_6 = ""
        conv.state.sched_code_7 = conv.state.sched_code_8 = ""
        conv.state.sched_price_1 = conv.state.sched_price_2 = conv.state.sched_price_3 = ""
        conv.state.sched_price_4 = conv.state.sched_price_5 = conv.state.sched_price_6 = ""
        conv.state.sched_price_7 = conv.state.sched_price_8 = ""

        sorted_dates = sorted(schedule.keys())
        lines = []
        for i, ds in enumerate(sorted_dates[:8]):
            f = schedule[ds]
            day_label = f"{f['weekday'].capitalize()} {ds[8:10]}.{ds[5:7]}."
            line = f"{day_label}: let {f['flight']}, polazak {f['dep_time']}, dolazak {f['arr_time']}, cena {f['price_eur']} evra"
            lines.append(line)
            slot = str(i + 1)
            setattr(conv.state, f"sched_date_{slot}", ds)
            setattr(conv.state, f"sched_code_{slot}", f["flight"])
            setattr(conv.state, f"sched_price_{slot}", str(f["price_eur"]))

        conv.state.flight_schedule = "\n".join(lines)
        conv.state.schedule_count = str(len(sorted_dates[:8]))
        flow.goto_step("Present Schedule", "raspored pronađen")
        return f"Pronađen raspored: {len(sorted_dates)} datuma."

    # ── SPECIFIC BOOKING MODE: single date ────────────────────────────────────
    if not date:
        return conv.functions.handoff(reason="NO_AVAILABILITY")

    date_str = str(date)[:10]
    result = search_flights(origin, destination, date_str, passengers, fare, conv=conv)
    flights = result.get("flights", [])

    if not flights:
        return conv.functions.handoff(reason="NO_AVAILABILITY")

    # Explicit assignments so the ADK validator registers these variables
    conv.state.alt_slot_1 = conv.state.alt_slot_2 = conv.state.alt_slot_3 = ""
    conv.state.flight_code_1 = conv.state.flight_code_2 = conv.state.flight_code_3 = ""
    conv.state.flight_price_1 = conv.state.flight_price_2 = conv.state.flight_price_3 = ""
    for i, f in enumerate(flights[:3]):
        label = f"Let {f['flight']} polazak {f['dep_time']}, dolazak {f['arr_time']}, {f['price_eur']} evra"
        if i == 0:
            conv.state.alt_slot_1 = label; conv.state.flight_code_1 = f["flight"]; conv.state.flight_price_1 = str(f["price_eur"])
        elif i == 1:
            conv.state.alt_slot_2 = label; conv.state.flight_code_2 = f["flight"]; conv.state.flight_price_2 = str(f["price_eur"])
        elif i == 2:
            conv.state.alt_slot_3 = label; conv.state.flight_code_3 = f["flight"]; conv.state.flight_price_3 = str(f["price_eur"])

    if len(flights) == 1:
        conv.state.chosen_flight = flights[0]["flight"]
        conv.state.chosen_price  = str(flights[0]["price_eur"])
        flow.goto_step("Confirm Booking", "jedan let pronađen")
        return f"Pronađen je jedan let: {conv.state.alt_slot_1}"
    else:
        flow.goto_step("Select Flight", "više letova pronađeno")
        return f"Pronađena su {len(flights)} leta za traženu rutu."
