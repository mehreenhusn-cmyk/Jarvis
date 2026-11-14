"""Jarvis memory (Part 9): "yaad rakho", dekho, sudharo, bhool jao. Sirf wahi yaad rakhta hai jo user ne khud bola."""
import re, time

SECRET = re.compile(r"password|passcode|\botp\b|\bpin\b|cvv|पासवर्ड|ओटीपी|पिन", re.I)
SAVE = re.compile(r"^\s*(?:yaad rakho|yad rakho|याद रखो|याद रखना|remember(?: that)?)\s*[:,\-]?\s*(.+)$", re.I | re.S)
LIST = re.compile(r"kya yaad hai|meri memor|memories dikhao|yaad kya|क्या याद है|याद क्या", re.I)
DEL = re.compile(r"^\s*(?:bhool jao|bhul jao|delete memory|भूल जाओ)\s*#?(\d+)\s*$", re.I)
UPD = re.compile(r"^\s*(?:sudhaar|sudhar|update memory|सुधार)\s*#?(\d+)\s*[:,\-]\s*(.+)$", re.I | re.S)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, device INT, text TEXT, ts REAL)")


def rows(c, dev):
    return c.execute("SELECT id, text FROM memories WHERE device=? ORDER BY id", (dev,)).fetchall()


def context(c, dev):
    """AI ko batane ke liye: user ne jo yaad rakhne bola. Isse bahar kuch invent nahi karna."""
    r = rows(c, dev)[-30:]
    return ("\n\nThe user asked you to remember these things (use only when useful, never invent beyond them):\n"
            + "\n".join(f"- {t}" for _, t in r)) if r else ""


def handle(c, dev, msg, hindi):
    """Memory ka command ho to jawab (text) lautata hai, warna None (tab normal AI chat)."""
    def say(hi, ro):
        return hi if hindi else ro
    m = SAVE.match(msg)
    if m:
        t = m.group(1).strip()[:300]
        if SECRET.search(t):
            return say("माफ़ कीजिए सर, पासवर्ड, ओटीपी या पिन मैं कभी सेव नहीं करता।", "Sorry sir, I never save passwords, OTPs or PINs.")
        if len(rows(c, dev)) >= 100:
            return say("सर, याददाश्त भर गई है। पहले कुछ हटाइए।", "Sir, memory is full (100). Please remove something first.")
        n = c.execute("INSERT INTO memories(device, text, ts) VALUES(?,?,?)", (dev, t, time.time())).lastrowid
        c.commit()
        return say(f"ठीक है सर, याद रख लिया (#{n}): {t}", f"Okay sir, saved (#{n}): {t}")
    m = DEL.match(msg)
    if m:
        k = c.execute("DELETE FROM memories WHERE id=? AND device=?", (int(m.group(1)), dev)).rowcount
        c.commit()
        return say("ठीक है सर, भूल गया।", "Okay sir, forgotten.") if k else say("सर, इस नंबर की कोई याद नहीं मिली।", "Sir, I found no memory with that number.")
    m = UPD.match(msg)
    if m:
        t = m.group(2).strip()[:300]
        if SECRET.search(t):
            return say("माफ़ कीजिए सर, पासवर्ड, ओटीपी या पिन मैं सेव नहीं करता।", "Sorry sir, I never save passwords, OTPs or PINs.")
        k = c.execute("UPDATE memories SET text=? WHERE id=? AND device=?", (t, int(m.group(1)), dev)).rowcount
        c.commit()
        return say("ठीक है सर, सुधार दिया।", "Okay sir, updated.") if k else say("सर, इस नंबर की कोई याद नहीं मिली।", "Sir, I found no memory with that number.")
    if LIST.search(msg) and len(msg) < 60:
        r = rows(c, dev)
        if not r:
            return say("सर, अभी मुझे कुछ याद रखने को नहीं कहा गया।", "Sir, you have not asked me to remember anything yet.")
        return say("सर, मुझे ये याद है:\n", "Sir, I remember this:\n") + "\n".join(f"#{i} {t}" for i, t in r)
    return None
