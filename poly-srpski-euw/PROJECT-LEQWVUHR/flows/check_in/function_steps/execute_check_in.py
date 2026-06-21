from _gen import *  # <AUTO GENERATED>
from functions.api_client import check_in as _check_in


def execute_check_in(conv: Conversation, flow: Flow):
    result = _check_in(
        conv.entities.booking_reference.value,
        {},
        conv=conv,
    )

    if result.get("success"):
        seat = result.get("seat", "")
        conv.write_metric("CHECK_IN_COMPLETED", "1", write_once=True)
        conv.exit_flow()
        return (
            f"Prijavljivanje je uspešno. Sedište je {seat}. "
            f"Potvrdi pozivaocu da je prijavljivanje završeno, navedi sedište i poželi prijatno putovanje. "
            f"Pitaj da li mogu još nešto da pomognem."
        )

    conv.write_metric("CHECK_IN_FAILED", "1", write_once=True)
    conv.exit_flow()
    return (
        "Prijavljivanje trenutno nije moguće. Predloži pozivaocu da se prijavi onlajn preko Er Srbija sajta "
        "ili na aerodromu. Pitaj da li mogu još nešto da pomognem."
    )
