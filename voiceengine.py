"""Voice Personality Engine (Part 51, fixed in Part 71). Do awaazen: TONY (normal baat-cheet) aur JARVIS (jaankari, kaam, reminder, briefing, alert, aur jab intent saaf na ho).
Awaaz intent se chuni jati hai, keywords se nahi. Dono profile pehli install se maujood hain, auto routing ON. Settings voice.json mein (restart ke baad bhi rehti hain).
SACH: Edge mein Hindi ka ek hi mard awaaz hai (Madhur), isliye Edge par Tony aur JARVIS Hindi mein SIRF pitch aur speed se alag hain (English mein alag awaazen). Asli do Hindi awaazen Sarvam se milti hain:
har profile ka apna Sarvam speaker hota hai (Tony: aditya, JARVIS: rahul, badal sakte ho). pick() batata hai ki dono sach mein alag awaaz hain ya nahi ("distinct")."""
import json, os, re

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice.json")
INTENTS = ("CONVERSATION", "INFORMATION", "TASK_CONFIRMATION", "REMINDER", "BRIEFING", "ALERT")
POLICY = {"CONVERSATION": "tony", "INFORMATION": "jarvis", "TASK_CONFIRMATION": "jarvis", "REMINDER": "jarvis", "BRIEFING": "jarvis", "ALERT": "jarvis"}
PROFILES = {
    "tony": {"hindi": "hi-IN-MadhurNeural", "english": "en-IN-PrabhatNeural", "pitch": 0, "rate": 8},
    "jarvis": {"hindi": "hi-IN-MadhurNeural", "english": "en-GB-RyanNeural", "pitch": -14, "rate": -10},
}
SPEAKERS = ("shubh",)  # Part 124: one voice only (Hussain, 17 Nov). Sarvam Shubh is the default for Hindi and English; Edge stays as the hidden backup when Sarvam fails
SPEAKER_DEFAULT = {"tony": "shubh", "jarvis": "shubh"}  # both personalities use Shubh; they differ only in speed
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
    s = {"auto": d.get("auto") is not False, "manual": d.get("manual") if d.get("manual") in PROFILES else "jarvis",
         "provider": "edge" if d.get("provider") == "edge" else "sarvam"}  # Part 124: Sarvam unless you chose Edge. No key or Sarvam fails: Edge speaks (app.py)
    sp = d.get("speakers") if isinstance(d.get("speakers"), dict) else {}
    s["speakers"] = {p: sp.get(p) if sp.get(p) in SPEAKERS else SPEAKER_DEFAULT[p] for p in PROFILES}
    if d.get("speaker") in SPEAKERS and "jarvis" not in sp:  # a speaker chosen before Part 71 belonged to JARVIS: keep that choice
        s["speakers"]["jarvis"] = d["speaker"]
    s["speaker"] = s["speakers"]["jarvis"]  # old name, kept so an older page still works
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
    if data.get("provider") in ("edge", "sarvam"):
        s["provider"] = data["provider"]
    if data.get("speaker") in SPEAKERS:  # old page: one speaker means JARVIS
        s["speakers"]["jarvis"] = data["speaker"]
    if isinstance(data.get("speakers"), dict):
        for p in PROFILES:
            if data["speakers"].get(p) in SPEAKERS:
                s["speakers"][p] = data["speakers"][p]
    s["speaker"] = s["speakers"]["jarvis"]
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
    if h:  # a hint we do not know: unclear, so JARVIS (calm and safe)
        return "UNCLEAR"
    t = str(text or "").strip()
    if t.startswith("⏰"):
        return "REMINDER"
    if ALERT.search(t):
        return "ALERT"
    if len(t) > 180 or "\n" in t or re.search(r"\d|https?://|sources?:|स्रोत", t, re.I):
        return "INFORMATION"
    return "CONVERSATION"


def pick(text, intent="", profile="", lang="hindi"):
    """Kaun si awaaz bolegi. profile dene par (Test button) wahi. Auto ON ho to intent se. Auto OFF ho to manual wali."""
    s = load()
    it = classify(text, intent)
    name = profile if profile in PROFILES else (POLICY.get(it, "jarvis") if s["auto"] else s["manual"])  # an intent we do not know falls to JARVIS
    k = "english" if lang == "english" else "hindi"
    distinct = (s["speakers"]["tony"] != s["speakers"]["jarvis"]) if s["provider"] == "sarvam" else (PROFILES["tony"][k] != PROFILES["jarvis"][k])
    return {"profile": name, "provider": s["provider"], "speaker": s["speakers"][name], "intent": it, "voice": PROFILES[name][k], "pitch": s[name]["pitch"], "rate": s[name]["rate"], "distinct": distinct}
