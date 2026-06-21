from _gen import *  # <AUTO GENERATED>
from functions.api_client import book_flight


def execute_booking(conv: Conversation, flow: Flow):
    flight = conv.state.chosen_flight
    date = conv.entities.travel_date.value if conv.entities.travel_date else ""
    passengers = conv.entities.num_passengers.value if conv.entities.num_passengers else 1
    fare = conv.entities.fare_preference.value if conv.entities.fare_preference else "economy"

    result = book_flight(flight, date, passengers, fare, conv=conv)

    if not result.get("success"):
        return conv.functions.handoff(reason="BOOKING_FAILED")

    ref = result.get("booking_ref", "")
    total = result.get("total_eur", 0)
    conv.state.booking_reference = ref
    conv.state.booking_total = str(total)
    conv.state.booking_created = True
    conv.write_metric("BOOKING_CREATED", "1", write_once=True)
    flow.goto_step("Booking Complete", "potvrđeno")
    return "Rezervacija je uspešno potvrđena."
