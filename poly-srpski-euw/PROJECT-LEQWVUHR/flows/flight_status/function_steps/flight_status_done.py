from _gen import *  # <AUTO GENERATED>


def flight_status_done(conv: Conversation, flow: Flow):
    conv.write_metric("FLIGHT_STATUS_COMPLETED", "1", write_once=True)
    conv.exit_flow()
    return "Pozivalac je dobio informacije o letu. Pitaj da li možeš još nešto da pomogneš."
