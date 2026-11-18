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


# ---- Part 101: Body Double. `body double 45 minute`: every 15 minutes a TEXT check-in `abhi bhi kaam par?` (Haan / Nahi) and a count at the end.
# It does not watch the screen and does not block any app. Lives in RAM only (a server restart ends it). The page asks /due every 10 seconds.
import remind

BD_START = re.compile(r"^\s*body\s+double\s+(\d{2,3})\s*(?:minute|minutes|min|mins|मिनट)\s*$", re.I)
BD_STOP = re.compile(r"^\s*body\s+double\s+(?:stop|khatam|band|off)\s*$", re.I)
BD_STEP = 900
BD = {}  # device -> {"start", "end", "next", "asked", "yes"}


def _bd_text(s, now_asked=False):
    mins = (s["end"] - s["start"]) // 60
    return (f"Body double done: {mins} minutes, {s['yes']} of {s['asked']} check-ins on task.", f"बॉडी डबल पूरा: {mins} मिनट, {s['asked']} में से {s['yes']} चेक-इन में काम पर।")


def bd_command(dev, msg, hindi, now):
    try:
        n = remind.tm(now)
    except (ValueError, TypeError):
        return None
    if BD_STOP.match(msg):
        s = BD.pop(dev, None)
        if not s:
            return "सर, बॉडी डबल चालू नहीं है।" if hindi else "Sir, no body double is on."
        s["end"] = n
        return _bd_text(s)[1 if hindi else 0]
    g = BD_START.match(msg)
    if not g:
        return None
    mins = int(g.group(1))
    if not 15 <= mins <= 180:
        return "सर, 15 से 180 मिनट रखिए।" if hindi else "Sir, choose 15 to 180 minutes."
    BD[dev] = {"start": n, "end": n + mins * 60, "next": n + BD_STEP, "asked": 0, "yes": 0}
    return (f"ठीक है, {mins} मिनट। हर 15 मिनट पर लिखकर पूछूँगा: abhi bhi kaam par? मैं स्क्रीन नहीं देखता और कोई ऐप नहीं रोकता। रोकने के लिए: body double stop" if hindi else
            f"Okay, {mins} minutes. Every 15 minutes I will ask in text: abhi bhi kaam par? I do not watch your screen and I block no app. To stop: body double stop")


def bd_due(dev, now):
    """For the page's /due poll: {"kind": "ask"} once per 15 minutes, {"kind": "end", "en", "hi"} once at the end. None otherwise."""
    s = BD.get(dev)
    if not s:
        return None
    try:
        n = remind.tm(now)
    except (ValueError, TypeError):
        return None
    if n >= s["end"]:
        BD.pop(dev, None)
        en, hi = _bd_text(s)
        return {"kind": "end", "en": en, "hi": hi}
    if n >= s["next"]:
        s["next"] += BD_STEP
        s["asked"] += 1
        return {"kind": "ask"}
    return None


def bd_answer(dev, yes):
    if dev in BD and yes:
        BD[dev]["yes"] += 1


# ---- Part 100: Timed modes. `meeting mode 45 minute`, `namaz mode 20 minute`, `sleep mode`, `focus 45 minute`. Same as Quiet (no voice, one short sentence) for that time;
# reminders come as text only; it ends by itself (the page keeps the clock). `normal mode` ends it sooner.
TIMED = re.compile(r"^\s*(meeting|namaz|sleep|focus)(?:\s+(?:mode|मोड))?(?:\s+(\d{1,3})\s*(?:minute|minutes|min|mins|मिनट))?\s*$", re.I)
DEFAULT = {"meeting": 45, "namaz": 20, "sleep": 480, "focus": None}


