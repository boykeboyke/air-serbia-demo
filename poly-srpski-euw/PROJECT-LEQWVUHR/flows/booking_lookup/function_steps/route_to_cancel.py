from _gen import *  # <AUTO GENERATED>


def route_to_cancel(conv: Conversation, flow: Flow):
    conv.goto_flow("cancel_booking")
