from _gen import *  # <AUTO GENERATED>


@func_description('API client utilities — not callable directly')
def api_client(conv: Conversation):
    return "API client module."


# --- Flight Status ---

def lookup_flight_status(flight_number, conv=None):
    if not conv or not flight_number:
        return {"found": False}
    try:
        response = conv.api.air_serbia_api.get_flight_status(flight_number)
        if response.status_code == 200:
            data = response.json()
            if data:
                data["found"] = True
                return data
            return {"found": False}
        else:
            conv.log.error("Flight status lookup failed", status=response.status_code, is_pii=False)
            return {"found": False}
    except Exception as e:
        conv.log.error("Flight status lookup error", error=str(e), is_pii=False)
        return {"found": False}


# --- Passenger / Booking Lookup ---

def lookup_passenger(phone, conv=None):
    if not conv or not phone:
        return {"found": False}
    try:
        response = conv.api.air_serbia_api.lookup_passenger(phone)
        if response.status_code == 200:
            data = response.json()
            if data:
                data["found"] = True
                return data
            return {"found": False}
        else:
            conv.log.error("Passenger lookup failed", status=response.status_code, is_pii=False)
            return {"found": False}
    except Exception as e:
        conv.log.error("Passenger lookup error", error=str(e), is_pii=False)
        return {"found": False}


def lookup_booking(booking_reference, conv=None):
    if not conv or not booking_reference:
        return {"found": False}
    try:
        response = conv.api.air_serbia_api.lookup_passenger(booking_reference)
        if response.status_code == 200:
            data = response.json()
            if data:
                data["found"] = True
                return data
            return {"found": False}
        else:
            conv.log.error("Booking lookup failed", status=response.status_code, is_pii=False)
            return {"found": False}
    except Exception as e:
        conv.log.error("Booking lookup error", error=str(e), is_pii=False)
        return {"found": False}


# --- Flight Search ---

def search_flights(origin_city, destination_city, travel_date, num_passengers, fare_preference, conv=None):
    # Flight search not yet supported by live API — return default availability
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


# --- Book Flight ---

def book_flight(flight, travel_date, num_passengers, fare_preference, conv=None):
    # Booking creation not yet supported by live API — return mock success
    if flight:
        return {"success": True, "booking_ref": "NEW001", "total_eur": 175}
    return {"success": False, "booking_ref": "", "total_eur": 0}


# --- Cancel Booking ---

def cancel_booking_api(booking_reference, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "booking not found"}
    try:
        response = conv.api.air_serbia_api.change_booking(
            json={"booking_reference": booking_reference, "action": "cancel"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data
            return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": data.get("reason", "cancellation failed")}
        else:
            conv.log.error("Cancel booking failed", status=response.status_code, is_pii=False)
            return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "service unavailable"}
    except Exception as e:
        conv.log.error("Cancel booking error", error=str(e), is_pii=False)
        return {"success": False, "refund_eur": 0, "refund_timeline": "", "reason": "service error"}


# --- Change Booking ---

def change_booking(booking_reference, changes, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        response = conv.api.air_serbia_api.change_booking(
            json={"booking_reference": booking_reference, **changes}
        )
        if response.status_code == 200:
            return response.json()
        else:
            conv.log.error("Change booking failed", status=response.status_code, is_pii=False)
            return {"success": False, "reason": "service unavailable"}
    except Exception as e:
        conv.log.error("Change booking error", error=str(e), is_pii=False)
        return {"success": False, "reason": "service error"}


# --- Add Baggage ---

def add_baggage(booking_reference, baggage_details, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        response = conv.api.air_serbia_api.add_baggage(
            json={"booking_reference": booking_reference, **baggage_details}
        )
        if response.status_code == 200:
            return response.json()
        else:
            conv.log.error("Add baggage failed", status=response.status_code, is_pii=False)
            return {"success": False, "reason": "service unavailable"}
    except Exception as e:
        conv.log.error("Add baggage error", error=str(e), is_pii=False)
        return {"success": False, "reason": "service error"}


# --- Check In ---

def check_in(booking_reference, passenger_details, conv=None):
    if not conv or not booking_reference:
        return {"success": False, "reason": "missing reference"}
    try:
        response = conv.api.air_serbia_api.check_in(
            json={"booking_reference": booking_reference, **passenger_details}
        )
        if response.status_code == 200:
            return response.json()
        else:
            conv.log.error("Check-in failed", status=response.status_code, is_pii=False)
            return {"success": False, "reason": "service unavailable"}
    except Exception as e:
        conv.log.error("Check-in error", error=str(e), is_pii=False)
        return {"success": False, "reason": "service error"}


# --- Loyalty Verification ---

def verify_loyalty_member(etihad_guest_number, member_surname, conv=None):
    # Loyalty verification not yet supported by live API — accept valid-looking pairs
    if etihad_guest_number and member_surname:
        return {"status": "match"}
    return {"status": "no_match"}


# --- Loyalty Status ---

def get_loyalty_status(etihad_guest_number, conv=None):
    # Loyalty status not yet supported by live API — return default
    if etihad_guest_number:
        return {"tier": "Silver", "miles_balance": 8500, "miles_expiry": "2027-06-01"}
    return None


# --- Log Complaint ---

def log_complaint_api(complaint_description, conv=None):
    return {"reference": "CS-2026-0451"}
