from _gen import *  # <AUTO GENERATED>


@func_description('Hand the call off — deflect to a callback when live transfer is unavailable')
@func_parameter('reason', 'short SCREAMING_SNAKE_CASE reason code for why we are handing off')
def handoff(conv: Conversation, reason: str):
    conv.write_metric("HANDOFF", reason, write_once=True)
    return {
        "utterance": (
            "I'm sorry, I'm not able to sort that out on this call. Our team can "
            "help — please call us back during business hours and we'll pick it up "
            "from there."
        ),
        "hangup": True,
    }
