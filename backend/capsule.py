"""Part 97: Time Capsule (text). `6 mahine baad yeh sunana: ...`, `1 saal baad yeh sunana: ...`, `30 din baad ...`, `2 hafte baad ...`.
Sealed text stays hidden until the day. Then a card appears ONCE; Jarvis reads it only after your tap (`Open and read aloud`). Later: `open capsule 3`.
`my capsules` lists sealed ones (dates only) and opened ones. `capsule hatao 3` removes one. Saved only on your words, never sent to the AI."""
import re
import time
import remind
from notes import SECRET

SAVE = re.compile(r"^\s*(\d{1,3})\s*(din|days?|hafte?|weeks?|mahine?|months?|saal|years?)\s+baad\s+(?:yeh|ye|ise|isko)\s+(?:sunana|sunao|dikhana|dikhao)\s*[:\-]\s*(.{3,500})$", re.I | re.S)
LIST = re.compile(r"^\s*(?:my\s+(?:time\s+)?capsules?|meri\s+capsules?|time\s+capsules?|capsules?\s+dikhao)\s*$", re.I)
OPEN = re.compile(r"^\s*open\s+capsule\s*#?(\d+)\s*$", re.I)
DROP = re.compile(r"^\s*capsule\s+(?:hatao|delete|remove)\s*#?(\d+)\s*$", re.I)
UNIT = (("din", 1), ("day", 1), ("haft", 7), ("week", 7), ("mahin", 30), ("month", 30), ("saal", 365), ("year", 365))
MAX_SEALED = 20


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS capsules(id INTEGER PRIMARY KEY, device INT, text TEXT, due INT, made INT, shown INT DEFAULT 0, opened INT DEFAULT 0)")


def _d(t):
    return time.strftime("%d %b %Y", time.gmtime(t))


def handle(c, dev, msg, hindi, now):
    m = msg.strip()
    if len(m) > 600:
        return None
    say = lambda hi, en: hi if hindi else en
    g = SAVE.match(m)
    if g:
        try:
            n = remind.tm(now)
        except (ValueError, TypeError):
            return say("सर, फ़ोन का समय नहीं पढ़ पाया।", "Sir, I could not read the phone time.")
        days = int(g.group(1)) * next(v for k, v in UNIT if g.group(2).lower().startswith(k))
        if days < 1 or days > 3650:
            return say("सर, 1 दिन से 10 साल के बीच रखिए।", "Sir, choose between 1 day and 10 years.")
        if SECRET.search(g.group(3)):
            return say("सर, पासवर्ड, OTP, PIN या कार्ड नंबर मैं सेव नहीं करता।", "Sir, I do not save a password, OTP, PIN or card number.")
        if c.execute("SELECT count(*) FROM capsules WHERE device=? AND opened=0", (dev,)).fetchone()[0] >= MAX_SEALED:
            return say("सर, 20 कैप्सूल सील हैं।", "Sir, 20 capsules are already sealed.")
        due = n - n % 86400 + days * 86400 + 8 * 3600  # opens at 8 in the morning on that day
        cur = c.execute("INSERT INTO capsules(device, text, due, made) VALUES(?,?,?,?)", (dev, g.group(3).strip(), due, n))
        c.commit()
        return say(f"ठीक है, कैप्सूल #{cur.lastrowid} सील हो गया। {_d(due)} को खुलेगा। तब तक मैं इसे दिखाऊँगा नहीं।", f"Sealed as capsule #{cur.lastrowid}. It opens on {_d(due)}. I will not show it before then.")
    if LIST.match(m):
        r = c.execute("SELECT id, due, opened, text FROM capsules WHERE device=? ORDER BY due", (dev,)).fetchall()
        if not r:
            return say("सर, कोई कैप्सूल नहीं। जैसे: 6 mahine baad yeh sunana: ...", "Sir, no capsules. Try: 6 mahine baad yeh sunana: ...")
        return say("टाइम कैप्सूल:\n", "Time capsules:\n") + "\n".join(f"#{i} " + (f"{say('खुला', 'opened')}: {t[:80]}" if o else f"{say('सील, खुलेगा', 'sealed, opens')} {_d(d)}") for i, d, o, t in r)
    g = OPEN.match(m)
    if g:
        try:
            n = remind.tm(now)
        except (ValueError, TypeError):
            return None
        r = c.execute("SELECT text, due FROM capsules WHERE device=? AND id=?", (dev, int(g.group(1)))).fetchone()
        if not r:
            return say("सर, ये कैप्सूल नहीं मिला।", "Sir, I found no such capsule.")
        if r[1] > n:
            return say(f"सर, ये {_d(r[1])} को खुलेगा।", f"Sir, this one opens on {_d(r[1])}.")
        c.execute("UPDATE capsules SET opened=1, shown=1 WHERE device=? AND id=?", (dev, int(g.group(1))))
        c.commit()
        return "📦 " + r[0]
    g = DROP.match(m)
    if g:
        cur = c.execute("DELETE FROM capsules WHERE device=? AND id=?", (dev, int(g.group(1))))
        c.commit()
        return say("ठीक है, हटा दिया।", "Okay, removed.") if cur.rowcount else say("सर, ये कैप्सूल नहीं मिला।", "Sir, I found no such capsule.")
    return None


def due(c, dev, now):
    """The card for a capsule whose day came (ONCE). It carries no text: the text is sent only after your tap (open_text)."""
    try:
        n = remind.tm(now)
    except (ValueError, TypeError):
        return None
    r = c.execute("SELECT id, made FROM capsules WHERE device=? AND opened=0 AND shown=0 AND due<=? ORDER BY due LIMIT 1", (dev, n)).fetchone()
    if not r:
        return None
    c.execute("UPDATE capsules SET shown=1 WHERE id=?", (r[0],))
    c.commit()
    return {"id": r[0], "made": _d(r[1])}


def open_text(c, dev, cid, now):
    """Text after your tap, only if its day has come; marks it opened. None otherwise."""
    try:
        n = remind.tm(now)
    except (ValueError, TypeError):
        return None
    r = c.execute("SELECT text FROM capsules WHERE device=? AND id=? AND due<=?", (dev, cid, n)).fetchone()
    if not r:
        return None
    c.execute("UPDATE capsules SET opened=1, shown=1 WHERE device=? AND id=?", (dev, cid))
    c.commit()
    return r[0]
