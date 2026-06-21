from _gen import *  # <AUTO GENERATED>


@func_description('Start the check-in flow')
def start_check_in(conv: Conversation):
    conv.goto_flow("check_in")
