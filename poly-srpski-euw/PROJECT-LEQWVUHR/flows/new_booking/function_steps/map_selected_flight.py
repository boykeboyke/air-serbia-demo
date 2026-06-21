from _gen import *  # <AUTO GENERATED>


def map_selected_flight(conv: Conversation, flow: Flow):
    slot_map = {
        "slot_1": (conv.state.flight_code_1, conv.state.flight_price_1),
        "slot_2": (conv.state.flight_code_2, conv.state.flight_price_2),
        "slot_3": (conv.state.flight_code_3, conv.state.flight_price_3),
    }
    selected = conv.entities.selected_flight.value if conv.entities.selected_flight else None
    choice = slot_map.get(selected)

    if choice and choice[0]:
        conv.state.chosen_flight = choice[0]
        conv.state.chosen_price = choice[1]
        flow.goto_step("Confirm Booking", "let izabran")
        return f"Pozivalac je izabrao let {choice[0]} po ceni od {choice[1]} evra."
    else:
        flow.goto_step("Select Flight", "nevažeći izbor — pitaj ponovo")
        return "Nije moguće utvrditi koji je let izabran. Pitaj ponovo."
