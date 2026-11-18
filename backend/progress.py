"""Jarvis progress (Part 34, honest counts Part 87): "app ka kaam kahan tak pahuncha?" or "mission" is answered from README.md (section 2 status column, Table A, and the Build order line).
No second list to keep: when a Part is marked DONE in the README, Jarvis knows it. Built means the code is written; it does NOT mean tested on the phone."""
import os, re

README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
ASK = re.compile(r"kitna (?:kaam|work) (?:ho gaya|hua|complete)|कितना काम (?:हो गया|हुआ)|kitna ho gaya|work status|status of (?:the )?(?:app|project)|kahan tak|kahaan tak|कहाँ तक|कहां तक|progress|प्रोग्रेस|how far|where are we|next part|kitne part|कितने पार्ट|what(?:'s| is) left|kya kya baaki|क्या क्या बाकी|कौन सा पार्ट|कौन-सा पार्ट|status of (?:the )?(?:app|jarvis)", re.I)
ABOUT = re.compile(r"\bapp\b|jarvis|\bparts?\b|kaam|काम|ऐप|एप|पार्ट|project|feature|plan", re.I)


def plan():
    """(done set, {part: short name}, build order list, optional list) read from README.md section 2 and the Build order line, or None if the file is missing."""
    try:
        t = open(README, encoding="utf-8").read()
    except OSError:
        return None
    sec = t.split("## 2. ", 1)[-1].split("\n## 3. ", 1)[0]
    done, names = set(), {}
    for m in re.finditer(r"^\| (\d+) \| ([^|]+?) \|.*\| ([^|]+) \|\s*$", sec, re.M):
        n = int(m.group(1))
        nm = re.split(r"[:.(,]", re.sub(r"[*`]", "", m.group(2)))[0].strip()
        w = (nm if len(nm) <= 40 else nm[:40].rsplit(" ", 1)[0]).split()
        while len(w) > 2 and w[-1].lower() in ("with", "the", "real", "a", "of", "and", "for", "to"):
            w.pop()
        names[n] = " ".join(w)
        if m.group(3).strip().lower().startswith("built"):
            done.add(n)
    o = re.search(r"\*\*Build order[^:]*:\*\*\s*([^\n]+)", t)
    order = [int(x) for x in re.findall(r"\d+", o.group(1).split("Optional")[0])] if o else sorted(n for n in names if n not in done and n > 0)
    opt = [int(x) for x in re.findall(r"\d+", o.group(1).split("Optional", 1)[1])] if o and "Optional" in o.group(1) else []
    return done, names, order, opt


def mission(db=None, dev=None):
    """Part 87: three SEPARATE counts, read from README section 2 (status column) and Table A (Result column).
    built = code written; tested = also tried on the phone; verified = Table A rows marked PASS. None if the README is missing."""
    try:
        t = open(README, encoding="utf-8").read()
    except OSError:
        return None
    sec = t.split("## 2. ", 1)[-1].split("\n## 3. ", 1)[0]
    c = {"built": 0, "tested": 0, "partly": 0, "planned": 0}
    for m in re.finditer(r"^\| (\d+)(?: to (\d+))? \|.*\| ([^|]+) \|\s*$", sec, re.M):
        n = int(m.group(2) or m.group(1)) - int(m.group(1)) + 1
        s = m.group(3).strip().lower()
        if s.startswith("built"):
            c["built"] += n
            c["tested"] += n if s.startswith("built, phone tested") else 0
            c["partly"] += n if s.startswith("built, partly") else 0
        elif s == "planned":
            c["planned"] += n
    ta = t.split("## 7. ", 1)[-1].split("\n## 8. ", 1)[0]
    res = [r.strip().lower() for r in re.findall(r"^\| \d+ \|.*\| ([^|]+) \|\s*$", ta, re.M)]
    if db is not None and dev is not None:  # Part 136: the rows you answered with `table a pass 12` win over the README column
        try:
            import phonetest
            res = [r["res"] for r in phonetest.merged(db, dev, t)] or res
        except Exception:
            pass
    c.update(tests=len(res), ok=res.count("pass"), fail=res.count("fail"))
    return c


def handle(msg, hindi, db=None, dev=None):
    """Answer text, or None if this is not a progress question."""
    if len(msg) > 120 or not ((ASK.search(msg) and ABOUT.search(msg)) or re.match(r"^\s*mission(?: view| status)?\s*[?.]?\s*$", msg, re.I)):
        return None
    p = plan()
    if p is None:
        return "सर, मुझे प्लान की फ़ाइल (README) नहीं मिली, इसलिए अभी पक्का नहीं बता सकता।" if hindi else "Sir, I cannot find the plan file (README), so I cannot tell you for sure right now."
    done, names, order, opt = p
    m = mission(db, dev)
    todo = [n for n in order if n not in done]
    nxt = ", ".join(f"{n} ({names.get(n, '?')})" for n in todo[:3])
    fl = f", {m['fail']} FAIL" if m["fail"] else ""
    if hindi:
        return (f"सर, README से सही गिनती। कोड बना: {m['built']} पार्ट। फ़ोन पर टेस्ट हुए: {m['tested']} (और {m['partly']} आधे)। "
                f"टेबल A में PASS: {m['tests']} में से {m['ok']}{fl}। अभी प्लान में: {m['planned']}। अगले: {nxt or 'कोई नहीं'}।")
    return (f"Sir, honest count from the README. Code built: {m['built']} Parts. Phone tested: {m['tested']} Parts (and {m['partly']} partly). "
            f"Verified on Table A: {m['ok']} of {m['tests']} tests PASS{fl}. Still planned: {m['planned']}. Next: {nxt or 'none'}.")
