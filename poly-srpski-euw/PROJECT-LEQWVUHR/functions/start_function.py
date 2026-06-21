from _gen import *  # <AUTO GENERATED>
import datetime as dt
from zoneinfo import ZoneInfo


def start_function(conv: Conversation):
    tz = ZoneInfo("Europe/Belgrade")
    now = dt.datetime.now(tz)

    conv.state.current_date = now.strftime("%A %d %B %Y")
    conv.state.current_time = now.strftime("%H:%M")
    conv.state.current_weekday = now.strftime("%A")
    conv.state.current_iso_date = now.strftime("%Y-%m-%d")

    conv.state.goodbye_line = "Hvala vam na pozivu. Prijatan dan!"
