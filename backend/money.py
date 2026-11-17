"""Parts 110 + 111: Money picture and What-if. Your own numbers only, plain arithmetic, no AI, nothing leaves the phone.
`kamai 40000 mahina` (income per month), `bachat 50000` (your savings in total; also 40k, 2 lakh), `kamai hatao`, `bachat hatao`.
`paisa picture` shows income, what you spent this month (Part 84) and what is left. `agar job chhod du` shows how many months the savings last at your last 30 days of spending.
It is a simple calculation, not advice."""
import calendar
import datetime
import re
import ledger
import spend

NUM = r"(\d[\d,]*(?:\.\d+)?)\s*(k|hazar|hazaar|thousand|lakh|lac|l)?"
INC = re.compile(r"^\s*(?:kamai|income|salary|कमाई|तनख्वाह)\s+" + NUM + r"(?:\s+(?:mahina|mahine|month|monthly|per\s+month|महीना|महीने))?\s*$", re.I)
SAV = re.compile(r"^\s*(?:bachat|savings?|बचत)\s+" + NUM + r"\s*$", re.I)
DEL = re.compile(r"^\s*(kamai|income|bachat|savings?)\s+(?:hatao|delete|clear|hata\s+do)\s*$", re.I)
PIC = re.compile(r"^\s*(?:paisa|paise|money)\s+(?:picture|dikhao|show)\s*$", re.I)
WHATIF = re.compile(r"^\s*(?:agar|if)\s+(?:main\s+|mai\s+|i\s+)?job\s+(?:chhod|chod|chhor|quit|leave)\w*(?:\s+(?:du|dun|doon|doo))?\s*\??\s*$", re.I)
MULT = {"k": 1e3, "hazar": 1e3, "hazaar": 1e3, "thousand": 1e3, "lakh": 1e5, "lac": 1e5, "l": 1e5}
SIMPLE = "यह सिर्फ़ सीधा हिसाब है, सलाह नहीं।", "This is a simple calculation, not advice."


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS money(id INTEGER PRIMARY KEY, device INT, kind TEXT, amount REAL)")


def _amt(g):
    try:
        v = float(g[0].replace(",", "")) * MULT.get((g[1] or "").lower(), 1)
    except ValueError:
        return None
    return v if 0 < v <= 1e9 else None


def get(c, dev, kind):
    r = c.execute("SELECT amount FROM money WHERE device=? AND kind=? ORDER BY id DESC LIMIT 1", (dev, kind)).fetchone()
    return r[0] if r else None


def _set(c, dev, kind, v):
    c.execute("DELETE FROM money WHERE device=? AND kind=?", (dev, kind))
    c.execute("INSERT INTO money(device, kind, amount) VALUES(?,?,?)", (dev, kind, v))
    c.commit()


def _month(c, dev, today):
    """(spent this month so far, days left in the month after today)."""
    _, _, mo = spend._ranges(today)
    d = datetime.date.fromisoformat(today)
    return spend._sum(c, dev, mo, today), calendar.monthrange(d.year, d.month)[1] - d.day


def picture(c, dev, now, hindi):
    say = lambda hi, en: hi if hindi else en
    today = spend._day(now)
    inc, sav = get(c, dev, "income"), get(c, dev, "savings")
    if inc is None and sav is None:
        return say("सर, पहले अपने नंबर बताइए। जैसे: kamai 40000 mahina और bachat 50000", "Sir, tell me your numbers first. For example: kamai 40000 mahina and bachat 50000")
    out = [say("आपकी पैसे की तस्वीर:", "Your money picture:")]
    if inc is not None:
        out.append(say("महीने की कमाई: ", "Income per month: ") + ledger.money(inc))
    if today:
        sp, left_days = _month(c, dev, today)
        out.append(say("इस महीने खर्चा (अब तक): ", "Spent this month so far: ") + ledger.money(sp))
        if inc is not None:
            left = inc - sp
            out.append(say("कमाई में से बचा: ", "Left from income: ") + (ledger.money(left) if left >= 0 else say("खर्चा कमाई से ", "over by ") + ledger.money(-left)))
            if left > 0 and left_days > 0:
                out.append(say(f"बचे {left_days} दिन में रोज़ करीब ", f"For the {left_days} days left, about ") + ledger.money(round(left / left_days)) + say(" तक", " a day"))
    if sav is not None:
        out.append(say("कुल बचत: ", "Savings in total: ") + ledger.money(sav))
    out.append(say(*SIMPLE))
    return "\n".join(out)


