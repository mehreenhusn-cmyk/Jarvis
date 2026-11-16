"""Jarvis reminders (Part 10): "Faisal ko 5000 dene hain 15 Nov ko yaad dilana". Tareekh AI se samajhta hai (ek chhota sawal).
Part 44: repeat ("roz", "har hafte", "har mahine", "har saal") aur birthday ("Faisal ka birthday 15 Nov", har saal subah 9 baje).
Time hamesha phone ke browser ka hai (server ka timezone nahi dekhte). Page khula ho tabhi reminder aata hai."""
import calendar, json, re, time

import people

DEL = re.compile(r"^\s*(?:reminder|रिमाइंडर)\s*(?:hatao|delete|cancel|हटाओ)\s*#?(\d+)\s*$", re.I)
LIST = re.compile(r"reminders?\s*(?:dikhao|list|batao|kya)|kya reminders?|रिमाइंडर\s*(?:दिखाओ|क्या)|^\s*(?:my\s+)?reminders?\s*\??\s*$", re.I)  # Part 44: 'my reminders' sirf list dikhaye, naya reminder na banaye
ADD = re.compile(r"yaad dila|remind|याद दिला|रिमाइंड", re.I)
REP = (("daily", re.compile(r"\b(?:roz|rozana|har\s*din|every\s*day|daily)\b|रोज़|रोज|हर दिन", re.I)),
       ("weekly", re.compile(r"\b(?:har\s*hafte|every\s*week|weekly)\b|हर हफ्ते|हर हफ़्ते", re.I)),
       ("monthly", re.compile(r"\b(?:har\s*mahine|every\s*month|monthly)\b|हर महीने", re.I)),
       ("yearly", re.compile(r"\b(?:har\s*saal|every\s*year|yearly|annually)\b|हर साल", re.I)))
