"""Parts 97 + 98: Time Capsule (text). `6 mahine baad yeh sunana: ...`, `1 saal baad yeh sunana: ...`, `30 din baad ...`, `2 hafte baad ...`.
Sealed text stays hidden until the day. Then a card appears ONCE; Jarvis reads it only after your tap (`Open and read aloud`). Later: `open capsule 3`.
`my capsules` lists sealed ones (dates only) and opened ones. `capsule hatao 3` removes one.
Part 98 (opens on a condition instead of a date): `phrase capsule himmat chahiye: ...` opens ONLY when you type that phrase to Jarvis; `ammi se 30 din baat na ho to yeh sunana: ...` opens when 30 days pass without
talking to a person you track in Part 95 (`touch.py`). A condition capsule never shows by itself before its condition is met. Saved only on your words, never sent to the AI."""
import datetime
import re
import time
import remind
from notes import SECRET

SAVE = re.compile(r"^\s*(\d{1,3})\s*(din|days?|hafte?|weeks?|mahine?|months?|saal|years?)\s+baad\s+(?:yeh|ye|ise|isko)\s+(?:sunana|sunao|dikhana|dikhao)\s*[:\-]\s*(.{3,500})$", re.I | re.S)
LIST = re.compile(r"^\s*(?:my\s+(?:time\s+)?capsules?|meri\s+capsules?|time\s+capsules?|capsules?\s+dikhao)\s*$", re.I)
OPEN = re.compile(r"^\s*open\s+capsule\s*#?(\d+)\s*$", re.I)
PHRASE = re.compile(r"^\s*phrase\s+capsule\s+(.{2,40}?)\s*[:\-]\s*(.{3,500})$", re.I | re.S)
SILENT = re.compile(r"^\s*(.{2,25}?)\s+se\s+(\d{1,3})\s+din\s+baat\s+na\s+ho\s+to\s+(?:yeh|ye)\s+(?:sunana|sunao|dikhana)\s*[:\-]\s*(.{3,500})$", re.I | re.S)
DROP = re.compile(r"^\s*capsule\s+(?:hatao|delete|remove)\s*#?(\d+)\s*$", re.I)
UNIT = (("din", 1), ("day", 1), ("haft", 7), ("week", 7), ("mahin", 30), ("month", 30), ("saal", 365), ("year", 365))
MAX_SEALED = 20


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS capsules(id INTEGER PRIMARY KEY, device INT, text TEXT, due INT, made INT, shown INT DEFAULT 0, opened INT DEFAULT 0)")
    have = {r[1] for r in c.execute("PRAGMA table_info(capsules)")}
    if "kind" not in have:  # Part 98: kind = date / phrase / silence, trig = the phrase, or 'name|days'
        c.execute("ALTER TABLE capsules ADD COLUMN kind TEXT DEFAULT 'date'")
        c.execute("ALTER TABLE capsules ADD COLUMN trig TEXT DEFAULT ''")


