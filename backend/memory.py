"""Jarvis memory (Part 9): "yaad rakho", dekho, sudharo, bhool jao. Sirf wahi yaad rakhta hai jo user ne khud bola."""
import re, time

SECRET = re.compile(r"password|passcode|\botp\b|\bpin\b|cvv|पासवर्ड|ओटीपी|पिन", re.I)
SAVE = re.compile(r"^\s*(?:yaad rakho|yad rakho|याद रखो|याद रखना|remember(?: that)?)\s*[:,\-]?\s*(.+)$", re.I | re.S)
LIST = re.compile(r"kya yaad hai|meri memor|memories dikhao|yaad kya|क्या याद है|याद क्या", re.I)
DEL = re.compile(r"^\s*(?:bhool jao|bhul jao|delete memory|भूल जाओ)\s*#?(\d+)\s*$", re.I)
UPD = re.compile(r"^\s*(?:sudhaar|sudhar|update memory|सुधार)\s*#?(\d+)\s*[:,\-]\s*(.+)$", re.I | re.S)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, device INT, text TEXT, ts REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS flags(device INT, name TEXT, val INT, PRIMARY KEY(device, name))")  # Parts 105 + 106: small on/off switches and one number each


def flag(c, dev, name):
    r = c.execute("SELECT val FROM flags WHERE device=? AND name=?", (dev, name)).fetchone()
    return r[0] if r else 0


def setflag(c, dev, name, val):
    c.execute("INSERT OR REPLACE INTO flags(device, name, val) VALUES(?,?,?)", (dev, name, int(val)))
    c.commit()


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


# ---- Part 54: Jarvis offers to remember a personal fact. It only OFFERS; saving happens when Hussain taps Yes (the page then sends "yaad rakho: ..."). ----
OWN = re.compile(r"^\s*(?:mere|meri|mera|my|मेरे|मेरी|मेरा)\s", re.I)
FACT = re.compile(r"\b(?:naam|name|birthday|janamdin|janmdin|age|umar|called)\b|नाम|जन्मदिन|उम्र", re.I)
QUESTION = re.compile(r"\b(?:kya|kaun|kaun sa|kaise|kab|kitna|what|who|when|which|how|why|tell|bata\w*)\b|क्या|कौन|कब|कैसे|कितना|बताओ|बताइए", re.I)


def suggest(msg):
    """The fact text if the message states a personal fact (\"mere bhatije ka naam Arman hai\"), else None. Never for questions or secrets."""
    m = msg.strip()
    if "?" in m or len(m) > 120 or len(m) < 8 or not OWN.match(m) or not FACT.search(m) or QUESTION.search(m) or SECRET.search(m) or SAVE.match(m):
        return None
    return m


# Part 88 (Memory Atlas): every table that holds personal data, in ONE list, so the Atlas, search (Part 89) and the guest guard (Part 118) use the same names.
# (table, name, extra filter, how to remove)
STORES = [("memories", "Memories", "", "Remove button"), ("people", "People notes", "", "Remove button"), ("notes", "Notes", "", "Remove button"),
          ("messages", "Chat history", "", "say: clear history"), ("listitems", "List items", "", "say: list se doodh hatao"),
          ("habits", "Habits", " AND day=''", "delete everything"), ("spend", "Expenses", "", "say: kharcha hatao"),
          ("decisions", "Decisions and unfinished", " AND done=0", "say: decision ho gaya N / adhoora khatam N"), ("moods", "Mood check-ins", " AND day!='care'", "delete everything"),
          ("touch", "Last talked people", "", "say: ammi track band karo"), ("contracts", "Habit contracts", "", "say: contract hatao gym"), ("capsules", "Time capsules", "", "say: capsule hatao N"), ("dreams", "Dream journal", "", "say: sapna hatao N"), ("signs", "Signs log", "", "say: sign hatao <text>"),
          ("ledger", "Money ledger", "", "delete everything"), ("reminders", "Reminders", "", "delete everything"),
          ("routines", "Routines", "", "delete everything"), ("flags", "Switches (honest question, drift)", " AND val=1 AND name IN ('honest','drift')", "say: sach sawal off / drift off"), ("tasks", "Task history", "", "delete everything"), ("dayreport", "Day report time", "", "delete everything")]


def atlas(c, dev):
    """Counts of everything Jarvis keeps for this device, and the notes (newest 50). Reads only; nothing is saved or sent anywhere."""
    st = [{"name": n, "count": c.execute(f"SELECT count(*) FROM {t} WHERE device=?{w}", (dev,)).fetchone()[0], "how": h} for t, n, w, h in STORES]
    nt = [{"id": i, "text": t} for i, t in c.execute("SELECT id, text FROM notes WHERE device=? ORDER BY id DESC LIMIT 50", (dev,))]
    return {"stores": st, "notes": nt}
