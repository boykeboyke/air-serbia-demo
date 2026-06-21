from _gen import *  # <AUTO GENERATED>
from functions.api_client import lookup_booking as _lookup_booking


def lookup_booking(conv: Conversation, flow: Flow):
    conv.state.booking_lookup_attempts = (conv.state.booking_lookup_attempts or 0) + 1
    result = _lookup_booking(conv.entities.booking_reference.value, conv=conv)

    if not result.get("found"):
        if conv.state.booking_lookup_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        conv.entities.booking_reference.value = None
        flow.goto_step("Collect Booking Reference", "not found — retry")
        return "Ta referentna oznaka nije pronađena. Zamolite pozivaoca da proveri i pokuša ponovo."

    conv.state.booking_looked_up = True
    conv.state.booking_route = result.get("route", "")
    conv.state.booking_date = result.get("date", "")
    conv.state.booking_passengers = str(result.get("passengers", ""))
    conv.state.booking_passenger_name = result.get("passenger_name", "")
    conv.state.booking_fare_class = result.get("fare_class", "")
    conv.state.booking_fare_type = result.get("fare_type", "")

    flow.goto_step("Present Booking Actions", "booking found")
    return "Rezervacija je pronađena."
