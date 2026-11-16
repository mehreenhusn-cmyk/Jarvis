"""Jarvis subah ka briefing (Part 14): aaj ke reminders + paas ki tareekh wale hisab. Seedha database se, AI ki zaroorat nahi.
Part 45: phone calendar ke events (sirf jab aap khud 'briefing' likhein), sujhav (suggestions): har din ke 3 se zyada nahi, quiet hours mein
apne aap nahi, har type alag band ho sakta hai. Settings brief.json mein (restart ke baad bhi rehti hain)."""
import json, os, re, time

import ledger, phone, remind

TRIG = re.compile(r"briefing|brief karo|aaj ka plan|aaj kya hai|my plan today|good morning jarvis|ब्रीफिंग|सुप्रभात", re.I)
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brief.json")
RULES = ("money", "birthday", "tomorrow")
ONOFF = r"(on|off|band|chalu|bandh)"
SET_ALL = re.compile(r"^\s*(?:suggestions?|sujhav)\s+" + ONOFF + r"\s*$", re.I)
SET_ONE = re.compile(r"^\s*(money|birthday|tomorrow)\s+suggestions?\s+" + ONOFF + r"\s*$", re.I)
SET_Q = re.compile(r"^\s*quiet hours?\s+(\d{1,2})\s*(?:to|-|se)\s*(\d{1,2})\s*$", re.I)
WEEK = re.compile(r"^\s*(?:weekly summary|week(?:ly)? report|(?:is )?hafte ka (?:summary|hisab)|साप्ताहिक सारांश)\s*$", re.I)  # Part 80
SHOW = re.compile(r"^\s*(?:briefing|suggestions?)\s+settings?\s*$", re.I)


