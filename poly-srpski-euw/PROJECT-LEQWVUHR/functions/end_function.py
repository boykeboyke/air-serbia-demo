from _gen import *  # <AUTO GENERATED>


def end_function(conv: Conversation):
    if conv.state.flight_status_checked:
        conv.write_metric("OUTCOME", "FLIGHT_STATUS", write_once=True)
    elif conv.state.booking_looked_up:
        conv.write_metric("OUTCOME", "BOOKING_LOOKUP", write_once=True)
    elif conv.state.booking_created:
        conv.write_metric("OUTCOME", "BOOKING_CREATED", write_once=True)
    elif conv.state.booking_cancelled:
        conv.write_metric("OUTCOME", "BOOKING_CANCELLED", write_once=True)
    elif conv.state.loyalty_checked:
        conv.write_metric("OUTCOME", "LOYALTY_CHECK", write_once=True)
    elif conv.state.complaint_logged:
        conv.write_metric("OUTCOME", "COMPLAINT", write_once=True)
