from _gen import *  # <AUTO GENERATED>
from functions.api_client import log_complaint_api


def submit_complaint(conv: Conversation, flow: Flow):
    description = conv.entities.complaint_description.value if conv.entities.complaint_description else ""
    result = log_complaint_api(description, conv=conv)

    ref = result.get("reference", "")
    conv.state.complaint_reference = ref
    conv.state.complaint_logged = True
    conv.write_metric("COMPLAINT_LOGGED", "1", write_once=True)
    flow.goto_step("Complaint Logged", "evidentirano")
    return "Žalba je uspešno evidentirana."
