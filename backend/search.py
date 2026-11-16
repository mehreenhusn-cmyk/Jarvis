"""Jarvis search everywhere (Part 89): "sab jagah dhundo Bombay" looks for the same WORDS (not the meaning) in notes, memories, people notes, lists and
reminders, and says where each hit came from. Reads only; nothing is saved, nothing goes to the AI. Later Parts add their store to SOURCES."""
import re

# (label, query with one ? for the device, how one hit is shown)
SOURCES = [("Notes", "SELECT id, text FROM notes WHERE device=? ORDER BY id DESC", "#{0}: {1}"),
           ("Memory", "SELECT id, text FROM memories WHERE device=? ORDER BY id DESC", "#{0}: {1}"),
           ("People", "SELECT name, note FROM people WHERE device=? ORDER BY id DESC", "{0}: {1}"),
           ("Lists", "SELECT list, item FROM listitems WHERE device=? ORDER BY id DESC", "{0}: {1}"),
           ("Reminders", "SELECT id, text FROM reminders WHERE device=? ORDER BY due DESC", "#{0}: {1}")]
WHERE = r"(?:sab|sabhi|saari|सब|सभी)\s+(?:jagah|जगह)"
VERB = r"(?:dhundo|dhoondo|khojo|dekho|ढूंढो|ढूँढो|खोजो)"
ASK = [re.compile(r"^\s*" + WHERE + r"\s+" + VERB + r"\s*[:,\-]?\s*(.{2,60}?)\s*$", re.I),
       re.compile(r"^\s*" + WHERE + r"\s+(.{2,60}?)\s+" + VERB + r"\s*$", re.I),
       re.compile(r"^\s*(?:search|find)\s+(?:everywhere|all)\s*(?:for|:)?\s+(.{2,60}?)\s*$", re.I)]
MAX_SHOW = 15


def handle(c, dev, msg, hindi):
    """Answer text, or None if this is not an 'everywhere' search."""
    term = next((m.group(1) for m in (p.match(msg) for p in ASK) if m), None)
    if not term:
        return None
    t = term.lower()
    hits = []
    for label, sql, fmt in SOURCES:
        for row in c.execute(sql, (dev,)).fetchall():
            if t in " ".join(str(x) for x in row).lower():
                hits.append(f"{label} {fmt.format(*row)}"[:140])
    if not hits:
        return (f"सर, '{term}' कहीं नहीं मिला। मैं वही शब्द ढूंढता हूँ, मतलब नहीं।" if hindi else
                f"Sir, I found '{term}' nowhere. I look for the same words, not the meaning.")
    head = f"सर, '{term}' {len(hits)} जगह मिला:" if hindi else f"Sir, found '{term}' in {len(hits)} place(s):"
    more = f"\n+{len(hits) - MAX_SHOW} more" if len(hits) > MAX_SHOW else ""
    return head + "\n" + "\n".join(hits[:MAX_SHOW]) + more
