"""Part 84: quick expense logger. "200 coffee", "kharcha 50 auto", "50 rupaye auto mein diye", "spent 300 on petrol".
Today, this week and this month in numbers, with a simple category from a short word list (no AI). "kharcha" shows the totals, "kharcha hatao" removes the last entry.
This is NOT the owe/get ledger (ledger.py): it is only what you spent. Same database, one small table. Never sent to the AI. Max 3000 entries."""
import datetime
import re

import ledger
import notes

AMT = r"(?:₹|rs\.?\s*|inr\s*)?(\d{1,7}(?:\.\d{1,2})?)\s*(?:₹|rs\b\.?|rupaye|rupees?|rupay|रुपये|रुपए)?"
LOG1 = re.compile(r"^\s*(?:kharcha|kharch|spent|spend|expense|खर्चा|खर्च)\s+" + AMT + r"\s*(?:on|ka|ki|ke|pe|par|mein|me|में|पर)?\s*(.{2,30}?)\s*$", re.I)
LOG2 = re.compile(r"^\s*" + AMT + r"\s*(?:ka|ki|ke)?\s*(.{2,30}?)\s+(?:(?:mein|me|pe|par|ka|ki|ke)\s+)?(?:de\s+diye|de\s+diya|diye|diya|kharch\s+kiya|kharch|kharcha|spent|lag\s+gaye|lage|laga|gaye|gaya|दिए|दिया|खर्च)\s*$", re.I)
BARE = re.compile(r"^\s*(?:₹|rs\.?\s*)?(\d{2,7}(?:\.\d{1,2})?)\s+([A-Za-z\u0900-\u097F]{2,20}(?:\s[A-Za-z\u0900-\u097F]{2,20})?)\s*$", re.I)
STOP = {"baje", "bje", "बजे", "minute", "minutes", "min", "mins", "sec", "second", "seconds", "din", "days", "day", "hour", "hours", "ghante", "ghanta", "saal", "year", "years", "mahine", "month", "months", "week", "weeks", "kg", "gram", "km", "percent", "number", "baar", "times", "log", "people", "baad", "am", "pm", "tareekh", "date", "se", "tak", "to", "ko", "ka", "ki", "ke", "hai", "hain", "tha", "thi"}
SHOW = re.compile(r"^\s*(?:(aaj|today|आज)\s+ka\s+|(?:is\s+hafte|this\s+week|weekly?|hafte)\s+ka\s+|(?:is\s+mahine|this\s+month|monthly?|mahine)\s+ka\s+)?(?:kharcha|kharch|expenses?|spending|खर्चा|खर्च)(?:\s+(?:dikhao|batao|summary|report|total|kitna(?:\s+hua)?))?\s*\??\s*$|^\s*kitna\s+kharcha(?:\s+hua)?\s*\??\s*$", re.I)
UNDO = re.compile(r"^\s*(?:(?:last\s+)?(?:kharcha|expense)\s+(?:hatao|delete|undo|remove)|undo\s+(?:kharcha|expense))(?:\s+#?(\d+))?\s*$", re.I)
CATS = {"food": "coffee chai tea lunch dinner breakfast khana nashta samosa pizza burger biryani juice snack snacks maggi lassi icecream paratha roti mithai",
        "travel": "auto uber ola cab bus metro train petrol diesel ticket rickshaw parking fuel toll",
        "bills": "recharge bijli bill rent wifi internet gas emi",
        "health": "dawai dawa medicine doctor",
        "shopping": "shopping kapde cloth clothes grocery sabzi doodh phal fruits"}
MAX_ROWS = 3000


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS spend(id INTEGER PRIMARY KEY, device INT, amount REAL, what TEXT, cat TEXT, day TEXT)")


def category(what):
    words = set(re.findall(r"[a-z]+", what.lower()))
    return next((k for k, v in CATS.items() if words & set(v.split())), "other")


def _day(now):
    d = str(now)[:10]
    try:
        datetime.date.fromisoformat(d)
        return d
    except ValueError:
        return None


def _sum(c, dev, since, until):
    return c.execute("SELECT COALESCE(SUM(amount),0) FROM spend WHERE device=? AND day>=? AND day<=?", (dev, since, until)).fetchone()[0]


def _ranges(today):
    d = datetime.date.fromisoformat(today)
    return today, (d - datetime.timedelta(days=6)).isoformat(), d.replace(day=1).isoformat()


