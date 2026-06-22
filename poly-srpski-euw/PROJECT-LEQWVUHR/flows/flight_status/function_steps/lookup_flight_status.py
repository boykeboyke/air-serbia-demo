from _gen import *  # <AUTO GENERATED>


# Demo fallback data for known Air Serbia routes (used when live connector unavailable)
_DEMO_FLIGHTS = {
    "JU500": {"flight": "JU500", "route": "Beograd (BEG) do Njujork JFK", "scheduled_dep": "15:30", "actual_dep": "15:30", "status": "on_time", "gate": "Terminal 2"},
    "JU324": {"flight": "JU324", "route": "Beograd (BEG) do Pariz CDG", "scheduled_dep": "10:40", "actual_dep": "10:40", "status": "on_time", "gate": "Terminal 2"},
    "JU700": {"flight": "JU700", "route": "Beograd (BEG) do London LHR", "scheduled_dep": "10:00", "actual_dep": "10:00", "status": "on_time", "gate": "Terminal 2"},
}


def lookup_flight_status(conv: Conversation, flow: Flow):
    conv.state.flight_lookup_attempts = (conv.state.flight_lookup_attempts or 0) + 1
    flight_number = conv.entities.flight_number.value if conv.entities.flight_number else ""

    result = _fetch_live_flight(flight_number, conv)

    if not result:
        result = _demo_fallback(flight_number)

    if not result:
        if conv.state.flight_lookup_attempts >= 2:
            return conv.functions.handoff(reason="LOOKUP_FAILED")
        conv.entities.flight_number.value = None
        flow.goto_step("Collect Flight Number", "not found — retry")
        return "Taj broj leta nije pronađen. Zamolite pozivaoca da proveri i pokuša ponovo."

    conv.state.flight_status_checked = True
    conv.state.flight_code = result.get("flight", flight_number)
    conv.state.flight_route = result.get("route", "")
    conv.state.flight_gate = result.get("gate") or "Još nije dodeljen"

    scheduled = result.get("scheduled_dep", "")
    actual = result.get("actual_dep", scheduled)
    status = result.get("status", "on_time")

    if status == "delayed":
        delay_mins = _calc_delay(scheduled, actual)
        conv.state.flight_status_result = f"Kasni (planirano {scheduled}, sada {actual}, otprilike {delay_mins} min kašnjenja)"
        conv.state.flight_departure = actual
    elif status == "cancelled":
        conv.state.flight_status_result = "Otkazan"
        conv.state.flight_departure = scheduled
    elif status == "landed":
        conv.state.flight_status_result = "Sleteo"
        conv.state.flight_departure = scheduled
    else:
        conv.state.flight_status_result = f"Na vreme — polazak {scheduled}"
        conv.state.flight_departure = scheduled

    gate_txt = conv.state.flight_gate
    flow.goto_step("Report Flight Status", "found")
    return (
        f"PODACI O LETU: {conv.state.flight_code} | "
        f"Ruta: {conv.state.flight_route} | "
        f"Status: {conv.state.flight_status_result} | "
        f"Gejt/terminal: {gate_txt}. "
        f"Saopšti pozivaocu sve ove informacije odmah i jasno. "
        f"Ako let kasni, prvo iskaži razumevanje pa onda daj ažurirane informacije."
    )


def _fetch_live_flight(flight_number, conv):
    """Try api_integrations.yaml connector, then UI connector."""
    raw = None

    for attempt in [
        lambda: conv.api.air_serbia_api.get_flight_status(flight_number=flight_number),
        lambda: conv.api.air_serbia_api.get_flight_status(flight_number),
        lambda: conv.api.get_flight_status(flight_number=flight_number),
    ]:
        try:
            resp = attempt()
            if resp is None:
                continue
            if hasattr(resp, "status_code"):
                if resp.status_code == 200:
                    raw = resp.json()
            elif isinstance(resp, dict) and resp:
                raw = resp
            if raw:
                break
        except Exception:
            continue

    if not raw or raw.get("source", "").startswith("sample data"):
        return None

    status_map = {
        "En route": "on_time", "Scheduled": "on_time",
        "Landed": "landed", "Cancelled": "cancelled", "Delayed": "delayed",
    }
    dep = raw.get("departure", {})
    arr = raw.get("arrival", {})
    return {
        "found": True,
        "flight": raw.get("flight_number", flight_number),
        "route": f"{dep.get('airport', '')} do {arr.get('airport', '')}",
        "scheduled_dep": dep.get("scheduled_local", ""),
        "actual_dep": dep.get("scheduled_local", ""),
        "status": status_map.get(raw.get("status", ""), "on_time"),
        "gate": dep.get("terminal", ""),
    }


def _demo_fallback(flight_number):
    data = _DEMO_FLIGHTS.get((flight_number or "").upper())
    if data:
        return {**data, "found": True}
    return None


def _calc_delay(scheduled, actual):
    try:
        sh, sm = scheduled.split(":")
        ah, am = actual.split(":")
        return str((int(ah) * 60 + int(am)) - (int(sh) * 60 + int(sm)))
    except Exception:
        return "nepoznato"
