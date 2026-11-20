"""Part 174: chat history list + search over ALL saved messages (not only the 50 on the screen).
Reading only: it never changes or deletes anything. One call, four answers, chosen by the fields the page sends:
  {}                 -> the days that have messages (newest first, with the count)
  {q: "word"}        -> messages that contain the word (newest first, at most 40)
  {day: "2026-11-21"} -> every message of that day (oldest first, at most 300)
  {day: "all"}       -> the last 3000 messages (for Copy all history)
The page sends off = seconds to add to the UTC time so that days follow the phone's clock."""
import re

PREFIX = "(phone action) "


def _off(d):
    try:
        return max(-50400, min(50400, int(d.get("off") or 0)))
    except (TypeError, ValueError):
        return 0


def _row(r):
    role, text, ts = r
    return {"role": role, "content": (text or "").replace(PREFIX, "", 1) if role == "assistant" else (text or ""), "ts": int(ts or 0)}


def query(c, dev, d):
    off = _off(d)
    day = str(d.get("day") or "").strip()[:10]
    q = str(d.get("q") or "").strip()[:60]
    if q:
        like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        rows = c.execute("SELECT role,content,ts FROM messages WHERE device=? AND content LIKE ? ESCAPE '\\' ORDER BY id DESC LIMIT 40", (dev, like)).fetchall()
        return {"msgs": [_row(r) for r in rows]}
    if day == "all":
        rows = c.execute("SELECT role,content,ts FROM (SELECT id,role,content,ts FROM messages WHERE device=? ORDER BY id DESC LIMIT 3000) ORDER BY id", (dev,)).fetchall()
        return {"msgs": [_row(r) for r in rows]}
    if day:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            return {"msgs": []}
        rows = c.execute("SELECT role,content,ts FROM messages WHERE device=? AND strftime('%Y-%m-%d', COALESCE(ts,0)+?, 'unixepoch')=? ORDER BY id LIMIT 300", (dev, off, day)).fetchall()
        return {"msgs": [_row(r) for r in rows]}
    rows = c.execute("SELECT strftime('%Y-%m-%d', COALESCE(ts,0)+?, 'unixepoch') AS d, COUNT(*) FROM messages WHERE device=? GROUP BY d ORDER BY d DESC LIMIT 90", (off, dev)).fetchall()
    return {"days": [{"day": a, "n": n} for a, n in rows if a and a != "1970-01-01"]}
