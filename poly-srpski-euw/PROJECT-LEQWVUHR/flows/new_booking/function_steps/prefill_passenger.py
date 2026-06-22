from _gen import *  # <AUTO GENERATED>


def prefill_passenger(conv: Conversation, flow: Flow):
    # If the caller's record is already loaded (start_function ran), pre-populate
    # their full name so Collect Passenger Details skips asking for it.
    name = getattr(conv.state, "passenger_name", None)
    if not name:
        first = getattr(conv.state, "first_name", "") or ""
        last = getattr(conv.state, "last_name", "") or ""
        name = (first + " " + last).strip() or None

    if name:
        conv.state.pax_name_known = name

    flow.goto_step("Collect Passenger Details", "prikupljanje podataka putnika")
    return f"Prelazi se na prikupljanje podataka putnika. Ime poznato: {name or 'nije poznato'}"
