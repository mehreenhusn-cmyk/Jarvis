"""Jarvis hisab (Part 11): "Faisal ko 5000 dene hain, 15 Nov ko yaad dilana". Sirf personal likhai-padhai, asli payment nahi.
Dena = mujhe dusre ko dene hain, Lena = mujhe dusre se lene hain. Tareekh AI se samajhta hai (ek chhota sawal)."""
import json, re, time

import memory, remind

ADD = re.compile(r"dene h|dena h|lene h|lena h|udhaar|udhar|उधार|देने हैं|देना है|लेने हैं|लेना है|\bowe", re.I)
LIST = re.compile(r"^\s*(?:mera\s+|mere\s+|मेरा\s+|मेरे\s+)?(?:baaki\s+|बाकी\s+|pura\s+|पूरा\s+)?(?:hisab|hisaab|ledger|हिसाब)(?:\s+(?:dikhao|batao|dikha|bata|list|dekho|kitna|दिखाओ|बताओ|दिखा|बता|देखो))?\s*[?.!]*\s*$"
                  r"|kitna\s*(?:dena|lena|baaki)|total\s*(?:dena|lena|baaki)|कितना\s*(?:देना|लेना|बाकी)", re.I)  # Part 153: "हम क्या गिर रहा है यार मेरे हिसाब" is a normal sentence, not the ledger
PAID = re.compile(r"^\s*(?:paid|chuka diya|mil gaya|चुका दिया|मिल गया)\s*#?(\d+)\s*$", re.I)
DEL = re.compile(r"^\s*(?:hisab hatao|hisaab hatao|ledger delete|हिसाब हटाओ)\s*#?(\d+)\s*$", re.I)


def init(c):
    c.execute("CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY, device INT, who TEXT, amount REAL, dir TEXT, due TEXT, note TEXT, paid INT DEFAULT 0, ts REAL)")


def money(a):
    return f"₹{a:,.0f}" if float(a).is_integer() else f"₹{a:,.2f}"


def day(d):
    return time.strftime("%d %b", time.strptime(d, "%Y-%m-%d"))


def line(i, who, a, dr, due):
    return f"#{i} {who} {'ko dena' if dr == 'dena' else 'se lena'} {money(a)}" + (f" ({day(due)})" if due else "")


def rows(c, dev):
    return c.execute("SELECT id, who, amount, dir, due FROM ledger WHERE device=? AND paid=0 ORDER BY id", (dev,)).fetchall()


def totals(r):
    return sum(a for _, _, a, d, _ in r if d == "dena"), sum(a for _, _, a, d, _ in r if d == "lena")


def handle(c, dev, msg, hindi, ask, now):
    def say(hi, ro):
        return hi if hindi else ro
    m = PAID.match(msg) or DEL.match(msg)
    if m:
        sql = "UPDATE ledger SET paid=1 WHERE id=? AND device=?" if PAID.match(msg) else "DELETE FROM ledger WHERE id=? AND device=?"
        k = c.execute(sql, (int(m.group(1)), dev)).rowcount
        c.commit()
        if not k:
            return say("सर, इस नंबर की एंट्री नहीं मिली।", "Sir, I found no entry with that number.")
        return say("ठीक है सर, हो गया।", "Okay sir, done.")
    if LIST.search(msg) and len(msg) < 60:
        r = rows(c, dev)
        if not r:
            return say("सर, कोई हिसाब बाकी नहीं है।", "Sir, there are no pending entries.")
        dn, ln = totals(r)
        return (say("सर, बाकी हिसाब:\n", "Sir, baaki hisab:\n") + "\n".join(line(*x) for x in r)
                + f"\n{say('कुल देना', 'Total dena')}: {money(dn)} | {say('कुल लेना', 'Total lena')}: {money(ln)}")
    if not ADD.search(msg) or not re.search(r"\d", msg) or len(msg) > 300:
        return None
    if memory.SECRET.search(msg):
        return say("माफ़ कीजिए सर, पासवर्ड, ओटीपी या पिन मैं सेव नहीं करता।", "Sorry sir, I never save passwords, OTPs or PINs.")
    try:
        n = remind.tm(now)
    except ValueError:
        return say("सर, फ़ोन का समय नहीं मिला, पेज रीफ़्रेश कीजिए।", "Sir, I could not get the phone time. Please refresh the page.")
    q = (f"Abhi ka local time: {now[:16]}. User ka message: {msg}\n"
         'Sirf ek JSON do: {"who": "naam", "amount": number, "direction": "dena" ya "lena", "due": "YYYY-MM-DD" ya null, "note": "chhota note ya khali"}. '
         '"dena" = user ko dusre ko paise dene hain. "lena" = user ko dusre se paise lene hain. amount sirf number. '
         "'kal', '15 Nov' jaise shabd abhi ke time se tareekh banao. Tareekh na ho to due null.")
    try:
        out, _ = ask([{"role": "user", "content": q}], "hinglish")
        j = json.loads(re.search(r"\{.*\}", out, re.S).group(0))
        who, a, dr = str(j["who"]).strip()[:40], float(j["amount"]), str(j["direction"]).strip().lower()
        due = str(j.get("due") or "")[:10] or None
        if due:
            remind.tm(due + " 09:00")
        assert who and a > 0 and dr in ("dena", "lena")
    except (RuntimeError, AttributeError, ValueError, KeyError, TypeError, AssertionError):
        return say("सर, मैं समझ नहीं पाया। ऐसे लिखिए: 'फ़ैसल को 5000 देने हैं, 15 नवंबर को'", "Sir, I could not understand. Try: 'I owe Faisal 5000, due 15 Nov'")
    i = c.execute("INSERT INTO ledger(device, who, amount, dir, due, note, ts) VALUES(?,?,?,?,?,?,?)",
                  (dev, who, a, dr, due, str(j.get("note") or "")[:100], time.time())).lastrowid
    extra = ""
    if due and remind.tm(due + " 09:00") >= n - 60:  # due date par subah 9 baje reminder bhi
        c.execute("INSERT INTO reminders(device, text, due) VALUES(?,?,?)",
                  (dev, f"{who} {'ko dena hai' if dr == 'dena' else 'se lena hai'} {money(a)}", remind.tm(due + " 09:00")))
        extra = say(" रिमाइंडर भी लगा दिया।", " Reminder bhi laga diya.")
    c.commit()
    return say("ठीक है सर, लिख लिया। ", "Okay sir, noted. ") + line(i, who, a, dr, due) + extra
