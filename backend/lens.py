"""Part 85 and 86: Context Lens. ONE card "your next best move" (Do, Why, Later) and a Now / Next / Later strip under it.
Everything comes from Jarvis's own tables (reminders, routines, money ledger, birthdays, habits) and the phone's battery. Fixed rules, no AI.
Nothing is saved and nothing is run: the Show button only types a command you could say yourself, and you tap it."""
import time

import habits, ledger, progress, remind

SOON = 60  # minutes: "now" means late or inside the next hour
SRC = {"rem": "Reminder", "rou": "Routine", "led": "Money", "bd": "Birthday", "hab": "Habit", "ph": "Phone", "proj": "Project"}
LENSES = ("all", "project", "phone", "life")  # Part 120: the chips on Home. all = Phone + Life (old behaviour); Project is shown only when you pick it


def _hm(t):
    return time.strftime("%H:%M", time.gmtime(t))


def _item(src, score, col, text, why, cmd, at=""):
    return {"src": SRC[src], "score": score, "col": col, "text": text, "why": why, "cmd": cmd, "at": at}


def _reminders(c, dev, n, start):
    out = []
    for text, due in c.execute("SELECT text, due FROM reminders WHERE device=? AND sent=0 AND due<? ORDER BY due", (dev, start + 2 * 86400)).fetchall():
        m = int((due - n) // 60)
        if m <= 0:
            out.append(_item("rem", 10, "now", text, f"Its time was {_hm(due)} and you were not told yet", "my reminders", _hm(due)))
        elif m <= SOON:
            out.append(_item("rem", 20, "now", text, f"In {m} minutes", "my reminders", _hm(due)))
        elif due < start + 86400:
            out.append(_item("rem", 80 + m / 1440, "next", text, f"Today at {_hm(due)}", "my reminders", _hm(due)))
        else:
            out.append(_item("rem", 200 + m / 2880, "later", text, f"Tomorrow at {_hm(due)}", "my reminders", "tmrw " + _hm(due)))
    return out


def _routines(c, dev, n, start):
    out, now_m, wd = [], int(n % 86400 // 60), time.gmtime(n).tm_wday
    for name, at, dy in c.execute("SELECT name, at, days FROM routines WHERE device=? AND at<>'' ORDER BY at", (dev,)).fetchall():
        if (dy == "wk" and wd >= 5) or (dy == "we" and wd < 5):
            continue
        d = int(at[:2]) * 60 + int(at[3:]) - now_m
        if 0 <= d <= SOON:
            out.append(_item("rou", 25, "now", f"Routine {name}", f"Starts in {d} minutes. You tap Run yourself", "routine " + name, at))
        elif d > SOON:
            out.append(_item("rou", 85 + d / 1440, "next", f"Routine {name}", f"Today at {at}", "routine " + name, at))
    return out


def _money(c, dev, day, soon):
    out = []
    for i, who, a, dr, due in ledger.rows(c, dev):
        if not due:
            continue
        txt = ledger.line(i, who, a, dr, due)
        if due < day:
            out.append(_item("led", 30, "now", txt, "This is late", "show ledger"))
        elif due == day:
            out.append(_item("led", 40, "now", txt, "Due today", "show ledger"))
        elif due <= soon:
            out.append(_item("led", 210, "later", txt, "Due in the next 2 days", "show ledger"))
    return out


def _people(c, dev, n):
    return [_item("bd", 35 if k == 0 else 220, "now" if k == 0 else "later", t.replace("🎂", "").strip(), "Birthday today" if k == 0 else f"Birthday on {on}", "my reminders") for k, t, on in remind.birthdays(c, dev, n, 3)]


def _habits(c, dev, now, evening):
    today, out = habits._today(now), []
    for name in habits._names(c, dev) if today else []:
        ds = habits._days(c, dev, name)
        if today in ds:
            continue
        k = habits.streak(ds, today)
        why = f"{k} day streak, keep it going" if k else "Not done yet today"
        out.append(_item("hab", 50 if evening else 90, "now" if evening else "next", name, why, "my habits"))
    return out


def _phone(ph):
    b = ph.get("battery") if isinstance(ph, dict) else None
    if not isinstance(b, (int, float)) or isinstance(b, bool) or ph.get("charging") or b > 19:
        return []
    if b <= 15:
        return [_item("ph", 5, "now", f"Battery is {b:.0f}%, plug in the charger", "It is not charging and it is low", "phone doctor")]
    return [_item("ph", 45, "now", f"Battery is {b:.0f}%, plug in the charger", "It is not charging", "battery settings kholo")]


def _project():
    """Part 120: Project lens. Two honest counts from the README (Part 87 numbers), nothing invented. Only shown with the Project chip."""
    m = progress.mission()
    if not m:
        return []
    out, tried = [], m.get("ok", 0) + m.get("fail", 0)
    if m.get("tests", 0) > tried:
        out.append(_item("proj", 20, "now", f"{m['tests'] - tried} of {m['tests']} phone tests not tried yet", "Built is not the same as tested", "mission"))
    left = m.get("built", 0) - m.get("tested", 0) - m.get("partly", 0)
    if left > 0:
        out.append(_item("proj", 60, "next", f"{left} built Parts are not tried on the phone", "Table A in the README lists the steps", "mission"))
    if m.get("planned", 0):
        out.append(_item("proj", 150, "later", f"{m['planned']} Parts are still planned", "The next one is in the README", "mission"))
    return out


def build(c, dev, now, ph=None, lens="all"):
    """{"card": {...} or None, "strip": {"now": [...], "next": [...], "later": [...]}}. Lower score = more urgent."""
    empty = {"card": None, "strip": {"now": [], "next": [], "later": []}}
    try:
        n = remind.tm(now)
    except ValueError:
        return empty
    start, day = n - n % 86400, str(now)[:10]
    soon = time.strftime("%Y-%m-%d", time.gmtime(n + 2 * 86400))
    lens = lens if lens in LENSES else "all"
    life = (_reminders(c, dev, n, start) + _routines(c, dev, n, start) + _money(c, dev, day, soon)
            + _people(c, dev, n) + _habits(c, dev, now, n % 86400 >= 18 * 3600))
    items = {"all": _phone(ph) + life, "phone": _phone(ph), "life": life, "project": _project()}[lens]  # Part 120: the chip filters the card AND the strip
    items.sort(key=lambda x: x["score"])
    if not items:
        return empty
    top, nxt = items[0], items[1] if len(items) > 1 else None
    later = (f"{nxt['at'] + ' ' if nxt['at'] else ''}{nxt['text']} ({nxt['src']})")[:90] if nxt else ""
    card = {"src": top["src"], "do": top["text"][:120], "why": top["why"], "later": later, "cmd": top["cmd"]}
    strip = {}
    for col in ("now", "next", "later"):
        rows = [x for x in items if x["col"] == col]
        strip[col] = [{"at": x["at"], "text": x["text"][:60], "src": x["src"]} for x in rows[:3]] + ([{"at": "", "text": f"+{len(rows) - 3} more", "src": ""}] if len(rows) > 3 else [])
    return {"card": card, "strip": strip}
