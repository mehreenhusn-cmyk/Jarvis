"""Jarvis task engine (Part 41): "Chrome kholo aur neeche scroll karo phir back jao" becomes ONE tracked task with steps.
The server only PLANS (it splits your own words into steps from the fixed action list) and KEEPS THE RECORD. The steps run in the app (Java),
which checks Stop, the phone-control switch and the app lock before every step and checks that each step really did something.
A step that needs your Yes (send, pay, delete, ...) or that types text is never put in a task: those stay one-by-one, with your own tap.
Part 46: a ROUTINE is a name for a task sentence you saved ("routine banao subah: Chrome kholo aur neeche scroll karo"). Running it plans the sentence again
through make(), so every rule above (switch, app only, Stop, no send/pay/delete/typing, lock only last) is checked again on every run."""
import json, re, time

import actions
import lang

STATES = ("CREATED", "PLANNING", "WAITING_FOR_PERMISSION", "WAITING_FOR_CONFIRMATION", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED")
END = ("COMPLETED", "PARTIAL", "FAILED", "CANCELLED")
OK_STEPS = ("open_app", "back", "home", "scroll", "click", "torch", "volume", "settings", "current_app", "lock")
MAX_STEPS = 6
STALE = 600  # a RUNNING task with no news for 10 minutes is dead (app killed or phone restarted)
SPLIT = re.compile(r"\s*(?:,|;|\band then\b|\bthen\b|\band\b|\bphir\b|\bfir\b|\baur\b|\buske baad\b|\bfir se\b|\bn\b|एंड|ऐंड|(?<!\S)(?:अने|आणि|मत्तु|मरियु|मर्रुम|अते|एबं)(?!\S)|फिर|और|उसके बाद)\s*", re.I)
TYPEWORD = re.compile(r"\b(?:type|likho|likh)\b|टाइप|लिखो", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, device INT, title TEXT, steps TEXT, state TEXT, cur INT DEFAULT 0, note TEXT DEFAULT '', ts REAL, upd REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS routines(id INTEGER PRIMARY KEY, device INT, name TEXT, phrase TEXT, ts REAL)")
    for col in ("at", "last"):  # Part 76: routine ka time (HH:MM, phone ka) aur kis din aakhri baar bataya; purani table mein sirf 2 naye column
        if col not in [r[1] for r in c.execute("PRAGMA table_info(routines)")]:
            c.execute(f"ALTER TABLE routines ADD COLUMN {col} TEXT DEFAULT ''")
    c.commit()


def restart(c):
    """Restart rule, called ONCE when the server starts: nothing can still be running, so RUNNING and VERIFYING tasks become FAILED with a note."""
    return sweep(c, 0)


def sweep(c, age=STALE):
    """RUNNING or VERIFYING tasks with no news for `age` seconds become FAILED with a note. age=0: all of them (server restart)."""
    now = time.time()
    n = c.execute("UPDATE tasks SET state='FAILED', note='Jarvis or the phone restarted while this task was running', upd=? "
                  "WHERE state IN ('RUNNING','VERIFYING') AND upd<=?", (now, now - age)).rowcount
    c.commit()
    return n


def _no_ai(*a, **k):
    raise RuntimeError("no AI inside a task plan")


def split(msg):
    """The message cut into step phrases, or [] if it is not a multi-step command."""
    m = lang.norm((msg or "").strip())  # Part 63: other Indian languages are read as Devanagari
    if not m or "?" in m or len(m) > 220 or TYPEWORD.search(m):
        return []
    parts = [p.strip() for p in SPLIT.split(m) if p and p.strip()]
    return parts if 2 <= len(parts) <= MAX_STEPS else []


def make(c, dev, msg, hindi, control, in_app, dry=False):
    """None = not a task (normal chat or single command). Else (reply text, action dict). The action {"type":"task",...} is run by the app."""
    say = lambda hi, en: hi if hindi else en
    parts = split(msg)
    if not parts:
        return None
    steps, texts, refused = [], [], False
    for p in parts:
        got = actions.handle(p, hindi, True, True, _no_ai)  # grammar only, the AI is never asked inside a task
        if not got:
            return None  # one piece is not a phone command, so this is normal talk
        text, act = got
        if act and act.get("type") == "call":  # Part 64: a call is never one step of a task, it is said on its own
            return say("सर, कॉल किसी काम का कदम नहीं बन सकता। कॉल अकेले बोलिए, जैसे \"अम्मी को कॉल करो\"। मैंने कुछ नहीं किया।",
                       "Sir, a call cannot be a step in a task. Please say the call on its own, like \"call Ammi\". I did nothing."), None
        if act and act.get("type") in ("alarm", "timer", "search", "media"):  # Part 66 and Part 60: said on their own, never a step of a task
            return say("सर, अलार्म, टाइमर और ऐप में सर्च किसी काम का कदम नहीं बनते। इन्हें अकेले बोलिए। मैंने कुछ नहीं किया।",
                       "Sir, an alarm, a timer or a search inside an app cannot be a step in a task. Please say it on its own. I did nothing."), None
        if not act or act.get("type") not in OK_STEPS:
            refused = True  # blocked (password, OTP...), needs a Yes, or not allowed in a task
            continue
        steps.append({k: act[k] for k in ("type", "name", "dir", "page", "on", "said") if k in act})
        texts.append(text)
    if refused:
        return say("सर, इस काम में ऐसा कदम है जो आपकी हाँ माँगता है (भेजना, पैसे, डिलीट) या जो मैं नहीं करता (पासवर्ड, OTP)। इन्हें एक-एक करके बोलिए। मैंने कुछ नहीं किया।",
                   "Sir, this task has a step that needs your own Yes (send, pay, delete) or that I never do (passwords, OTPs). Please give those one at a time. I did nothing."), None
    if any(s["type"] == "lock" for s in steps[:-1]):
        return say("सर, फ़ोन लॉक सिर्फ़ आख़िरी कदम हो सकता है। मैंने कुछ नहीं किया।", "Sir, locking the phone can only be the last step. I did nothing."), None
    if dry:  # Part 46: only check that the sentence is a valid task; nothing is created
        return "", {"steps": steps, "texts": texts}
    if not in_app:
        return say("सर, फ़ोन कंट्रोल सिर्फ़ Jarvis ऐप में चलता है।", "Sir, phone control works only in the Jarvis Android app."), None
    if not control:
        return say("फ़ोन कंट्रोल बंद है सर। Settings में \"Phone control\" चालू कीजिए।", "Phone control is OFF, sir. Turn it on in Settings, under Phone control."), None
    now = time.time()
    cur = c.execute("INSERT INTO tasks(device, title, steps, state, cur, ts, upd) VALUES(?,?,?,?,?,?,?)",
                    (dev, msg.strip()[:120], json.dumps(steps), "CREATED", 0, now, now))
    c.commit()
    head = say(f"ठीक है सर, {len(steps)} कदम का काम:", f"Okay sir, a task with {len(steps)} steps:")
    return head + "\n" + "\n".join(f"{i + 1}. {t.rstrip('.')}" for i, t in enumerate(texts)), {"type": "task", "id": cur.lastrowid, "steps": steps, "texts": texts}


def update(c, dev, tid, state, cur=None, note=""):
    """The page tells the server how the task is going. A finished task never changes again. True if saved."""
    if state not in STATES:
        return False
    row = c.execute("SELECT state FROM tasks WHERE id=? AND device=?", (tid, dev)).fetchone()
    if not row or row[0] in END:
        return False
    c.execute("UPDATE tasks SET state=?, cur=COALESCE(?, cur), note=?, upd=? WHERE id=? AND device=?", (state, cur, str(note)[:200], time.time(), tid, dev))
    c.commit()
    return True


def finish(c, dev, tid, results, cancelled=False):
    """Final state from what the app really reported, step by step. Returns the state (or '' if the task is unknown or already finished)."""
    row = c.execute("SELECT steps, state FROM tasks WHERE id=? AND device=?", (tid, dev)).fetchone()
    if not row or row[1] in END:
        return ""
    total = len(json.loads(row[0]))
    res = [r for r in (results if isinstance(results, list) else []) if isinstance(r, dict)][:MAX_STEPS]
    good = sum(1 for r in res if r.get("ok") is True)
    bad = next((r for r in res if r.get("ok") is not True), None)
    state = "CANCELLED" if cancelled else "COMPLETED" if good == total else "FAILED" if good == 0 else "PARTIAL"
    note = "" if state == "COMPLETED" else ("cancelled by you" if cancelled else str((bad or {}).get("err") or "stopped"))[:60]
    c.execute("UPDATE tasks SET state=?, cur=?, note=?, upd=? WHERE id=? AND device=?", (state, good, note, time.time(), tid, dev))
    c.commit()
    return state


def recent(c, dev, n=5):
    sweep(c)
    rows = c.execute("SELECT id, title, state, cur, steps, note, ts FROM tasks WHERE device=? ORDER BY id DESC LIMIT ?", (dev, n)).fetchall()
    return [{"id": i, "title": t, "state": s, "done": k, "total": len(json.loads(st)), "note": nt, "ts": int(ts or 0)} for i, t, s, k, st, nt, ts in rows]


RSAVE = re.compile(r"^\s*(?:routine banao|save routine|new routine|routine save karo)\s+(.{1,30}?)\s*[:\-]\s*(.+)$", re.I | re.S)
RLIST = re.compile(r"^\s*(?:my\s+)?routines?(?:\s+list)?\s*\??\s*$", re.I)
RDEL = re.compile(r"^\s*(?:routine\s+(?:delete|hatao|remove)|(?:delete|remove)\s+routine)\s+(.{1,30}?)\s*$", re.I)
RRUN = (re.compile(r"^\s*(?:run routine|start routine|routine chalao|routine run)\s+(.{1,30}?)\s*$", re.I), re.compile(r"^\s*(.{1,30}?)\s+routine\s+(?:chalao|run|start)\s*$", re.I))
RPLAIN = re.compile(r"^\s*routine\s+(.{1,30}?)\s*$", re.I)


RTIME = re.compile(r"^\s*(?:schedule\s+)?routine\s+(.{1,30}?)(?:\s+(?:roz|rozana|daily|every\s*day|har\s*din|at))?(?:\s+(subah|savere|dopahar|shaam|raat))?\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm|baje|bje|बजे)?\s*(subah|savere|dopahar|shaam|raat)?\s*$", re.I)
RTOFF = re.compile(r"^\s*routine\s+(.{1,30}?)\s+(?:time\s+(?:hatao|band|off|remove)|no\s+time|unschedule)\s*$", re.I)


def _hour(h, w):
    w = (w or "").lower()
    if w in ("pm", "shaam"):
        return h + 12 if h < 12 else h
    if w == "dopahar":
        return h + 12 if 1 <= h <= 5 else h
    if w == "raat":
        return h + 12 if 6 <= h <= 11 else (0 if h == 12 else h)
    return 0 if (w == "am" and h == 12) else h


def due_routines(c, dev, now):
    """Part 76: jin routines ka time ho gaya (phone ke 'now' se). Din mein ek hi baar; 3 ghante se zyada late ho to chup rehta hai. Chalata nahi, sirf bataata hai (chalane ke liye aapka ek tap)."""
    day, hm = str(now)[:10], str(now)[11:16]
    if not re.fullmatch(r"\d{4}-\d\d-\d\d", day) or not re.fullmatch(r"\d\d:\d\d", hm):
        return []
    out, nm = [], int(hm[:2]) * 60 + int(hm[3:])
    for i, name, at in c.execute("SELECT id, name, at FROM routines WHERE device=? AND at<>'' AND at<=? AND last<>?", (dev, hm, day)).fetchall():
        c.execute("UPDATE routines SET last=? WHERE id=?", (day, i))
        if nm - (int(at[:2]) * 60 + int(at[3:])) <= 180:
            out.append({"name": name, "at": at})
    c.commit()
    return out


def scheduled(c, dev):
    return [{"name": n, "at": a} for n, a in c.execute("SELECT name, at FROM routines WHERE device=? AND at<>'' ORDER BY at", (dev,))]


def routine(c, dev, msg, hindi, control, in_app):
    """Part 46. None = not a routine command. Else (reply, action): the action is the same task action the app already runs."""
    say = lambda hi, en: hi if hindi else en
    m = RSAVE.match(msg)
    if m:
        name, phrase = m.group(1).strip().lower(), m.group(2).strip()[:220]
        got = make(c, dev, phrase, hindi, True, True, dry=True)
        if got is None:
            return say("सर, इसमें 2 से 6 फ़ोन-कदम चाहिए, \"और\" या \"फिर\" से जुड़े। जैसे: routine banao subah: Chrome kholo aur neeche scroll karo", "Sir, a routine needs 2 to 6 phone steps joined by \"aur\" or \"then\". Example: routine banao subah: Chrome kholo aur neeche scroll karo"), None
        if got[1] is None:
            return got  # refused (send, pay, delete, password, lock not last...): nothing saved
        n = c.execute("SELECT count(*) FROM routines WHERE device=? AND name<>?", (dev, name)).fetchone()[0]
        if n >= 10:
            return say("सर, 10 रूटीन की सीमा पूरी हो गई। एक हटाइए।", "Sir, the limit of 10 routines is full. Delete one first."), None
        c.execute("DELETE FROM routines WHERE device=? AND name=?", (dev, name))
        c.execute("INSERT INTO routines(device, name, phrase, ts) VALUES(?,?,?,?)", (dev, name, phrase, time.time()))
        c.commit()
        return say(f"ठीक है सर, रूटीन \"{name}\" सेव हो गया ({len(got[1]['steps'])} कदम)। चलाने के लिए: routine {name}", f"Okay sir, routine \"{name}\" saved ({len(got[1]['steps'])} steps). To run it say: routine {name}"), None
    if RLIST.match(msg):
        r = [(n + (f" ({a})" if a else ""), p) for n, p, a in c.execute("SELECT name, phrase, at FROM routines WHERE device=? ORDER BY id", (dev,)).fetchall()]
        if not r:
            return say("सर, कोई रूटीन सेव नहीं है। जैसे: routine banao subah: Chrome kholo aur neeche scroll karo", "Sir, no routines saved. Try: routine banao subah: Chrome kholo aur neeche scroll karo"), None
        return say("सर, ये रूटीन हैं:\n", "Sir, your routines:\n") + "\n".join(f"- {n}: {p}" for n, p in r), None
    m = RDEL.match(msg)
    if m:
        k = c.execute("DELETE FROM routines WHERE device=? AND name=?", (dev, m.group(1).strip().lower())).rowcount
        c.commit()
        return (say("ठीक है सर, रूटीन हटा दिया।", "Okay sir, routine removed.") if k else say("सर, ये रूटीन नहीं मिला।", "Sir, I did not find that routine.")), None
    m = RTOFF.match(msg)
    if m:
        k = c.execute("UPDATE routines SET at='' WHERE device=? AND name=?", (dev, m.group(1).strip().lower())).rowcount
        c.commit()
        return (say("ठीक है सर, इस रूटीन का समय हटा दिया।", "Okay sir, the time of this routine is removed.") if k else say("सर, ये रूटीन नहीं मिला।", "Sir, I did not find that routine.")), None
    m = RTIME.match(msg)
    if m:
        name, h, mi = m.group(1).strip().lower(), _hour(int(m.group(3)), m.group(2) or m.group(5) or m.group(6)), int(m.group(4) or 0)
        if h > 23 or mi > 59:
            return say("सर, समय समझ नहीं आया। जैसे: routine subah roz 7 baje", "Sir, I could not read that time. Example: routine subah roz 7 baje"), None
        k = c.execute("UPDATE routines SET at=?, last='' WHERE device=? AND name=?", (f"{h:02d}:{mi:02d}", dev, name)).rowcount
        c.commit()
        if not k:
            return say("सर, ये रूटीन नहीं मिला। \"my routines\" बोलिए।", "Sir, I did not find that routine. Say \"my routines\"."), None
        return say(f"ठीक है सर, रूटीन \"{name}\" रोज़ {h:02d}:{mi:02d} पर बताऊँगा, आपके एक टैप से चलेगा। (24 घंटे का समय है, ग़लत हो तो फिर बोलिए)", f"Okay sir, I will tell you every day at {h:02d}:{mi:02d} (24-hour clock) that routine \"{name}\" is due; it runs on your one tap. Wrong time? Say it again."), None
    name, explicit = None, True
    for rx in RRUN:
        m = rx.match(msg)
        if m:
            name = m.group(1).strip().lower()
            break
    if name is None:
        m = RPLAIN.match(msg)
        name, explicit = (m.group(1).strip().lower() if m else None), False
    if name is None:
        return None
    row = c.execute("SELECT phrase FROM routines WHERE device=? AND name=?", (dev, name)).fetchone()
    if not row:
        return (say("सर, ये रूटीन नहीं मिला। \"my routines\" बोलिए।", "Sir, I did not find that routine. Say \"my routines\".") , None) if explicit else None
    got = make(c, dev, row[0], hindi, control, in_app)  # same checks as a normal task, again, on every run
    if got is None:
        return say("सर, ये रूटीन अब ठीक नहीं बैठता। इसे दोबारा बनाइए।", "Sir, this routine no longer works. Please save it again."), None
    return (say(f"रूटीन \"{name}\":\n", f"Routine \"{name}\":\n") + got[0]), got[1]
