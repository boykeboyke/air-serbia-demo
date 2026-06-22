from _gen import *  # <AUTO GENERATED>


@func_description('API client utilities — not callable directly')
def api_client(conv: Conversation):
    return "API client module."


# --- Flight Status ---

def lookup_flight_status(flight_number, conv=None):
    """Fallback mock — primary path goes through lookup_flight_status.py/_fetch_live_flight."""
    if not conv or not flight_number:
        return {"found": False}
    try:
        data = conv.api.get_flight_status(flight_number=flight_number)
        if data:
            data["found"] = True
            return data
        return {"found": False}
    except Exception as e:
        conv.log.error("Flight status lookup error", error=str(e), is_pii=False)
        return {"found": False}


# --- Passenger / Booking Lookup ---

def _flatten_passenger(data):
    """Flatten Railway passenger response into the structure flows expect."""
    if not data:
        return {"found": False}
    booking = data.get("upcoming_booking", {})
    return {
        "found": True,
        "passenger_name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "pnr": booking.get("pnr", ""),
        "flight": booking.get("flight", ""),
        "route": booking.get("route", ""),
        "date": booking.get("date", ""),
        "dep_time": booking.get("dep_time", ""),
        "arr_time": booking.get("arr_time", ""),
        "seat": booking.get("seat", ""),
        "fare_type": booking.get("fare", ""),
        "fare_class": booking.get("fare", ""),
        "passengers": 1,
        "tier": data.get("tier", ""),
        "miles": data.get("miles", 0),
    }


def _call_passenger_api(phone, conv):
    """Try api_integrations.yaml connector then UI connector, return raw dict or None."""
    for attempt in [
        lambda: conv.api.air_serbia_api.lookup_passenger(phone=phone),
        lambda: conv.api.air_serbia_api.lookup_passenger(phone),
        lambda: conv.api.lookup_passenger(phone=phone),
    ]:
        try:
            resp = attempt()
            if resp is None:
                continue
            if hasattr(resp, "status_code"):
                if resp.status_code == 200:
                    return resp.json()
            elif isinstance(resp, dict) and resp:
                return resp
        except Exception:
            continue
    return None


def lookup_passenger(phone, conv=None):
    if not conv or not phone:
        return {"found": False}
    try:
        data = _call_passenger_api(phone, conv)
        return _flatten_passenger(data)
    except Exception as e:
        conv.log.error("Passenger lookup error", error=str(e), is_pii=False)
        return {"found": False}


def lookup_booking(booking_reference, conv=None):
    if not conv or not booking_reference:
        return {"found": False}
    try:
        data = _call_passenger_api(booking_reference, conv)
        return _flatten_passenger(data)
    except Exception as e:
        conv.log.error("Booking lookup error", error=str(e), is_pii=False)
        return {"found": False}


# --- Flight Search (live via Duffel / our /api/flight-search endpoint) ---

_CITY_TO_IATA = {
    # Serbian / local names
    "beograd": "BEG", "belgrade": "BEG",
    "dubrovnik": "DBV",
    "split": "SPU",
    "tivat": "TIV", "podgorica": "TGD",
    "pariz": "CDG", "paris": "CDG",
    "london": "LHR",
    "njujork": "JFK", "new york": "JFK",
    "amsterdam": "AMS",
    "beč": "VIE", "bec": "VIE", "vienna": "VIE", "wien": "VIE",
    "rim": "FCO", "rome": "FCO", "roma": "FCO",
    "madrid": "MAD",
    "barcelona": "BCN",
    "istanbul": "IST",
    "atina": "ATH", "athens": "ATH",
    "zurich": "ZRH", "cirih": "ZRH",
    "frankfurt": "FRA",
    "berlin": "BER",
    "brisel": "BRU", "brussels": "BRU",
    "nikozija": "LCA", "nicosia": "LCA", "larnaka": "LCA",
    "solun": "SKG", "thessaloniki": "SKG",
    "moskva": "SVO", "moscow": "SVO",
    "abu dabi": "AUH", "abu dhabi": "AUH",
    "dubai": "DXB",
    "doha": "DOH",
    "tel aviv": "TLV", "tel avid": "TLV",
    "sarajevo": "SJJ",
    "skoplje": "SKP", "skopje": "SKP",
    "tirana": "TIA",
    "budimpesta": "BUD", "budapest": "BUD",
    "bukurest": "OTP", "bucharest": "OTP",
    "sofija": "SOF", "sofia": "SOF",
    "zagreb": "ZAG",
    "ljubljana": "LJU",
    "prag": "PRG", "prague": "PRG",
    "varšava": "WAW", "warsaw": "WAW",
    "kijev": "KBP", "kyiv": "KBP",
    "minhen": "MUC", "munich": "MUC", "münchen": "MUC",
    "milan": "MXP", "milano": "MXP",
    "barcelona": "BCN",
    "nice": "NCE", "nica": "NCE",
    "lisabon": "LIS", "lisbon": "LIS",
    "kopenhagen": "CPH", "copenhagen": "CPH",
    "stokholm": "ARN", "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    "varšava": "WAW", "warszawa": "WAW",
    "toronto": "YYZ",
    "čikago": "ORD", "chicago": "ORD",
}

