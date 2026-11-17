"""Parts 113 + 114: reminders by place and by Bluetooth. Your own words and text only, never sent to the AI.
Part 113: `is jagah ko ghar naam do` saves the spot you stand on (name, position, radius 150 m). Then `jab ghar pahunchu doodh lena yaad dilana`
or `jab ghar se niklu chabi lena` fires once on arriving or leaving (`har baar` = every time). `place reminders`, `place reminder hatao 2`,
`jagah hatao ghar`, `jagah radius ghar 300`, `place watch off` / `place watch on`.
Part 114: `jab JBL bluetooth jude to gaadi ka note dekhna` shows a note when a Bluetooth device with that word in its name connects.
The phone position is compared INSIDE the Android app and thrown away: it never reaches this server, the AI or any file. Only the spots you saved are kept.
Battery: the app looks every 2 minutes near a saved place and every 10 minutes far from all of them, and only while a reminder exists."""
import re

import place
from notes import SECRET

MAX_PLACES, MAX_WATCH = 8, 20
N = r"(.{2,20}?)"
T = r"(.{3,140})"
OPEN = r"^\s*(?:jab|jb|when)\s+(?:main\s+|mai\s+|mein\s+|i\s+)?(?:apne\s+|apni\s+|my\s+|the\s+)?"
GAP = r"\s*(?:to\s+|toh\s+|tab\s+|,\s*)?"
ARR = r"(?:(?:pahunch|pohonch|pahoch|pahuch)\w*(?:\s+(?:jau+n?|jaye|gaya))?|aau+n?|aa\s*jau+n?|aa\s*gaya|aa\s*jaye)"
LEA = r"(?:nikl\w*|chhod\w*|chod\w*)"
SAVE = (re.compile(r"^\s*(?:is\s+jagah\s+ko|yahan\s+ko|yeh\s+jagah|ye\s+jagah)\s+" + N + r"\s+(?:naam\s+do|save\s+karo|set\s+karo|bana\s+do|rakho|rakh\s+do)\s*$", re.I),
        re.compile(r"^\s*(?:save\s+(?:this\s+place|this\s+spot|here)\s+as|name\s+this\s+place)\s+" + N + r"\s*$", re.I))
ADDP = ((re.compile(OPEN + N + r"\s+(?:pe\s+|par\s+|me\s+|mein\s+|tak\s+|at\s+)?" + ARR + GAP + T + r"$", re.I), "arrive", False),
        (re.compile(OPEN + N + r"\s+se\s+(?:bahar\s+)?" + LEA + GAP + T + r"$", re.I), "leave", False),
        (re.compile(r"^\s*remind\s+me\s+(?:to\s+)?" + T + r"\s+when\s+i\s+(?:reach|arrive\s+at|get(?:\s+to)?)\s+(?:the\s+|my\s+)?" + N + r"\s*$", re.I), "arrive", True),
        (re.compile(r"^\s*remind\s+me\s+(?:to\s+)?" + T + r"\s+when\s+i\s+(?:leave|exit|get\s+out\s+of)\s+(?:the\s+|my\s+)?" + N + r"\s*$", re.I), "leave", True))
BTW = re.compile(r"\b(?:bluetooth|bt)\b\s*", re.I)  # Part 114: a message is a Bluetooth one only when it says so
ADDB = ((re.compile(OPEN + N + r"\s+(?:connect\w*|jud\w*|jod\w*|lag\w*)(?:\s+(?:ho\w*|jaye|jaaye|jata\s+hai))?" + GAP + T + r"$", re.I), False),
        (re.compile(r"^\s*remind\s+me\s+(?:to\s+)?" + T + r"\s+when\s+(?:my\s+)?" + N + r"\s+(?:connects?|gets?\s+connected)\s*$", re.I), True))
