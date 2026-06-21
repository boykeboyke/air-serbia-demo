from _gen import *  # <AUTO GENERATED>


@func_description('Ljubazno završi poziv i prekini vezu.')
def goodbye_and_hang_up(conv: Conversation):
    return {
        "utterance": conv.state.goodbye_line or "Hvala vam što ste pozvali Er Srbiju. Prijatan dan!",
        "hangup": True,
    }
