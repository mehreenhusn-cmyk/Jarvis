"""Part 143: What Jarvis learned. COUNTS only, from commands Jarvis already runs (whom you call, which app you open, in which hour).
Never the words you said, never the screen. Every line on the card has Keep and Delete. Jarvis only SUGGESTS (the page shows a Yes button).
It never acts alone. Words: `seekhna band karo` (off), `seekhna chalu karo` (on), `seekha dikhao` (list), `seekha bhool jao` (erase all)."""
import re, time

KIND = {"call": "call", "open_app": "open"}
SHOW = re.compile(r"^\s*(?:what (?:has )?jarvis (?:has )?learned|what did you learn|jarvis ne kya seekha|kya seekha|seekha dikhao|सीखा दिखाओ)\s*\??\s*$", re.I)
OFF = re.compile(r"^\s*(?:seekhna band(?: karo)?|stop learning|सीखना बंद(?: करो)?)\s*$", re.I)
ON = re.compile(r"^\s*(?:seekhna chalu(?: karo)?|start learning|सीखना चालू(?: करो)?)\s*$", re.I)
WIPE = re.compile(r"^\s*(?:seekha bhool jao|forget what you learned|forget learned)\s*$", re.I)
NAME = re.compile(r"^[\w\u0900-\u097F][\w\u0900-\u097F .'-]{0,29}$")
MIN_N, MIN_DAYS, EXPIRE = 3, 3, 30  # a pattern needs 3 times on 3 days; unkept lines older than 30 days go away


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS learned(id INTEGER PRIMARY KEY, device INT, kind TEXT, name TEXT, hour INT, n INT DEFAULT 0, days INT DEFAULT 0, last TEXT DEFAULT '', keep INT DEFAULT 0, sug TEXT DEFAULT '', UNIQUE(device,kind,name,hour))")  # keep: 0 new, 1 kept, -1 deleted (counts erased, not learned again)
    c.execute("CREATE TABLE IF NOT EXISTS learnset(device INT PRIMARY KEY, on_ INT DEFAULT 1)")


def is_on(c, dev):
    r = c.execute("SELECT on_ FROM learnset WHERE device=?", (dev,)).fetchone()
    return r is None or r[0] == 1


def _day(t):
    return time.strftime("%Y-%m-%d", t)


def note(c, dev, action):
    """Count one command. Only a call by name or an app open; nothing else, and never when learning is off."""
    if not isinstance(action, dict) or action.get("type") not in KIND or action.get("raw") or not is_on(c, dev):
        return
    name = str(action.get("name") or "").strip().lower()
    if not NAME.match(name):
        return
    t = time.localtime()
    kind, hr, day = KIND[action["type"]], t.tm_hour, _day(t)
    r = c.execute("SELECT id, last, keep FROM learned WHERE device=? AND kind=? AND name=? AND hour=?", (dev, kind, name, hr)).fetchone()
    if r is None:
        c.execute("INSERT INTO learned(device,kind,name,hour,n,days,last) VALUES(?,?,?,?,1,1,?)", (dev, kind, name, hr, day))
    elif r[2] != -1:
        c.execute("UPDATE learned SET n=n+1, days=days+(?), last=? WHERE id=?", (1 if r[1] != day else 0, day, r[0]))
    old = _day(time.localtime(time.time() - EXPIRE * 86400))
    c.execute("DELETE FROM learned WHERE device=? AND keep=0 AND last<?", (dev, old))
    c.commit()


def _hr(h):
    return f"{h % 12 or 12} {'am' if h < 12 else 'pm'}"


def _text(kind, name, h, n, d):
    return f"You usually {'call' if kind == 'call' else 'open'} {name.title()} around {_hr(h)} ({n} times on {d} days)"


def rows(c, dev):
    return [{"id": i, "text": _text(k, nm, h, n, d), "keep": kp == 1}
            for i, k, nm, h, n, d, kp in c.execute("SELECT id,kind,name,hour,n,days,keep FROM learned WHERE device=? AND keep>=0 AND n>=2 ORDER BY n DESC LIMIT 20", (dev,))]


def suggest(c, dev):
    """One offer for THIS hour, only if it was not done or offered today. The page asks; Yes runs the normal command."""
    if not is_on(c, dev):
        return None
    t = time.localtime()
    r = c.execute("SELECT id,kind,name FROM learned WHERE device=? AND keep>=0 AND hour=? AND n>=? AND days>=? AND last<>? AND sug<>? ORDER BY n DESC LIMIT 1",
                  (dev, t.tm_hour, MIN_N, MIN_DAYS, _day(t), _day(t))).fetchone()
    if not r:
        return None
    verb = "call" if r[1] == "call" else "open"
    return {"id": r[0], "text": f"Sir, around this time you usually {verb} {r[2].title()}. Shall I?", "cmd": f"{verb} {r[2]}"}


def act(c, dev, i, what):
    if what == "keep":
        c.execute("UPDATE learned SET keep=1 WHERE id=? AND device=? AND keep>=0", (i, dev))
    elif what == "delete":
        c.execute("UPDATE learned SET keep=-1, n=0, days=0, last='' WHERE id=? AND device=?", (i, dev))
    elif what in ("yes", "later"):
        c.execute("UPDATE learned SET sug=? WHERE id=? AND device=?", (_day(time.localtime()), i, dev))
    c.commit()


def handle(c, dev, msg, hindi):
    if len(msg) > 60:
        return None
    say = lambda hi, en: hi if hindi else en
    if OFF.match(msg):
        c.execute("INSERT OR REPLACE INTO learnset(device,on_) VALUES(?,0)", (dev,))
        c.commit()
        return say("ठीक है सर, मैं सीखना बंद कर रहा हूँ। जो सीखा है वो कार्ड में है, मिटाने के लिए \"seekha bhool jao\" बोलिए।", "Okay sir, I stopped learning. What I learned stays on the card. Say \"seekha bhool jao\" to erase it.")
    if ON.match(msg):
        c.execute("INSERT OR REPLACE INTO learnset(device,on_) VALUES(?,1)", (dev,))
        c.commit()
        return say("ठीक है सर, फिर से सीख रहा हूँ। सिर्फ़ गिनती, आपके शब्द या स्क्रीन नहीं।", "Okay sir, I am learning again. Counts only, never your words or screen.")
    if WIPE.match(msg):
        c.execute("DELETE FROM learned WHERE device=?", (dev,))
        c.commit()
        return say("सर, जो सीखा था सब मिटा दिया।", "Sir, everything I learned is erased.")
    if SHOW.match(msg):
        r = rows(c, dev)
        head = say("सर, मैंने अब तक यह सीखा है (सिर्फ़ गिनती):", "Sir, this is what I learned so far (counts only):") if r else say("सर, अभी कुछ नहीं सीखा। एक ही समय पर बार-बार कॉल या ऐप खोलना चाहिए।", "Sir, nothing learned yet. It needs a call or an app you repeat around the same hour on a few days.")
        return head + ("\n" + "\n".join("- " + x["text"] for x in r) if r else "") + ("" if is_on(c, dev) else "\n(Learning is OFF.)")
    return None
