from _gen import *  # <AUTO GENERATED>


@func_description('Start the Etihad Guest loyalty check flow')
def start_loyalty_check(conv: Conversation):
    conv.goto_flow("loyalty_check")
