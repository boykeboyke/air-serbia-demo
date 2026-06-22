from _gen import *  # <AUTO GENERATED>
import datetime as dt
from zoneinfo import ZoneInfo
from functions.api_client import lookup_passenger


def start_function(conv: Conversation):
    tz = ZoneInfo("Europe/Belgrade")
    now = dt.datetime.now(tz)

    conv.state.current_date = now.strftime("%A %d %B %Y")
    conv.state.current_time = now.strftime("%H:%M")
    conv.state.current_weekday = now.strftime("%A")
    conv.state.current_iso_date = now.strftime("%Y-%m-%d")

    conv.state.goodbye_line = "Hvala vam na pozivu. Prijatan dan!"

    # Look up passenger by ANI (caller's phone number, auto-provided by the telephony layer).
    # For webchat/demo sessions conv.caller_number may be None — the lookup still works because
    # our demo API returns Milan Petrović for any phone value.
    phone = conv.caller_number or "+381641234567"
    try:
        rec = lookup_passenger(phone, conv=conv)
        if rec.get("found"):
            conv.state.passenger_name    = rec.get("passenger_name", "")
            conv.state.first_name        = rec.get("passenger_name", "").split()[0]
            conv.state.pnr               = rec.get("pnr", "")
            conv.state.flight_number     = rec.get("flight", "")
            conv.state.route             = rec.get("route", "")
            conv.state.departure_local   = rec.get("dep_time", "")
            conv.state.cabin             = rec.get("fare_class", "")
            conv.state.seat              = rec.get("seat", "")
    except Exception:
        pass
