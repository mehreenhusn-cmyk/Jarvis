"""Part 83: shopping and packing lists by voice. "list me doodh bread add karo", "list dikhao", "list se doodh hatao", "list saaf karo".
A second word before "list" makes another list ("packing list me charger add karo"). Same database, one small table. Never sent to the AI.
Passwords, OTPs, PINs and card numbers are refused (same rule as notes). Limits: 100 items in all, 40 characters an item, 15 items an add."""
import re
import time

import notes

LW = r"(?:list|लिस्ट)"
IN = r"(?:me|mein|mai|में)"
NAME = r"([A-Za-z\u0900-\u097F]{2,15})"
SKIP = {"meri", "mera", "my", "the", "ye", "yeh", "is", "show", "ek", "a", "mere", "मेरी", "मेरा", "ये", "यह"}
ADDV = r"(?:add\s+karo|add\s+kar\s+do|add\s+kar|add|jodo|jod\s+do|daalo|dalo|daal\s+do|likho|likh\s+do|जोड़ो|जोड़\s+दो|डालो|डाल\s+दो|लिखो)"
ADD = re.compile(r"^\s*(?:" + NAME + r"\s+)?" + LW + r"\s+" + IN + r"\s+(.+?)\s+" + ADDV + r"\s*$", re.I)
SHOW = [re.compile(p, re.I) for p in (
    r"^\s*(?:" + NAME + r"\s+)?" + LW + r"\s+(?:dikhao|dikha\s+do|batao|show|दिखाओ|बताओ)\s*$",
    r"^\s*(?:show|dikhao|meri|my|मेरी)\s+(?:my\s+)?(?:" + NAME + r"\s+)?" + LW + r"(?:\s+(?:dikhao|batao|दिखाओ))?\s*$",
    r"^\s*(?:" + NAME + r"\s+)?" + LW + r"\s+" + IN + r"\s+(?:kya\s+(?:hai|bacha\s+hai)|kitna\s+bacha\s+hai|क्या\s+है)\s*\??\s*$",
    r"^\s*(?:" + NAME + r"\s+)?" + LW + r"\s+(?:kitna\s+bacha\s+hai|में\s+कितना\s+बचा\s+है)\s*\??\s*$")]
DELV = r"(?:hatao|hata\s+do|hata\s+de|remove|delete|nikalo|nikal\s+do|le\s+liya|le\s+li|done|ho\s+gaya|हटाओ|निकालो|ले\s+लिया)"
DEL = re.compile(r"^\s*(?:" + NAME + r"\s+)?" + LW + r"\s+(?:se|" + IN + r")\s+(.+?)\s+" + DELV + r"\s*$", re.I)
CLEAR = re.compile(r"^\s*(?:(?:" + NAME + r"\s+)?" + LW + r"\s+(?:saaf|khali|clear|साफ़|साफ|खाली)(?:\s+karo|\s+kar\s+do|\s+करो)?|clear\s+(?:my\s+)?(?:" + NAME + r"\s+)?" + LW + r")\s*$", re.I)
MAX_ALL, MAX_ITEM, MAX_ADD = 100, 40, 15


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS listitems(id INTEGER PRIMARY KEY, device INT, list TEXT, item TEXT, ts REAL)")


def _name(g):
    g = (g or "").strip().lower()
    return "shopping" if not g or g in SKIP else g


def _rows(c, dev, name):
    return c.execute("SELECT id, item FROM listitems WHERE device=? AND list=? ORDER BY id", (dev, name)).fetchall()


def _show(c, dev, name, hindi):
    r = _rows(c, dev, name)
    if not r:
        return f"सर, {name} लिस्ट खाली है। बोलिए: \"list me doodh add karo\"।" if hindi else f"Sir, the {name} list is empty. Say \"list me doodh add karo\"."
    return (f"सर, आपकी {name} लिस्ट ({len(r)}):\n" if hindi else f"Sir, your {name} list ({len(r)}):\n") + "\n".join(f"{i + 1}. {x}" for i, (_, x) in enumerate(r))


def handle(c, dev, msg, hindi):
    """Reply text for a list command, else None (so the normal chat pipeline goes on)."""
    m = re.sub(r"\s+", " ", msg.strip())
    if len(m) > 400:
        return None
    say = lambda hi, en: hi if hindi else en
    for rx in SHOW:
        g = rx.match(m)
        if g:
            return _show(c, dev, _name(g.group(1)), hindi)
    if CLEAR.match(m):
        g = CLEAR.match(m)
        name = _name(g.group(1) or g.group(2))
        k = c.execute("DELETE FROM listitems WHERE device=? AND list=?", (dev, name)).rowcount
        c.commit()
        return say(f"ठीक है सर, {name} लिस्ट साफ़ ({k} चीज़ें हटीं)।", f"Okay sir, the {name} list is cleared ({k} item(s) removed).")
    g = DEL.match(m)
    if g:
        name, what = _name(g.group(1)), g.group(2).strip().lower().lstrip("#")
        rows = _rows(c, dev, name)
        hit = [rows[int(what) - 1]] if what.isdigit() and 1 <= int(what) <= len(rows) else [r for r in rows if r[1].lower() == what] or [r for r in rows if what in r[1].lower()][:1]
        if not hit:
            return say(f"सर, {name} लिस्ट में \"{what}\" नहीं मिला।", f"Sir, I found no \"{what}\" in the {name} list.")
        c.execute("DELETE FROM listitems WHERE id=? AND device=?", (hit[0][0], dev))
        c.commit()
        return say(f"ठीक है सर, \"{hit[0][1]}\" हटा दिया।", f"Okay sir, \"{hit[0][1]}\" removed from the {name} list.")
    g = ADD.match(m)
    if g:
        name = _name(g.group(1))
        sep = r"\s*(?:,|;|\band\b|\baur\b|और)\s*"  # with commas or "aur" each part is one item ("brown bread, doodh"); with only spaces each word is one item
        items = [x.strip(" .") for x in re.split(sep if re.search(sep, g.group(2)) else r"\s+", g.group(2)) if x.strip(" .")]
        if not items:
            return None
        if any(notes.SECRET.search(x) for x in items):
            return say("सर, मैं पासवर्ड, OTP, PIN या कार्ड नंबर नहीं सहेजता, इसलिए लिस्ट में कुछ नहीं जोड़ा।", "Sir, I do not save passwords, OTPs, PINs or card numbers, so nothing was added.")
        if len(items) > MAX_ADD or any(len(x) > MAX_ITEM for x in items):
            return say("सर, एक बार में 15 चीज़ें और हर चीज़ 40 अक्षर तक।", "Sir, 15 items at a time and 40 characters each at most.")
        have = {x.lower() for _, x in _rows(c, dev, name)}
        new = [x for x in dict.fromkeys(i.lower() for i in items) if x not in have]
        if c.execute("SELECT count(*) FROM listitems WHERE device=?", (dev,)).fetchone()[0] + len(new) > MAX_ALL:
            return say("सर, लिस्ट भर गई (100 चीज़ें)। कुछ हटाइए: \"list se doodh hatao\"।", "Sir, the lists are full (100 items). Remove some: \"list se doodh hatao\".")
        for x in new:
            c.execute("INSERT INTO listitems(device, list, item, ts) VALUES(?,?,?,?)", (dev, name, x, time.time()))
        c.commit()
        if not new:
            return say(f"सर, ये पहले से {name} लिस्ट में हैं।", f"Sir, these are already in the {name} list.")
        return say(f"ठीक है सर, {name} लिस्ट में जोड़ा: ", f"Okay sir, added to the {name} list: ") + ", ".join(new)
    return None
