"""Part 201: the names of the apps on this phone (only launcher apps; the page reads them with no extra permission).
Only NAMES are kept (never package names, never usage), only on this phone server, never sent to the AI. Used to understand a spoken app name in Hindi, English or mixed."""
import hashlib, json, re, time
import lang

MAXN = 400


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS appnames(device INT PRIMARY KEY, names TEXT, h TEXT, ts REAL)")


def save(c, dev, names):
    """The page sends the list when it changed. Returns how many names are kept, or None if the list is not usable."""
    if not isinstance(names, list):
        return None
    out = []
    for n in names[:MAXN]:
        n = str(n).strip()[:60]
        if len(n) >= 2 and n not in out:
            out.append(n)
    h = hashlib.sha1("\n".join(out).encode("utf-8")).hexdigest()[:12]
    c.execute("INSERT OR REPLACE INTO appnames(device, names, h, ts) VALUES(?,?,?,?)", (dev, json.dumps(out, ensure_ascii=False), h, time.time()))
    c.commit()
    return len(out)


def load(c, dev):
    row = c.execute("SELECT names FROM appnames WHERE device=?", (dev,)).fetchone()
    try:
        return json.loads(row[0]) if row else []
    except ValueError:
        return []


def _skel(s):
    """Roman letters without vowels and double letters: 'यूट्यूब', 'youtube' and 'yootyoob' end up close."""
    s = s if lang.is_latin(s) else (lang.romanize(s) or s)
    s = re.sub(r"[^a-z0-9]", "", s.lower().replace("w", "v").replace("ph", "f").replace("kh", "k"))
    return re.sub(r"(.)\1+", r"\1", re.sub(r"(?<=.)[aeiou]", "", s))


def _ed(a, b):
    p = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        q = [i]
        for j in range(1, len(b) + 1):
            q.append(min(q[j - 1] + 1, p[j] + 1, p[j - 1] + (a[i - 1] != b[j - 1])))
        p = q
    return p[-1]


def resolve(names, said):
    """The ONE installed app name that fits what was said, or '' (two equal fits = no answer, the app then asks)."""
    q = _skel(said)
    if len(q) < 3 or not names:
        return ""
    best, hit = 99, []
    for n in names:
        k = _skel(n)
        if len(k) < 3:
            continue
        d = 0 if k == q else 1 if (len(q) >= 4 and (k.startswith(q) or q.startswith(k))) else _ed(q, k)
        if d > max(1, min(len(q), len(k)) // 4):
            continue
        if d < best:
            best, hit = d, [n]
        elif d == best and n not in hit:
            hit.append(n)
    return hit[0] if len(hit) == 1 else ""
