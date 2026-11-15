"""Jarvis calls, contacts (Part 19) and phone calendar (Part 44). The Android app reads them only when you ask. Metadata only: names, numbers, times, event titles.
No messages, no call audio. No AI sees this data: the reply is made here. The reply is not saved in chat history."""
import re, time

CALLQ = re.compile(r"missed calls?|who called|recent calls|call history|call log|मिस्ड कॉल|किसका कॉल", re.I)
CN = re.compile(r"^\s*(?:find contact|contact number of|contact for|contact)\s+(.{1,40}?)\s*\??\s*$", re.I)
CALQ2 = re.compile(r"\b(?:my calendar|calendar events?|upcoming events|events (?:today|tomorrow|this week)|calendar (?:mein|me) kya|calendar dikhao|aaj ke events|kal ke events)\b|कैलेंडर", re.I)
KIND = {1: "Incoming", 2: "Outgoing", 3: "Missed", 4: "Voicemail", 5: "Rejected", 6: "Blocked"}


def private(msg):
    """True if this message is about calls or contacts (so the reply must not be saved)."""
    return bool(CALLQ.search(msg) or CN.match(msg) or CALQ2.search(msg))


def when(ms):
    return time.strftime("%d %b, %I:%M %p", time.localtime(ms / 1000))


def handle(msg, calls, contact, hindi, cal=None):
    """Reply text, or None if the message is not about calls or contacts."""
    def say(hi, en):
        return hi if hindi else en
    need_app = say("सर, यह सिर्फ़ Jarvis Android ऐप में चलता है, Chrome में नहीं।", "Sir, this works only in the Jarvis Android app, not in Chrome.")
    need_perm = say("सर, फ़ोन में अनुमति दीजिए और फिर पूछिए।", "Sir, please allow the permission on the phone, then ask again.")
    if CALQ2.search(msg):
        if cal is None:
            return need_app
        if isinstance(cal, dict):
            return need_perm
        rows = [e for e in cal if isinstance(e, dict)][:20]
        if not rows:
            return say("सर, इस समय में कोई इवेंट नहीं है।", "Sir, no calendar events in that time.")
        out, day = [], ""
        for e in rows:
            t = time.gmtime if e.get("allDay") else time.localtime  # poore din ke event UTC mein aate hain
            s = t(int(e.get("begin", 0)) / 1000)
            d = time.strftime("%a %d %b", s)
            if d != day:
                day = d
                out.append(d + ":")
            hm = say("पूरा दिन", "all day") if e.get("allDay") else time.strftime("%I:%M %p", s)
            out.append(f"- {hm} {str(e.get('title') or '(no title)')[:60]}" + (f" ({str(e['where'])[:40]})" if e.get("where") else ""))
        return say("सर, आपके इवेंट:\n", "Sir, your events:\n") + "\n".join(out)
    if CALLQ.search(msg):
        if calls is None:
            return need_app
        if isinstance(calls, dict):
            return need_perm
        missed = bool(re.search(r"missed|मिस्ड", msg, re.I))
        rows = [c for c in calls if isinstance(c, dict) and (c.get("type") == 3 or not missed)][:15]
        if not rows:
            return say("सर, कोई मिस्ड कॉल नहीं मिली।", "Sir, no missed calls found.") if missed else say("सर, कोई कॉल नहीं मिली।", "Sir, no calls found.")
        out = []
        for c in rows:
            who = c.get("name") or c.get("number") or "?"
            dur = f", {int(c.get('sec', 0)) // 60} min {int(c.get('sec', 0)) % 60} s" if c.get("type") in (1, 2) and c.get("sec") else ""
            out.append(f"- {KIND.get(c.get('type'), 'Call')}: {who} ({when(c.get('ts', 0))}{dur})")
        return say("सर, ये रही कॉल की जानकारी:\n", "Sir, here are your calls:\n") + "\n".join(out)
    if CN.match(msg):
        if contact is None:
            return need_app
        if isinstance(contact, dict):
            return need_perm
        rows = [c for c in contact if isinstance(c, dict)][:5]
        if not rows:
            return say("सर, ये नाम कॉन्टैक्ट में नहीं मिला।", "Sir, I did not find that name in your contacts.")
        return "\n".join(f"- {c.get('name')}: {c.get('number')}" for c in rows)
    return None
