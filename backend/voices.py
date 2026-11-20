"""Part 144: known voices. Only numbers are kept: a voice print of 128 numbers (never a recording), a name, the date of the last talk.
Saved ONLY after the person said yes aloud and the owner tapped Save. Stays in the phone's database, is in the guest guard,
is wiped by `delete everything`, is never sent to the AI and is never used as a password or for security."""
import json, math, re, time
import memory, people

MATCH = 0.45  # cosine distance under this = the same voice. UNTESTED on a real phone: tune it after the first tests (README Part 144)
UNSURE = 0.60  # between MATCH and this Jarvis says he is not sure and asks, he never guesses
MAXV = 20
NAME = re.compile(r"^[^\W\d_][\w .'\-]{0,29}$", re.U)
LIST = re.compile(r"^\s*(?:known voices|voices i know|kiski awaaz (?:yaad|pata) hai|kin kin ki awaaz (?:yaad|pata) hai|awaaz list)\s*\??\s*$", re.I)
FORGET = re.compile(r"^\s*(?:forget voice|delete voice|awaaz bhool(?:o| jao)?|awaaz hatao)\s+(.{1,30}?)\s*$", re.I)
FORGET_ALL = re.compile(r"^\s*(?:forget all voices|delete all voices|sab awaaz (?:bhool jao|bhoolo|hatao|mitao))\s*$", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS voices(id INTEGER PRIMARY KEY, device INT, name TEXT, vec TEXT, owner INT, last REAL, ts REAL)")


def clean(v):
    """The 128 numbers from the phone, or None if they are not numbers."""
    if not isinstance(v, list) or not 64 <= len(v) <= 512:
        return None
    try:
        out = [float(x) for x in v]
    except (TypeError, ValueError):
        return None
    return out if all(math.isfinite(x) for x in out) and any(out) else None


def dist(a, b):
    if len(a) != len(b):
        return 9.0
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return 9.0 if not na or not nb else 1.0 - sum(x * y for x, y in zip(a, b)) / (na * nb)


def rows(c, dev):
    return [{"name": n, "owner": bool(o), "last": l} for n, o, l in c.execute("SELECT name, owner, last FROM voices WHERE device=? ORDER BY id", (dev,))]


def days_ago(t):
    return None if not t else max(0, int((time.time() - t) // 86400))


def match(c, dev, vec):
    """Who is it? state is match, unsure or unknown. No score is shown to anyone. On a match the date of the last talk is renewed."""
    v = clean(vec)
    if v is None:
        return {"state": "bad"}
    best = None
    for i, n, o, raw, last in c.execute("SELECT id, name, owner, vec, last FROM voices WHERE device=?", (dev,)).fetchall():
        try:
            d = dist(v, json.loads(raw))
        except ValueError:
            continue
        if best is None or d < best[0]:
            best = (d, i, n, o, last)
    if best is None or best[0] >= UNSURE:
        return {"state": "unknown"}
    d, i, n, o, last = best
    if d >= MATCH:
        return {"state": "unsure", "name": n}
    c.execute("UPDATE voices SET last=? WHERE id=?", (time.time(), i))
    c.commit()
    pn = [] if o else people.notes(c, dev, n)
    return {"state": "match", "name": n, "owner": bool(o), "ago": days_ago(last), "note": pn[-1] if pn else ""}


def save(c, dev, name, vec, owner):
    """Only called after a yes. Same name again = the new numbers are averaged in. Returns True or a short reason."""
    v = clean(vec)
    name = (name or "").strip()
    if v is None:
        return "bad voice numbers"
    if owner:
        name = "Owner"
    elif not NAME.match(name) or memory.SECRET.search(name):
        return "that name cannot be saved"
    row = c.execute("SELECT id, vec FROM voices WHERE device=? AND lower(name)=?", (dev, name.lower())).fetchone()
    if row:
        try:
            old = json.loads(row[1])
            if len(old) == len(v):
                v = [(a + b) / 2 for a, b in zip(old, v)]
        except ValueError:
            pass
        c.execute("UPDATE voices SET vec=?, last=? WHERE id=?", (json.dumps(v), time.time(), row[0]))
    else:
        if c.execute("SELECT count(*) FROM voices WHERE device=?", (dev,)).fetchone()[0] >= MAXV:
            return "too many voices saved (20)"
        c.execute("INSERT INTO voices(device, name, vec, owner, last, ts) VALUES(?,?,?,?,?,?)", (dev, name, json.dumps(v), 1 if owner else 0, time.time(), time.time()))
    c.commit()
    return True


def forget(c, dev, name=None):
    if name is None:
        k = c.execute("DELETE FROM voices WHERE device=?", (dev,)).rowcount
    else:
        k = c.execute("DELETE FROM voices WHERE device=? AND lower(name)=?", (dev, name.lower().strip())).rowcount
    c.commit()
    return k


def handle(c, dev, msg, hindi):
    """Chat words that need no microphone: the list, and forgetting one voice or all. Starting a voice check is done by the page."""
    def say(hi, en):
        return hi if hindi else en
    if LIST.match(msg):
        r = rows(c, dev)
        if not r:
            return say("सर, मुझे अभी किसी की आवाज़ याद नहीं है।", "Sir, I do not remember anyone's voice yet. Say: meri awaaz yaad rakho")
        return say("मुझे इनकी आवाज़ याद है: ", "I remember these voices: ") + ", ".join(("you (owner)" if x["owner"] else x["name"]) for x in r) + say("। मिटाने के लिए: awaaz bhoolo नाम", ". To delete one say: awaaz bhoolo NAME")
    if FORGET_ALL.match(msg):
        return say("ठीक है सर, सब आवाज़ें मिटा दीं।", "Done, sir. All saved voices are deleted.") if forget(c, dev) else say("सर, कोई आवाज़ सेव नहीं थी।", "Sir, no voice was saved.")
    m = FORGET.match(msg)
    if m:
        n = m.group(1).strip()
        k = forget(c, dev, "Owner" if re.match(r"^(?:meri|my|owner|mera)$", n, re.I) else n)
        return say(f"ठीक है सर, {n} की आवाज़ मिटा दी।", f"Done, sir. The voice of {n} is deleted.") if k else say(f"सर, {n} की आवाज़ सेव नहीं है।", f"Sir, I have no saved voice for {n}.")
    return None
