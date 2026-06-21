from _gen import *  # <AUTO GENERATED>


def keep_booking(conv: Conversation, flow: Flow):
    conv.exit_flow()
    return "Pozivalac je odlučio da zadrži rezervaciju. Potvrdi da rezervacija ostaje nepromenjena i pitaj ima li još nešto."
