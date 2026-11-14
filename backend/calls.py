"""Jarvis calls and contacts (Part 19). The Android app reads them only when you ask. Metadata only: names, numbers, times.
No messages, no call audio. No AI sees this data: the reply is made here. The reply is not saved in chat history."""
import re, time

CALLQ = re.compile(r"missed calls?|who called|recent calls|call history|call log|मिस्ड कॉल|किसका कॉल", re.I)
CN = re.compile(r"^\s*(?:find contact|contact number of|contact for|contact)\s+(.{1,40}?)\s*\??\s*$", re.I)
KIND = {1: "Incoming", 2: "Outgoing", 3: "Missed", 4: "Voicemail", 5: "Rejected", 6: "Blocked"}


def private(msg):
    """True if this message is about calls or contacts (so the reply must not be saved)."""
    return bool(CALLQ.search(msg) or CN.match(msg))


def when(ms):
    return time.strftime("%d %b, %I:%M %p", time.localtime(ms / 1000))


def handle(msg, calls, contact, hindi):
    """Reply text, or None if the message is not about calls or contacts."""
    def say(hi, en):
        return hi if hindi else en
    need_app = say("सर, यह सिर्फ़ Jarvis Android ऐप में चलता है, Chrome में नहीं।", "Sir, this works only in the Jarvis Android app, not in Chrome.")
    need_perm = say("सर, फ़ोन में अनुमति दीजिए और फिर पूछिए।", "Sir, please allow the permission on the phone, then ask again.")
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
