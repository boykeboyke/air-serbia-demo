from _gen import *  # <AUTO GENERATED>
from functions.api_client import search_flights


def check_availability(conv: Conversation, flow: Flow):
    origin = conv.entities.origin_city.value if conv.entities.origin_city else None
    destination = conv.entities.destination_city.value if conv.entities.destination_city else None
    date = conv.entities.travel_date.value if conv.entities.travel_date else None
    passengers = conv.entities.num_passengers.value if conv.entities.num_passengers else None
    fare = conv.entities.fare_preference.value if conv.entities.fare_preference else "economy"

    result = search_flights(origin, destination, date, passengers, fare, conv=conv)

    flights = result.get("flights", [])
    available = result.get("available", False)
    alternatives = result.get("alternatives", False)

    if not flights:
        return conv.functions.handoff(reason="NO_AVAILABILITY")

    if len(flights) >= 1:
        f1 = flights[0]
        conv.state.alt_slot_1 = f"Let {f1['flight']} polazak {f1['dep_time']}, dolazak {f1['arr_time']}, {f1['price_eur']} evra"
        conv.state.flight_code_1 = f1["flight"]
        conv.state.flight_price_1 = f1["price_eur"]
    if len(flights) >= 2:
        f2 = flights[1]
        conv.state.alt_slot_2 = f"Let {f2['flight']} polazak {f2['dep_time']}, dolazak {f2['arr_time']}, {f2['price_eur']} evra"
        conv.state.flight_code_2 = f2["flight"]
        conv.state.flight_price_2 = f2["price_eur"]
    if len(flights) >= 3:
        f3 = flights[2]
        conv.state.alt_slot_3 = f"Let {f3['flight']} polazak {f3['dep_time']}, dolazak {f3['arr_time']}, {f3['price_eur']} evra"
        conv.state.flight_code_3 = f3["flight"]
        conv.state.flight_price_3 = f3["price_eur"]

    if available:
        flow.goto_step("Select Flight", "letovi pronađeni")
        return "Pronađeni su letovi za traženu rutu i datum."
    elif alternatives:
        flow.goto_step("Select Flight", "alternativni letovi dostupni")
        return "Tačan datum nije bio dostupan, ali postoje alternativni letovi na susednim datumima."
