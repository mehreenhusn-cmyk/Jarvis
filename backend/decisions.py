"""Parts 93 + 94: Decision Debt and Unfinished business. Saved ONLY on your words, never sent to the AI.
`sochenge baad mein: phone lena hai`, `pending decisions`, `decision ho gaya 2`  |  `adhoora: Faisal se baat`, `adhoora dikhao`, `adhoora khatam 2`.
The briefing shows up to 2 decisions older than 3 days, and 1 unfinished item at most once in 3 days."""
import re
import remind
from notes import SECRET

DEC = re.compile(r"^\s*(?:sochenge\s+baad\s+mein|sochenge\s+baad|decide\s+later|सोचेंगे\s+बाद\s+में)\s*[:\-]\s*(.{2,200})$", re.I | re.S)
UNF = re.compile(r"^\s*(?:adhoora|अधूरा|unfinished)\s*[:\-]\s*(.{2,200})$", re.I | re.S)
LDEC = re.compile(r"^\s*(?:pending\s+decisions?|decisions?\s+(?:dikhao|list)|baaki\s+decisions?)\s*$", re.I)
LUNF = re.compile(r"^\s*(?:adhoora\s+(?:dikhao|list)|my\s+unfinished(?:\s+business)?|adhoore\s+kaam)\s*$", re.I)
CDEC = re.compile(r"^\s*decision\s+ho\s+gaya\s*#?(\d+)\s*$", re.I)
CUNF = re.compile(r"^\s*adhoora\s+khatam\s*#?(\d+)\s*$", re.I)
MAX_OPEN = 50


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY, device INT, kind TEXT, text TEXT, day INT, shown INT DEFAULT 0, done INT DEFAULT 0)")


def _day(now):
    try:
        return remind.tm(now) // 86400
    except (ValueError, TypeError):
        return 0  # unreadable phone time: still saved, just no age


def _save(c, dev, kind, text, now, hindi):
    if SECRET.search(text):
        return "सर, पासवर्ड, OTP, PIN या कार्ड नंबर मैं यहाँ सेव नहीं करता।" if hindi else "Sir, I do not save a password, OTP, PIN or card number here."
    if c.execute("SELECT count(*) FROM decisions WHERE device=? AND kind=? AND done=0", (dev, kind)).fetchone()[0] >= MAX_OPEN:
        return "सर, 50 खुली बातें हैं, पहले कुछ बंद कीजिए।" if hindi else "Sir, 50 are already open. Close a few first."
    cur = c.execute("INSERT INTO decisions(device, kind, text, day) VALUES(?,?,?,?)", (dev, kind, text.strip()[:200], _day(now)))
    c.commit()
    return (f"ठीक है, #{cur.lastrowid} सेव किया।" if hindi else f"Saved as #{cur.lastrowid}.") + (" बाद में पूछूँगा।" if hindi and kind == "d" else " I will remind you in the briefing." if kind == "d" else "")


def _list(c, dev, kind, hindi):
    r = c.execute("SELECT id, text FROM decisions WHERE device=? AND kind=? AND done=0 ORDER BY id", (dev, kind)).fetchall()
    if not r:
        return "सर, कुछ बाकी नहीं है।" if hindi else "Sir, nothing is open."
    return ("बाकी:\n" if hindi else "Open:\n") + "\n".join(f"#{i}  {t}" for i, t in r)


def _close(c, dev, kind, n, hindi):
    cur = c.execute("UPDATE decisions SET done=1 WHERE device=? AND kind=? AND id=? AND done=0", (dev, kind, n))
    c.commit()
    if not cur.rowcount:
        return f"सर, #{n} नहीं मिला।" if hindi else f"Sir, I found no open #{n}."
    return f"#{n} बंद।" if hindi else f"#{n} closed."


def handle(c, dev, msg, hindi, now):
    if len(msg) > 400:
        return None
    for rx, kind in ((DEC, "d"), (UNF, "u")):
        m = rx.match(msg)
        if m:
            return _save(c, dev, kind, m.group(1), now, hindi)
    if LDEC.match(msg):
        return _list(c, dev, "d", hindi)
    if LUNF.match(msg):
        return _list(c, dev, "u", hindi)
    for rx, kind in ((CDEC, "d"), (CUNF, "u")):
        m = rx.match(msg)
        if m:
            return _close(c, dev, kind, int(m.group(1)), hindi)
    return None


def lines(c, dev, now, hindi):
    """Briefing lines: up to 2 decisions open for 3+ days; 1 unfinished item, at most once in 3 days."""
    day = _day(now)
    if not day:
        return []
    out = [f"- #{i} {t} " + ("(फ़ैसला बाकी)" if hindi else "(still to decide)") for i, t in
           c.execute("SELECT id, text FROM decisions WHERE device=? AND kind='d' AND done=0 AND day>0 AND day<=? ORDER BY day LIMIT 2", (dev, day - 3))]
    u = c.execute("SELECT id, text FROM decisions WHERE device=? AND kind='u' AND done=0 AND shown<=? ORDER BY shown, id LIMIT 1", (dev, day - 3)).fetchone()
    if u:
        out.append(f"- #{u[0]} {u[1]} " + ("(अधूरा)" if hindi else "(unfinished)"))
        c.execute("UPDATE decisions SET shown=? WHERE id=?", (day, u[0]))
        c.commit()
    return out
