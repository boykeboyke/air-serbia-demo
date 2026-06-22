from _gen import *  # <AUTO GENERATED>


@func_description('Hand the call off — deflect to a callback when live transfer is unavailable')
@func_parameter('reason', 'short SCREAMING_SNAKE_CASE reason code for why we are handing off')
def handoff(conv: Conversation, reason: str):
    conv.write_metric("HANDOFF", reason, write_once=True)
    return {
        "utterance": (
            "Žao mi je, ne mogu to da rešim tokom ovog poziva. "
            "Naš tim može da vam pomogne — pozovite nas ponovo i bićemo vam na usluzi."
        ),
        "hangup": True,
    }
