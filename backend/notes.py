"""Part 71/72: voice notes. Saved ONLY when you say "note karo ..." (your words are the permission). Listed and searched later by voice.
Same database, one small table. Notes are never sent to the AI. Secrets (password, OTP, PIN, CVV, card numbers) are refused."""
import re
import time

SECRET = re.compile(r"password|passcode|\botp\b|\bpin\b|\bcvv\b|card number|पासवर्ड|ओटीपी|पिन|\b\d{12,19}\b", re.I)
VERB = r"(?:karo|kar\s+lo|kar\s+do|kar\s+le|likho|likh\s+lo|likh\s+do|likh\s+le|lo|करो|कर\s+लो|कर\s+दो|लिखो|लिख\s+लो)"
SAVE = re.compile(r"^\s*(?:(?:ek|a|एक)\s+)?(?:voice\s+)?(?:note|नोट)\s+" + VERB + r"\s*[:,\-]?\s*(?:ki|ke|that|कि)?\s*(.+)$|"
                  r"^\s*(?:(?:note\s+down|take\s+(?:a\s+)?note|note\s+this|voice\s+note)\s*[:,\-]?|note\s*[:\-])\s*(?:that\s+)?(.+)$", re.I | re.S)
LIST = re.compile(r"^\s*(?:(?:meri|mere|my|मेरी|मेरे)\s+(?:last\s+|recent\s+)?(?:notes?|नोट्स?)(?:\s+(?:dikhao|batao|list|show|दिखाओ|बताओ))?|show\s+(?:my\s+)?notes|notes?\s+(?:dikhao|list|batao|दिखाओ)|last\s+notes?)\s*$", re.I)
FIND = [re.compile(p, re.I) for p in (
    r"^\s*(?:my\s+)?(?:notes?|नोट्स?)\s+(?:me|mein|mai|में)\s+(.+?)\s+(?:dhundo|dhoondo|khojo|search(?:\s+karo)?|dekho|dikhao|ढूंढो|ढूँढो|खोजो)\s*$",
    r"^\s*search\s+(?:my\s+)?notes?\s+for\s+(.+?)\s*$",
    r"^\s*(.+?)\s+(?:wala|wali|वाला|वाली)\s+(?:note|नोट)\s*(?:dikhao|batao|dikha\s+do|दिखाओ)?\s*$")]
DEL = re.compile(r"^\s*(?:(?:delete|remove|hatao|hata\s+do|mita\s+do|हटाओ)\s+(?:note|नोट)\s*#?(\d+)|(?:note|नोट)\s*#?(\d+)\s+(?:delete|hata\s+do|hatao|mita\s+do|हटाओ))\s*$", re.I)
MAX_NOTES, MAX_LEN = 300, 500


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, device INT, text TEXT, ts REAL)")


def _when(ts):
    return time.strftime("%d %b %H:%M", time.localtime(ts))


def _show(rows, hindi, head_en, head_hi):
    if not rows:
        return None
    lines = [f"#{i}  {_when(t)}  {x}" for i, x, t in rows]
    return (head_hi if hindi else head_en) + "\n" + "\n".join(lines)


def handle(c, dev, msg, hindi):
    """Reply text for a notes command, else None (so the normal chat pipeline goes on)."""
    m = msg.strip()
    if len(m) > 700:
        return None
    d = DEL.match(m)
    if d:
        n = int(d.group(1) or d.group(2))
        got = c.execute("DELETE FROM notes WHERE id=? AND device=?", (n, dev)).rowcount
        c.commit()
        return (f"नोट #{n} हटा दिया सर।" if hindi else f"Note #{n} deleted, sir.") if got else (f"सर, #{n} नंबर का नोट नहीं मिला।" if hindi else f"Sir, I found no note #{n}.")
    if LIST.match(m):
        rows = c.execute("SELECT id, text, ts FROM notes WHERE device=? ORDER BY id DESC LIMIT 8", (dev,)).fetchall()
        return _show(rows, hindi, "Your latest notes, sir:", "आपके आख़िरी नोट सर:") or ("अभी कोई नोट नहीं है सर। बोलिए \"note karo ...\"।" if hindi else "You have no notes yet, sir. Say \"note karo ...\".")
    for rx in FIND:
        f = rx.match(m)
        if f:
            q = f.group(1).strip().lower()
            if len(q) < 2:
                return None
            allrows = c.execute("SELECT id, text, ts FROM notes WHERE device=? ORDER BY id DESC", (dev,)).fetchall()
            rows = [r for r in allrows if q in r[1].lower()][:8]  # plain text match in Python, no SQL pattern characters to escape
            return _show(rows, hindi, f'Notes with "{q}":', f'"{q}" वाले नोट:') or (f'सर, "{q}" वाला कोई नोट नहीं मिला।' if hindi else f'Sir, I found no note with "{q}".')
    s = SAVE.match(m)
    if s:
        text = (s.group(1) or s.group(2) or "").strip()
        if len(text) < 2:
            return None
        if SECRET.search(text):
            return "सर, मैं पासवर्ड, OTP, PIN या कार्ड नंबर नहीं सहेजता, इसलिए यह नोट नहीं बना।" if hindi else "Sir, I do not save passwords, OTPs, PINs or card numbers, so this note was not saved."
        if len(text) > MAX_LEN:
            return "सर, नोट बहुत लंबा है (500 अक्षर तक)।" if hindi else "Sir, that note is too long (500 characters at most)."
        if c.execute("SELECT count(*) FROM notes WHERE device=?", (dev,)).fetchone()[0] >= MAX_NOTES:
            return "सर, नोट भर गए (300)। पुराने हटाइए: \"delete note 3\"।" if hindi else "Sir, the notes are full (300). Delete old ones: \"delete note 3\"."
        cur = c.execute("INSERT INTO notes(device, text, ts) VALUES(?,?,?)", (dev, text, time.time()))
        c.commit()
        return f"नोट #{cur.lastrowid} सहेज लिया सर: {text}" if hindi else f"Note #{cur.lastrowid} saved, sir: {text}"
    return None