def _resolve_iata(city_name):
    """Resolve a free-text city name to an IATA airport code."""
    if not city_name:
        return None
    s = city_name.strip().lower()
    # Already looks like an IATA code
    if len(s) == 3 and s.isalpha():
        return s.upper()
    return _CITY_TO_IATA.get(s)


_DEMO_ROUTES = {
    ("BEG", "CDG"): [
        {"flight": "JU324", "dep_time": "10:40", "arr_time": "13:00", "price_eur": 189},
        {"flight": "JU326", "dep_time": "18:15", "arr_time": "20:30", "price_eur": 215},
    ],
    ("BEG", "LHR"): [
        {"flight": "JU700", "dep_time": "10:00", "arr_time": "12:45", "price_eur": 199},
        {"flight": "JU702", "dep_time": "16:30", "arr_time": "19:15", "price_eur": 229},
    ],
    ("BEG", "JFK"): [
        {"flight": "JU500", "dep_time": "15:30", "arr_time": "18:45", "price_eur": 649},
    ],
    ("BEG", "AMS"): [
        {"flight": "JU400", "dep_time": "09:15", "arr_time": "11:30", "price_eur": 159},
        {"flight": "JU402", "dep_time": "17:00", "arr_time": "19:15", "price_eur": 175},
    ],
    ("BEG", "VIE"): [
        {"flight": "JU350", "dep_time": "08:00", "arr_time": "08:55", "price_eur": 89},
        {"flight": "JU352", "dep_time": "14:30", "arr_time": "15:25", "price_eur": 99},
    ],
    ("BEG", "IST"): [
        {"flight": "JU450", "dep_time": "11:00", "arr_time": "13:30", "price_eur": 129},
        {"flight": "JU452", "dep_time": "19:00", "arr_time": "21:30", "price_eur": 145},
    ],
    ("BEG", "ATH"): [
        {"flight": "JU200", "dep_time": "07:30", "arr_time": "09:15", "price_eur": 99},
        {"flight": "JU202", "dep_time": "15:00", "arr_time": "16:45", "price_eur": 115},
    ],
    ("BEG", "FCO"): [
        {"flight": "JU600", "dep_time": "09:00", "arr_time": "10:30", "price_eur": 139},
        {"flight": "JU602", "dep_time": "16:45", "arr_time": "18:15", "price_eur": 155},
    ],
    ("BEG", "SPU"): [
        {"flight": "JU860", "dep_time": "08:30", "arr_time": "09:30", "price_eur": 75},
        {"flight": "JU862", "dep_time": "17:00", "arr_time": "18:00", "price_eur": 89},
    ],
    ("BEG", "DBV"): [
        {"flight": "JU850", "dep_time": "09:00", "arr_time": "10:05", "price_eur": 79},
        {"flight": "JU852", "dep_time": "17:30", "arr_time": "18:35", "price_eur": 95},
    ],
    ("BEG", "TGD"): [
        {"flight": "JU800", "dep_time": "07:45", "arr_time": "08:30", "price_eur": 65},
        {"flight": "JU802", "dep_time": "16:30", "arr_time": "17:15", "price_eur": 75},
    ],
    ("BEG", "ZAG"): [
        {"flight": "JU900", "dep_time": "07:00", "arr_time": "07:50", "price_eur": 55},
        {"flight": "JU902", "dep_time": "18:00", "arr_time": "18:50", "price_eur": 69},
    ],
    ("BEG", "FRA"): [
        {"flight": "JU300", "dep_time": "08:45", "arr_time": "10:30", "price_eur": 149},
        {"flight": "JU302", "dep_time": "16:00", "arr_time": "17:45", "price_eur": 169},
    ],
    ("BEG", "BER"): [
        {"flight": "JU310", "dep_time": "09:30", "arr_time": "11:15", "price_eur": 139},
        {"flight": "JU312", "dep_time": "17:30", "arr_time": "19:15", "price_eur": 155},
    ],
    ("BEG", "BRU"): [
        {"flight": "JU360", "dep_time": "10:00", "arr_time": "12:00", "price_eur": 169},
    ],
    ("BEG", "ZRH"): [
        {"flight": "JU370", "dep_time": "09:45", "arr_time": "11:30", "price_eur": 159},
    ],
    ("BEG", "MAD"): [
        {"flight": "JU380", "dep_time": "11:30", "arr_time": "14:30", "price_eur": 199},
    ],
    ("BEG", "BCN"): [
        {"flight": "JU390", "dep_time": "10:15", "arr_time": "13:00", "price_eur": 189},
    ],
    ("BEG", "DXB"): [
        {"flight": "JU550", "dep_time": "22:00", "arr_time": "04:30", "price_eur": 399},
    ],
}


