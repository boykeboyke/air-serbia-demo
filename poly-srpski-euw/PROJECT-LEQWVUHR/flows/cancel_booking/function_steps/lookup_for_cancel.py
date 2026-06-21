from _gen import *  # <AUTO GENERATED>
from functions.api_client import lookup_booking as _lookup_booking


def lookup_for_cancel(conv: Conversation, flow: Flow):
    conv.state.cancel_lookup_attempts = (conv.state.cancel_lookup_attempts or 0) + 1
    result = _lookup_booking(conv.entities.booking_reference.value, conv=conv)

    if not result.get("found"):
        if conv.state.cancel_lookup_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        conv.entities.booking_reference.value = None
        flow.goto_step("Collect Cancel Reference", "nije pronađeno — pokušaj ponovo")
        return "Ta referentna oznaka nije pronađena. Zamolite pozivaoca da proveri i pokuša ponovo."

    conv.state.cancel_route = result.get("route", "")
    conv.state.cancel_date = result.get("date", "")
    conv.state.cancel_passengers = str(result.get("passengers", ""))
    conv.state.cancel_passenger_name = result.get("passenger_name", "")
    conv.state.cancel_fare_type = result.get("fare_type", "")

    flow.goto_step("Confirm Cancellation", "rezervacija pronađena za otkazivanje")
    return (
        f"Rezervacija je pronađena. Pročitaj pozivaocu: "
        f"Ruta: {conv.state.cancel_route}, "
        f"Datum: {conv.state.cancel_date}, "
        f"Putnik: {conv.state.cancel_passenger_name}, "
        f"Vrsta karte: {conv.state.cancel_fare_type}. "
        f"Objasni politiku povraćaja: Standardne karte dobijaju povraćaj za 5-7 radnih dana. "
        f"Promo karte nisu podložne povratu sredstava."
    )
