from _gen import *  # <AUTO GENERATED>


def handle_no_selection(conv: Conversation, flow: Flow):
    return conv.functions.handoff(reason="NO_AVAILABILITY")
