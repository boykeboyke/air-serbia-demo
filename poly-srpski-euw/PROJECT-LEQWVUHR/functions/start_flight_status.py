from _gen import *  # <AUTO GENERATED>


@func_description('Start the flight status check flow')
def start_flight_status(conv: Conversation):
    conv.goto_flow("flight_status")
