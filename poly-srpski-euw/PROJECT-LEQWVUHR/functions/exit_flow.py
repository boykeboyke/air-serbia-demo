from _gen import *  # <AUTO GENERATED>


@func_description('Pozivalac želi da odustane od trenutnog zadatka bez završetka.')
def exit_flow(conv: Conversation):
    conv.exit_flow()
    return "Potvrdi da nećemo nastaviti sa započetim, zatim pitaj da li ima još nešto."
