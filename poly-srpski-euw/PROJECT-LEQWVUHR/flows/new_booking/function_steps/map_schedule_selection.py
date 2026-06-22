from _gen import *  # <AUTO GENERATED>


def map_schedule_selection(conv: Conversation, flow: Flow):
    selected_date = conv.entities.schedule_date.value if conv.entities.schedule_date else None
    if not selected_date:
        flow.goto_step("Present Schedule", "datum nije prepoznat — pitaj ponovo")
        return "Nije moguće prepoznati izabrani datum."

    selected_str = str(selected_date)[:10]

    # Match against stored schedule slots
    chosen_flight = None
    chosen_price = None
    for i in range(1, 9):
        slot_date = getattr(conv.state, f"sched_date_{i}", None)
        if slot_date and str(slot_date)[:10] == selected_str:
            chosen_flight = getattr(conv.state, f"sched_code_{i}", None)
            chosen_price  = getattr(conv.state, f"sched_price_{i}", None)
            break

    if not chosen_flight:
        flow.goto_step("Present Schedule", "datum nije u rasporedu — pitaj ponovo")
        return f"Datum {selected_str} nije pronađen u rasporedu. Prikaži ponovo."

    # Carry the selected date forward as travel_date and set passengers default if missing
    conv.state.chosen_flight = chosen_flight
    conv.state.chosen_price  = str(chosen_price)
    if not conv.entities.num_passengers:
        conv.state._default_passengers = "1"

    flow.goto_step("Confirm Booking", f"izabran {selected_str} — {chosen_flight}")
    return f"Pozivalac je izabrao {selected_str}, let {chosen_flight}, cena {chosen_price} EUR."
