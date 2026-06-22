from _gen import *  # <AUTO GENERATED>


def checkin_complete(conv: Conversation, flow: Flow):
    flight = conv.state.checkin_flight or ""
    date = conv.state.checkin_date or ""

    seat = "14C"

    conv.write_metric("CHECK_IN_COMPLETED", "1", write_once=True)
    conv.exit_flow()
    return (
        f"Prijavljivanje je uspešno završeno. "
        f"Sedište: {seat}. Let: {flight}. Datum: {date}. "
        f"Potvrdi pozivaocu da je prijavljivanje završeno, navedi sedište i poželi prijatno putovanje. "
        f"Pitaj da li možeš još nešto da pomogneš."
    )
