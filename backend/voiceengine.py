"""Voice Personality Engine (Part 51). Do awaazen: TONY (baat-cheet) aur JARVIS (jaankari, kaam, reminder, briefing, alert).
Awaaz intent se chuni jati hai, keywords se nahi. Na samjhe to JARVIS. Settings voice.json mein (restart ke baad bhi rehti hain).
Dono awaazen Edge se hain (free). Hindi mein ek hi mard awaaz hai (Madhur), isliye farq pitch aur speed ka hai. English mein alag awaazen."""
import json, os, re

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice.json")
INTENTS = ("CONVERSATION", "INFORMATION", "TASK_CONFIRMATION", "REMINDER", "BRIEFING", "ALERT")
POLICY = {"CONVERSATION": "tony", "INFORMATION": "jarvis", "TASK_CONFIRMATION": "jarvis", "REMINDER": "jarvis", "BRIEFING": "jarvis", "ALERT": "jarvis"}
PROFILES = {
    "tony": {"hindi": "hi-IN-MadhurNeural", "english": "en-IN-PrabhatNeural", "pitch": 0, "rate": 8},
    "jarvis": {"hindi": "hi-IN-MadhurNeural", "english": "en-GB-RyanNeural", "pitch": -14, "rate": -10},
}
ALERT = re.compile(r"\b(alert|warning|urgent|danger|emergency|low battery)\b|खतरा|khatra|सावधान", re.I)


def _n(v, lo, hi, d):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return d


def load():
    """Saved settings. File missing ya kharab ho to defaults."""
    try:
        d = json.load(open(FILE, encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    d = d if isinstance(d, dict) else {}
    s = {"auto": d.get("auto") is not False, "manual": d.get("manual") if d.get("manual") in PROFILES else "jarvis"}
    for p, base in PROFILES.items():
        o = d.get(p) if isinstance(d.get(p), dict) else {}
        s[p] = {"pitch": _n(o.get("pitch"), -50, 50, base["pitch"]), "rate": _n(o.get("rate"), -30, 30, base["rate"])}
    return s


def save(data):
    """Sirf jo diya wahi badalta hai; har number ki hadd check hoti hai."""
    s = load()
    if isinstance(data.get("auto"), bool):
        s["auto"] = data["auto"]
    if data.get("manual") in PROFILES:
        s["manual"] = data["manual"]
    for p in PROFILES:
        o = data.get(p)
        if isinstance(o, dict):
            s[p]["pitch"] = _n(o.get("pitch"), -50, 50, s[p]["pitch"])
            s[p]["rate"] = _n(o.get("rate"), -30, 30, s[p]["rate"])
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f)
    os.replace(tmp, FILE)
    return s


def classify(text, hint=""):
    """Page jab intent bhejta hai (reminder, briefing, task) wahi maante hain. Warna text se andaza."""
    h = str(hint or "").upper()
    if h in INTENTS:
        return h
    t = str(text or "").strip()
    if t.startswith("⏰"):
        return "REMINDER"
    if ALERT.search(t):
        return "ALERT"
    if len(t) > 180 or "\n" in t or re.search(r"\d", t):
        return "INFORMATION"
    return "CONVERSATION"


def pick(text, intent="", profile="", lang="hindi"):
    """Kaun si awaaz bolegi. profile dene par (Test button) wahi. Auto ON ho to intent se. Auto OFF ho to manual wali."""
    s = load()
    it = classify(text, intent)
    name = profile if profile in PROFILES else (POLICY.get(it, "jarvis") if s["auto"] else s["manual"])
    return {"profile": name, "intent": it, "voice": PROFILES[name]["english" if lang == "english" else "hindi"], "pitch": s[name]["pitch"], "rate": s[name]["rate"]}
