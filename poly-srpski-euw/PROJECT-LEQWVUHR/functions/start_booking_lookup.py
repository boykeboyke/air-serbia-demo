from _gen import *  # <AUTO GENERATED>


@func_description('Start the booking lookup flow')
def start_booking_lookup(conv: Conversation):
    conv.goto_flow("booking_lookup")
