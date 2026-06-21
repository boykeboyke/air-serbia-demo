from _gen import *  # <AUTO GENERATED>


@func_description('Start the add baggage flow')
def start_add_baggage(conv: Conversation):
    conv.goto_flow("add_baggage")