def load():
    """Saved settings. File missing ya kharab ho to defaults."""
    try:
        d = json.load(open(FILE, encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    d = d if isinstance(d, dict) else {}
    r = d.get("rules") if isinstance(d.get("rules"), dict) else {}
    q = d.get("quiet") if isinstance(d.get("quiet"), list) and len(d.get("quiet")) == 2 else [22, 7]
    try:
        q = [max(0, min(23, int(q[0]))), max(0, min(23, int(q[1])))]
    except (TypeError, ValueError):
        q = [22, 7]
    return {"on": d.get("on") is not False, "rules": {k: r.get(k) is not False for k in RULES}, "quiet": q,
            "day": str(d.get("day", "")), "shown": d.get("shown") if isinstance(d.get("shown"), int) else 0}


def save(s):
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f)
    os.replace(tmp, FILE)


def quiet(s, hour):
    a, b = s["quiet"]
    return a != b and (a <= hour < b if a < b else hour >= a or hour < b)


def suggest(c, dev, n, hindi, s, auto):
    """Sujhav ki lines. Din ke 3 se zyada nahi (manual aur auto dono mila kar). Auto mein quiet hours ka dhyan."""
    day = time.strftime("%Y-%m-%d", time.gmtime(n))
    if s["day"] != day:
        s["day"], s["shown"] = day, 0
    room = 3 - s["shown"]
    if not s["on"] or room <= 0 or (auto and quiet(s, time.gmtime(n).tm_hour)):
        return []
    say = (lambda hi, ro: hi if hindi else ro)
    out, start = [], n - n % 86400
    if s["rules"]["money"]:
        late = [x for x in ledger.rows(c, dev) if x[4] and x[4] < day]
        if late:
            out.append(say(f"{len(late)} हिसाब की तारीख़ निकल चुकी है। 'show ledger' देखिए।", f"{len(late)} ledger entries are past their date. Say 'show ledger'."))
    if s["rules"]["birthday"]:
        out += [f"{t} - {on}" for k, t, on in remind.birthdays(c, dev, n, 4) if k >= 1]  # Part 75: same helper as Home, no duplicate SQL
    if s["rules"]["tomorrow"]:
        k = c.execute("SELECT count(*) FROM reminders WHERE device=? AND sent=0 AND due>=? AND due<?", (dev, start + 86400, start + 2 * 86400)).fetchone()[0]
        if k:
            out.append(say(f"कल {k} रिमाइंडर हैं।", f"Tomorrow you have {k} reminder(s)."))
    out = out[:room]
    s["shown"] += len(out)
    save(s)
    return out


def events(cal, hindi):
    """Calendar ke aaj ke events ki lines (app se aaye, kuch save nahi hota)."""
    if not isinstance(cal, list):
        return []
    out = []
    for e in [e for e in cal if isinstance(e, dict)][:8]:
        t = time.gmtime if e.get("allDay") else time.localtime
        hm = ("पूरा दिन" if hindi else "all day") if e.get("allDay") else time.strftime("%H:%M", t(int(e.get("begin", 0)) / 1000))
        out.append(f"- {hm} {str(e.get('title') or '(no title)')[:50]}")
    return out


def build(c, dev, now, hindi, auto=False, cal=None, ph=None):
    """Text lautata hai. auto=True aur kuch na ho to '' (page ko chup rehna hai)."""
    try:
        n = remind.tm(now)
    except ValueError:
        return ""
    end = n - n % 86400 + 86400
    rem = c.execute("SELECT text, due FROM reminders WHERE device=? AND sent=0 AND due<? ORDER BY due", (dev, end)).fetchall()
    L = ledger.rows(c, dev)
    soon = time.strftime("%Y-%m-%d", time.gmtime(n + 2 * 86400))
    near = [x for x in L if x[4] and x[4] <= soon]
    ev = events(cal, hindi)
    sug = suggest(c, dev, n, hindi, load(), auto)
    bd = [(t, k, on) for k, t, on in remind.birthdays(c, dev, n, 3)]  # Part 75: janamdin aaj se 3 din tak
    nt = [] if auto else [r[0][:80] for r in c.execute("SELECT text FROM notes WHERE device=? ORDER BY id DESC LIMIT 2", (dev,))]  # latest notes: sirf jab aap khud briefing maangein
    pw = [f"{x} {y}" for x, y in phone.analyze(ph, hindi)[:2]] if isinstance(ph, dict) else []  # Part 80: phone problems (battery, storage, heat...) in the briefing, only when there is one
    if not rem and not near and not ev and not sug and not pw and not any(k == 0 for _, k, _ in bd) and auto:
        return ""
    say = (lambda hi, ro: hi if hindi else ro)
    out = [say("सुप्रभात सर।", "Suprabhat sir.") + " " + time.strftime("%d %b", time.gmtime(n))]
    if ev:
        out.append(say("आज का कैलेंडर:", "Today's calendar:"))
        out += ev
    if rem:
        out.append(say("आज के रिमाइंडर:", "Today's reminders:"))
        out += [f"- {time.strftime('%H:%M', time.gmtime(d))} {t}" for t, d in rem]
    if near:
        out.append(say("पास की तारीख़ वाला हिसाब:", "Paas ki tareekh wala hisab:"))
        out += ["- " + ledger.line(*x) for x in near]
    if L:
        dn, ln = ledger.totals(L)
        out.append(f"{say('कुल देना', 'You owe')}: {ledger.money(dn)} | {say('कुल लेना', 'You get')}: {ledger.money(ln)}")
    if bd:
        out.append(say("जन्मदिन:", "Birthdays:"))
        out += [f"- {t} - " + (say("आज", "today") if k == 0 else on) for t, k, on in bd]
    if nt:
        out.append(say("ताज़ा नोट्स:", "Latest notes:"))
        out += [f"- {x}" for x in nt]
    if not rem and not near and not ev and not bd and not pw:
        out.append(say("आज कुछ ज़रूरी बाकी नहीं है।", "Nothing important is pending today."))
    if pw:
        out.append(say("फ़ोन:", "Phone:"))
        out += ["- " + x for x in pw]
    if sug:
        out.append(say("सुझाव:", "Suggestions:"))
        out += ["- " + x for x in sug]
    return "\n".join(out)


def weekly(c, dev, now, hindi):
    """Part 80: last 7 days in numbers, from the tables Jarvis already has. Nothing new is saved."""
    try:
        n = remind.tm(now)
    except ValueError:
        return ""
    say = (lambda hi, ro: hi if hindi else ro)
    real = time.time() - 7 * 86400
    rem = c.execute("SELECT count(*) FROM reminders WHERE device=? AND sent=1 AND rep='' AND text NOT LIKE '🎂%' AND due>=? AND due<=?", (dev, n - 7 * 86400, n)).fetchone()[0]
    nts = c.execute("SELECT count(*) FROM notes WHERE device=? AND ts>=?", (dev, real)).fetchone()[0]
    tk = dict(c.execute("SELECT state, count(*) FROM tasks WHERE device=? AND ts>=? GROUP BY state", (dev, real)).fetchall())
    L = ledger.rows(c, dev)
    late = len([x for x in L if x[4] and x[4] < time.strftime("%Y-%m-%d", time.gmtime(n))])
    bd = remind.birthdays(c, dev, n, 7)
    out = [say("पिछले 7 दिन:", "Last 7 days:"),
           f"- {say('रिमाइंडर बताए गए', 'Reminders told')}: {rem}",
           f"- {say('फ़ोन टास्क/रूटीन पूरे', 'Phone tasks/routines completed')}: {tk.get('COMPLETED', 0)} ({say('अधूरे/फ़ेल', 'partial/failed')}: {tk.get('PARTIAL', 0) + tk.get('FAILED', 0)})",
           f"- {say('नोट्स सेव', 'Notes saved')}: {nts}",
           f"- {say('खुला हिसाब', 'Open ledger entries')}: {len(L)} ({say('तारीख़ निकली', 'past date')}: {late})"]
    if bd:
        out.append(f"- {say('आने वाले जन्मदिन (7 दिन)', 'Birthdays in the next 7 days')}: " + ", ".join(f"{t.replace('🎂 ', '')} ({on})" for _, t, on in bd))
    return "\n".join(out)


def settings(msg, hindi):
    """'suggestions off', 'birthday suggestions off', 'quiet hours 22 to 7', 'briefing settings'. Na samjhe to None."""
    s = load()
    say = (lambda hi, ro: hi if hindi else ro)
    m, o, q = SET_ALL.match(msg), SET_ONE.match(msg), SET_Q.match(msg)
    if m:
        s["on"] = m.group(1).lower() in ("on", "chalu")
        save(s)
        return say("ठीक है सर, सुझाव चालू।", "Okay sir, suggestions are ON.") if s["on"] else say("ठीक है सर, सुझाव बंद।", "Okay sir, suggestions are OFF.")
    if o:
        s["rules"][o.group(1).lower()] = o.group(2).lower() in ("on", "chalu")
        save(s)
        return f"Okay sir, {o.group(1).lower()} suggestions: " + ("ON." if s["rules"][o.group(1).lower()] else "OFF.")
    if q:
        a, b = int(q.group(1)), int(q.group(2))
        if a > 23 or b > 23:
            return say("सर, घंटा 0 से 23 के बीच बताइए।", "Sir, use hours from 0 to 23, for example: quiet hours 22 to 7")
        s["quiet"] = [a, b]
        save(s)
        return f"Okay sir, no automatic suggestions from {a}:00 to {b}:00." if a != b else "Okay sir, quiet hours are OFF."
    if SHOW.match(msg):
        r = ", ".join(f"{k} {'ON' if v else 'OFF'}" for k, v in s["rules"].items())
        return f"Suggestions: {'ON' if s['on'] else 'OFF'} ({r}). Max 3 a day. Quiet hours: {s['quiet'][0]}:00 to {s['quiet'][1]}:00 (only automatic ones wait)."
    return None


def handle(c, dev, msg, hindi, now, cal=None, ph=None):
    r = settings(msg, hindi) if len(msg) < 50 else None
    if r:
        return r
    if WEEK.match(msg):
        return weekly(c, dev, now, hindi) or None
    return build(c, dev, now, hindi, False, cal, ph) if TRIG.search(msg) and len(msg) < 50 else None
