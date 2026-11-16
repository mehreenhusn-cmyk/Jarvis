"""Part 83: habit and streak tracker. First "habit banao gym", then "aaj gym gaya" or "medicine le li" or "gym done" marks today.
"my habits" shows the streaks, "habit report" shows the last 7 days. Only a habit YOU made is ever marked, so normal chat ("kaam ho gaya") is never taken by mistake.
One small table: a row with an empty day is the habit itself, a row with a day is one check-in. Stays on the phone, never sent to the AI. Max 10 habits."""
import datetime
import re

import notes

N = r"(.{2,25}?)"
MAKE = re.compile(r"^\s*(?:habit\s+(?:banao|add|new|jodo)|new\s+habit|add\s+habit|आदत\s+(?:जोड़ो|बनाओ))\s+" + N + r"\s*$", re.I)
DROP = re.compile(r"^\s*(?:habit\s+(?:hatao|delete|remove)|(?:delete|remove)\s+habit|आदत\s+हटाओ)\s+" + N + r"\s*$", re.I)
LIST = re.compile(r"^\s*(?:my\s+habits?|meri\s+habits?|habits?(?:\s+(?:list|dikhao|streaks?))?|मेरी\s+आदतें|आदतें)\s*$", re.I)
REPORT = re.compile(r"^\s*(?:habit\s+report|habits?\s+(?:ka\s+)?(?:report|summary)|weekly\s+habit\s+report|आदतों\s+की\s+रिपोर्ट)\s*$", re.I)
STREAK = re.compile(r"^\s*" + N + r"\s+streak\s*$", re.I)
DONE = re.compile(r"^\s*(?:(?:aaj|today|आज)\s+)?(?:habit\s+)?" + N + r"\s+(?:gaya|gayi|gaye|kar\s+liya|kar\s+li|kar\s+le|le\s+li|le\s+liya|kiya|ho\s+gaya|ho\s+gayi|done|complete|completed|did\s+it|गया|गई|कर\s+लिया|ले\s+ली|ले\s+लिया|किया)\s*$", re.I)
MAX_HABITS = 10


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY, device INT, name TEXT, day TEXT DEFAULT '')")


def _names(c, dev):
    return [r[0] for r in c.execute("SELECT name FROM habits WHERE device=? AND day='' ORDER BY id", (dev,))]


def _days(c, dev, name):
    return {r[0] for r in c.execute("SELECT day FROM habits WHERE device=? AND name=? AND day<>''", (dev, name))}


def _today(now):
    d = str(now)[:10]
    return d if re.fullmatch(r"\d{4}-\d\d-\d\d", d) else None


def streak(days, today):
    """Days in a row up to today. If today is not marked yet, the streak is still alive from yesterday."""
    d = datetime.date.fromisoformat(today)
    if d.isoformat() not in days:
        d -= datetime.timedelta(days=1)
    k = 0
    while d.isoformat() in days:
        k += 1
        d -= datetime.timedelta(days=1)
    return k


def _find(names, text):
    t = text.strip().lower()
    return next((n for n in names if n == t), None)


def summary(c, dev, now, hindi):
    """Lines for the briefing: only the habits NOT marked yet today, with their streak. [] when there is nothing to say."""
    today, out = _today(now), []
    for n in _names(c, dev) if today else []:
        ds = _days(c, dev, n)
        if today not in ds:
            k = streak(ds, today)
            out.append(f"- {n}: " + ("आज बाकी" if hindi else "not done yet today") + (f" ({k} " + ("दिन की लकीर" if hindi else "day streak") + ")" if k else ""))
    return out


def done_count(c, dev, now):
    """(habits done today, all habits) for the day summary."""
    today, names = _today(now), _names(c, dev)
    return (sum(1 for n in names if today in _days(c, dev, n)) if today else 0), len(names)


def handle(c, dev, msg, hindi, now):
    """Reply text for a habit command, else None (so the normal chat pipeline goes on)."""
    m = re.sub(r"\s+", " ", msg.strip())
    if len(m) > 80:
        return None
    say = lambda hi, en: hi if hindi else en
    names, today = _names(c, dev), _today(now)
    g = MAKE.match(m)
    if g:
        n = g.group(1).strip().lower()
        if notes.SECRET.search(n):
            return say("सर, ये नाम नहीं सहेजूँगा।", "Sir, I will not save that name.")
        if n in names:
            return say(f"सर, \"{n}\" पहले से है।", f"Sir, \"{n}\" is already there.")
        if len(names) >= MAX_HABITS:
            return say("सर, 10 आदतों की सीमा पूरी हो गई। एक हटाइए।", "Sir, the limit of 10 habits is full. Remove one first.")
        c.execute("INSERT INTO habits(device, name, day) VALUES(?,?,'')", (dev, n))
        c.commit()
        return say(f"ठीक है सर, आदत \"{n}\" बन गई। अब बोलिए: aaj {n} gaya", f"Okay sir, habit \"{n}\" created. Now say: aaj {n} gaya (or: {n} done)")
    g = DROP.match(m)
    if g:
        n = _find(names, g.group(1))
        if not n:
            return say("सर, ये आदत नहीं मिली। \"my habits\" बोलिए।", "Sir, I did not find that habit. Say \"my habits\".")
        c.execute("DELETE FROM habits WHERE device=? AND name=?", (dev, n))
        c.commit()
        return say(f"ठीक है सर, \"{n}\" और उसका रिकॉर्ड हटा दिया।", f"Okay sir, \"{n}\" and its record are removed.")
    if LIST.match(m):
        if not names:
            return say("सर, अभी कोई आदत नहीं है। जैसे: habit banao gym", "Sir, no habits yet. Try: habit banao gym")
        if not today:
            return None
        return say("सर, आपकी आदतें:\n", "Sir, your habits:\n") + "\n".join(
            f"- {n}: {streak(_days(c, dev, n), today)} " + say("दिन लगातार", "day streak") + (" ✅" if today in _days(c, dev, n) else "") for n in names)
    if REPORT.match(m):
        if not names or not today:
            return say("सर, अभी कोई आदत नहीं है।", "Sir, no habits yet.") if not names else None
        week = [(datetime.date.fromisoformat(today) - datetime.timedelta(days=i)).isoformat() for i in range(7)]
        return say("पिछले 7 दिन:\n", "Last 7 days:\n") + "\n".join(f"- {n}: {len(_days(c, dev, n) & set(week))}/7 " + say("दिन", "days") for n in names)
    g = STREAK.match(m)
    if g and _find(names, g.group(1)) and today:
        n = _find(names, g.group(1))
        return say(f"सर, \"{n}\" की लकीर {streak(_days(c, dev, n), today)} दिन है।", f"Sir, your \"{n}\" streak is {streak(_days(c, dev, n), today)} day(s).")
    g = DONE.match(m)
    n = _find(names, g.group(1)) if g else None
    if n and today:
        if today in _days(c, dev, n):
            return say(f"सर, \"{n}\" आज पहले से लिखा है।", f"Sir, \"{n}\" is already marked for today.")
        c.execute("INSERT INTO habits(device, name, day) VALUES(?,?,?)", (dev, n, today))
        c.commit()
        k = streak(_days(c, dev, n), today)
        return say(f"शाबाश सर! \"{n}\" आज लिख लिया। लगातार {k} दिन।", f"Well done, sir! \"{n}\" is marked for today. {k} day(s) in a row.")
    return None