RAD = re.compile(r"^\s*(?:jagah\s+radius|place\s+radius|radius)\s+" + N + r"\s+(\d{2,4})\s*(?:m|meter|metre|mtr)?\s*$", re.I)
DELP = re.compile(r"^\s*(?:jagah|place)\s+(?:hatao|delete|remove)\s+" + N + r"\s*$", re.I)
DELW = re.compile(r"^\s*(?:place|jagah|bluetooth|bt)\s+(?:reminder|note)s?\s+(?:hatao|delete|remove)\s+#?(\d+)\s*$", re.I)
LIST = re.compile(r"^\s*(?:place\s+reminders?|jagah\s+(?:wale\s+)?reminders?|meri\s+jagah(?:en|ein)?|my\s+places|bluetooth\s+reminders?)\s*$", re.I)
SW = re.compile(r"^\s*place\s+watch\s+(on|off|chalu\s+karo|band\s+karo)\s*$", re.I)
TAIL = re.compile(r"[\s,.]*(?:ye\s+|yeh\s+)?(?:mujhe\s+|muje\s+)?(?:yaad\s*dila\w*|yaad\s*karana|bata\w*|bol\w*|remind\s*(?:me|karna|kar\s*do)?)\s*[.!]?\s*$", re.I)
HEAD = re.compile(r"^(?:ki\s+|ke\s+|to\s+|toh\s+|tab\s+|that\s+)+", re.I)
REPW = re.compile(r"\b(?:har\s*baar|every\s*time|hamesha|always)\b", re.I)
ALIAS = {"home": "ghar", "ghar": "home"}
CH = set()  # devices whose list changed: the page then hands the new copy to the Android app


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS places(id INTEGER PRIMARY KEY, device INT, name TEXT, lat REAL, lon REAL, r INT DEFAULT 150)")
    c.execute("CREATE TABLE IF NOT EXISTS pwatch(id INTEGER PRIMARY KEY, device INT, kind TEXT, target TEXT, ev TEXT, text TEXT, rep INT DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS pcfg(device INT PRIMARY KEY, on_ INT DEFAULT 1)")


def _on(c, dev):
    r = c.execute("SELECT on_ FROM pcfg WHERE device=?", (dev,)).fetchone()
    return 0 if r and r[0] == 0 else 1


def sync(c, dev):
    """The copy the Android app keeps. Empty lists while the switch is off, so the watch stops."""
    on = _on(c, dev)
    pl = [{"id": i, "name": n, "lat": a, "lon": o, "r": r} for i, n, a, o, r in c.execute("SELECT id, name, lat, lon, r FROM places WHERE device=? ORDER BY id", (dev,))] if on else []
    w = [{"id": i, "kind": k, "target": t, "ev": e, "text": x, "rep": p} for i, k, t, e, x, p in c.execute("SELECT id, kind, target, ev, text, rep FROM pwatch WHERE device=? ORDER BY id", (dev,))] if on else []
    return {"on": on, "places": pl, "w": w}


def take(c, dev):
    """After a chat command that changed something: the new copy once, else None."""
    if dev in CH:
        CH.discard(dev)
        return sync(c, dev)
    return None


def fired(c, dev, wid):
    """The app says a once-only reminder has been shown: remove it. `har baar` ones stay."""
    c.execute("DELETE FROM pwatch WHERE device=? AND id=? AND rep=0", (dev, wid))
    c.commit()
    return True


def _clean(t):
    rep = 1 if REPW.search(t) else 0
    t = TAIL.sub("", HEAD.sub("", TAIL.sub("", REPW.sub("", t))))
    return re.sub(r"\s+", " ", t).strip(" ,.-"), rep


def _find(rows, n):
    n = n.strip().lower()
    for key in (n, ALIAS.get(n)):
        for r in rows:
            if key and r[1] == key:
                return r
    for r in rows:
        if len(n) >= 3 and (r[1].startswith(n) or n.startswith(r[1])):
            return r
    return None


