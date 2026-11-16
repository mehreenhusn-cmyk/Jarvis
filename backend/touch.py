"""Part 95: Last talked. Only people YOU pick: `ammi track karo`, then `ammi se baat hui` (sets today). `ammi track 10 din` changes the days (default 7).
The briefing says `Ammi se 7 din se baat nahi hui`. No call log, no WhatsApp reading, never sent to the AI. `ammi track band karo` removes it. Max 10 people."""
import datetime
import re
import habits
from notes import SECRET

N = r"(.{2,25}?)"
ADD = re.compile(r"^\s*" + N + r"\s+track\s+(?:karo|kar\s+do|on)\s*$", re.I)
DAYS = re.compile(r"^\s*" + N + r"\s+track\s+(\d{1,3})\s+(?:din|days?)\s*$", re.I)
OFF = re.compile(r"^\s*" + N + r"\s+track\s+(?:band\s+karo|band|off)\s*$", re.I)
SPOKE = re.compile(r"^\s*" + N + r"\s+(?:se|ko)\s+baat\s+(?:hui|ho\s+gayi|kar\s+li)\s*$", re.I)
LIST = re.compile(r"^\s*(?:tracked\s+people|kis\s+kis\s+ko\s+track|last\s+talked)\s*$", re.I)
MAX_PEOPLE = 10


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS touch(id INTEGER PRIMARY KEY, device INT, name TEXT, last TEXT, every INT DEFAULT 7)")


def _rows(c, dev):
    return c.execute("SELECT name, last, every FROM touch WHERE device=? ORDER BY id", (dev,)).fetchall()


def _ago(last, today):
    try:
        return (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)).days
    except ValueError:
        return None


def handle(c, dev, msg, hindi, now):
    m = re.sub(r"\s+", " ", msg.strip())
    if len(m) > 60:
        return None
    say = lambda hi, en: hi if hindi else en
    today, rows = habits._today(now), _rows(c, dev)
    names = [r[0] for r in rows]
    if LIST.match(m):
        if not rows:
            return say("सर, किसी को ट्रैक नहीं कर रहा। जैसे: ammi track karo", "Sir, nobody is tracked. Try: ammi track karo")
        return say("आख़िरी बात:\n", "Last talked:\n") + "\n".join(
            f"- {n.title()}: " + (say(f"{a} दिन पहले", f"{a} day(s) ago") if (a := _ago(l, today)) is not None else "?") + f" ({e} " + say("दिन की सीमा", "day limit") + ")" for n, l, e in rows)
    for rx in (DAYS, ADD):
        g = rx.match(m)
        if g:
            n, e = g.group(1).strip().lower(), (int(g.group(2)) if rx is DAYS else 7)
            if SECRET.search(n) or not today or not 1 <= e <= 365:
                return say("सर, ये नहीं हो पाया।", "Sir, that did not work.")
            if n in names:
                c.execute("UPDATE touch SET every=? WHERE device=? AND name=?", (e, dev, n))
            elif len(names) >= MAX_PEOPLE:
                return say("सर, 10 लोगों की सीमा पूरी है।", "Sir, the limit of 10 people is full.")
            else:
                c.execute("INSERT INTO touch(device, name, last, every) VALUES(?,?,?,?)", (dev, n, today, e))
            c.commit()
            return say(f"ठीक है, {n.title()} से {e} दिन बात न हो तो ब्रीफिंग बताएगी।", f"Okay. If {e} days pass without talking to {n.title()}, the briefing will say so.")
    g = OFF.match(m)
    if g and g.group(1).strip().lower() in names:
        c.execute("DELETE FROM touch WHERE device=? AND name=?", (dev, g.group(1).strip().lower()))
        c.commit()
        return say("ठीक है, ट्रैक बंद।", "Okay, tracking stopped.")
    g = SPOKE.match(m)
    if g and g.group(1).strip().lower() in names and today:
        c.execute("UPDATE touch SET last=? WHERE device=? AND name=?", (today, dev, g.group(1).strip().lower()))
        c.commit()
        return say(f"ठीक है, {g.group(1).strip().title()} से आज बात लिख ली।", f"Okay, noted: you talked to {g.group(1).strip().title()} today.")
    return None


def lines(c, dev, now, hindi):
    """Briefing lines: tracked people whose limit passed, longest silence first (max 3)."""
    today, out = habits._today(now), []
    for n, l, e in _rows(c, dev) if today else []:
        a = _ago(l, today)
        if a is not None and a >= e:
            out.append((a, f"- {n.title()} से {a} दिन से बात नहीं हुई" if hindi else f"- Haven't talked to {n.title()} for {a} days"))
    return [t for _, t in sorted(out, reverse=True)[:3]]