def whatif(c, dev, now, hindi):
    say = lambda hi, en: hi if hindi else en
    today = spend._day(now)
    sav = get(c, dev, "savings")
    if not today:
        return say("सर, फ़ोन का समय नहीं पढ़ पाया।", "Sir, I could not read the phone time.")
    if sav is None:
        return say("सर, पहले बचत बताइए। जैसे: bachat 50000", "Sir, tell me your savings first. For example: bachat 50000")
    since = (datetime.date.fromisoformat(today) - datetime.timedelta(days=29)).isoformat()
    m = spend._sum(c, dev, since, today)
    days = c.execute("SELECT count(DISTINCT day) FROM spend WHERE device=? AND day>=? AND day<=?", (dev, since, today)).fetchone()[0]
    if m <= 0:
        return say("सर, पिछले 30 दिन का कोई खर्चा नहीं लिखा, इसलिए हिसाब नहीं लगा सकता। जैसे लिखिए: 200 coffee", "Sir, no spending noted in the last 30 days, so I cannot work it out. Try: 200 coffee")
    n = sav / m
    out = [say(f"अगर कमाई रुक जाए: बचत {ledger.money(sav)}, पिछले 30 दिन का खर्चा {ledger.money(m)}, तो करीब {n:.1f} महीने चलेगा।",
               f"If income stops: savings {ledger.money(sav)}, spending of the last 30 days {ledger.money(m)}, so about {n:.1f} months."),
           say("इसमें वो खर्चे नहीं हैं जो आपने लिखे नहीं (किराया, बिल, EMI...)।", "It leaves out anything you did not note (rent, bills, EMI...).")]
    if days < 7:
        out.append(say(f"खर्चा सिर्फ़ {days} दिन का लिखा है, इसलिए यह मोटा अंदाज़ा है।", f"Spending is noted for only {days} day{'s' if days != 1 else ''}, so this is rough."))
    out.append(say(*SIMPLE))
    return "\n".join(out)


def handle(c, dev, msg, hindi, now):
    if len(msg) > 60:
        return None
    say = lambda hi, en: hi if hindi else en
    m = DEL.match(msg)
    if m:
        kind = "income" if m.group(1).lower() in ("kamai", "income") else "savings"
        k = c.execute("DELETE FROM money WHERE device=? AND kind=?", (dev, kind)).rowcount
        c.commit()
        return say("ठीक है, हटा दिया।", "Okay, removed.") if k else say("सर, यह सेव नहीं था।", "Sir, that was not saved.")
    for rx, kind in ((INC, "income"), (SAV, "savings")):
        m = rx.match(msg)
        if m:
            v = _amt(m.groups())
            if v is None:
                return say("सर, नंबर समझ नहीं आया। जैसे: kamai 40000 mahina", "Sir, I could not read that number. Try: kamai 40000 mahina")
            _set(c, dev, kind, v)
            return (say("कमाई लिख ली: ", "Income noted: ") + ledger.money(v) + say(" महीना।", " per month.")) if kind == "income" else (say("बचत लिख ली: ", "Savings noted: ") + ledger.money(v) + ".")
    if PIC.match(msg):
        return picture(c, dev, now, hindi)
    if WHATIF.match(msg):
        return whatif(c, dev, now, hindi)
    return None


def line(c, dev, now, hindi):
    """One briefing line (as a list) only when you gave an income: what is left this month."""
    today, inc = spend._day(now), get(c, dev, "income")
    if not today or inc is None:
        return []
    sp, _ = _month(c, dev, today)
    left = inc - sp
    return [(f"- इस महीने कमाई में से {ledger.money(left)} बचा है" if left >= 0 else f"- इस महीने खर्चा कमाई से {ledger.money(-left)} ज़्यादा है") if hindi else
            (f"- {ledger.money(left)} left from this month's income" if left >= 0 else f"- Spending is {ledger.money(-left)} over this month's income")]