def _parse(m):
    """-> (kind, name, event, text, repeat) or None. kind is place or bt."""
    b = BTW.search(m)
    if b and not re.search(ARR + "|" + LEA, m[:b.start()], re.I):  # Part 114
        s = BTW.sub("", m, count=1)
        for rx, en in ADDB:
            g = rx.match(s)
            if g:
                t, n = (g.group(1), g.group(2)) if en else (g.group(2), g.group(1))
                t, rep = _clean(t)
                return "bt", re.sub(r"\s+(?:ka|ki|ke)$", "", n.strip().lower()), "connect", t, rep
    for rx, ev, en in ADDP:
        g = rx.match(m)
        if g:
            t, n = (g.group(1), g.group(2)) if en else (g.group(2), g.group(1))
            t, rep = _clean(t)
            return "place", n.strip().lower(), ev, t, rep
    return None


def handle(c, dev, msg, hindi, loc):
    m = re.sub(r"\s+", " ", msg.strip())
    if len(m) > 200:
        return None
    say = lambda hi, en: hi if hindi else en
    rows = c.execute("SELECT id, name, lat, lon, r FROM places WHERE device=? ORDER BY id", (dev,)).fetchall()
    for rx in SAVE:
        g = rx.match(m)
        if g:
            n = g.group(1).strip().lower()
            p = place.parse(loc)
            if SECRET.search(n):
                return say("सर, ये नाम नहीं रख सकता।", "Sir, I cannot use that name.")
            if not p:
                return say("सर, लोकेशन नहीं मिली। लोकेशन की अनुमति दीजिए और फिर बोलिए।", "Sir, I could not get your location. Allow location access and say it again.")
            if p[2] > 200:
                return say(f"सर, लोकेशन सिर्फ ±{p[2]} मीटर पक्की है। खुली जगह से फिर बोलिए।", f"Sir, the position is only accurate to ±{p[2]} m. Stand in the open and say it again.")
            r = 150 if p[2] <= 100 else min(300, int(p[2] * 1.5))
            old = next((x for x in rows if x[1] == n), None)
            if old:
                c.execute("UPDATE places SET lat=?, lon=?, r=? WHERE id=?", (p[0], p[1], r, old[0]))
            elif len(rows) >= MAX_PLACES:
                return say("सर, 8 जगहों की सीमा पूरी है। `jagah hatao <naam>` बोलिए।", "Sir, the limit of 8 places is full. Say `jagah hatao <name>` first.")
            else:
                c.execute("INSERT INTO places(device, name, lat, lon, r) VALUES(?,?,?,?,?)", (dev, n, p[0], p[1], r))
            c.commit()
            CH.add(dev)
            return say(f"ठीक है, ये जगह '{n.title()}' सेव हो गई (दायरा {r} मीटर)। लोकेशन फ़ोन के अंदर ही जाँची जाती है, कहीं भेजी या सेव नहीं होती।",
                       f"Okay, this spot is saved as '{n.title()}' (radius {r} m). The position is checked inside the phone only, never sent or saved.")
    g = RAD.match(m)
    if g:
        x, r = _find(rows, g.group(1)), int(g.group(2))
        if not x or not 50 <= r <= 1000:
            return say("सर, जगह नहीं मिली या दायरा 50 से 1000 मीटर के बीच रखिए।", "Sir, place not found, or keep the radius between 50 and 1000 m.")
        c.execute("UPDATE places SET r=? WHERE id=?", (r, x[0]))
        c.commit()
        CH.add(dev)
        return say(f"ठीक है, {x[1].title()} का दायरा {r} मीटर।", f"Okay, the radius of {x[1].title()} is {r} m.")
    g = DELP.match(m)
    if g:
        x = _find(rows, g.group(1))
        if not x:
            return say("सर, ये जगह सेव नहीं है।", "Sir, that place is not saved.")
        c.execute("DELETE FROM pwatch WHERE device=? AND kind='place' AND target=?", (dev, x[1]))
        c.execute("DELETE FROM places WHERE id=?", (x[0],))
        c.commit()
        CH.add(dev)
        return say(f"ठीक है, {x[1].title()} और उसके रिमाइंडर हटा दिए।", f"Okay, {x[1].title()} and its reminders are removed.")
    g = DELW.match(m)
    if g:
        n = c.execute("DELETE FROM pwatch WHERE device=? AND id=?", (dev, int(g.group(1)))).rowcount
        c.commit()
        CH.add(dev)
        return say("ठीक है, हटा दिया।", "Okay, removed.") if n else say("सर, इस नंबर का रिमाइंडर नहीं मिला।", "Sir, no reminder with that number.")
    g = SW.match(m)
    if g:
        on = 1 if g.group(1).lower() in ("on", "chalu karo") else 0
        c.execute("INSERT OR REPLACE INTO pcfg(device, on_) VALUES(?,?)", (dev, on))
        c.commit()
        CH.add(dev)
        return say("ठीक है, जगह और ब्लूटूथ रिमाइंडर चालू।", "Okay, place and Bluetooth reminders are ON.") if on else say("ठीक है, जगह और ब्लूटूथ चेक बंद। रिमाइंडर सेव हैं।", "Okay, place and Bluetooth checking is OFF. The reminders stay saved.")
    if LIST.match(m):
        ws = c.execute("SELECT id, kind, target, ev, text, rep FROM pwatch WHERE device=? ORDER BY id", (dev,)).fetchall()
        if not rows and not ws:
            return say("सर, कोई जगह या ब्लूटूथ रिमाइंडर नहीं है। जैसे: `is jagah ko ghar naam do`", "Sir, there are no place or Bluetooth reminders. Try: `is jagah ko ghar naam do`")
        evn = {"arrive": "on arriving", "leave": "on leaving", "connect": "when connected"}
        out = [f"#{i} {'Bluetooth ' if k == 'bt' else ''}{t.title()} ({evn[e]}{', every time' if p else ''}): {x}" for i, k, t, e, x, p in ws]
        out += [f"Place: {x[1].title()} ({x[4]} m)" for x in rows]
        return ("Place and Bluetooth reminders" + (" (switch is OFF)" if not _on(c, dev) else "") + ":\n") + "\n".join(out)
    got = _parse(m)
    if not got:
        return None
    kind, n, ev, t, rep = got
    if SECRET.search(t) or SECRET.search(n) or not 3 <= len(t) <= 120:
        return say("सर, ये रिमाइंडर नहीं बन पाया।", "Sir, that reminder did not work.")
    if kind == "place":
        x = _find(rows, n)
        if not x:
            return say(f"सर, '{n}' जगह सेव नहीं है। वहाँ जाकर बोलिए: `is jagah ko {n} naam do`", f"Sir, the place '{n}' is not saved. Go there and say: `is jagah ko {n} naam do`")
        n = x[1]
    if c.execute("SELECT count(*) FROM pwatch WHERE device=?", (dev,)).fetchone()[0] >= MAX_WATCH:
        return say("सर, 20 रिमाइंडर की सीमा पूरी है।", "Sir, the limit of 20 place and Bluetooth reminders is full.")
    c.execute("INSERT INTO pwatch(device, kind, target, ev, text, rep) VALUES(?,?,?,?,?,?)", (dev, kind, n, ev, t, rep))
    c.execute("INSERT OR IGNORE INTO pcfg(device, on_) VALUES(?,1)", (dev,))
    c.commit()
    CH.add(dev)
    how = {"arrive": ("पहुँचेंगे", "reach"), "leave": ("निकलेंगे", "leave")}.get(ev)
    when = say(f"{n.title()} {how[0]}", f"you {how[1]} {n.title()}") if kind == "place" else say(f"'{n}' ब्लूटूथ जुड़ेगा", f"the Bluetooth '{n}' connects")
    return say(f"ठीक है, जब {when} तब दिखाऊँगा: {t}" + (" (हर बार)" if rep else " (एक बार)") + "। फ़ोन कुछ मिनट देर से देख सकता है।",
               f"Okay, when {when} I will show: {t}" + (" (every time)" if rep else " (once)") + ". The phone may notice a few minutes late. Android may ask for permission.")
