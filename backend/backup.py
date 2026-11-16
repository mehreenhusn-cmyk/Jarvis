"""Jarvis backup (Part 47): memory, people, reminders, ledger and routines (chat history only if you tick it) in ONE file locked with a passphrase.
The lock is OpenSSL's AES-256 with a key made from your passphrase (pbkdf2, 200000 rounds). We do not write our own encryption.
Needs: pkg install openssl-tool (Termux). The passphrase is never saved, never put in chat, never written to a log.
The file goes to the phone's Downloads folder (same place as the zips) with the name Jarvis_backup_DATE.jbk.
Restore is a MERGE: it only adds what is not already there (preview first). API keys, pairing and tasks are never in a backup."""
import base64, glob, hashlib, json, os, re, subprocess, tempfile, time

import memory, people

DIR = os.environ.get("JARVIS_DL") or os.path.join(os.path.expanduser("~"), "storage", "downloads")
MAGIC = "JARVISBK1"
# table: (columns saved, columns that make a row "the same", extra WHERE)
T = {"memories": ("text", "text", ""), "notes": ("text,ts", "text", ""), "people": ("name,note", "name,note", ""),
     "reminders": ("text,due,rep", "text,due,rep", "AND sent=0"), "ledger": ("who,amount,dir,due,note,paid", "who,amount,dir,due,note,paid", "AND paid=0"),
     "routines": ("name,phrase,at,days", "name", ""), "messages": ("role,content,ts", "role,content,ts", ""),
     "listitems": ("list,item", "list,item", ""), "habits": ("name,day", "name,day", ""), "spend": ("amount,what,cat,day", "amount,what,cat,day", ""),
     "decisions": ("kind,text,day,shown", "kind,text,day", "AND done=0"), "moods": ("day,score", "day", ""),
     "touch": ("name,last,every", "name", ""), "contracts": ("name,start,days,penalty", "name", ""),
     "capsules": ("text,due,made,opened", "text,due", "")}  # Parts 93-96  # Part 83: shopping lists, habits and their check-ins; Part 84: spending
NAME = re.compile(r"^Jarvis_backup_[0-9A-Za-z_\-]{1,40}\.jbk$")
PHRASE = "DELETE ALL MY JARVIS DATA"
ASK = re.compile(r"^\s*(?:delete|erase|wipe)\s+(?:everything|all my (?:jarvis )?data)\s*$", re.I)
HOW = re.compile(r"^\s*(?:backup|backup kaise|how (?:do i|to) (?:make a )?backup|restore)\s*\??\s*$", re.I)


def _ssl(decrypt, data, pw):
    """openssl enc. Passphrase goes in on stdin (not on the command line, not in a file)."""
    if len(pw) < 8:
        raise RuntimeError("passphrase must be at least 8 characters")
    fi, fo = tempfile.mkstemp(), tempfile.mkstemp()
    os.close(fo[0])
    try:
        os.write(fi[0], data)
        os.close(fi[0])
        cmd = ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-iter", "200000", "-salt", "-a", "-A", "-pass", "stdin", "-in", fi[1], "-out", fo[1]] + (["-d"] if decrypt else [])
        try:
            r = subprocess.run(cmd, input=pw.encode(), capture_output=True, timeout=60)
        except FileNotFoundError:
            raise RuntimeError("openssl is not installed. Run in Termux: pkg install openssl-tool")
        if r.returncode != 0:
            raise RuntimeError("wrong passphrase, or the file is damaged" if decrypt else "could not lock the file")
        return open(fo[1], "rb").read()
    finally:
        for p in (fi[1], fo[1]):
            try:
                os.remove(p)
            except OSError:
                pass


def _pack(obj):
    body = json.dumps(obj, ensure_ascii=False)
    return (MAGIC + "\n" + hashlib.sha256(body.encode()).hexdigest() + "\n" + body).encode()


def _unpack(raw):
    try:
        magic, digest, body = raw.decode().split("\n", 2)
        ok = magic == MAGIC and hashlib.sha256(body.encode()).hexdigest() == digest
        obj = json.loads(body) if ok else None
    except (ValueError, UnicodeDecodeError):
        ok, obj = False, None
    if not ok or not isinstance(obj, dict) or not isinstance(obj.get("data"), dict):
        raise RuntimeError("wrong passphrase, or the file is damaged")
    return obj["data"]


def export(c, dev, chat=False):
    out = {}
    for t, (cols, _, extra) in T.items():
        if t == "messages" and not chat:
            continue
        out[t] = [list(r) for r in c.execute(f"SELECT {cols} FROM {t} WHERE device=? {extra} ORDER BY id", (dev,))]
    return out


def make(c, dev, pw, chat=False):
    """Writes the file. Returns {file, dir, counts}."""
    if not os.path.isdir(DIR):
        raise RuntimeError("Downloads folder not found. Run in Termux: termux-setup-storage")
    data = export(c, dev, chat)
    blob = _ssl(False, _pack({"v": 1, "made": int(time.time()), "data": data}), pw)
    name = time.strftime("Jarvis_backup_%Y-%m-%d_%H%M.jbk")
    path = os.path.join(DIR, name)
    with open(path, "wb") as f:
        f.write(blob)
    return {"file": name, "dir": DIR, "counts": {t: len(v) for t, v in data.items()}}


