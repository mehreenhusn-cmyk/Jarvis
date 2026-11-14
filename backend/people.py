"""Jarvis people profiles (Part 20): notes about friends and family. Only what the user says. Stored on the phone."""
import re, time
import memory

SAVE = re.compile(r"^\s*(?:note about|notes about|profile of|add person|about person)\s+(.{1,40}?)\s*[:\-]\s*(.+)$", re.I | re.S)
SHOW = re.compile(r"^\s*(?:who is|tell me about|about)\s+(.{1,40}?)\s*\??\s*$", re.I)
LIST = re.compile(r"^\s*(?:my people|people|list people|show people)\s*\??\s*$", re.I)
DEL = re.compile(r"^\s*(?:forget person|remove person|delete person)\s+(.{1,40}?)\s*$", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY, device INT, name TEXT, note TEXT, ts REAL)")


def notes(c, dev, name):
    return [r[0] for r in c.execute("SELECT note FROM people WHERE device=? AND lower(name)=? ORDER BY id", (dev, name.lower()))]


def all_people(c, dev):
    names = [r[0] for r in c.execute("SELECT name FROM people WHERE device=? GROUP BY lower(name) ORDER BY min(id)", (dev,))]
    return [{"name": n, "notes": notes(c, dev, n)} for n in names]


def delete(c, dev, name):
    k = c.execute("DELETE FROM people WHERE device=? AND lower(name)=?", (dev, name.lower().strip())).rowcount
    c.commit()
    return k


def context(c, dev, msg):
    """If the message names a saved person, tell the AI what the user said about them."""
    out = []
    for p in all_people(c, dev):
        if re.search(r"\b" + re.escape(p["name"]) + r"\b", msg, re.I):
            out.append(f"- {p['name']}: " + "; ".join(p["notes"]))
    return ("\n\nThe user told you these facts about people (use only when useful, never invent more):\n" + "\n".join(out[:5])) if out else ""


def handle(c, dev, msg, hindi):
    """Return a reply if this is a people command, else None."""
    def say(hi, en):
        return hi if hindi else en
    m = SAVE.match(msg)
    if m:
        name, note = m.group(1).strip(), m.group(2).strip()[:300]
        if memory.SECRET.search(note):
            return say("माफ़ कीजिए सर, पासवर्ड, ओटीपी या पिन मैं सेव नहीं करता।", "Sorry sir, I never save passwords, OTPs or PINs.")
        ps = all_people(c, dev)
        if len(ps) >= 40 and name.lower() not in [p["name"].lower() for p in ps]:
            return say("सर, 40 लोगों की सीमा पूरी हो गई।", "Sir, the limit of 40 people is full.")
        if len(notes(c, dev, name)) >= 20:
            return say("सर, इनके बारे में 20 नोट हो चुके हैं।", "Sir, there are already 20 notes about this person.")
        c.execute("INSERT INTO people(device, name, note, ts) VALUES(?,?,?,?)", (dev, name, note, time.time()))
        c.commit()
        return say(f"ठीक है सर, {name} के बारे में लिख लिया।", f"Okay sir, noted about {name}: {note}")
    if LIST.match(msg):
        ps = all_people(c, dev)
        if not ps:
            return say("सर, अभी कोई व्यक्ति सेव नहीं है।", "Sir, no people saved yet. Try: note about Faisal: old friend")
        return say("सर, ये लोग सेव हैं: ", "Sir, I know these people: ") + ", ".join(p["name"] for p in ps)
    m = DEL.match(msg)
    if m:
        return say("ठीक है सर, हटा दिया।", "Okay sir, removed.") if delete(c, dev, m.group(1)) else say("सर, ये नाम नहीं मिला।", "Sir, I did not find that name.")
    m = SHOW.match(msg)
    if m:
        n = notes(c, dev, m.group(1).strip())
        if n:  # unknown names fall through to the normal AI chat
            return f"{m.group(1).strip()}:\n" + "\n".join("- " + x for x in n)
    return None