def _demo_flight_search(origin_iata, dest_iata, date_str):
    """Return demo flights for origin→dest, any date."""
    key = (origin_iata or "BEG", dest_iata)
    flights = _DEMO_ROUTES.get(key)
    if not flights:
        return []
    return flights


def search_flights(origin_city, destination_city, travel_date, num_passengers, fare_preference, conv=None):
    origin = _resolve_iata(origin_city) or "BEG"
    destination = _resolve_iata(destination_city)
    if not destination or not travel_date:
        return {"available": False, "alternatives": False, "flights": []}

    cabin = fare_preference if fare_preference in ("economy", "business") else "economy"
    pax = int(num_passengers) if num_passengers else 1

    date_str = str(travel_date)[:10] if travel_date else None
    if not date_str:
        return {"available": False, "alternatives": False, "flights": []}

    raw = None
    if conv:
        for attempt in [
            lambda: conv.api.air_serbia_api.search_flights(
                origin=origin, destination=destination,
                date=date_str, cabin_class=cabin, passengers=pax),
            lambda: conv.api.search_flights(
                origin=origin, destination=destination,
                date=date_str, cabin_class=cabin, passengers=pax),
        ]:
            try:
                resp = attempt()
                if resp is None:
                    continue
                if hasattr(resp, "status_code") and resp.status_code == 200:
                    raw = resp.json()
                elif isinstance(resp, dict) and resp.get("flights"):
                    raw = resp
                if raw:
                    break
            except Exception:
                continue

    if raw and raw.get("flights"):
        flights = [
            {
                "flight":    f.get("flight", ""),
                "dep_time":  f.get("departs", f.get("dep_time", "")),
                "arr_time":  f.get("arrives", f.get("arr_time", "")),
                "price_eur": f.get("price_eur", 0),
            }
            for f in raw["flights"]
        ]
        return {"available": True, "alternatives": False, "flights": flights}

    # Demo fallback — return hardcoded routes when live connector is unavailable
    demo = _demo_flight_search(origin, destination, date_str)
    if demo:
        price_mult = 1.2 if cabin == "business" else 1.0
        flights = [{**f, "price_eur": int(f["price_eur"] * price_mult)} for f in demo]
        return {"available": True, "alternatives": False, "flights": flights}

    return {"available": False, "alternatives": False, "flights": []}


# --- Book Flight (mock confirmation — real Duffel order creation requires full passenger PII) ---

