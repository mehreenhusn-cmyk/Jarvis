"""Part 146: Unknown sentences. A short, command-looking sentence that the phone grammar could not understand is kept on the phone (the sentence only).
If your NEXT message (within 5 minutes) is a clear command that works, Jarvis pairs the two. One tap on Teach in Settings > Your Data makes the
unclear sentence mean that command from then on. Jarvis never guesses, never asks the AI, and a taught sentence still goes through every normal check
(Phone control, Stop, confirm for risky steps). Calls, messages, clicks, typing and alarms are never taught.
Words: `unknown dikhao` (list), `unknown teach 2`, `unknown hatao 2`, `unknown band karo` (off: no saving, no using), `unknown chalu karo` (on), `unknown saaf karo` (erase all)."""
import re, time
import actions, memory

SHOW = re.compile(r"^\s*(?:unknown (?:dikhao|show|list|sentences)|samajh nahi aaya dikhao|na samjhe dikhao)\s*$", re.I)
OFF = re.compile(r"^\s*(?:unknown (?:band(?: karo)?|off)|समझ नहीं आया बंद)\s*$", re.I)
ON = re.compile(r"^\s*(?:unknown (?:chalu(?: karo)?|on))\s*$", re.I)
WIPE = re.compile(r"^\s*unknown (?:saaf karo|saaf|clear|erase)\s*$", re.I)
TEACH = re.compile(r"^\s*unknown (?:teach|sikhao)\s*#?(\d{1,6})\s*$", re.I)
DROP = re.compile(r"^\s*unknown (?:hatao|delete|remove)\s*#?(\d{1,6})\s*$", re.I)
PHONE = re.compile(r"torch|flash ?light|wi-?fi|bluetooth|volume|brightness|alarm|timer|\bhome\b|\bback\b|scroll|\bapp\b|chrome|youtube|whatsapp|टॉर्च|वाईफाई|ब्लूटूथ|वॉल्यूम|अलार्म|टाइमर|होम|स्क्रीन|ऐप|स्क्रॉल", re.I)
TEACH_OK = {"open_app", "back", "home", "scroll", "settings", "torch", "volume", "media", "search", "timer", "current_app", "lock"}  # never: call, click, type, tap, look, confirm, task, alarm, swipe
# Part 165: "galat samjha". You say `nahi, woh nahi` after a sentence Jarvis got wrong, then the right command. Jarvis offers: remember this meaning? Yes = taught (same as `unknown teach N`).
WRONG = re.compile(r"^\s*(?:(?:nahi|nahin|no|nope)[\s,]+)?(?:(?:woh|wo|vo|yeh|ye|that|this)(?:\s+wala)?\s+(?:nahi|nahin|galat|wrong)|not that(?: one)?|wrong one|galat (?:samjha|samjhe|samjhi)|you (?:got|understood) (?:it|that) wrong|that'?s wrong|गलत समझा|वो नहीं|यह नहीं)\s*[.!]?\s*$", re.I)
PREV, ARM = {}, {}  # device -> (last sentence, time) / (the sentence you said was misread, time). RAM only
LAST = {}  # device -> (sentence, time). RAM only: the pairing window is 5 minutes
WINDOW, KEEP_N, EXPIRE = 300, 40, 30


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS unknown(id INTEGER PRIMARY KEY, device INT, said TEXT, meaning TEXT DEFAULT '', taught INT DEFAULT 0, n INT DEFAULT 1, day TEXT DEFAULT '', UNIQUE(device, said))")
    c.execute("CREATE TABLE IF NOT EXISTS unkset(device INT PRIMARY KEY, on_ INT DEFAULT 1)")


def is_on(c, dev):
    r = c.execute("SELECT on_ FROM unkset WHERE device=?", (dev,)).fetchone()
    return r is None or r[0] == 1


def norm(s):
    return " ".join(re.sub(r"[^\w\u0900-\u097F ]", " ", (s or "").lower()).split())


def _safe(s):
    """No password, OTP, PIN, card, long number, or risky step; short enough to be a command."""
    d = re.sub(r"[\s-]", "", s)
    return bool(s) and len(s) <= 80 and not memory.SECRET.search(s) and not actions.secret_text(s) and not actions.blocked(s) \
        and not re.search(r"\d{4,}", d) and actions.risk_of(s) is None