def week_total(c, dev, now):
    """Spent in the last 7 days (today included) and today, for the briefing and the day summary. (0, 0) if the phone time is unreadable."""
    t = _day(now)
    if not t:
        return 0, 0
    today, wk, _ = _ranges(t)
    return _sum(c, dev, wk, today), _sum(c, dev, today, today)


def _text(c, dev, now, hindi):
    say = lambda hi, en: hi if hindi else en
    today, wk, mo = _ranges(_day(now))
    t, w, m = _sum(c, dev, today, today), _sum(c, dev, wk, today), _sum(c, dev, mo, today)
    if not w and not m:
        return say("सर, अभी कोई खर्चा नहीं लिखा। जैसे: 200 coffee", "Sir, no spending noted yet. Try: 200 coffee")
    out = [say("सर, आपका खर्चा:", "Sir, your spending:"), f"- {say('आज', 'Today')}: {ledger.money(t)}", f"- {say('7 दिन', 'Last 7 days')}: {ledger.money(w)}", f"- {say('इस महीने', 'This month')}: {ledger.money(m)}"]
    cats = c.execute("SELECT cat, SUM(amount) FROM spend WHERE device=? AND day>=? AND day<=? GROUP BY cat ORDER BY 2 DESC", (dev, wk, today)).fetchall()
    if cats:
        out.append(say("7 दिन, किस पर:", "Last 7 days, on what:") + " " + ", ".join(f"{k} {ledger.money(v)}" for k, v in cats))
    last = c.execute("SELECT id, amount, what, day FROM spend WHERE device=? ORDER BY id DESC LIMIT 3", (dev,)).fetchall()
    out.append(say("आख़िरी:", "Latest:") + " " + ", ".join(f"#{i} {ledger.money(a)} {x}" for i, a, x, _ in last))
    return "\n".join(out)


def handle(c, dev, msg, hindi, now):
    """Reply text for an expense command, else None (so the normal chat pipeline goes on)."""
    m = re.sub(r"\s+", " ", msg.strip())
    if len(m) > 80:
        return None
    say = lambda hi, en: hi if hindi else en
    day = _day(now)
    u = UNDO.match(m)
    if u:
        row = c.execute("SELECT id, amount, what FROM spend WHERE device=? " + ("AND id=?" if u.group(1) else "") + " ORDER BY id DESC LIMIT 1", (dev, int(u.group(1))) if u.group(1) else (dev,)).fetchone()
        if not row:
            return say("सर, ऐसी कोई एंट्री नहीं मिली।", "Sir, I found no such entry.")
        c.execute("DELETE FROM spend WHERE id=? AND device=?", (row[0], dev))
        c.commit()
        return say(f"ठीक है सर, #{row[0]} {ledger.money(row[1])} {row[2]} हटा दिया।", f"Okay sir, removed #{row[0]} {ledger.money(row[1])} {row[2]}.")
    if SHOW.match(m):
        return _text(c, dev, now, hindi) if day else None
    g = LOG1.match(m) or LOG2.match(m)
    if not g:
        b = BARE.match(m)
        g = b if b and float(b.group(1)) >= 10 and not (set(b.group(2).lower().split()) & STOP) else None
    if not g or not day:
        return None
    amount, what = float(g.group(1)), re.sub(r"\s+(?:mein|me|pe|par|ka|ki|ke|on)$", "", g.group(2).strip().lower())
    if not (0 < amount <= 1000000) or len(what) < 2:
        return None
    if notes.SECRET.search(what):
        return say("सर, ये नहीं सहेजूँगा।", "Sir, I will not save that.")
    if c.execute("SELECT count(*) FROM spend WHERE device=?", (dev,)).fetchone()[0] >= MAX_ROWS:
        return say("सर, खर्चे की सूची भर गई (3000)।", "Sir, the spending list is full (3000 entries).")
    i = c.execute("INSERT INTO spend(device, amount, what, cat, day) VALUES(?,?,?,?,?)", (dev, amount, what, category(what), day)).lastrowid
    w, t = week_total(c, dev, now)
    return say(f"लिख लिया सर: #{i} {ledger.money(amount)} {what} ({category(what)}). आज {ledger.money(t)}, 7 दिन {ledger.money(w)}। हटाने के लिए: kharcha hatao",
               f"Noted, sir: #{i} {ledger.money(amount)} {what} ({category(what)}). Today {ledger.money(t)}, 7 days {ledger.money(w)}. To remove: kharcha hatao")
