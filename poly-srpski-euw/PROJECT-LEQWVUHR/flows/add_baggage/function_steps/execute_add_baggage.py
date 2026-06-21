from _gen import *  # <AUTO GENERATED>
from functions.api_client import add_baggage as _add_baggage


def execute_add_baggage(conv: Conversation, flow: Flow):
    baggage_count = conv.entities.baggage_count.value if conv.entities.baggage_count else "1"
    result = _add_baggage(
        conv.entities.booking_reference.value,
        {"count": int(baggage_count)},
        conv=conv,
    )

    if result.get("success"):
        total_price = result.get("total_price_eur", 0)
        conv.write_metric("BAGGAGE_ADDED", str(baggage_count), write_once=True)
        conv.exit_flow()
        return (
            f"Prtljag je uspešno dodat. Ukupna cena je {total_price} EUR. "
            f"Potvrdi pozivaocu da je prtljag dodat i navedi cenu. Pitaj da li mogu još nešto da pomognem."
        )

    conv.write_metric("BAGGAGE_ADD_FAILED", "1", write_once=True)
    return conv.functions.handoff(reason="API_ERROR")
