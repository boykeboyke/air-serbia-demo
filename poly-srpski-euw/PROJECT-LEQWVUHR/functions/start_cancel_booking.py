from _gen import *  # <AUTO GENERATED>


@func_description('Start the booking cancellation flow')
def start_cancel_booking(conv: Conversation):
    conv.goto_flow("cancel_booking")
