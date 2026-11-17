"""Part 109: Life Timeline. ONE list of what you did, newest first, read from what Jarvis already keeps: reminders that rang, routines and tasks that ran, notes you saved, expenses you noted.
Nothing new is stored and nothing is sent to the AI. Filters: all, reminders, tasks, notes, expenses. Chat: `timeline`, `timeline notes`, `timeline expenses`... The page has a Timeline tab with the same filters.
Calls, contacts, messages and the chat itself are never in it."""
import re
import time
import remind

KINDS = {"reminders": "reminder", "reminder": "reminder", "tasks": "task", "task": "task", "routines": "task", "routine": "task", "notes": "note", "note": "note",
         "expenses": "expense", "expense": "expense", "kharcha": "expense", "all": "all", "": "all"}
ASK = re.compile(r"^\s*(?:my\s+)?(?:life\s+)?timeline(?:\s+(reminders?|tasks?|routines?|notes?|expenses?|kharcha|all))?\s*$", re.I)
LABEL = {"reminder": ("⏰", "Reminder done", "रिमाइंडर"), "task": ("▶", "Task ran", "टास्क चला"), "note": ("📝", "Note saved", "नोट"), "expense": ("💸", "Expense noted", "खर्चा")}
STATE = {"COMPLETED": "done", "FAILED": "failed", "PARTIAL": "partly done", "CANCELLED": "cancelled"}


def _off(now):
    """Seconds between the real clock and the phone's clock (reminders are kept in phone time)."""
    return remind.tm(now) - time.time()


def items(c, dev, now, kind="all", before=None, limit=30):
    """Newest first, in phone time. `before` is the `at` of the last item you already have. Text is cut to 100 characters."""
    kind = KINDS.get(str(kind).lower(), "all")
    try:
        off = _off(now)
    except ValueError:
        return []
    top = before if isinstance(before, (int, float)) and before > 0 else 10 ** 12
    k = min(max(int(limit), 1), 60)
    rows = []
    if kind in ("all", "reminder"):
        rows += [("reminder", t, d, True) for t, d in c.execute("SELECT text, due FROM reminders WHERE device=? AND sent=1 AND due<? ORDER BY due DESC LIMIT ?", (dev, top, k))]
    if kind in ("all", "task"):
        rows += [("task", f"{t} ({STATE.get(s, s.lower())})", u + off, True) for t, s, u in
                 c.execute("SELECT title, state, upd FROM tasks WHERE device=? AND state IN ('COMPLETED','FAILED','PARTIAL','CANCELLED') AND upd+?<? ORDER BY upd DESC LIMIT ?", (dev, off, top, k))]
    if kind in ("all", "note"):
        rows += [("note", t, s + off, True) for t, s in c.execute("SELECT text, ts FROM notes WHERE device=? AND ts+?<? ORDER BY ts DESC LIMIT ?", (dev, off, top, k))]
    if kind in ("all", "expense"):
        for a, w, d in c.execute("SELECT amount, what, day FROM spend WHERE device=? ORDER BY id DESC LIMIT ?", (dev, k)):
            try:
                at = remind.tm(d + " 12:00")  # only the day is kept for an expense, so it sits at noon and shows no time
            except ValueError:
                continue
            if at < top:
                rows.append(("expense", (f"₹{a:,.0f}" if float(a).is_integer() else f"₹{a:,.2f}") + f" {w}", at, False))
    rows.sort(key=lambda r: -r[2])
    return [{"kind": kd, "text": str(t)[:100], "at": int(at), "date": time.strftime("%d %b", time.gmtime(at)), "time": time.strftime("%H:%M", time.gmtime(at)) if tm else ""}
            for kd, t, at, tm in rows[:k]]


def handle(c, dev, msg, hindi, now):
    m = ASK.match(msg) if len(msg) < 40 else None
    if not m:
        return None
    rows = items(c, dev, now, m.group(1) or "all", None, 15)
    if not rows:
        return "सर, टाइमलाइन में अभी कुछ नहीं है।" if hindi else "Sir, nothing in the timeline yet."
    out, day = [("आपकी टाइमलाइन:" if hindi else "Your timeline:")], ""
    for r in rows:
        if r["date"] != day:
            day = r["date"]
            out.append(day)
        out.append(f"- {r['time'] + ' ' if r['time'] else ''}{LABEL[r['kind']][0]} {r['text']}")
    return "\n".join(out)
