"""Part 136: Table A runner. Words: `table a next` (the next test row with PASS / FAIL / Skip buttons), `table a pass 12`, `table a fail 12 note`,
`table a skip 12`, `table a note <text>`, `table a show 12`, `table a status`, `table a fails`.
The rows are read from README section 7. Your answers are kept in the phone's database (with date and note), NOT in the README, so a new zip never erases them.
Your answer wins over the README Result column. Part 87 reads these answers for the Verified count. Nothing here does anything on the phone."""
import os, re, time

README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
CMD = re.compile(r"^\s*(?:table\s*a|tablea)\s+(next|agla|status|fails?|note|show|row|pass|fail|skip)(?:\s+(\d{1,3})(?![\w]))?(?:\s+(.{1,200}?))?\s*[.!]?\s*$", re.I)
NEXT = re.compile(r"^\s*(?:next test|agla test|अगला टेस्ट)\s*[.!?]?\s*$", re.I)
CUR, PENDING = {}, {}  # RAM: the row last shown or answered; the buttons the page should draw for the reply


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS tablea(device INT, row INT, result TEXT, note TEXT DEFAULT '', day TEXT DEFAULT '', PRIMARY KEY(device,row))")


def table_rows(t=None):
    """Rows of Table A from README section 7: [{n, try, exp, apk, res}]. [] if the README or the table is missing."""
    try:
        t = t if t is not None else open(README, encoding="utf-8").read()
    except OSError:
        return []
    sec = t.split("## 7. ", 1)[-1].split("\n## 8. ", 1)[0]
    out = []
    for ln in sec.split("\n"):
        p = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(p) >= 5 and p[0].isdigit():
            out.append({"n": int(p[0]), "try": " | ".join(p[1:-3]), "exp": p[-3], "apk": p[-2], "res": p[-1].lower()})
    return out


def merged(c, dev, t=None):
    """README rows, but a row you answered here takes the answer (pass / fail / skip) and its note and day."""
    got = {r: (s, n, d) for r, s, n, d in c.execute("SELECT row,result,note,day FROM tablea WHERE device=?", (dev,))}
    rows = table_rows(t)
    for r in rows:
        r["note"], r["day"] = "", ""
        if r["n"] in got:
            r["res"], r["note"], r["day"] = got[r["n"]]
    return rows


def _count(rows):
    k = [r["res"] for r in rows]
    return {"tests": len(k), "ok": k.count("pass"), "fail": k.count("fail"), "skip": k.count("skip")}


def _next(rows):
    """First row not answered; skipped rows come after the fresh ones."""
    return next((r for r in rows if r["res"] not in ("pass", "fail", "skip")), None) or next((r for r in rows if r["res"] == "skip"), None)


def _show(r, k, hindi):
    say = lambda hi, en: hi if hindi else en
    CUR[r["_dev"]] = r["n"]
    PENDING[r["_dev"]] = {"row": r["n"]}
    head = say(f"टेबल A, टेस्ट {r['n']} ({k['tests']} में से {k['ok']} PASS)", f"Table A, test {r['n']} ({k['ok']} of {k['tests']} PASS so far)")
    return (f"{head}\n{say('करो', 'Try')}: {r['try']}\n{say('होना चाहिए', 'Expect')}: {r['exp']}\n{say('नया APK चाहिए', 'New APK needed')}: {r['apk']}" + (f"\n{say('पुराना नोट', 'Old note')}: {r['note']}" if r["note"] else ""))


def take(dev):
    """Buttons for the page, once: {row}. The page shows PASS / FAIL / Skip under the reply."""
    return PENDING.pop(dev, None)


def handle(c, dev, msg, hindi):
    """Reply text or None. Never touches the phone."""
    if len(msg) > 260:
        return None
    m = CMD.match(msg)
    if not m and not NEXT.match(msg):
        return None
    say = lambda hi, en: hi if hindi else en
    verb, num, note = ((m.group(1).lower(), m.group(2), (m.group(3) or "").strip()) if m else ("next", None, ""))
    rows = merged(c, dev)
    if not rows:
        return say("सर, README में टेबल A नहीं मिली।", "Sir, I cannot find Table A in the README.")
    for r in rows:
        r["_dev"] = dev
    k, by = _count(rows), {r["n"]: r for r in rows}
    if verb in ("next", "agla"):
        r = _next(rows)
        return _show(r, k, hindi) if r else say(f"सर, सारे {k['tests']} टेस्ट हो गए: {k['ok']} PASS, {k['fail']} FAIL।", f"Sir, all {k['tests']} tests are answered: {k['ok']} PASS, {k['fail']} FAIL.")
    if verb == "status":
        left = k["tests"] - k["ok"] - k["fail"]
        return say(f"सर, टेबल A: {k['tests']} में से {k['ok']} PASS, {k['fail']} FAIL, {k['skip']} Skip, {left} बाकी।", f"Sir, Table A: {k['ok']} of {k['tests']} PASS, {k['fail']} FAIL, {k['skip']} skipped, {left} not done.")
    if verb.startswith("fail") and verb != "fail":  # "table a fails": the list of failed rows with notes
        f = [r for r in rows if r["res"] == "fail"]
        return (say("सर, FAIL टेस्ट:", "Sir, FAIL tests:") + "\n" + "\n".join(f"{r['n']}. {r['try'][:70]}" + (f" - {r['note']}" if r["note"] else "") for r in f)) if f else say("सर, कोई FAIL नहीं है।", "Sir, no test is marked FAIL.")
    if verb in ("show", "row"):
        r = by.get(int(num or 0))
        return _show(r, k, hindi) if r else say("सर, यह नंबर टेबल A में नहीं है।", "Sir, that number is not in Table A.")
    n = int(num) if num else CUR.get(dev)
    if verb == "note":
        n, note = (CUR.get(dev), (f"{num} {note}".strip() if num else note))
    if n not in by:
        return say("सर, कौन सा टेस्ट? ऐसे बोलिए: table a pass 12", "Sir, which test? Say it like this: table a pass 12")
    if verb == "note":
        if not note:
            return say("सर, नोट लिखिए: table a note <क्या हुआ>", "Sir, write the note: table a note <what happened>")
        c.execute("INSERT OR IGNORE INTO tablea(device,row,result,day) VALUES(?,?,?,?)", (dev, n, by[n]["res"], time.strftime("%Y-%m-%d")))
        c.execute("UPDATE tablea SET note=? WHERE device=? AND row=?", (note[:200], dev, n))
        c.commit()
        return say(f"सर, टेस्ट {n} का नोट सेव हो गया।", f"Sir, the note for test {n} is saved.")
    res = {"pass": "pass", "fail": "fail", "skip": "skip"}[verb]
    c.execute("INSERT OR REPLACE INTO tablea(device,row,result,note,day) VALUES(?,?,?,?,?)", (dev, n, res, note[:200], time.strftime("%Y-%m-%d")))
    c.commit()
    CUR[dev] = n
    by[n]["res"] = res
    k = _count(rows)
    out = say(f"सर, टेस्ट {n}: {res.upper()} सेव हो गया ({time.strftime('%d %b')})।", f"Sir, test {n}: {res.upper()} saved ({time.strftime('%d %b')}).") + f" {k['ok']}/{k['tests']} PASS."
    if res == "fail" and not note:
        out += " " + say("चाहें तो नोट लिखिए: table a note <क्या हुआ>", "If you want, add a note: table a note <what happened>")
    nx = _next(rows)
    return out + ("\n\n" + _show(nx, k, hindi) if nx else "\n" + say("सारे टेस्ट हो गए।", "All tests are answered."))
