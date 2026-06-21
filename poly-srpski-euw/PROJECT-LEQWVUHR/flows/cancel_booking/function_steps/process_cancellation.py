from _gen import *  # <AUTO GENERATED>
from functions.api_client import cancel_booking_api


def process_cancellation(conv: Conversation, flow: Flow):
    result = cancel_booking_api(conv.entities.booking_reference.value, conv=conv)

    if not result.get("success"):
        reason = result.get("reason", "nepoznata greška")
        conv.exit_flow()
        return (
            f"Otkazivanje nije moglo biti obrađeno zbog: {reason}. "
            f"Obavesti pozivaoca i pitaj ima li još nešto u čemu možeš pomoći."
        )

    refund = result.get("refund_eur", 0)
    timeline = result.get("refund_timeline", "5-7 radnih dana")
    conv.state.refund_amount = str(refund)
    conv.state.refund_timeline = timeline
    conv.state.booking_cancelled = True
    conv.write_metric("BOOKING_CANCELLED", "1", write_once=True)
    flow.goto_step("Cancellation Complete", "uspešno")
    return "Otkazivanje je uspešno obrađeno."
