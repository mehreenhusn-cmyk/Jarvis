"""Jarvis task engine (Part 41): "Chrome kholo aur neeche scroll karo phir back jao" becomes ONE tracked task with steps.
The server only PLANS (it splits your own words into steps from the fixed action list) and KEEPS THE RECORD. The steps run in the app (Java),
which checks Stop, the phone-control switch and the app lock before every step and checks that each step really did something.
A step that needs your Yes (send, pay, delete, ...) or that types text is never put in a task: those stay one-by-one, with your own tap."""
import json, re, time

import actions

STATES = ("CREATED", "PLANNING", "WAITING_FOR_PERMISSION", "WAITING_FOR_CONFIRMATION", "RUNNING", "VERIFYING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED")
END = ("COMPLETED", "PARTIAL", "FAILED", "CANCELLED")
OK_STEPS = ("open_app", "back", "home", "scroll", "click", "torch", "volume", "settings", "current_app", "lock")
MAX_STEPS = 6
STALE = 600  # a RUNNING task with no news for 10 minutes is dead (app killed or phone restarted)
SPLIT = re.compile(r"\s*(?:,|;|\band then\b|\bthen\b|\band\b|\bphir\b|\bfir\b|\baur\b|\buske baad\b|\bfir se\b|फिर|और|उसके बाद)\s*", re.I)
TYPEWORD = re.compile(r"\b(?:type|likho|likh)\b|टाइप|लिखो", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, device INT, title TEXT, steps TEXT, state TEXT, cur INT DEFAULT 0, note TEXT DEFAULT '', ts REAL, upd REAL)")
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
    m = (msg or "").strip()
    if not m or "?" in m or len(m) > 220 or TYPEWORD.search(m):
        return []
    parts = [p.strip() for p in SPLIT.split(m) if p and p.strip()]
    return parts if 2 <= len(parts) <= MAX_STEPS else []


def make(c, dev, msg, hindi, control, in_app):
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
        if not act or act.get("type") not in OK_STEPS:
            refused = True  # blocked (password, OTP...), needs a Yes, or not allowed in a task
            continue
        steps.append({k: act[k] for k in ("type", "name", "dir", "page", "on") if k in act})
        texts.append(text)
    if refused:
        return say("सर, इस काम में ऐसा कदम है जो आपकी हाँ माँगता है (भेजना, पैसे, डिलीट) या जो मैं नहीं करता (पासवर्ड, OTP)। इन्हें एक-एक करके बोलिए। मैंने कुछ नहीं किया।",
                   "Sir, this task has a step that needs your own Yes (send, pay, delete) or that I never do (passwords, OTPs). Please give those one at a time. I did nothing."), None
    if any(s["type"] == "lock" for s in steps[:-1]):
        return say("सर, फ़ोन लॉक सिर्फ़ आख़िरी कदम हो सकता है। मैंने कुछ नहीं किया।", "Sir, locking the phone can only be the last step. I did nothing."), None
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
