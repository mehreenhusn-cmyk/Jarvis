"""Jarvis progress (Part 34): "app ka kaam kahan tak pahuncha?" is answered from README.md (section 11.6 table and the Build order line).
No second list to keep: when a Part is marked DONE in the README, Jarvis knows it. Built means the code is written; it does NOT mean tested on the phone."""
import os, re

README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
BASE = 26  # Parts 1 to 26 were finished before the 11.6 table starts
ASK = re.compile(r"kitna (?:kaam|work) (?:ho gaya|hua|complete)|कितना काम (?:हो गया|हुआ)|kitna ho gaya|work status|status of (?:the )?(?:app|project)|kahan tak|kahaan tak|कहाँ तक|कहां तक|progress|प्रोग्रेस|how far|where are we|next part|kitne part|कितने पार्ट|what(?:'s| is) left|kya kya baaki|क्या क्या बाकी|कौन सा पार्ट|कौन-सा पार्ट|status of (?:the )?(?:app|jarvis)", re.I)
ABOUT = re.compile(r"\bapp\b|jarvis|\bparts?\b|kaam|काम|ऐप|एप|पार्ट|project|feature|plan", re.I)


def plan():
    """(done set, {part: short name}, build order list, optional list) read from README.md, or None if the file is missing."""
    try:
        t = open(README, encoding="utf-8").read()
    except OSError:
        return None
    sec = t.split("### 11.6 ", 1)[-1].split("### 11.6b", 1)[0]
    done, names = set(), {}
    for m in re.finditer(r"^\| (\d+)( DONE)? \| ([^|]+?) \|", sec, re.M):
        n = int(m.group(1))
        nm = re.split(r"[:.(,]", m.group(3))[0].strip()
        w = (nm if len(nm) <= 40 else nm[:40].rsplit(" ", 1)[0]).split()
        while len(w) > 2 and w[-1].lower() in ("with", "the", "real", "a", "of", "and", "for", "to"):
            w.pop()
        names[n] = " ".join(w)
        if m.group(2):
            done.add(n)
    o = re.search(r"\*\*Build order[^:]*:\*\*\s*([^\n]+)", t)
    order = [int(x) for x in re.findall(r"\d+", o.group(1).split("Optional")[0])] if o else sorted(n for n in names if n not in done)
    opt = [int(x) for x in re.findall(r"\d+", o.group(1).split("Optional", 1)[1])] if o and "Optional" in o.group(1) else []
    return done, names, order, opt


def handle(msg, hindi):
    """Answer text, or None if this is not a progress question."""
    if len(msg) > 120 or not (ASK.search(msg) and ABOUT.search(msg)):
        return None
    p = plan()
    if p is None:
        return "सर, मुझे प्लान की फ़ाइल (README) नहीं मिली, इसलिए अभी पक्का नहीं बता सकता।" if hindi else "Sir, I cannot find the plan file (README), so I cannot tell you for sure right now."
    done, names, order, opt = p
    todo = [n for n in order if n not in done]
    ds = sorted(done)
    last = ", ".join(map(str, ds))
    nxt = ", ".join(f"{n} ({names.get(n, '?')})" for n in todo[:3])
    built = BASE + len(done)
    total = BASE + len(names)
    if hindi:
        return (f"सर, प्लान के {total} पार्ट में से {built} बन चुके हैं (कोड लिखा गया, फ़ोन पर टेस्ट अलग बात है)। 26 के बाद बने: {last}। "
                f"ज़रूरी पार्ट अभी बाकी: {len(todo)}। अगले: {nxt or 'कोई नहीं'}। वैकल्पिक: {', '.join(map(str, opt)) or 'कोई नहीं'}।")
    return (f"Sir, {built} of the {total} planned Parts are built (code written; phone testing is a separate step). Built so far after Part 26: {last}. "
            f"Required Parts still to build: {len(todo)}. Next: {nxt or 'none'}. Optional: {', '.join(map(str, opt)) or 'none'}.")