_PNR_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def _generate_pnr():
    import hashlib, time
    seed = str(time.time()).encode()
    h = hashlib.sha256(seed).hexdigest()
    return "".join(_PNR_CHARS[int(h[i*2:i*2+2], 16) % len(_PNR_CHARS)] for i in range(6))

def book_flight(flight, travel_date, num_passengers, fare_preference, price_per_pax=None, passenger_details=None, conv=None):
    if not flight:
        return {"success": False, "booking_ref": "", "total_eur": 0}
    pax = int(num_passengers) if num_passengers else 1
    per_pax = float(price_per_pax) if price_per_pax else 150.0
    total = round(per_pax * pax, 2)
    if conv and passenger_details:
        conv.log.info("New booking passenger details collected", is_pii=True,
                      flight=flight, date=str(travel_date), passengers=pax,
                      name=passenger_details.get("full_name", ""),
                      email=passenger_details.get("email", ""))
    return {"success": True, "booking_ref": _generate_pnr(), "total_eur": total}


# --- Cancel Booking ---

def _call_post_api(conv, operation, **kwargs):
    """Try api_integrations.yaml then UI connector for POST operations. Returns dict or None."""
    for getter in [
        lambda: getattr(conv.api.air_serbia_api, operation),
        lambda: getattr(conv.api, operation),
    ]:
        try:
            fn = getter()
            resp = fn(**kwargs)
            if resp is None:
                continue
            if hasattr(resp, "status_code"):
                if resp.status_code == 200:
                    return resp.json()
            elif isinstance(resp, dict) and resp:
                return resp
        except Exception:
            continue
    return None


def cancel_booking_api(booking_reference, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "booking not found"}
    try:
        data = _call_post_api(conv, "change_booking", pnr=booking_reference, action="cancel")
        if data and data.get("status") in ("confirmed", "cancelled"):
            return {"success": True, "refund_eur": 0, "refund_timeline": "5-7 radnih dana", "reason": ""}
        # Demo fallback — always succeed for demo purposes
        return {"success": True, "refund_eur": 0, "refund_timeline": "5-7 radnih dana", "reason": ""}
    except Exception as e:
        conv.log.error("Cancel booking error", error=str(e), is_pii=False)
        return {"success": True, "refund_eur": 0, "refund_timeline": "5-7 radnih dana", "reason": ""}


# --- Change Booking ---

def change_booking(booking_reference, changes, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        data = _call_post_api(conv, "change_booking", pnr=booking_reference, **changes)
        if data:
            return {"success": True, **data}
        return {"success": True, "status": "confirmed"}
    except Exception as e:
        conv.log.error("Change booking error", error=str(e), is_pii=False)
        return {"success": True, "status": "confirmed"}


# --- Add Baggage ---

def add_baggage(booking_reference, baggage_details, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        extra_bags = int(baggage_details.get("count", 1))
        data = _call_post_api(conv, "add_baggage", pnr=booking_reference, extra_bags=extra_bags)
        price = data.get("price_eur", extra_bags * 35) if data else extra_bags * 35
        return {"success": True, "total_price_eur": price}
    except Exception as e:
        conv.log.error("Add baggage error", error=str(e), is_pii=False)
        return {"success": True, "total_price_eur": 35}


# --- Check In ---

def check_in(booking_reference, passenger_details, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        data = _call_post_api(conv, "check_in", pnr=booking_reference)
        seat = data.get("seat", "14A") if data else "14A"
        return {"success": True, "seat": seat}
    except Exception as e:
        conv.log.error("Check-in error", error=str(e), is_pii=False)
        return {"success": True, "seat": "14A"}


# --- Loyalty (mock — no live loyalty API) ---

def verify_loyalty_member(etihad_guest_number, member_surname, conv=None):
    if etihad_guest_number and member_surname:
        return {"status": "match"}
    return {"status": "no_match"}


def get_loyalty_status(etihad_guest_number, conv=None):
    if etihad_guest_number:
        return {"tier": "Silver", "miles_balance": 18450, "miles_expiry": "2027-06-01"}
    return None


# --- Log Complaint (mock) ---

def log_complaint_api(complaint_description, conv=None):
    return {"reference": "CS-2026-0451"}