def _quiet(c, dev, trig, now):
    """Part 98: True when the tracked person has not been talked to for the capsule's days (reads Part 95's `touch` table)."""
    try:
        who, days = trig.split("|")
        last = c.execute("SELECT last FROM touch WHERE device=? AND name=?", (dev, who)).fetchone()
        today = datetime.datetime.utcfromtimestamp(remind.tm(now)).date()
        return bool(last) and (today - datetime.date.fromisoformat(last[0])).days >= int(days)
    except (ValueError, TypeError, OverflowError):
        return False


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
    g = PHRASE.match(m) or SILENT.match(m)
    if g:
        ph = g.re is PHRASE
        text = g.group(2 if ph else 3).strip()
        if SECRET.search(text) or (ph and SECRET.search(g.group(1))):
            return say("सर, पासवर्ड, OTP, PIN या कार्ड नंबर मैं सेव नहीं करता।", "Sir, I do not save a password, OTP, PIN or card number.")
        try:
            n = remind.tm(now)
        except (ValueError, TypeError):
            return say("सर, फ़ोन का समय नहीं पढ़ पाया।", "Sir, I could not read the phone time.")
        if c.execute("SELECT count(*) FROM capsules WHERE device=? AND opened=0", (dev,)).fetchone()[0] >= MAX_SEALED:
            return say("सर, 20 कैप्सूल सील हैं।", "Sir, 20 capsules are already sealed.")
        if ph:
            trig = g.group(1).strip().lower()
        else:
            who, days = g.group(1).strip().lower(), int(g.group(2))
            if not 7 <= days <= 365 or not c.execute("SELECT 1 FROM touch WHERE device=? AND name=?", (dev, who)).fetchone():
                return say(f"सर, पहले ट्रैक कीजिए: {who} track karo (और 7 से 365 दिन)।", f"Sir, track the person first: {who} track karo (and use 7 to 365 days).")
            trig = f"{who}|{days}"
        cur = c.execute("INSERT INTO capsules(device, text, due, made, kind, trig) VALUES(?,?,?,?,?,?)", (dev, text, n, n, "phrase" if ph else "silence", trig))
        c.commit()
        return say(f"ठीक है, कैप्सूल #{cur.lastrowid} सील। ", f"Sealed as capsule #{cur.lastrowid}. ") + (say(f"जब आप \"{trig}\" लिखेंगे तभी खुलेगा।", f"It opens only when you type \"{trig}\".") if ph else say(f"{who.title()} से {days} दिन बात न हो तो खुलेगा।", f"It opens if {days} days pass without talking to {who.title()}."))
    if LIST.match(m):
        r = c.execute("SELECT id, due, opened, text, kind, trig FROM capsules WHERE device=? ORDER BY id", (dev,)).fetchall()
        if not r:
            return say("सर, कोई कैप्सूल नहीं। जैसे: 6 mahine baad yeh sunana: ...", "Sir, no capsules. Try: 6 mahine baad yeh sunana: ...")
        def how(d, k, tg):
            if k == "phrase":
                return say(f"खुलेगा जब आप \"{tg}\" लिखें", f"opens when you type \"{tg}\"")
            if k == "silence":
                a, b = tg.split("|")
                return say(f"खुलेगा अगर {a.title()} से {b} दिन बात न हो", f"opens if {b} days pass without {a.title()}")
            return f"{say('सील, खुलेगा', 'sealed, opens')} {_d(d)}"
        return say("टाइम कैप्सूल:\n", "Time capsules:\n") + "\n".join(f"#{i} " + (f"{say('खुला', 'opened')}: {t[:80]}" if o else how(d, k, tg)) for i, d, o, t, k, tg in r)
    g = OPEN.match(m)
    if g:
        try:
            n = remind.tm(now)
        except (ValueError, TypeError):
            return None
        r = c.execute("SELECT text, due, kind, trig FROM capsules WHERE device=? AND id=?", (dev, int(g.group(1)))).fetchone()
        if not r:
            return say("सर, ये कैप्सूल नहीं मिला।", "Sir, I found no such capsule.")
        if r[2] == "phrase":
            return say("सर, ये सिर्फ़ तब खुलता है जब आप वो शब्द लिखें।", "Sir, this one opens only when you type its phrase.")
        if r[2] == "silence" and not _quiet(c, dev, r[3], now):
            return say("सर, अभी शर्त पूरी नहीं हुई।", "Sir, its condition is not met yet.")
        if r[2] == "date" and r[1] > n:
            return say(f"सर, ये {_d(r[1])} को खुलेगा।", f"Sir, this one opens on {_d(r[1])}.")
        c.execute("UPDATE capsules SET opened=1, shown=1 WHERE device=? AND id=?", (dev, int(g.group(1))))
        c.commit()
        return "📦 " + r[0]
    g = DROP.match(m)
    if g:
        cur = c.execute("DELETE FROM capsules WHERE device=? AND id=?", (dev, int(g.group(1))))
        c.commit()
        return say("ठीक है, हटा दिया।", "Okay, removed.") if cur.rowcount else say("सर, ये कैप्सूल नहीं मिला।", "Sir, I found no such capsule.")
    low = m.lower()  # Part 98: a phrase capsule opens ONLY when its phrase is typed to Jarvis (after every other command was checked)
    for i, t, tg in c.execute("SELECT id, text, trig FROM capsules WHERE device=? AND kind='phrase' AND opened=0", (dev,)).fetchall():
        if tg and tg in low:
            c.execute("UPDATE capsules SET opened=1, shown=1 WHERE id=?", (i,))
            c.commit()
            return "📦 " + t
    return None


def due(c, dev, now):
    """The card for a capsule whose day came (ONCE). It carries no text: the text is sent only after your tap (open_text)."""
    try:
        n = remind.tm(now)
    except (ValueError, TypeError):
        return None
    r = c.execute("SELECT id, made FROM capsules WHERE device=? AND opened=0 AND shown=0 AND kind='date' AND due<=? ORDER BY due LIMIT 1", (dev, n)).fetchone()
    if not r:  # Part 98: a silence capsule whose condition is now met
        for i, mk, tg in c.execute("SELECT id, made, trig FROM capsules WHERE device=? AND opened=0 AND shown=0 AND kind='silence'", (dev,)).fetchall():
            if _quiet(c, dev, tg, now):
                r = (i, mk)
                break
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
    r = c.execute("SELECT text, kind, trig FROM capsules WHERE device=? AND id=? AND (kind='date' AND due<=? OR kind='silence')", (dev, cid, n)).fetchone()
    if not r:
        return None
    if r[1] == "silence" and not _quiet(c, dev, r[2], now):
        return None
    c.execute("UPDATE capsules SET opened=1, shown=1 WHERE device=? AND id=?", (dev, cid))
    c.commit()
    return r[0]
