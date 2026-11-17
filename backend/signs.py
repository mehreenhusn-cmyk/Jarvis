"""Part 104: Signs log. `sign: 11:11 dekha`, `signs dikhao` (counts repeats), `sign hatao 11:11`. Only what YOU type; nothing is detected by itself, nothing is read from the phone,
nothing goes to the AI. Jarvis only counts. It does not say what a sign means."""
import re
import time
import remind
from notes import SECRET

SAVE = re.compile(r"^\s*sign\s*[:\-]\s*(.{1,60})$", re.I)
LIST = re.compile(r"^\s*(?:signs\s+dikhao|my\s+signs|signs\s+list)\s*$", re.I)
DROP = re.compile(r"^\s*sign\s+hatao\s+(.{1,60})$", re.I)
TAIL = {"dekha", "dikha", "dikhi", "dekhi", "again", "phir", "fir", "saw", "seen"}
MAX = 300


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS signs(id INTEGER PRIMARY KEY, device INT, text TEXT, day INT, made INT)")


def _norm(t):
    w = re.sub(r"\s+", " ", t.strip().lower()).split(" ")
    while len(w) > 1 and w[-1] in TAIL:
        w.pop()
    return " ".join(w)


def handle(c, dev, msg, hindi, now):
    say = lambda hi, en: hi if hindi else en
    g = SAVE.match(msg)
    if g:
        t = _norm(g.group(1))
        if SECRET.search(t):
            return say("सर, ये यहाँ सेव नहीं करूँगा।", "Sir, I will not save that here.")
        if c.execute("SELECT count(*) FROM signs WHERE device=?", (dev,)).fetchone()[0] >= MAX:
            return say("सर, 300 एंट्री भर गईं।", "Sir, 300 entries are full.")
        try:
            n = remind.tm(now)
        except (ValueError, TypeError):
            n = 0
        c.execute("INSERT INTO signs(device, text, day, made) VALUES(?,?,?,?)", (dev, t, n // 86400 if n else 0, n))
        c.commit()
        k = c.execute("SELECT count(*) FROM signs WHERE device=? AND text=?", (dev, t)).fetchone()[0]
        return say(f"ठीक है, \"{t}\" लिख लिया। अब तक {k} बार।", f"Noted \"{t}\". That is {k} time(s) so far.")
    if LIST.match(msg):
        r = c.execute("SELECT text, count(*), max(day) FROM signs WHERE device=? GROUP BY text ORDER BY count(*) DESC, max(day) DESC LIMIT 15", (dev,)).fetchall()
        if not r:
            return say("सर, कुछ नहीं लिखा। जैसे: sign: 11:11 dekha", "Sir, nothing noted. Try: sign: 11:11 dekha")
        return say("आपके साइन (कितनी बार):\n", "Your signs (how many times):\n") + "\n".join(f"- {t}: {k} " + say("बार", "time(s)") + f", {say('आख़िरी', 'last')} {time.strftime('%d %b', time.gmtime(d * 86400)) if d else '?'}" for t, k, d in r)
    g = DROP.match(msg)
    if g:
        cur = c.execute("DELETE FROM signs WHERE device=? AND text=?", (dev, _norm(g.group(1))))
        c.commit()
        return say("ठीक है, हटा दिया।", "Okay, removed.") if cur.rowcount else say("सर, ये नहीं मिला।", "Sir, I found no such entry.")
    return None
