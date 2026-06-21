from _gen import *  # <AUTO GENERATED>
from functions.api_client import verify_loyalty_member as _verify_loyalty_member


def verify_loyalty_member(conv: Conversation, flow: Flow):
    conv.state.loyalty_verify_attempts = (conv.state.loyalty_verify_attempts or 0) + 1

    guest_number = conv.entities.etihad_guest_number.value if conv.entities.etihad_guest_number else ""
    surname = conv.entities.member_surname.value if conv.entities.member_surname else ""

    if not guest_number or not surname:
        if conv.state.loyalty_verify_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        if conv.entities.member_surname:
            conv.entities.member_surname.value = None
        flow.goto_step("Collect Surname", "verification failed — retry")
        return "Nedostaju podaci. Zamolite pozivaoca da ponovi prezime."

    result = _verify_loyalty_member(guest_number, surname, conv=conv)

    if result.get("status") == "match":
        conv.state.loyalty_verified = True
        conv.state.loyalty_member_name = surname
        flow.goto_step("lookup_loyalty_status", "verified")
        return "Identitet je uspešno potvrđen."

    if conv.state.loyalty_verify_attempts >= 2:
        return conv.functions.handoff(reason="LOOKUP_FAILED")

    if conv.entities.member_surname:
        conv.entities.member_surname.value = None
    flow.goto_step("Collect Surname", "verification failed — retry")
    return "Ti podaci se ne poklapaju. Zamolite pozivaoca da ponovo pokuša sa prezimenom."
