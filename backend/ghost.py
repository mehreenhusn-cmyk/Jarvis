"""Part 107: Context Ghost. `Chrome kholo research ke liye` opens Chrome as usual and keeps the reason ("research") for 7 days.
The next time you open the SAME app through Jarvis, it asks ONCE if you want to continue that work. Jarvis does not watch other app use, it only knows what you said to it.
`ghost dikhao` shows the saved reasons, `ghost bhool jao` deletes them. Text only, never sent to the AI."""
import re
import time
import actions
from notes import SECRET

SHOW = re.compile(r"^\s*ghost\s+(?:dikhao|show)\s*$", re.I)
DROP = re.compile(r"^\s*ghost\s+(?:bhool\s+jao|hatao|clear)\s*$", re.I)
KEEP = 7 * 86400


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS ghost(id INTEGER PRIMARY KEY, device INT, app TEXT, reason TEXT, ts REAL, asked INT DEFAULT 0)")


def _split(msg):
    """(open command, reason) or None. Two shapes: `Chrome kholo research ke liye` (reason before `ke liye`) and `open Chrome for research` (reason after `for`)."""
    w = msg.split()
    if not 3 <= len(w) <= 9:
        return None
    low = [x.lower() for x in w]
    if len(w) >= 4 and low[-2] in ("ke", "के") and low[-1] in ("liye", "lie", "लिए"):
        for i in range(1, len(w) - 2):  # the shortest start that is an open command; the rest up to `ke liye` is the reason
            if len(w) - 2 - i <= 4 and actions.parse(" ".join(w[:i])):
                return " ".join(w[:i]), " ".join(w[i:-2])
    for k in range(1, len(w) - 1):
        if low[k] in ("for", "liye", "lie", "लिए") and k + 1 < len(w) and len(w) - k - 1 <= 4:
            cmd = w[:k - 1] if low[k - 1] in ("ke", "के") else w[:k]
            if cmd and actions.parse(" ".join(cmd)):
                return " ".join(cmd), " ".join(w[k + 1:])
    return None


def pre(c, dev, msg, hindi):
    """Returns (message without the reason, note for the reply, app label), or (msg, None, None) when the message has no reason."""
    got = _split(msg.strip()) if len(msg) < 130 and "?" not in msg else None
    if not got:
        return msg, None, None
    cmd, reason = got[0], got[1].strip(" .!?")
    name = actions.parse(cmd)
    if not name or len(reason) < 3 or SECRET.search(reason):
        return msg, None, None
    app = actions.canon(name)
    c.execute("DELETE FROM ghost WHERE device=? AND app=?", (dev, app))
    c.execute("INSERT INTO ghost(device, app, reason, ts) VALUES(?,?,?,?)", (dev, app, reason[:60], time.time()))
    c.commit()
    return cmd, (f"मैं 7 दिन याद रखूँगा कि {app} किसलिए खोला: {reason}" if hindi else f"I will remember for 7 days why you opened {app}: {reason}"), app


def ask(c, dev, action, saved):
    """After an open_app action: the saved reason for that app, only once, only within 7 days, and never in the same turn it was saved."""
    if not isinstance(action, dict) or action.get("type") != "open_app" or not action.get("name") or saved == action.get("name"):
        return None
    r = c.execute("SELECT id, reason FROM ghost WHERE device=? AND app=? AND asked=0 AND ts>? ORDER BY id DESC LIMIT 1", (dev, action["name"], time.time() - KEEP)).fetchone()
    if not r:
        return None
    c.execute("UPDATE ghost SET asked=1 WHERE id=?", (r[0],))
    c.commit()
    return {"app": action["name"], "reason": r[1]}


def handle(c, dev, msg, hindi):
    if len(msg) > 30:
        return None
    if SHOW.match(msg):
        r = c.execute("SELECT app, reason, ts FROM ghost WHERE device=? AND ts>? ORDER BY id DESC", (dev, time.time() - KEEP)).fetchall()
        if not r:
            return "सर, अभी कोई वजह सेव नहीं है। जैसे: Chrome kholo research ke liye" if hindi else "Sir, no reason is saved. Try: Chrome kholo research ke liye"
        return ("सेव की हुई वजहें (7 दिन):\n" if hindi else "Saved reasons (kept 7 days):\n") + "\n".join(f"- {a}: {t} ({max(1, int((time.time() - s) // 86400))}d)" for a, t, s in r)
    if DROP.match(msg):
        k = c.execute("DELETE FROM ghost WHERE device=?", (dev,)).rowcount
        c.commit()
        return ("ठीक है, सब वजहें भूल गया।" if hindi else "Okay, all saved reasons are forgotten.") if k else ("सर, कुछ सेव नहीं था।" if hindi else "Sir, nothing was saved.")
    return None
