from _gen import *  # <AUTO GENERATED>


def decline_check_in(conv: Conversation, flow: Flow):
    conv.exit_flow()
    return "Pozivalac je odustao od prijavljivanja. Potvrdi da nećemo nastaviti i pitaj da li mogu još nešto da pomognem."