def looks_like_command(msg):
    w = set(actions._words(msg))
    return actions._command_like(msg) and bool((actions.NEAR & w) or PHONE.search(msg))


def _day():
    return time.strftime("%Y-%m-%d")


def _prev(dev, msg):
    s = norm(msg)
    if s and not WRONG.match(msg) and _safe(s):
        PREV[dev] = (s, time.time())


def note(c, dev, msg, in_app):
    """Keep one sentence the grammar missed. Only in the Jarvis app, only a command-looking one, never a secret, never when off."""
    if not in_app or not is_on(c, dev) or not isinstance(msg, str):
        return
    s = norm(msg)
    if not s or not looks_like_command(msg) or not _safe(s):
        return
    _prev(dev, msg)  # Part 165
    r = c.execute("SELECT taught FROM unknown WHERE device=? AND said=?", (dev, s)).fetchone()
    if r is None:
        c.execute("INSERT INTO unknown(device, said, day) VALUES(?,?,?)", (dev, s, _day()))
    else:
        c.execute("UPDATE unknown SET n=n+1, day=? WHERE device=? AND said=?", (_day(), dev, s))
    old = time.strftime("%Y-%m-%d", time.localtime(time.time() - EXPIRE * 86400))
    c.execute("DELETE FROM unknown WHERE device=? AND taught=0 AND day<?", (dev, old))
    c.execute("DELETE FROM unknown WHERE device=? AND taught=0 AND id NOT IN (SELECT id FROM unknown WHERE device=? AND taught=0 ORDER BY id DESC LIMIT ?)", (dev, dev, KEEP_N))
    c.commit()
    if r is None or r[0] == 0:
        LAST[dev] = (s, time.time())


def pair(c, dev, msg, action):
    """The message after an unclear one worked as a plain command: remember it as the possible meaning. Nothing is taught yet."""
    arm = ARM.pop(dev, None)
    last = LAST.pop(dev, None)
    m = norm(msg)
    okact = is_on(c, dev) and isinstance(action, dict) and action.get("type") in TEACH_OK and not action.get("raw") and bool(m) and _safe(m)
    if arm and time.time() - arm[1] <= WINDOW and okact and arm[0] != m and _safe(arm[0]):  # Part 165: you said `nahi, woh nahi`, then this right command: offer to remember
        r = c.execute("SELECT id FROM unknown WHERE device=? AND said=?", (dev, arm[0])).fetchone()
        if r is None:
            c.execute("INSERT INTO unknown(device, said, meaning, day) VALUES(?,?,?,?)", (dev, arm[0], m, _day()))
            r = c.execute("SELECT id FROM unknown WHERE device=? AND said=?", (dev, arm[0])).fetchone()
        else:
            c.execute("UPDATE unknown SET meaning=?, taught=0, day=? WHERE id=? AND device=?", (m, _day(), r[0], dev))
        c.commit()
        PREV.pop(dev, None)
        return {"id": r[0], "said": arm[0], "meaning": m}
    _prev(dev, msg)
    if not last or time.time() - last[1] > WINDOW or not okact or m == last[0]:
        return
    c.execute("UPDATE unknown SET meaning=? WHERE device=? AND said=? AND taught=0", (m, dev, last[0]))
    c.commit()
    return None


def expand(c, dev, msg):
    """A taught sentence (exact match) becomes its command text. Everything after that is the normal path with all its checks."""
    if not isinstance(msg, str) or len(msg) > 80 or not is_on(c, dev):
        return msg
    r = c.execute("SELECT meaning FROM unknown WHERE device=? AND said=? AND taught=1 AND meaning<>''", (dev, norm(msg))).fetchone()
    return r[0] if r else msg


def rows(c, dev):
    return [{"id": i, "said": s, "meaning": m, "taught": t == 1, "n": n}
            for i, s, m, t, n in c.execute("SELECT id, said, meaning, taught, n FROM unknown WHERE device=? ORDER BY taught DESC, id DESC LIMIT 30", (dev,))]


def act(c, dev, i, what):
    if what == "teach":
        c.execute("UPDATE unknown SET taught=1 WHERE id=? AND device=? AND meaning<>''", (i, dev))
    elif what == "forget":
        c.execute("UPDATE unknown SET taught=0 WHERE id=? AND device=?", (i, dev))
    elif what == "delete":
        c.execute("DELETE FROM unknown WHERE id=? AND device=?", (i, dev))
    c.commit()


