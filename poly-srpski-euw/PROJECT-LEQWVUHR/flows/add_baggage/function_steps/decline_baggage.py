from _gen import *  # <AUTO GENERATED>


def decline_baggage(conv: Conversation, flow: Flow):
    conv.exit_flow()
    return "Pozivalac je odustao od dodavanja prtljaga. Potvrdi da nećemo dodati prtljag i pitaj da li mogu još nešto da pomognem."
