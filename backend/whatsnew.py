"""Jarvis what's new (Part 117): "last update", "kya kya add hua", "last 5 updates" are answered from the zips this phone already
processed (~/.jarvis_done: name, time, files inside) and that Part's row in README section 2. No AI and no GitHub call:
Jarvis only knows what this phone received and pushed."""
import os, re, time, zipfile
import progress

DONE = os.path.expanduser("~/.jarvis_done")
LAST = re.compile(r"\b(?:last|latest|recent|newest|pichl\w*|aakhri|akhri)\b|what(?:'s| is) new|kya\s+naya", re.I)
THING = re.compile(r"\b(?:updates?|updated|implement\w*|added?|add\s+hua|pushed?|naya|new)\b|github", re.I)
PROJ = re.compile(r"\b(?:jarvis|github|zips?|parts?|files?|implement\w*|pushed?)\b", re.I)
BARE = re.compile(r"^\s*(?:(?:last|latest)\s+(?:\d{1,2}\s+)?updates?|kya\s+(?:kya\s+)?(?:add|update|naya)\s*(?:hua|hui|aaya)|what(?:'s| is) new)\s*[?.]?\s*$", re.I)


def asked(msg):
    return len(msg) <= 140 and bool(BARE.match(msg) or (LAST.search(msg) and THING.search(msg) and PROJ.search(msg)))


def updates():
    """[(mtime, zip name)] newest first; copies named dup_ are skipped."""
    try:
        names = [f for f in os.listdir(DONE) if re.match(r"Jarvis_part\d+\w*\.zip$", f)]
    except OSError:
        return []
    return sorted(((os.path.getmtime(os.path.join(DONE, f)), f) for f in names), reverse=True)


def row(n):
    """(what it does, files, lines) of Part n from README section 2, or None."""
    try:
        t = open(progress.README, encoding="utf-8").read()
    except OSError:
        return None
    sec = t.split("## 2. ", 1)[-1].split("\n## 3. ", 1)[0]
    for m in re.finditer(r"^\| (\d+)(?: to (\d+))? \| (.+?) \| ([^|]*) \| ([^|]*) \| [^|]* \| [^|]* \|\s*$", sec, re.M):
        if int(m.group(1)) <= n <= int(m.group(2) or m.group(1)):
            clean = lambda s: re.sub(r"[*`]", "", s).strip()
            d = clean(m.group(3))
            d = d if len(d) <= 220 else d[:220].rsplit(" ", 1)[0] + "..."
            return d, clean(m.group(4)), clean(m.group(5))
    return None


def inside(name):
    try:
        with zipfile.ZipFile(os.path.join(DONE, name)) as z:
            f = [x for x in z.namelist() if not x.endswith("/")]
    except (OSError, zipfile.BadZipFile):
        return ""
    return ", ".join(f[:8]) + (f" (+{len(f) - 8} more)" if len(f) > 8 else "")


def handle(msg, hindi, note=""):
    """Answer text, or None if this is not a 'what was updated' question. note = the header text 'name|time|result' from sync.sh."""
    if not asked(msg):
        return None
    ups = updates()
    if not ups:
        return "सर, अभी तक कोई अपडेट ज़िप नहीं मिली।" if hindi else "Sir, I find no update zips on this phone yet."
    k = re.search(r"\b(\d{1,2})\b", msg)
    n = max(1, min(8, int(k.group(1)))) if k else (3 if re.search(r"kya\s+kya", msg, re.I) else 1)
    out = []
    for i, (mt, name) in enumerate(ups[:n]):
        pn = int(re.search(r"part(\d+)", name).group(1))
        r = row(pn)
        when = time.strftime("%d %b %H:%M", time.localtime(mt))
        if n > 1:
            out.append(f"{i + 1}. Part {pn} ({when}): " + (r[0][:90] if r else "no README row"))
            continue
        res = note.split("|")[2] if note.count("|") >= 2 and note.split("|")[0] == name else ""
        out.append(("आख़िरी अपडेट: " if hindi else "Last update: ") + f"{name}, {when}" + (f" ({res})" if res else "") + ".")
        out.append(f"Part {pn}: " + (r[0] if r else "no README row for this Part"))
        if r:
            out.append(f"Files: {r[1]}. Lines: {r[2]}.")
        z = inside(name)
        if z:
            out.append(f"In the zip: {z}")
    return "\n".join(out)
