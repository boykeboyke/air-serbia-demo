from _gen import *  # <AUTO GENERATED>


@func_description('Start the complaint logging flow')
def start_log_complaint(conv: Conversation):
    conv.goto_flow("log_complaint")
