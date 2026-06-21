from _gen import *  # <AUTO GENERATED>


@func_description("Escalate the conversation when the caller needs help beyond the assistant's capabilities")
@func_parameter('reason', 'Brief description of why the call is being escalated')
def escalate_call(conv: Conversation, reason: str):
  conv.write_metric("ESCALATION_REASON", reason)
  return (
    "Let the caller know that you would normally connect them with a team member "
    "who can help, but this is a demo environment and live transfers are not "
    "currently configured. Ask if there's anything else you can assist with."
  )