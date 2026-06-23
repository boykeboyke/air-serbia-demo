from _gen import *  # <AUTO GENERATED>


@func_description('Switch the conversation language to match the caller. Call this the INSTANT you detect the caller speaking a different language than you are currently using, BEFORE you reply. Pass "en" for English or "sr" for Serbian. This is a real runtime switch — a prompt rule alone does not change the voice/ASR language.')
@func_parameter('language', 'Target language: "en" (English) or "sr" (Serbian).')
def set_caller_language(conv: Conversation, language: str):
    code = (language or "").strip().lower()
    if code in ("en", "en-us", "en-gb", "english", "engleski"):
        conv.set_language("en-US")
        conv.state.active_language = "en-US"
        conv.state.goodbye_line = "Thank you for calling Air Serbia. Have a great day!"
        return "Language switched to English. Continue the conversation in English from now on."
    # default to Serbian
    conv.set_language("sr-RS")
    conv.state.active_language = "sr-RS"
    conv.state.goodbye_line = "Hvala vam na pozivu. Prijatan dan!"
    return "Jezik je prebačen na srpski. Nastavi razgovor na srpskom od sada."
