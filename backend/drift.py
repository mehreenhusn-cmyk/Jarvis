"""Part 106: Topic drift. `drift on`, then `drift dikhao` compares the words you typed most in the last 30 days with the 30 days before, from your own chat history.
Plain word counts. No AI, nothing leaves the phone, nothing new is saved (only the on/off switch). Needs about 2 months of history; it says so when there is not enough."""
import re
import time
import memory

ON = re.compile(r"^\s*drift\s+(on|off)\s*$", re.I)
SHOW = re.compile(r"^\s*(?:drift\s+(?:dikhao|show)|topic\s+drift)\s*$", re.I)
WORD = re.compile(r"[a-z\u0900-\u097f]{3,}", re.I)
STOP = set("""the and for you that this with have are was but not what how can please jarvis hey hello okay ok yes sir tell show give make let get set put
 about from your his her they them our out all any one two its it's just like want need will would could should there here when then than into over some more much very
 also been being does did doing done had has who why which where mera meri mere hai hain hoon tha thi the kar karo kijiye kiya kya kyu kyun nahi nahin haan aur ya toh to
 mein main me se ko ka ki ke par pe yeh ye woh wo abhi aaj kal bhi hi ek koi kuch sab apna apni tum aap tumhara mujhe mujhko batao bata dikhao kholo chalu band
 हैं है का की के को से में पर और यह वह तो भी एक कर करो कुछ मेरा मेरी मुझे""".split())
DAY = 86400
MIN_MSGS = 8  # per month; below this the comparison would be noise


def _top(rows):
    n = {}
    for (t,) in rows:
        for w in WORD.findall(t.lower()):
            if w not in STOP:
                n[w] = n.get(w, 0) + 1
    return n


def _best(n, k):
    return [w for w, _ in sorted(n.items(), key=lambda x: (-x[1], x[0]))[:k]]


def compare(c, dev, hindi, ts=None):
    say = lambda hi, en: hi if hindi else en
    ts = ts or time.time()
    old = c.execute("SELECT MIN(ts) FROM messages WHERE device=? AND role='user' AND ts>0", (dev,)).fetchone()[0]
    a = c.execute("SELECT content FROM messages WHERE device=? AND role='user' AND ts>=? AND ts<?", (dev, ts - 60 * DAY, ts - 30 * DAY)).fetchall()
    b = c.execute("SELECT content FROM messages WHERE device=? AND role='user' AND ts>=?", (dev, ts - 30 * DAY)).fetchall()
    if len(a) < MIN_MSGS or len(b) < MIN_MSGS:
        have = int((ts - old) // DAY) if old else 0
        return say(f"सर, तुलना के लिए करीब 2 महीने की चैट चाहिए। अभी {have} दिन की है ({len(a)} और {len(b)} संदेश)।",
                   f"Sir, I need about 2 months of chat to compare. Right now there are {have} days ({len(a)} messages last month, {len(b)} this month).")
    na, nb = _top(a), _top(b)
    top_a, top_b = _best(na, 10), _best(nb, 10)
    rise = [f"{w} ({na.get(w, 0)} → {nb[w]})" for w in top_b if w not in top_a][:5]
    fade = [f"{w} ({na[w]} → {nb.get(w, 0)})" for w in top_a if w not in top_b][:5]
    out = [say("पिछले 30 दिन बनाम उससे पहले के 30 दिन (सिर्फ़ शब्द गिने हैं):", "Last 30 days vs the 30 days before (word counts only):"),
           say("इस महीने सबसे ज़्यादा: ", "Most this month: ") + ", ".join(f"{w} {nb[w]}" for w in top_b[:5]),
           say("पिछले महीने सबसे ज़्यादा: ", "Most last month: ") + ", ".join(f"{w} {na[w]}" for w in top_a[:5])]
    out.append(say("नए उभरे: ", "Rising: ") + (", ".join(rise) if rise else say("कोई नहीं", "none")))
    out.append(say("कम हुए: ", "Fading: ") + (", ".join(fade) if fade else say("कोई नहीं", "none")))
    out.append(say("यह सिर्फ़ गिनती है, मतलब नहीं। AI इस्तेमाल नहीं हुआ।", "This is only counting, not meaning. No AI was used."))
    return "\n".join(out)


def handle(c, dev, msg, hindi):
    if len(msg) > 30:
        return None
    m = ON.match(msg)
    if m:
        on = m.group(1).lower() == "on"
        memory.setflag(c, dev, "drift", 1 if on else 0)
        return (("ठीक है। अब बोलिए: drift dikhao। यह सिर्फ़ आपकी चैट के शब्द गिनता है, AI नहीं।" if hindi else "Okay. Now say: drift dikhao. It only counts words in your own chat, no AI.") if on
                else ("ठीक है, ड्रिफ़्ट बंद।" if hindi else "Okay, drift is off."))
    if not SHOW.match(msg):
        return None
    if not memory.flag(c, dev, "drift"):
        return "सर, यह बंद है। चालू करने के लिए बोलिए: drift on" if hindi else "Sir, this is off. To start, say: drift on"
    return compare(c, dev, hindi)