REPHI = {"daily": "रोज़", "weekly": "हर हफ़्ते", "monthly": "हर महीने", "yearly": "हर साल"}
MON = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
DATE = r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:of\s+)?([A-Za-z]{3,9})|([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?|(\d{1,2})\s*[/-]\s*(\d{1,2})"
BD1 = re.compile(r"^\s*birthday\s*(?:of|for|:|-)?\s*(.{1,40}?)\s*(?:is\s+on|on|:|-)\s*(.{3,20}?)\s*$", re.I)
BD2 = re.compile(r"^\s*(.{1,40}?)(?:'s|\s+ka|\s+ki)?\s+(?:birthday|bday|janamdin|janmdin)\s*(?:is\s+on|hai|on|:|-)?\s*(.{3,20}?)(?:\s+(?:ko\s+)?hai)?\s*$", re.I)
BDL = re.compile(r"^\s*(?:my\s+)?birthdays?\s*(?:dikhao|list|batao|kab)?\s*\??\s*$", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, device INT, text TEXT, due REAL, sent INT DEFAULT 0)")
    if "rep" not in [r[1] for r in c.execute("PRAGMA table_info(reminders)")]:  # Part 44: purani table mein ek naya column, kuch hatta nahi
        c.execute("ALTER TABLE reminders ADD COLUMN rep TEXT DEFAULT ''")


def tm(s):
    return calendar.timegm(time.strptime(str(s).strip()[:16], "%Y-%m-%d %H:%M"))


def show(t):
    return time.strftime("%d %b %H:%M", time.gmtime(t))


def nxt(t, rep):
    """Agli baar ka time (UTC-jaisa number). Mahina ya saal chhota ho to din ghata dete hain (31 -> 30, 29 Feb -> 28 Feb)."""
    g = time.gmtime(t)
    if rep == "daily":
        return t + 86400
    if rep == "weekly":
        return t + 7 * 86400
    y, m = (g.tm_year, g.tm_mon + 1) if rep == "monthly" else (g.tm_year + 1, g.tm_mon)
    if m > 12:
        y, m = y + 1, 1
    return calendar.timegm((y, m, min(g.tm_mday, calendar.monthrange(y, m)[1]), g.tm_hour, g.tm_min, 0))


def future(t, rep, n):
    """Repeat wale reminder ko pehli aisi baar tak aage badhao jo ab se pehle na ho."""
    while t < n and rep:
        t = nxt(t, rep)
    return t


def due(c, dev, now):
    """Jin reminders ka time ho gaya wo lautao. Ek baar wale 'sent' ho jate hain; repeat wale agli baar par chale jate hain."""
    try:
        n = tm(now)
    except ValueError:
        return []
    r = c.execute("SELECT id, text, due, rep FROM reminders WHERE device=? AND sent=0 AND due<=? ORDER BY due", (dev, n)).fetchall()
    for i, _, d, rep in r:
        if rep:
            c.execute("UPDATE reminders SET due=? WHERE id=?", (future(nxt(d, rep), rep, n + 1), i))
        else:
            c.execute("UPDATE reminders SET sent=1 WHERE id=?", (i,))
    c.commit()
    return [{"id": i, "text": t} for i, t, _, _ in r]


def today(c, dev, now):
    """Part 56: aaj ke reminders (page ke 'now' ke hisab se), time ke order me. done=1 matlab bata diya gaya."""
    try:
        n = tm(now)
    except ValueError:
        return []
    start = n - n % 86400
    r = c.execute("SELECT id, text, due, sent FROM reminders WHERE device=? AND due>=? AND due<? ORDER BY due", (dev, start, start + 86400)).fetchall()
    return [{"id": i, "text": t, "at": time.strftime("%H:%M", time.gmtime(d)), "done": int(s)} for i, t, d, s in r]


def birthdays(c, dev, n, days=7):
    """Part 75: agle 'days' din ke janamdin (aaj bhi), [(kitne din baad, text, '15 Nov')]. Subah 9 baje ke baad bhi aaj wala dikhta hai (din-mahina se nikalte hain)."""
    start, y, out = n - n % 86400, time.gmtime(n).tm_year, []
    for t, d in c.execute("SELECT text, due FROM reminders WHERE device=? AND rep='yearly' AND text LIKE '🎂%'", (dev,)):
        g = time.gmtime(d)
        for yy in (y, y + 1):
            ts = calendar.timegm((yy, g.tm_mon, min(g.tm_mday, calendar.monthrange(yy, g.tm_mon)[1]), 0, 0, 0))
            if ts >= start:
                break
        if (ts - start) // 86400 < days:
            out.append(((ts - start) // 86400, t, time.strftime("%d %b", time.gmtime(ts))))
    return sorted(out)


def pdate(txt):
    """'15 Nov', 'Nov 15', '15/11' se (din, mahina). Samajh na aaye to None."""
    m = re.fullmatch(DATE, txt.strip().rstrip("."), re.I)
    if not m:
        return None
    a, b, c2, d, e, f = m.groups()
    day, mon = (int(a), MON.get((b or "")[:3].lower())) if a else (int(d), MON.get((c2 or "")[:3].lower())) if d else (int(e), int(f))
    return (day, mon) if mon and 1 <= mon <= 12 and 1 <= day <= calendar.monthrange(2024, mon)[1] else None


def birthday(c, dev, name, dm, hindi, n):
    """Har saal subah 9 baje ek reminder. Wahi naam dobara aaye to purana hat jata hai."""
    day, mon = dm
    y = time.gmtime(n).tm_year
    t = calendar.timegm((y, mon, min(day, calendar.monthrange(y, mon)[1]), 9, 0, 0))
    if t < n:
        y += 1
        t = calendar.timegm((y, mon, min(day, calendar.monthrange(y, mon)[1]), 9, 0, 0))
    text = f"🎂 {name} ka birthday"
    c.execute("DELETE FROM reminders WHERE device=? AND rep='yearly' AND lower(text)=?", (dev, text.lower()))
    i = c.execute("INSERT INTO reminders(device, text, due, rep) VALUES(?,?,?,'yearly')", (dev, text, t)).lastrowid
    c.commit()
    people.add(c, dev, name, "birthday " + time.strftime("%d %b", time.gmtime(t)))
    d = time.strftime("%d %b", time.gmtime(t))
    return (f"ठीक है सर, {name} का जन्मदिन {d} को हर साल सुबह 9 बजे याद दिलाऊँगा (#{i})." if hindi
            else f"Okay sir, I will remind you of {name}'s birthday every year on {d} at 09:00 (#{i}).")


def handle(c, dev, msg, hindi, ask, now):
    def say(hi, ro):
        return hi if hindi else ro
    m = DEL.match(msg)
    if m:
        k = c.execute("DELETE FROM reminders WHERE id=? AND device=?", (int(m.group(1)), dev)).rowcount
        c.commit()
        return say("ठीक है सर, रिमाइंडर हटा दिया।", "Okay sir, reminder removed.") if k else say("सर, वो रिमाइंडर नहीं मिला।", "Sir, I could not find that reminder.")
    if BDL.match(msg):
        r = c.execute("SELECT id, text, due FROM reminders WHERE device=? AND rep='yearly' AND text LIKE '🎂%' ORDER BY due", (dev,)).fetchall()
        if not r:
            return say("सर, कोई जन्मदिन सेव नहीं है। ऐसे कहिए: 'Faisal ka birthday 15 Nov'", "Sir, no birthdays saved. Try: Faisal ka birthday 15 Nov")
        return say("सर, ये जन्मदिन सेव हैं:\n", "Sir, these birthdays are saved:\n") + "\n".join(f"#{i} {show(d)[:6]} - {t}" for i, t, d in r)
    for rx in (BD1, BD2):
        b = rx.match(msg)
        if b and pdate(b.group(2)):
            try:
                n = tm(now)
            except ValueError:
                return say("सर, फ़ोन का समय नहीं मिला, पेज रीफ़्रेश कीजिए।", "Sir, I could not get the phone time. Please refresh the page.")
            return birthday(c, dev, b.group(1).strip(" ,.'"), pdate(b.group(2)), hindi, n)
    if LIST.search(msg) and len(msg) < 60:
        r = c.execute("SELECT id, text, due, rep FROM reminders WHERE device=? AND sent=0 ORDER BY due", (dev,)).fetchall()
        if not r:
            return say("सर, कोई रिमाइंडर बाकी नहीं है।", "Sir, you have no pending reminders.")
        return say("सर, ये रिमाइंडर बाकी हैं:\n", "Sir, these reminders are pending:\n") + "\n".join(f"#{i} {show(d)} - {t}" + (f" 🔁 {REPHI[p] if hindi else p}" if p else "") for i, t, d, p in r)
    if not ADD.search(msg) or len(msg) > 300:
        return None
    try:
        n = tm(now)
    except ValueError:
        return say("सर, फ़ोन का समय नहीं मिला, पेज रीफ़्रेश कीजिए।", "Sir, I could not get the phone time. Please refresh the page.")
    q = (f"Abhi ka local time: {now[:16]} ({time.strftime('%A', time.gmtime(n))}). User ka message: {msg}\n"
         'Sirf ek JSON do: {"text": "kya yaad dilana hai, chhota", "when": "YYYY-MM-DD HH:MM"}. '
         "Sirf tareekh ho to 09:00 lo. 'kal', 'shaam', '2 ghante baad' jaise shabd abhi ke time se nikalo. "
         'Samay samajh na aaye to when null do.')
    try:
        out, _ = ask([{"role": "user", "content": q}], "hinglish")
        j = json.loads(re.search(r"\{.*\}", out, re.S).group(0))
        d = tm(j["when"])
        text = str(j["text"]).strip()[:200]
        assert text
    except (RuntimeError, AttributeError, ValueError, KeyError, TypeError, AssertionError):
        return say("सर, मैं समय नहीं समझ पाया। जैसे लिखिए: 'कल सुबह 9 बजे चाय याद दिलाना'", "Sir, I could not understand the time. Try: 'remind me tomorrow 9 am to drink tea'")
    rep = next((k for k, rx in REP if rx.search(msg)), "")
    if d < n - 60 and not rep:
        return say("सर, वो समय तो निकल चुका है।", "Sir, that time has already passed.")
    d = future(d, rep, n - 60)  # repeat wala ho aur pehla time nikal chuka ho to agli baar se shuru
    i = c.execute("INSERT INTO reminders(device, text, due, rep) VALUES(?,?,?,?)", (dev, text, d, rep)).lastrowid
    c.commit()
    tag = (f" ({REPHI[rep]})" if hindi else f" (repeats {rep})") if rep else ""
    return say(f"ठीक है सर, {show(d)} को याद दिलाऊँगा{tag} (#{i}): {text}", f"Okay sir, I will remind you on {show(d)}{tag} (#{i}): {text}")
