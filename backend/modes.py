"""Voice modes (Part 58). \"research mode on\", \"quiet mode\", \"focus mode\", \"normal mode\". The page keeps the mode and sends it with every chat message.
research = every question is searched on the web and answered with sources. quiet = Jarvis does not speak and keeps replies to one short sentence.
focus = short replies, no small talk. normal = as usual. Switching is only a setting: it never does anything on the phone."""
import re

MODES = ("normal", "research", "quiet", "focus")
SAY = {
    "normal": ("Normal mode, sir.", "नॉर्मल मोड चालू, सर।"),
    "research": ("Research mode is on, sir. I will search the web for every question and name my sources.", "रिसर्च मोड चालू, सर। हर सवाल इंटरनेट पर खोजूँगा और स्रोत बताऊँगा।"),
    "quiet": ("Quiet mode is on, sir. I will not speak and I will keep replies short.", "क्वाइट मोड चालू, सर। मैं बोलूँगा नहीं, जवाब छोटे रहेंगे।"),
    "focus": ("Focus mode is on, sir. Short answers, no small talk.", "फोकस मोड चालू, सर। छोटे जवाब, फालतू बात नहीं।"),
}
EXTRA = {
    "quiet": "\n\n[Mode: QUIET. Reply in ONE short sentence. No suggestions and no small talk.]",
    "focus": "\n\n[Mode: FOCUS. Reply in at most two short sentences. No small talk, no jokes, no extra suggestions.]",
}
WORD = {"research": "research|रिसर्च|khoj", "quiet": "quiet|क्वाइट|shaant|chup", "focus": "focus|फोकस", "normal": "normal|नॉर्मल|samanya"}
PAT = re.compile(r"^\s*(?:jarvis[\s,]+|जार्विस[\s,]+)?(?:switch to\s+|turn on\s+)?(%s)\s+(?:mode|मोड)(?:\s+(on|off|karo|chalu|band|चालू|बंद))?\s*[.!]?\s*$" % "|".join(WORD.values()), re.I)


def handle(msg, hindi):
    """(reply, mode) or None."""
    m = PAT.match(msg or "")
    if not m:
        return None
    w, how = m.group(1).lower(), (m.group(2) or "").lower()
    name = next(k for k, v in WORD.items() if re.fullmatch(v, w, re.I))
    if how in ("off", "band", "बंद"):
        name = "normal"
    return SAY[name][1 if hindi else 0], name


def extra(mode):
    return EXTRA.get(mode, "")
