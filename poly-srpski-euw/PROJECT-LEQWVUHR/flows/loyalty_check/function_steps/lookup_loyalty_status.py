from _gen import *  # <AUTO GENERATED>
from functions.api_client import get_loyalty_status


def lookup_loyalty_status(conv: Conversation, flow: Flow):
    guest_number = conv.entities.etihad_guest_number.value if conv.entities.etihad_guest_number else ""
    result = get_loyalty_status(guest_number, conv=conv)

    if not result:
        return conv.functions.handoff(reason="LOOKUP_FAILED")

    tier = result.get("tier", "")
    miles = result.get("miles_balance", 0)
    expiry = result.get("miles_expiry", "")

    conv.state.loyalty_tier = tier
    conv.state.loyalty_miles = f"{miles:,}"
    conv.state.loyalty_expiry = expiry
    conv.state.loyalty_checked = True
    flow.goto_step("Report Loyalty Status", "found")
    return "Status lojalnosti je uspešno preuzet."
