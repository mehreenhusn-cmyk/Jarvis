"""Part 158: a SHORT summary of the older chat, so Jarvis understands words like `woh wala` or `usko` even when the thing was said a long time ago.
The AI always gets the last 20 messages itself (Part 126). Messages older than that are folded into ONE short text (max 700 characters).
Numbers like OTPs or cards are hidden before the summary is made. It is only a helper for the AI: never shown, never sent anywhere else.
`clear history` deletes it too, and `delete everything` as well."""
import re

import screen

KEEP = 20    # newest messages the AI reads word for word
EVERY = 10   # a new summary is made when this many older messages are not summarized yet
MAXC = 700   # characters
SKIP = ("(phone action)", "(photo)", "(answer about your screen", "(reply ideas")  # these lines were never real talk (or were not saved on purpose)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS chatsum(device INT PRIMARY KEY, text TEXT, upto INT, ts REAL)")


def get(c, dev):
    r = c.execute("SELECT text, upto FROM chatsum WHERE device=?", (dev,)).fetchone()
    return (r[0] or "", r[1] or 0) if r else ("", 0)


def context(c, dev):
    """Extra instructions for the AI: the summary of the older chat, or an empty string."""
    t = get(c, dev)[0]
    return ("\n\nEarlier in this chat (a short summary of older messages; it can be incomplete, never invent beyond it):\n" + t) if t else ""


def wipe(c, dev):
    c.execute("DELETE FROM chatsum WHERE device=?", (dev,))
    c.commit()


def _line(role, content):
    t = str(content or "").strip()
    if not t or t.startswith(SKIP):
        return ""
    t = re.sub(r"\s+", " ", screen.redact(t)[0])[:300]
    return ("Hussain: " if role == "user" else "Jarvis: ") + t


def due(c, dev):
    """The older messages that are not summarized yet (a list of (id, role, content)), or None when it is not time."""
    b = c.execute("SELECT id FROM messages WHERE device=? ORDER BY id DESC LIMIT 1 OFFSET ?", (dev, KEEP - 1)).fetchone()
    if not b:
        return None
    upto = get(c, dev)[1]
    rows = c.execute("SELECT id, role, content FROM messages WHERE device=? AND id>? AND id<? ORDER BY id LIMIT 60", (dev, upto, b[0])).fetchall()
    return rows if len(rows) >= EVERY else None


def update(c, dev, ask):
    """ask = app.ask(history, style, extra) -> (reply, via). True if a new summary was saved. Never raises."""
    try:
        rows = due(c, dev)
        if not rows:
            return False
        last = rows[-1][0]
        lines = [x for x in (_line(r, t) for _, r, t in rows) if x]
        if len(lines) < 3:
            c.execute("INSERT OR REPLACE INTO chatsum(device, text, upto, ts) VALUES(?,?,?,strftime('%s','now'))", (dev, get(c, dev)[0], last))
            c.commit()
            return False
        old = get(c, dev)[0]
        ask_text = ("Make ONE short summary (plain text, at most 600 characters) of this chat between Hussain and his assistant Jarvis. "
                    "Keep: what the topics were, names of people or things he mentioned, what he decided or asked for, and what was left open. "
                    "Use the same words and language mix he used. Never add anything that is not in the lines. No numbers like OTP, card or password.\n\n"
                    + (("Earlier summary:\n" + old + "\n\n") if old else "") + "New lines:\n" + "\n".join(lines))
        reply, via = ask([{"role": "user", "content": ask_text}], "english", "")
        if via == "mock":
            return False
        text = re.sub(r"\s+", " ", screen.redact(str(reply or ""))[0]).strip()[:MAXC]
        if len(text) < 20:
            return False
        c.execute("INSERT OR REPLACE INTO chatsum(device, text, upto, ts) VALUES(?,?,?,strftime('%s','now'))", (dev, text, last))
        c.commit()
        return True
    except Exception:
        return False