def files():
    out = []
    for p in sorted(glob.glob(os.path.join(DIR, "Jarvis_backup_*.jbk")), reverse=True)[:10]:
        n = os.path.basename(p)
        if NAME.match(n):
            out.append({"name": n, "size": os.path.getsize(p), "ts": int(os.path.getmtime(p))})
    return out


def _load(name, pw):
    if not NAME.match(str(name)):
        raise RuntimeError("file name not allowed")
    p = os.path.join(DIR, name)
    if not os.path.isfile(p):
        raise RuntimeError("backup file not found")
    return _unpack(_ssl(True, open(p, "rb").read(), pw))


def _new_rows(c, dev, t, rows):
    """Rows of the backup that are not on this phone yet (and are safe: no password, OTP or PIN words)."""
    cols, key, extra = T[t]
    names = cols.split(",")
    idx = [names.index(k) for k in key.split(",")]
    have = {tuple(r) for r in c.execute(f"SELECT {key} FROM {t} WHERE device=?", (dev,))}
    out = []
    for r in rows if isinstance(rows, list) else []:
        if t == "routines" and isinstance(r, list) and len(r) == 2:
            r = r + ["", ""]  # Part 82: backups made before this Part have no time or days
        if not isinstance(r, list) or len(r) != len(names):
            continue
        if t == "routines":  # Part 82: the routine's time (HH:MM) and days (wk, we or empty) come back too; anything odd becomes "every day, no time"
            r = r[:2] + [r[2] if isinstance(r[2], str) and re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", r[2]) else "", r[3] if r[3] in ("wk", "we") else ""]
        if any(isinstance(x, str) and memory.SECRET.search(x) for x in r):
            continue
        k = tuple(r[i] for i in idx)
        if k not in have:
            have.add(k)
            out.append(r)
    return out


def preview(c, dev, name, pw):
    data = _load(name, pw)
    return {t: {"new": len(_new_rows(c, dev, t, data.get(t, []))), "total": len(data.get(t, []) if isinstance(data.get(t), list) else [])} for t in T if t in data}


def restore(c, dev, name, pw):
    """Merge: adds only new rows. People go through people.add (its limits), memories stop at 100."""
    data = _load(name, pw)
    added = {}
    for t, (cols, _, _) in T.items():
        if t not in data:
            continue
        new, n = _new_rows(c, dev, t, data[t]), 0
        for r in new:
            if t == "people":
                n += 1 if people.add(c, dev, r[0], r[1]) else 0
                continue
            if t == "memories" and c.execute("SELECT count(*) FROM memories WHERE device=?", (dev,)).fetchone()[0] >= 100:
                break
            if t == "notes" and c.execute("SELECT count(*) FROM notes WHERE device=?", (dev,)).fetchone()[0] >= 300:
                break
            ph = ",".join("?" * len(r))
            extra_cols, extra_vals = ("device,ts", (dev, time.time())) if t in ("memories", "routines") else ("device", (dev,))
            if t == "reminders":
                extra_cols, extra_vals = "device,sent", (dev, 0)
            c.execute(f"INSERT INTO {t}({cols},{extra_cols}) VALUES({ph},{','.join('?' * len(extra_vals))})", list(r) + list(extra_vals))
            n += 1
        added[t] = n
    c.commit()
    return added


def wipe(c, dev):
    for t in ("memories", "notes", "people", "reminders", "ledger", "routines", "messages", "tasks", "listitems", "habits", "dayreport", "spend", "decisions", "moods", "touch", "contracts", "capsules"):
        c.execute(f"DELETE FROM {t} WHERE device=?", (dev,))
    c.commit()


def handle(c, dev, msg, hindi):
    """Chat words only: how to back up, and 'delete everything' with a typed phrase. The passphrase is NEVER typed in chat."""
    say = lambda hi, en: hi if hindi else en
    if msg.strip() == PHRASE:
        wipe(c, dev)
        return say("ठीक है सर, मेरी याददाश्त, लोग, रिमाइंडर, हिसाब, रूटीन, टास्क और चैट हिस्ट्री सब मिटा दी। API key और पेयरिंग नहीं छुए।", "Done, sir. Memory, people, reminders, ledger, routines, tasks and chat history are all deleted. API keys and pairing are untouched.")
    if ASK.match(msg):
        return say(f"सर, ये सब मिट जाएगा: याददाश्त, लोग, रिमाइंडर, हिसाब, रूटीन, टास्क, चैट। पहले Settings > Backup से बैकअप बनाइए। पक्का हो तो ठीक यही लिखिए (बड़े अक्षरों में): {PHRASE}",
                   f"Sir, this will delete memory, people, reminders, ledger, routines, tasks and chat. Make a backup first (Settings > Backup). If you are sure, type exactly (capital letters): {PHRASE}")
    if HOW.match(msg):
        return say("सर, बैकअप Settings में \"Backup\" कार्ड से बनता है। पासवर्ड चैट में मत लिखिए।", "Sir, make a backup in Settings, in the \"Backup\" card. Never type the passphrase in chat.")
    return None
