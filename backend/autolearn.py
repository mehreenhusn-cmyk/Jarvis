"""Part 155: Jarvis picks up facts and likes from what Hussain SAYS (his own words only, never the screen, the web or other people's text).
Every 8 normal chats the AI is asked for at most 3 lasting facts ("Hussain follows Bitcoin", "Hussain's cousin is Arman").
 - Small, harmless facts are saved by themselves. They are shown with `kya samjha`, and each can be deleted: `galat hai #N`.
 - Health, religion, politics, family trouble, addresses are only OFFERED (the page shows Yes / No, like Part 54). Nothing is saved without Yes.
 - Money, banks, loans, passwords, OTPs, PINs, cards, IDs and numbers are NEVER picked up, not even offered.
Off: `auto seekhna band karo` (or the old `seekhna band karo`). Erase all: `auto seekha bhool jao`."""
import hashlib, json, re, time

import learn, memory, screen

EVERY, MAXSAVED = 8, 60
BLOCK = re.compile(r"password|passcode|\botp\b|\bpin\b|cvv|\bcard\b|aadhaar|aadhar|\bpan\b|passport|licen[cs]e|\bbank\b|account|\bloan\b|karz|debt|salary|income|kamai|paise|paisa|rupee|rupay|rupaye|₹|\brs\b|\bupi\b|insurance|"
                   r"पासवर्ड|ओटीपी|पिन|आधार|बैंक|लोन|सैलरी|पैसे|पैसा|रुपये|कमाई", re.I)
ASK = re.compile(r"health|\bsick\b|\bill\b|disease|doctor|medic|dawai|bimar|cancer|diabet|religion|dharm|namaz|\bpuja\b|church|politic|\bparty\b|\bvote\b|girlfriend|boyfriend|\bwife\b|\bhusband\b|shaadi|divorce|address|ghar ka pata|"
                 r"स्वास्थ|बीमार|दवा|धर्म|राजनीत|पत्नी|पति|शादी", re.I)
SHOW = re.compile(r"^\s*(?:kya samjha|jo samjha dikhao|auto facts|what did you pick up|jarvis ne kya samjha)\s*\??\s*$", re.I)
DEL = re.compile(r"^\s*(?:galat hai|auto bhool jao|auto forget)\s*#?(\d+)\s*$", re.I)
WIPE = re.compile(r"^\s*(?:auto seekha bhool jao|forget auto facts)\s*$", re.I)
OFF = re.compile(r"^\s*(?:auto seekhna band(?: karo)?|stop auto learning)\s*$", re.I)
ON = re.compile(r"^\s*(?:auto seekhna chalu(?: karo)?|start auto learning)\s*$", re.I)
STOPW = {"hussain", "likes", "like", "interested", "usually", "follows", "that", "with", "from", "this", "have", "about", "wants", "loves"}


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS autofacts(id INTEGER PRIMARY KEY, device INT, text TEXT, status TEXT, sig TEXT, ts REAL)")


def _toks(t):
    return [w for w in re.findall(r"[\w\u0900-\u097F]+", str(t).lower()) if len(w) >= 3]


def _sig(t):
    return hashlib.sha1(" ".join(sorted(set(_toks(t)))).encode()).hexdigest()[:16]


def is_on(c, dev):
    return learn.is_on(c, dev) and not memory.flag(c, dev, "autolearn_off")


def saved(c, dev):
    return c.execute("SELECT id, text FROM autofacts WHERE device=? AND status='saved' ORDER BY id", (dev,)).fetchall()


def today(c, dev, now=None):
    """Facts saved in the last 24 hours (the text only)."""
    since = (time.time() if now is None else now) - 86400
    return [t for (t,) in c.execute("SELECT text FROM autofacts WHERE device=? AND status='saved' AND ts>? ORDER BY id", (dev, since))]


def forget(c, dev, i):
    """Delete one fact for good: the words go, a short fingerprint stays so the same thing is not picked up again. True if it existed."""
    k = c.execute("UPDATE autofacts SET status='no', text='' WHERE id=? AND device=? AND status!='no'", (i, dev)).rowcount
    c.commit()
    return bool(k)


def context(c, dev):
    r = saved(c, dev)[-25:]
    return ("\n\nFacts Jarvis picked up from what Hussain said (not checked; use only when useful; he can delete any of them):\n" + "\n".join("- " + t for _, t in r)) if r and is_on(c, dev) else ""


def _inputs(c, dev):
    out = []
    for (t,) in reversed(c.execute("SELECT content FROM messages WHERE device=? AND role='user' ORDER BY id DESC LIMIT 10", (dev,)).fetchall()):
        t = re.sub(r"\s+", " ", screen.redact(str(t))[0]).strip()
        if 6 <= len(t) <= 300 and not BLOCK.search(t):
            out.append(t)
    return out


def _known(c, dev, fact):
    """True if (nearly) the same thing is already saved, offered, taught or was deleted by Hussain."""
    s = set(_toks(fact))
    if not s:
        return True
    sg = _sig(fact)
    for t, sig in c.execute("SELECT text, sig FROM autofacts WHERE device=?", (dev,)):
        if sig == sg:
            return True
        o = set(_toks(t))
        if o and len(s & o) / len(s | o) >= 0.7:
            return True
    for _, t in memory.rows(c, dev):
        o = set(_toks(t))
        if o and len(s & o) / len(s | o) >= 0.7:
            return True
    return False


