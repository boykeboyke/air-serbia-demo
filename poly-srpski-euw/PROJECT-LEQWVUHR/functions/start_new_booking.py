from _gen import *  # <AUTO GENERATED>


@func_description('Start the new booking flow')
def start_new_booking(conv: Conversation):
    conv.goto_flow("new_booking")