# ---- Part 137: Quiet mode with exceptions. `quiet mode 2 hours except namaz, Ammi`: quiet for that time (no voice, short replies), but a SPOKEN alert (a reminder, for example)
# whose text has one of those words is still read aloud. Exceptions only allow speech: they never run anything on the phone. Up to 5 words, one word each.
QX = re.compile(r"^\s*(?:jarvis[\s,]+)?(?:quiet|shaant|chup|क्वाइट)(?:\s+(?:mode|मोड))?\s+(\d{1,3})\s*(minute|minutes|min|mins|मिनट|hour|hours|hr|hrs|ghanta|ghante|घंटा|घंटे)\s*(?:(?:except|siwaye|sivay|chhodke|ke\s+alawa|ko\s+chhodkar)\s+(.+?))?\s*[.!]?\s*$", re.I)
QX_NOTIME = re.compile(r"^\s*(?:quiet|shaant|chup)(?:\s+mode)?\s+(?:except|siwaye|sivay)\s+\S", re.I)
ALIAS = {"namaz": ("namaz", "नमाज़", "नमाज", "azan", "azaan", "अज़ान", "अजान"), "ammi": ("ammi", "अम्मी"), "abbu": ("abbu", "अब्बू"), "mummy": ("mummy", "मम्मी"), "papa": ("papa", "पापा"),
         "doctor": ("doctor", "डॉक्टर"), "dawai": ("dawai", "दवाई", "दवा", "medicine"), "medicine": ("medicine", "dawai", "दवाई", "दवा")}
XWORD = re.compile(r"^[\w\u0900-\u097F]{2,20}$")


def quiet_timed(msg, hindi):
    """(reply, {"name": "quiet", "min", "ex": words to match, "exn": words as said}) or None."""
    say = lambda hi, en: hi if hindi else en
    if QX_NOTIME.match(msg or ""):
        return say("सर, कितनी देर? ऐसे बोलिए: quiet mode 2 hours except namaz, Ammi", "Sir, for how long? Say it like this: quiet mode 2 hours except namaz, Ammi"), None
    g = QX.match(msg or "")
    if not g:
        return None
    n = int(g.group(1)) * (60 if g.group(2).lower() in ("hour", "hours", "hr", "hrs", "ghanta", "ghante", "घंटा", "घंटे") else 1)
    if not 5 <= n <= 600:
        return say("सर, 5 मिनट से 10 घंटे के बीच रखिए।", "Sir, choose between 5 minutes and 10 hours."), None
    words = [w.strip().lower() for w in re.split(r"\s*(?:,|&|\band\b|\baur\b|और)\s*", g.group(3) or "") if w.strip()]
    if len(words) > 5 or not all(XWORD.match(w) for w in words):
        return say("सर, अपवाद में सिर्फ़ एक-एक शब्द रखिए, ज़्यादा से ज़्यादा 5। जैसे: namaz, Ammi", "Sir, give one word for each exception, at most 5. For example: namaz, Ammi"), None
    ex = sorted({a for w in words for a in ALIAS.get(w, (w,))})
    when = f"{n // 60} घंटे" if hindi and n % 60 == 0 else f"{n} मिनट" if hindi else (f"{n // 60} hour{'s' if n >= 120 else ''}" if n % 60 == 0 else f"{n} minutes")
    tail = (say(f" अपवाद: {', '.join(words)} (इनके बारे में अलर्ट बोलकर आएँगे)।", f" Exceptions: {', '.join(words)} (alerts about these are still spoken).")) if words else ""
    return say(f"क्वाइट मोड {when} के लिए। आवाज़ बंद, जवाब छोटे।{tail} जल्दी खत्म करने के लिए: normal mode", f"Quiet mode for {when}. No voice, short replies.{tail} To end sooner say: normal mode"), {"name": "quiet", "min": n, "ex": ex, "exn": words}


def timed(msg, hindi):
    """(reply, {"name", "min"}) or None. `focus` needs minutes (plain `focus mode` is the old Part 58 setting)."""
    q = quiet_timed(msg, hindi)  # Part 137
    if q:
        return q
    g = TIMED.match(msg or "")
    if not g:
        return None
    name = g.group(1).lower()
    mins = int(g.group(2)) if g.group(2) else DEFAULT[name]
    if not mins:
        return None
    if not 5 <= mins <= 600:
        return ("सर, 5 से 600 मिनट रखिए।" if hindi else "Sir, choose 5 to 600 minutes."), None
    n = name.title()
    return (f"{n} मोड {mins} मिनट के लिए। आवाज़ बंद, जवाब छोटे, रिमाइंडर सिर्फ़ लिखकर। अपने आप खत्म होगा; जल्दी खत्म करने के लिए: normal mode" if hindi else
            f"{n} mode for {mins} minutes. No voice, short replies, reminders as text. It ends by itself; to end sooner say: normal mode"), {"name": name, "min": mins}
