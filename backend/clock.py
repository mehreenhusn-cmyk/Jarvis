"""Jarvis clock (Part 36b): Jarvis knows WHEN things were said and how long the user was away.
The AI gets one short line (time now, gap since the last message, times of the last few messages). It never saves anything new."""
import time


def gap(sec):
    """Short human words for a time gap: '40 seconds', '5 minutes', '2 hours', '3 days'."""
    s = int(max(0, sec))
    if s < 90:
        return f"{s} seconds"
    if s < 5400:
        return f"{round(s / 60)} minutes"
    if s < 172800:
        return f"{round(s / 3600)} hours"
    return f"{round(s / 86400)} days"


def hm(ts, now=None):
    """'18:02' for today, '14 Nov 18:02' for an older day (server clock = phone clock, because both run on this phone)."""
    now = now or time.time()
    t = time.localtime(ts)
    if time.strftime("%Y%m%d", t) == time.strftime("%Y%m%d", time.localtime(now)):
        return time.strftime("%H:%M", t)
    return time.strftime("%d %b %H:%M", t)


def context(rows, prev_ts, now=None):
    """rows = [(role, ts), ...] newest last, prev_ts = time of the message before this one (or None).
    Returns text for the AI, or '' when there is nothing to say."""
    now = now or time.time()
    out = ["Time now: " + time.strftime("%A %d %b %Y, %H:%M", time.localtime(now)) + "."]
    if prev_ts:
        g = now - prev_ts
        out.append(f"The user's last message before this one was {gap(g)} ago." + (" Treat it as a fresh start, not a reply to your old answer." if g > 3600 else ""))
    if rows:
        out.append("Recent message times: " + ", ".join(f"{'user' if r == 'user' else 'you'} {hm(t, now)}" for r, t in rows[-6:]) + ".")
    out.append("Use times only when they help (for example 'you asked this 2 hours ago'). Never write timestamps in your reply.")
    return "\n" + " ".join(out)
