from _gen import *  # <AUTO GENERATED>
from functions.api_client import lookup_booking as _lookup_booking


def lookup_for_baggage(conv: Conversation, flow: Flow):
    conv.state.baggage_lookup_attempts = (conv.state.baggage_lookup_attempts or 0) + 1
    result = _lookup_booking(conv.entities.booking_reference.value, conv=conv)

    if not result.get("found"):
        if conv.state.baggage_lookup_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        if conv.entities.booking_reference:
            conv.entities.booking_reference.value = None
        flow.goto_step("Collect Booking Reference For Baggage", "not found — retry")
        return "Ta referentna oznaka nije pronađena. Zamoli pozivaoca da proveri i pokuša ponovo."

    conv.state.baggage_route = result.get("route", "")
    conv.state.baggage_date = result.get("date", "")
    conv.state.baggage_passenger_name = result.get("passenger_name", "")

    flow.goto_step("Collect Baggage Count", "booking found")
    return (
        f"Rezervacija pronađena: {conv.state.baggage_passenger_name}, "
        f"ruta {conv.state.baggage_route}, datum {conv.state.baggage_date}. "
        f"Kratko potvrdi rutu i datum pozivaocu, zatim pitaj koliko dodatnih kofera želi da doda."
    )
