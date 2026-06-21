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


def lookup_passenger(phone, conv=None):
    if not conv or not phone:
        return {"found": False}
    try:
        data = conv.api.lookup_passenger(phone=phone)
        return _flatten_passenger(data)
    except Exception as e:
        conv.log.error("Passenger lookup error", error=str(e), is_pii=False)
        return {"found": False}


def lookup_booking(booking_reference, conv=None):
    if not conv or not booking_reference:
        return {"found": False}
    try:
        # Demo API ignores the reference and always returns the demo passenger
        data = conv.api.lookup_passenger(phone=booking_reference)
        return _flatten_passenger(data)
    except Exception as e:
        conv.log.error("Booking lookup error", error=str(e), is_pii=False)
        return {"found": False}


# --- Flight Search (mock — no live search API) ---

def search_flights(origin_city, destination_city, travel_date, num_passengers, fare_preference, conv=None):
    if origin_city and destination_city:
        return {
            "available": True,
            "alternatives": False,
            "flights": [
                {"flight": "JU700", "dep_time": "10:00", "arr_time": "12:30", "price_eur": 175},
                {"flight": "JU702", "dep_time": "16:30", "arr_time": "19:00", "price_eur": 205},
            ],
        }
    return {"available": False, "alternatives": False, "flights": []}


# --- Book Flight (mock) ---

def book_flight(flight, travel_date, num_passengers, fare_preference, conv=None):
    if flight:
        return {"success": True, "booking_ref": "NEW001", "total_eur": 175}
    return {"success": False, "booking_ref": "", "total_eur": 0}


# --- Cancel Booking ---

def cancel_booking_api(booking_reference, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "booking not found"}
    try:
        data = conv.api.change_booking(pnr=booking_reference, action="cancel")
        if data and data.get("status") in ("confirmed", "cancelled"):
            return {"success": True, "refund_eur": 0, "refund_timeline": "5-7 radnih dana", "reason": ""}
        return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "cancellation failed"}
    except Exception as e:
        conv.log.error("Cancel booking error", error=str(e), is_pii=False)
        return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "service error"}


# --- Change Booking ---

def change_booking(booking_reference, changes, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        data = conv.api.change_booking(pnr=booking_reference, **changes)
        if data and data.get("status") == "confirmed":
            return {"success": True, **data}
        return {"success": False, "reason": "service unavailable"}
    except Exception as e:
        conv.log.error("Change booking error", error=str(e), is_pii=False)
        return {"success": False, "reason": "service error"}


# --- Add Baggage ---

def add_baggage(booking_reference, baggage_details, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        extra_bags = int(baggage_details.get("count", 1))
        data = conv.api.add_baggage(pnr=booking_reference, extra_bags=extra_bags)
        if data and data.get("status") == "confirmed":
            return {"success": True, "total_price_eur": data.get("price_eur", extra_bags * 35)}
        return {"success": False, "reason": "service unavailable"}
    except Exception as e:
        conv.log.error("Add baggage error", error=str(e), is_pii=False)
        return {"success": False, "reason": "service error"}


# --- Check In ---

def check_in(booking_reference, passenger_details, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        data = conv.api.check_in(pnr=booking_reference)
        if data and data.get("status") == "checked_in":
            return {"success": True, "seat": data.get("seat", "")}
        return {"success": False, "reason": "check-in unavailable"}
    except Exception as e:
        conv.log.error("Check-in error", error=str(e), is_pii=False)
        return {"success": False, "reason": "service error"}


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
