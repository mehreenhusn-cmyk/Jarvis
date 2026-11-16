"""Part 118: Assist mode, guest session. Words and tap only. While it is on, NOTHING is saved (no memory, people, notes, lists, habits,
expenses, reminders, chat history). The guest chat lives in RAM only and is erased on End & erase, on a server restart, or after 30 minutes of quiet.
Aadhaar-like, card and phone numbers are masked BEFORE the text goes to the AI. The AI provider still receives the (masked) text."""
import re, time

IDLE = 1800  # seconds of quiet before the session erases itself
ACTIVE = {}  # device -> {"t": last time, "h": [turns]}  (RAM only, never written to disk)
START = re.compile(r"^\s*(?:guest\s+session\s+(?:shuru|start|on|chalu)|start\s+guest(?:\s+session)?|guest\s+mode(?:\s+(?:on|start|shuru))?|assist\s+mode(?:\s+(?:on|start|shuru))?)\s*[.!]?\s*$", re.I)
END = re.compile(r"^\s*(?:end\s*(?:&|and)\s*erase|end\s+guest(?:\s+session)?|guest\s+session\s+(?:end|khatam|band|off)|guest\s+(?:band|khatam)|(?:assist|guest)\s+mode\s+(?:off|end|band))\s*[.!]?\s*$", re.I)
CARD = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
AADHAAR = re.compile(r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)")
PHONE = re.compile(r"(?<!\d)(?:\+?91[ -]?)?[6-9]\d{4}[ -]?\d{5}(?!\d)")
RULE = ("\n\nGUEST SESSION: you are helping another person, a guest of the owner. Use nothing about the owner. Nothing is saved, so never offer notes, reminders or memory. "
        "Help only with words: translate, explain simply, make a plan, answer questions. For a medicine or a form, explain only what is written and say: doctor ya pharmacist se confirm karo. "
        "If you are not sure, say so. Never ask for a password, OTP, PIN or card number. Reply in the language the guest uses, in short simple sentences.")
TXT = {
    "start": ("Guest session is on. Nothing is saved: no memory, notes, lists or chat history. The words still go to the AI provider, so do not share secrets. Say \"end and erase\" when done.",
              "गेस्ट सेशन चालू है। कुछ भी सेव नहीं होगा: न मेमोरी, न नोट्स, न लिस्ट, न चैट। शब्द फिर भी AI कंपनी के पास जाते हैं, इसलिए राज़ मत बताइए। खत्म करने के लिए \"end and erase\" बोलिए।"),
    "end": ("Guest session ended. The guest chat is erased.", "गेस्ट सेशन खत्म। गेस्ट की चैट मिटा दी गई।"),
    "none": ("No guest session is on.", "गेस्ट सेशन चालू नहीं है।"),
}


def mask(t):
    """Card (13 to 19 digits), then Aadhaar-like (12 digits), then phone (10 digits) are replaced before the AI sees the text."""
    t = CARD.sub("[card hidden]", t)
    t = AADHAAR.sub("[id number hidden]", t)
    return PHONE.sub("[phone hidden]", t)


def on(dev):
    g = ACTIVE.get(dev)
    if g and time.time() - g["t"] > IDLE:
        ACTIVE.pop(dev, None)  # quiet for too long: erased by itself
        return False
    return g is not None


def command(dev, msg, hindi):
    """(reply, guest on?) for start and end words, else None."""
    i = 1 if hindi else 0
    if START.match(msg):
        ACTIVE[dev] = {"t": time.time(), "h": []}
        return TXT["start"][i], True
    if END.match(msg):
        was = ACTIVE.pop(dev, None) is not None
        return TXT["end" if was else "none"][i], False
    return None


def add(dev, role, text):
    """Keep one turn in RAM (last 12 turns only) and return the guest chat so far."""
    g = ACTIVE[dev]
    g["t"] = time.time()
    g["h"] = (g["h"] + [{"role": role, "content": text[:1500]}])[-12:]
    return list(g["h"])
