"""Part 157: Jarvis ASKS at the right moment, never acts alone. Built on what Jarvis already knows (your habits, what it picked up today).
One offer at a time, at most 2 answered per day, never before 7 am or after 11 pm. Every offer has Yes, Not now and Never (that kind of offer is gone for good).
Yes only sends the normal command, exactly as if you had typed it. Offers (on top of Part 143's `you usually call X around now`):
 - evening (after 8 pm): `today I picked up N new things from your talk. Show?` (Part 155; the same list `kya samjha` shows)
 - evening (after 7 pm): a habit with a streak of 2 or more that is not marked today: `Is it done? Shall I log it?`
Switch: `sujhav band karo` / `sujhav chalu karo`. It also stops with `seekhna band karo` (Part 143). Money, calls and messages are never offered here."""
import re
import time

import autolearn, habits, learn, memory

OFF = re.compile(r"^\s*(?:sujhav|suggestions?)\s+(?:band|off)(?:\s+karo)?\s*$", re.I)
ON = re.compile(r"^\s*(?:sujhav|suggestions?)\s+(?:chalu|on)(?:\s+karo)?\s*$", re.I)
MAX_PER_DAY = 2


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS nudges(id INTEGER PRIMARY KEY, device INT, key TEXT, day TEXT DEFAULT '', state TEXT DEFAULT '', UNIQUE(device, key))")


def is_on(c, dev):
    return learn.is_on(c, dev) and not memory.flag(c, dev, "nudge_off")


def _day(now):
    return time.strftime("%Y-%m-%d", time.localtime(now))


def _candidates(c, dev, hr, day, now):
    """(key, text, command) in the order they are tried."""
    out = []
    if hr >= 20:
        n = len(autolearn.today(c, dev, now))
        if n:
            out.append(("learned", f"Sir, aaj maine aapki baaton se {n} nayi baat{'ein' if n > 1 else ''} samjhi. Dikhaun?", "kya samjha"))
    if hr >= 19:
        for name in habits._names(c, dev):
            days = habits._days(c, dev, name)
            if day not in days and habits.streak(days, day) >= 2:
                out.append((f"habit:{name}", f"Sir, aaj {name} abhi tak mark nahi hua (streak {habits.streak(days, day)} din). Ho gaya ho to log kar dun?", f"aaj {name} gaya"))
    return out


def suggest(c, dev, now=None):
    """ONE offer {id (negative), text, cmd, never} or None. Nothing is marked here; the answer (act) marks it."""
    if not is_on(c, dev):
        return None
    now = time.time() if now is None else now
    hr, day = time.localtime(now).tm_hour, _day(now)
    if hr < 7 or hr >= 23:
        return None
    if c.execute("SELECT count(*) FROM nudges WHERE device=? AND day=?", (dev, day)).fetchone()[0] >= MAX_PER_DAY:
        return None
    for key, text, cmd in _candidates(c, dev, hr, day, now):
        r = c.execute("SELECT id, day, state FROM nudges WHERE device=? AND key=?", (dev, key)).fetchone()
        if r and (r[2] == "no" or r[1] == day):
            continue
        if not r:
            c.execute("INSERT INTO nudges(device, key) VALUES(?,?)", (dev, key))
            c.commit()
            r = c.execute("SELECT id, day, state FROM nudges WHERE device=? AND key=?", (dev, key)).fetchone()
        return {"id": -r[0], "text": text, "cmd": cmd, "never": True}
    return None


def act(c, dev, nid, what, now=None):
    """The answer to an offer: yes / later (not again today) or never (this kind is gone)."""
    if what not in ("yes", "later", "never"):
        return
    c.execute("UPDATE nudges SET day=?, state=? WHERE id=? AND device=?", (_day(time.time() if now is None else now), "no" if what == "never" else what, abs(nid), dev))
    c.commit()


def handle(c, dev, msg, hindi):
    if len(msg) > 40:
        return None
    say = lambda hi, en: hi if hindi else en
    if OFF.match(msg):
        memory.setflag(c, dev, "nudge_off", 1)
        return say("ठीक है सर, अब मैं अपनी तरफ़ से कुछ नहीं सुझाऊँगा।", "Okay sir, I will not suggest anything on my own any more.")
    if ON.match(msg):
        memory.setflag(c, dev, "nudge_off", 0)
        return say("ठीक है सर, सही मौक़े पर सुझाव दूँगा, पर पूछकर ही, खुद कुछ नहीं करूँगा।", "Okay sir, I will suggest things at the right moment, but only ask. I never act alone.")
    return None


def wipe(c, dev):
    c.execute("DELETE FROM nudges WHERE device=?", (dev,))
    c.commit()
