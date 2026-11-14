"""Jarvis reminders (Part 10): "Faisal ko 5000 dene hain 15 Nov ko yaad dilana". Tareekh AI se samajhta hai (ek chhota sawal).
Time hamesha phone ke browser ka hai (server ka timezone nahi dekhte). Page khula ho tabhi reminder aata hai."""
import calendar, json, re, time

DEL = re.compile(r"^\s*(?:reminder|रिमाइंडर)\s*(?:hatao|delete|cancel|हटाओ)\s*#?(\d+)\s*$", re.I)
LIST = re.compile(r"reminders?\s*(?:dikhao|list|batao|kya)|kya reminders?|रिमाइंडर\s*(?:दिखाओ|क्या)", re.I)
ADD = re.compile(r"yaad dila|remind|याद दिला|रिमाइंड", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, device INT, text TEXT, due REAL, sent INT DEFAULT 0)")


def tm(s):
    return calendar.timegm(time.strptime(str(s).strip()[:16], "%Y-%m-%d %H:%M"))


def show(t):
    return time.strftime("%d %b %H:%M", time.gmtime(t))


def due(c, dev, now):
    """Jin reminders ka time ho gaya wo lautao aur 'sent' mark karo."""
    try:
        n = tm(now)
    except ValueError:
        return []
    r = c.execute("SELECT id, text FROM reminders WHERE device=? AND sent=0 AND due<=? ORDER BY due", (dev, n)).fetchall()
    for i, _ in r:
        c.execute("UPDATE reminders SET sent=1 WHERE id=?", (i,))
    c.commit()
    return [{"id": i, "text": t} for i, t in r]


def handle(c, dev, msg, hindi, ask, now):
    def say(hi, ro):
        return hi if hindi else ro
    m = DEL.match(msg)
    if m:
        k = c.execute("DELETE FROM reminders WHERE id=? AND device=?", (int(m.group(1)), dev)).rowcount
        c.commit()
        return say("ठीक है सर, रिमाइंडर हटा दिया।", "Theek hai sir, reminder hata diya.") if k else say("सर, वो रिमाइंडर नहीं मिला।", "Sir, wo reminder nahi mila.")
    if LIST.search(msg) and len(msg) < 60:
        r = c.execute("SELECT id, text, due FROM reminders WHERE device=? AND sent=0 ORDER BY due", (dev,)).fetchall()
        if not r:
            return say("सर, कोई रिमाइंडर बाकी नहीं है।", "Sir, koi reminder baaki nahi hai.")
        return say("सर, ये रिमाइंडर बाकी हैं:\n", "Sir, ye reminders baaki hain:\n") + "\n".join(f"#{i} {show(d)} - {t}" for i, t, d in r)
    if not ADD.search(msg) or len(msg) > 300:
        return None
    try:
        n = tm(now)
    except ValueError:
        return say("सर, फ़ोन का समय नहीं मिला, पेज रीफ़्रेश कीजिए।", "Sir, phone ka time nahi mila, page refresh karo.")
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
        return say("सर, मैं समय नहीं समझ पाया। जैसे लिखिए: 'कल सुबह 9 बजे चाय याद दिलाना'", "Sir, time samajh nahi aaya. Aise likho: 'kal subah 9 baje chai yaad dilana'")
    if d < n - 60:
        return say("सर, वो समय तो निकल चुका है।", "Sir, wo time to nikal chuka hai.")
    i = c.execute("INSERT INTO reminders(device, text, due) VALUES(?,?,?)", (dev, text, d)).lastrowid
    c.commit()
    return say(f"ठीक है सर, {show(d)} को याद दिलाऊँगा (#{i}): {text}", f"Theek hai sir, {show(d)} ko yaad dilaunga (#{i}): {text}")
