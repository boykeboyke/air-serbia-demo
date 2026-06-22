from _gen import *  # <AUTO GENERATED>
from functions.api_client import book_flight


def execute_booking(conv: Conversation, flow: Flow):
    flight = conv.state.chosen_flight
    date = conv.entities.travel_date.value if conv.entities.travel_date else ""
    passengers = conv.entities.num_passengers.value if conv.entities.num_passengers else 1
    fare = conv.entities.fare_preference.value if conv.entities.fare_preference else "economy"

    price = conv.state.chosen_price
    passenger_details = {
        "full_name":        conv.entities.passenger_full_name.value   if conv.entities.passenger_full_name   else "",
        "email":            conv.entities.passenger_email.value        if conv.entities.passenger_email        else "",
        "dob":              str(conv.entities.passenger_dob.value)     if conv.entities.passenger_dob          else "",
        "nationality":      conv.entities.passenger_nationality.value  if conv.entities.passenger_nationality  else "",
        "passport_number":  conv.entities.passenger_passport_number.value if conv.entities.passenger_passport_number else "",
        "passport_expiry":  str(conv.entities.passenger_passport_expiry.value) if conv.entities.passenger_passport_expiry else "",
    }
    conv.state.booking_email = passenger_details["email"]
    result = book_flight(flight, date, passengers, fare, price, passenger_details, conv=conv)

    if not result.get("success"):
        return conv.functions.handoff(reason="BOOKING_FAILED")

    ref = result.get("booking_ref", "")
    total = result.get("total_eur", price)
    conv.state.booking_reference = ref
    conv.state.booking_total = str(total)
    conv.state.booking_created = True
    conv.write_metric("BOOKING_CREATED", "1", write_once=True)
    flow.goto_step("Booking Complete", "potvrđeno")
    return "Rezervacija je uspešno potvrđena."
