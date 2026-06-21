from _gen import *  # <AUTO GENERATED>
from functions.api_client import lookup_booking as _lookup_booking


def lookup_for_checkin(conv: Conversation, flow: Flow):
    conv.state.checkin_lookup_attempts = (conv.state.checkin_lookup_attempts or 0) + 1
    result = _lookup_booking(conv.entities.booking_reference.value, conv=conv)

    if not result.get("found"):
        if conv.state.checkin_lookup_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        if conv.entities.booking_reference:
            conv.entities.booking_reference.value = None
        flow.goto_step("Collect Booking Reference For Check In", "not found — retry")
        return "Ta referentna oznaka nije pronađena. Zamoli pozivaoca da proveri i pokuša ponovo."

    conv.state.checkin_flight = result.get("route", "")
    conv.state.checkin_date = result.get("date", "")
    conv.state.checkin_passenger_name = result.get("passenger_name", "")

    flow.goto_step("Confirm Check In", "booking found")
    return (
        f"Rezervacija pronađena: {conv.state.checkin_passenger_name}, "
        f"let {conv.state.checkin_flight}, datum {conv.state.checkin_date}. "
        f"Potvrdi pozivaocu detalje leta i pitaj da li želi da se prijavi."
    )
