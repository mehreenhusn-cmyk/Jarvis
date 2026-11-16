"""Part 96: Mood check-in, ONLY when you say it. `mood 3` (1 to 5), `aaj mood low` (low 2, ok 3, high 4), `mood history`, `mood care on` / `mood care off`.
Never sent to the AI, never guessed from your words. With `mood care on`, after 4 low check-ins in a row the briefing adds one gentle line. Jarvis is not a doctor."""
import re
import remind

SET = re.compile(r"^\s*(?:aaj\s+)?mood\s+(?:([1-5])|(low|ok|high))\s*$", re.I)
HIST = re.compile(r"^\s*mood\s+history\s*$", re.I)
CARE = re.compile(r"^\s*mood\s+care\s+(on|off)\s*$", re.I)
WORD = {"low": 2, "ok": 3, "high": 4}


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS moods(id INTEGER PRIMARY KEY, device INT, day TEXT, score INT)")  # day = 'care' is the switch row


def _day(now):
    try:
        return str(remind.tm(now) // 86400)
    except (ValueError, TypeError):
        return ""


def _care(c, dev):
    return c.execute("SELECT 1 FROM moods WHERE device=? AND day='care' AND score=1", (dev,)).fetchone() is not None


def handle(c, dev, msg, hindi, now):
    if len(msg) > 40:
        return None
    m = CARE.match(msg)
    if m:
        c.execute("DELETE FROM moods WHERE device=? AND day='care'", (dev,))
        c.execute("INSERT INTO moods(device, day, score) VALUES(?,?,?)", (dev, "care", 1 if m.group(1).lower() == "on" else 0))
        c.commit()
        on = m.group(1).lower() == "on"
        return ("ठीक है, 4 कम मूड के बाद ब्रीफिंग में एक नरम लाइन आएगी।" if on else "ठीक है, मूड केयर बंद।") if hindi else ("Okay. After 4 low check-ins in a row the briefing adds one gentle line." if on else "Okay, mood care is off.")
    if HIST.match(msg):
        r = c.execute("SELECT day, score FROM moods WHERE device=? AND day!='care' ORDER BY CAST(day AS INT) DESC LIMIT 14", (dev,)).fetchall()
        if not r:
            return "सर, अभी कोई मूड नहीं लिखा। जैसे: mood 3" if hindi else "Sir, no mood noted yet. Try: mood 3"
        import time
        return ("मूड (1 बहुत कम, 5 बढ़िया):\n" if hindi else "Mood (1 very low, 5 great):\n") + "\n".join(f"{time.strftime('%d %b', time.gmtime(int(d) * 86400))}: {s}" for d, s in r)
    m = SET.match(msg)
    if not m:
        return None
    day = _day(now)
    if not day:
        return "सर, फ़ोन का समय नहीं पढ़ पाया, इसलिए मूड सेव नहीं हुआ।" if hindi else "Sir, I could not read the phone time, so the mood was not saved."
    s = int(m.group(1)) if m.group(1) else WORD[m.group(2).lower()]
    c.execute("DELETE FROM moods WHERE device=? AND day=?", (dev, day))
    c.execute("INSERT INTO moods(device, day, score) VALUES(?,?,?)", (dev, day, s))
    c.commit()
    out = (f"मूड {s}/5 लिख लिया।" if hindi else f"Mood {s}/5 noted.")
    if s <= 1:
        out += " अगर बहुत भारी लगे तो किसी अपने से बात कीजिए, या Tele-MANAS 14416 पर कॉल कीजिए।" if hindi else " If it feels too heavy, talk to someone you trust or call Tele-MANAS 14416."
    return out


def line(c, dev, now, hindi):
    """One gentle briefing line (as a list), only with `mood care on`, after 4 low check-ins in a row (newest within 2 days, all within 6 days)."""
    day = _day(now)
    if not day or not _care(c, dev):
        return []
    r = c.execute("SELECT CAST(day AS INT), score FROM moods WHERE device=? AND day!='care' ORDER BY CAST(day AS INT) DESC LIMIT 4", (dev,)).fetchall()
    if len(r) < 4 or any(s > 2 for _, s in r) or int(day) - r[0][0] > 2 or r[0][0] - r[3][0] > 6:
        return []
    return ["- चार दिन से मूड कम लिखा है। बात करनी हो या कोई छोटा सा काम आसान करवाना हो तो बोलिए। मैं डॉक्टर नहीं हूँ।" if hindi else
            "- Your last 4 check-ins were low. Want to talk, or want one small thing made easier? Say so. I am not a doctor."]