def _parse(reply):
    m = re.search(r"\[.*\]", str(reply or ""), re.S)
    try:
        arr = json.loads(m.group(0)) if m else []
    except ValueError:
        return []
    return [x for x in arr if isinstance(x, dict)][:3]


def take(c, dev, reply, lines):
    """Sort what the AI said: save the small and safe ones, queue the sensitive ones for a Yes. Returns (saved, queued)."""
    joined = " ".join(lines).lower()
    n_saved = n_ask = 0
    have = len(saved(c, dev))
    for x in _parse(reply):
        f = re.sub(r"\s+", " ", str(x.get("fact") or "")).strip()[:120]
        if len(f) < 8 or BLOCK.search(f) or re.search(r"\d{5,}", f.replace(" ", "")) or memory.SECRET.search(f):
            continue
        if not any(w in joined for w in _toks(f) if len(w) >= 4 and w not in STOPW):  # it must rest on his own words, not on a guess
            continue
        if _known(c, dev, f):
            continue
        sens = bool(ASK.search(f)) or x.get("sens") is True
        if not sens and have + n_saved >= MAXSAVED:
            continue
        c.execute("INSERT INTO autofacts(device, text, status, sig, ts) VALUES(?,?,?,?,strftime('%s','now'))", (dev, f, "ask" if sens else "saved", _sig(f)))
        n_ask += sens
        n_saved += not sens
    c.commit()
    return n_saved, n_ask


def note(c, dev, ask):
    """Called after a normal AI chat (in the background). Every 8th time it asks the AI. Never raises."""
    try:
        if not is_on(c, dev):
            return False
        n = memory.flag(c, dev, "autolearn_n") + 1
        if n < EVERY:
            memory.setflag(c, dev, "autolearn_n", n)
            return False
        memory.setflag(c, dev, "autolearn_n", 0)
        lines = _inputs(c, dev)
        if len(lines) < 3:
            return False
        q = ("Below are things Hussain said to his phone assistant. Pick up to 3 LASTING facts or likes about HIM that he stated himself "
             "(an interest, a preference, a person in his life, a routine, a plan). Skip questions, guesses, news, and anything about other people's business. "
             "Never money, banks, passwords, numbers, IDs or addresses. Use his own words and names. "
             'Answer ONLY with JSON, like [{"fact": "Hussain follows Bitcoin", "sens": false}] (sens = true for health, religion, politics, family matters), or [] if there is nothing.\n\nLines:\n'
             + "\n".join("- " + t for t in lines))
        reply, via = ask([{"role": "user", "content": q}], "english", "")
        if via == "mock":
            return False
        take(c, dev, reply, lines)
        return True
    except Exception:
        return False


def pending(c, dev):
    """ONE sensitive fact to ask about (the page shows Yes / No; Yes saves it as a normal memory). It is asked only once."""
    if not is_on(c, dev):
        return None
    r = c.execute("SELECT id, text FROM autofacts WHERE device=? AND status='ask' ORDER BY id LIMIT 1", (dev,)).fetchone()
    if not r:
        return None
    c.execute("UPDATE autofacts SET status='asked' WHERE id=?", (r[0],))
    c.commit()
    return r[1]


def handle(c, dev, msg, hindi):
    if len(msg) > 60:
        return None
    say = lambda hi, en: hi if hindi else en
    if OFF.match(msg):
        memory.setflag(c, dev, "autolearn_off", 1)
        return say("ठीक है सर, अब आपकी बातों से तथ्य नहीं उठाऊँगा। जो उठाए थे वो रहेंगे, मिटाने के लिए \"auto seekha bhool jao\" बोलिए।", "Okay sir, I will not pick up facts from your talk any more. Those already picked up stay. Say \"auto seekha bhool jao\" to erase them.")
    if ON.match(msg):
        memory.setflag(c, dev, "autolearn_off", 0)
        return say("ठीक है सर, फिर से आपकी बातों से छोटे तथ्य उठाऊँगा। पैसा, बैंक, पासवर्ड और नंबर कभी नहीं।", "Okay sir, I pick up small facts from your talk again. Never money, banks, passwords or numbers.")
    if WIPE.match(msg):
        c.execute("DELETE FROM autofacts WHERE device=?", (dev,))
        c.commit()
        return say("सर, उठाए हुए सब तथ्य मिटा दिए।", "Sir, every fact I picked up is erased.")
    m = DEL.match(msg)
    if m:
        k = forget(c, dev, int(m.group(1)))
        return say("ठीक है सर, भूल गया और दोबारा नहीं उठाऊँगा।", "Okay sir, forgotten, and I will not pick it up again.") if k else say("सर, इस नंबर का कोई तथ्य नहीं मिला।", "Sir, I found no fact with that number.")
    if SHOW.match(msg):
        r = saved(c, dev)
        if not r:
            return say("सर, अभी मैंने आपकी बातों से कुछ नहीं उठाया।", "Sir, I have not picked up anything from your talk yet.") + ("" if is_on(c, dev) else "\n(Picking up is OFF.)")
        return say("सर, मैंने आपकी बातों से ये उठाया है (गलत हो तो \"galat hai #N\"):", "Sir, this is what I picked up from your talk (wrong? say \"galat hai #N\"):") + "\n" + "\n".join(f"#{i} {t}" for i, t in r) + ("" if is_on(c, dev) else "\n(Picking up is OFF.)")
    return None


def wipe(c, dev):
    c.execute("DELETE FROM autofacts WHERE device=?", (dev,))
    c.commit()
