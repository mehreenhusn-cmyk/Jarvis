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


def timed(msg, hindi):
    """(reply, {"name", "min"}) or None. `focus` needs minutes (plain `focus mode` is the old Part 58 setting)."""
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
