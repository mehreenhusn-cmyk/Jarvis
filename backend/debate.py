"""Part 92: Debate Jarvis. `debate ruthless: ...`, `debate spiritual: ...`, `debate opposite: ...`. Only when you call it. Jarvis argues that side for 10 minutes
(the page shows a badge), then goes back to normal. `debate stop` ends it at once. RAM only, nothing is saved, never in a guest session."""
import re
import time

START = re.compile(r"^\s*debate\s+(ruthless|spiritual|opposite)\s*[:\-]\s*(.{2,500})$", re.I | re.S)
STOP = re.compile(r"^\s*debate\s+(?:stop|khatam|band|off)\s*$", re.I)
TTL = 600
ACTIVE = {}  # device -> (style, ends at)
STYLE = {
    "ruthless": "Be blunt and hard. Attack the weak points of his idea, give no comfort and no flattery. No insults, no mockery of him as a person.",
    "spiritual": "Argue from calm values: meaning, patience, contentment, relationships. Gentle and wise. Never claim a religion or a belief as proven fact.",
    "opposite": "Argue the exact opposite of what he said, with the best honest arguments for that side. Do not invent facts or numbers.",
}


def command(dev, msg, hindi):
    """Text for `debate stop`; for a start phrase it switches the debate on and returns None (the AI then answers in that style)."""
    if STOP.match(msg):
        return ("ठीक है, डिबेट बंद। अब सामान्य मोड।" if hindi else "Okay, the debate is over. Back to normal.") if ACTIVE.pop(dev, None) else ("सर, डिबेट चालू नहीं है।" if hindi else "Sir, no debate is on.")
    m = START.match(msg)
    if m:
        ACTIVE[dev] = (m.group(1).lower(), time.time() + TTL)
    return None


def label(dev):
    a = ACTIVE.get(dev)
    if a and time.time() < a[1]:
        return a[0]
    ACTIVE.pop(dev, None)
    return ""


def extra(dev):
    s = label(dev)
    return ("\n\n[DEBATE MODE, " + s + ", 10 minutes, chosen by the user: " + STYLE[s] + " Keep it short and in the user's language. It is a debate, not advice: he decides. "
            "If he sounds in real distress or speaks of hurting himself, stop debating and answer with care.]") if s else ""
