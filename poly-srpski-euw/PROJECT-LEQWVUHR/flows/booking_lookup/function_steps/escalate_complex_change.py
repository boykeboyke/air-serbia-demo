from _gen import *  # <AUTO GENERATED>


def escalate_complex_change(conv: Conversation, flow: Flow):
    return conv.functions.handoff(reason="COMPLEX_CHANGE")