def handle(c, dev, msg, hindi):
    if len(msg) > 40:
        return None
    say = lambda hi, en: hi if hindi else en
    if WRONG.match(msg):  # Part 165
        p = PREV.pop(dev, None)
        if not is_on(c, dev) or not p or time.time() - p[1] > WINDOW:
            return say("ठीक है सर, माफ़ कीजिए। बताइए आपको क्या चाहिए।", "Okay sir, sorry. Tell me what you wanted.")
        ARM[dev] = (p[0], time.time())
        return say("माफ़ कीजिए सर। अब सही कमांड बोलिए, जैसे \"open youtube\"। मैं उसे कर दूँगा और पूछूँगा कि \"" + p[0] + "\" का यही मतलब याद रखूँ या नहीं।",
                   "Sorry, sir. Now say the right command, like \"open youtube\". I will do it and then ask if I should remember that \"" + p[0] + "\" means it.")
    if OFF.match(msg):
        c.execute("INSERT OR REPLACE INTO unkset(device,on_) VALUES(?,0)", (dev,))
        c.commit()
        return say("ठीक है सर, अब नए वाक्य नहीं सहेजूँगा और सिखाए हुए वाक्य भी नहीं चलेंगे। सब वैसे ही रखा है, मिटाने के लिए \"unknown saaf karo\" बोलिए।", "Okay sir, I stop saving sentences and taught sentences pause too. Everything stays; say \"unknown saaf karo\" to erase it.")
    if ON.match(msg):
        c.execute("INSERT OR REPLACE INTO unkset(device,on_) VALUES(?,1)", (dev,))
        c.commit()
        return say("ठीक है सर, फिर से चालू। सिर्फ़ वाक्य सहेजता हूँ, कुछ चलता नहीं।", "Okay sir, it is ON again. I keep only the sentence; nothing runs.")
    if WIPE.match(msg):
        c.execute("DELETE FROM unknown WHERE device=?", (dev,))
        c.commit()
        LAST.pop(dev, None)
        return say("सर, न समझे हुए और सिखाए हुए सारे वाक्य मिटा दिए।", "Sir, all unknown and taught sentences are erased.")
    g = TEACH.match(msg) or DROP.match(msg)
    if g:
        i, what = int(g.group(1)), "teach" if TEACH.match(msg) else "delete"
        r = c.execute("SELECT meaning FROM unknown WHERE id=? AND device=?", (i, dev)).fetchone()
        if not r:
            return say("सर, इस नंबर का कोई वाक्य नहीं मिला। \"unknown dikhao\" बोलिए।", "Sir, no sentence has that number. Say \"unknown dikhao\".")
        if what == "teach" and not r[0]:
            return say("सर, अभी इसका मतलब नहीं पता। इसके बाद साफ़ कमांड बोलिए, जैसे \"open youtube\", फिर यहाँ सिखाइए।", "Sir, I do not know what it means yet. Say the clear command right after it, like \"open youtube\", then teach it here.")
        act(c, dev, i, what)
        return say("ठीक है सर, सिखा दिया।" if what == "teach" else "ठीक है सर, हटा दिया।", "Okay sir, taught." if what == "teach" else "Okay sir, removed.")
    if SHOW.match(msg):
        r = rows(c, dev)
        if not r:
            return say("सर, अभी कोई न समझा हुआ वाक्य नहीं है।", "Sir, no unknown sentence yet.") + ("" if is_on(c, dev) else "\n(Unknown sentences is OFF.)")
        lines = [f"{x['id']}. \"{x['said']}\"" + (f" = \"{x['meaning']}\"" if x["meaning"] else "") + (" (taught)" if x["taught"] else "") for x in r]
        return say("सर, ये वाक्य मुझे समझ नहीं आए (सिर्फ़ वाक्य):", "Sir, these sentences I did not understand (the sentence only):") + "\n" + "\n".join(lines) + "\n" + say("सिखाने के लिए: unknown teach N", "To teach: unknown teach N") + ("" if is_on(c, dev) else "\n(Unknown sentences is OFF.)")
    return None
