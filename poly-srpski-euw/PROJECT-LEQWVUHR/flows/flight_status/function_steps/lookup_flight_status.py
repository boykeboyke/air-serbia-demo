from _gen import *  # <AUTO GENERATED>
from functions.api_client import lookup_flight_status as _lookup_flight_status_mock


def lookup_flight_status(conv: Conversation, flow: Flow):
    conv.state.flight_lookup_attempts = (conv.state.flight_lookup_attempts or 0) + 1
    flight_number = conv.entities.flight_number.value if conv.entities.flight_number else ""

    # Call the Railway demo server which proxies AviationStack live.
    # Note: direct outbound requests() from Studio functions are network-sandboxed
    # and fail with DNS errors. The Railway server handles the live API call instead.
    # Wire this connector in Studio UI: GET https://air-serbia-demo-production.up.railway.app/api/flight-status/{flight_number}
    result = _fetch_live_flight(flight_number, conv)

    # Fall back to mock data if connector unavailable
    if not result:
        result = _lookup_flight_status_mock(flight_number, conv=conv)

    if not result.get("found"):
        if conv.state.flight_lookup_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        conv.entities.flight_number.value = None
        flow.goto_step("Collect Flight Number", "not found — retry")
        return "Taj broj leta nije pronađen. Zamolite pozivaoca da proveri i pokuša ponovo."

    conv.state.flight_status_checked = True
    flight = result.get("flight", "")
    route = result.get("route", "")
    scheduled = result.get("scheduled_dep", "")
    actual = result.get("actual_dep", "")
    status = result.get("status", "")
    gate = result.get("gate", "")

    conv.state.flight_code = flight
    conv.state.flight_route = route
    conv.state.flight_gate = gate or "Još nije dodeljen"

    if status == "delayed":
        delay_mins = _calc_delay(scheduled, actual)
        conv.state.flight_status_result = f"Kasni (planirano {scheduled}, sada {actual}, otprilike {delay_mins} minuta kašnjenja)"
        conv.state.flight_departure = actual
    elif status == "cancelled":
        conv.state.flight_status_result = "Otkazan"
        conv.state.flight_departure = scheduled
    elif status == "landed":
        conv.state.flight_status_result = "Sleteo"
        conv.state.flight_departure = scheduled
    else:
        conv.state.flight_status_result = "Na vreme"
        conv.state.flight_departure = scheduled

    flow.goto_step("Report Flight Status", "found")
    return "Status leta je uspešno preuzet."


def _fetch_live_flight(flight_number, conv):
    """Fetch real-time flight data via the Railway demo server (which proxies AviationStack).
    Requires the HTTP connector 'get_flight_status' wired in Studio UI to:
      GET https://air-serbia-demo-production.up.railway.app/api/flight-status/{flight_number}
    """
    try:
        result = conv.api.get_flight_status(flight_number=flight_number)
        if not result or result.get("source", "").startswith("sample data"):
            return None

        status_map = {
            "En route": "on_time",
            "Scheduled": "on_time",
            "Landed": "landed",
            "Cancelled": "cancelled",
            "Delayed": "delayed",
        }
        status_raw = result.get("status", "")
        dep = result.get("departure", {})
        arr = result.get("arrival", {})

        return {
            "found": True,
            "flight": result.get("flight_number", flight_number),
            "route": f"{dep.get('airport', '')} do {arr.get('airport', '')}",
            "scheduled_dep": dep.get("scheduled_local", ""),
            "actual_dep": dep.get("scheduled_local", ""),
            "status": status_map.get(status_raw, "on_time"),
            "gate": dep.get("terminal", ""),
        }
    except Exception:
        return None


def _calc_delay(scheduled, actual):
    try:
        sh, sm = scheduled.split(":")
        ah, am = actual.split(":")
        return str((int(ah) * 60 + int(am)) - (int(sh) * 60 + int(sm)))
    except Exception:
        return "nepoznato"
