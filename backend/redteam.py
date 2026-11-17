"""Part 91: Red Team. `red team: yeh phone kharidna hai`. The AI gets ONLY your own Jarvis numbers (this month's spending, habit streaks, things you asked it to remember),
asks 3 hard questions and gives 2 counter-points. Only when you say the words. Not for guest sessions (they never reach this). Nothing is saved."""
import re
import sqlite3
import decisions, habits, ledger, memory, spend

RT = re.compile(r"^\s*red\s*team\s*[:\-]\s*(.{4,300})$", re.I | re.S)
PROMPT = ("RED TEAM: the user wants his own plan or decision attacked so he does not fool himself. Use ONLY the FACTS below about HIS life; never invent a number, price, date or fact about the thing itself. "
          "Answer in exactly this shape: 3 hard questions (one line each, aimed at his real weak spot), then 2 counter-points against the plan (one line each), then the last line: Decision tumhara hai. "
          "If FACTS is empty, say Jarvis has no numbers about him yet, and still ask the 3 questions. No advice to buy, sell or invest; you are not a financial or legal adviser. Short, direct, kind.")


def facts(c, dev, now):
    out = []
    try:
        day = spend._day(now)
        if day:
            today, _, mo = spend._ranges(day)
            m = spend._sum(c, dev, mo, today)
            if m:
                cats = c.execute("SELECT cat, SUM(amount) FROM spend WHERE device=? AND day>=? AND day<=? GROUP BY cat ORDER BY 2 DESC LIMIT 3", (dev, mo, today)).fetchall()
                out.append("Spent this month: " + ledger.money(m) + (" (top: " + ", ".join(f"{k} {ledger.money(v)}" for k, v in cats) + ")" if cats else ""))
            t = habits._today(now)
            for n in habits._names(c, dev)[:6] if t else []:
                out.append(f"Habit {n}: {habits.streak(habits._days(c, dev, n), t)} day streak")
        out += ["He asked Jarvis to remember: " + t[:120] for _, t in memory.rows(c, dev)[-10:]]
    except (sqlite3.Error, ValueError, TypeError, AttributeError):
        pass  # a missing number is left out, never guessed
    return out


def handle(c, dev, msg, hindi, ask, now):
    m = RT.match(msg)
    if not m:
        return None
    f = facts(c, dev, now)
    try:
        reply, _ = ask([{"role": "user", "content": "Plan or decision to attack:\n<<<\n" + m.group(1).strip() + "\n>>>"}], "hindi" if hindi else "english",
                       "\n\n" + PROMPT + "\nFACTS:\n" + ("\n".join("- " + x for x in f) if f else "(none)"))
    except RuntimeError as e:
        return ("सर, AI से जवाब नहीं मिला: " if hindi else "Sir, no answer from the AI: ") + str(e)[:150]
    return reply


# ---- Part 105: One honest question. `sach sawal on` -> at most ONE hard question every 14 days, only when you say `sach sawal`.
# The AI gets only COUNTS (open decisions, unfinished items, habit streak numbers, mood average). No names, no texts. The reply says what was sent.
SO_SET = re.compile(r"^\s*sach\s+sawal\s+(on|off)\s*$", re.I)
SO_ASK = re.compile(r"^\s*sach\s+sawal\s*$", re.I)
EVERY = 14
HQ_PROMPT = ("ONE HONEST QUESTION: the user switched this on himself. Ask exactly ONE hard but kind question (one line, at most 25 words) that fits the COUNTS below. "
             "Use only these counts; never invent a fact, never name a person, no advice, no diagnosis, no judgement. Output the question only.")


def counts(c, dev, now):
    """Numbers only. Nothing the user typed is in here."""
    out = []
    day = decisions._day(now)
    try:
        if day:
            o = c.execute("SELECT count(*), MIN(CASE WHEN day>0 THEN day END) FROM decisions WHERE device=? AND kind='d' AND done=0", (dev,)).fetchone()
            if o[0]:
                out.append(f"open decisions: {o[0]}" + (f", the oldest is {day - o[1]} days old" if o[1] else ""))
            u = c.execute("SELECT count(*) FROM decisions WHERE device=? AND kind='u' AND done=0", (dev,)).fetchone()[0]
            if u:
                out.append(f"unfinished items: {u}")
            ms = [x[0] for x in c.execute("SELECT score FROM moods WHERE device=? AND day!='care' AND CAST(day AS INT)>=?", (dev, day - 14))]
            if ms:
                out.append(f"mood check-ins in the last 14 days: {len(ms)}, average {sum(ms) / len(ms):.1f} of 5")
        t = habits._today(now)
        names = habits._names(c, dev) if t else []
        if names:
            st = [habits.streak(habits._days(c, dev, n), t) for n in names]
            out.append(f"habits: {len(names)}, longest streak {max(st)} days, {sum(1 for x in st if x == 0)} with no streak now")
    except (sqlite3.Error, ValueError, TypeError, AttributeError):
        pass  # a missing number is left out, never guessed
    return out


def honest(c, dev, msg, hindi, ask, now):
    if len(msg) > 30:
        return None
    say = lambda hi, en: hi if hindi else en
    m = SO_SET.match(msg)
    if m:
        on = m.group(1).lower() == "on"
        memory.setflag(c, dev, "honest", 1 if on else 0)
        return say("ठीक है। मैं 14 दिन में ज़्यादा से ज़्यादा एक कड़ा सवाल पूछूँगा, तभी जब आप बोलें: sach sawal। AI को सिर्फ़ गिनती जाएगी।",
                   "Okay. At most ONE hard question every 14 days, only when you say: sach sawal. The AI gets only counts, no names and no texts.") if on else \
            say("ठीक है, सच सवाल बंद।", "Okay, honest question is off.")
    if not SO_ASK.match(msg):
        return None
    if not memory.flag(c, dev, "honest"):
        return say("सर, यह बंद है। चालू करने के लिए बोलिए: sach sawal on", "Sir, this is off. To start, say: sach sawal on")
    day = decisions._day(now)
    if not day:
        return say("सर, फ़ोन का समय नहीं पढ़ पाया, इसलिए सवाल नहीं पूछा।", "Sir, I could not read the phone time, so I did not ask.")
    left = memory.flag(c, dev, "honest_last") + EVERY - day
    if memory.flag(c, dev, "honest_last") and left > 0:
        return say(f"सर, अगला सवाल {left} दिन बाद।", f"Sir, the next question is in {left} day{'s' if left != 1 else ''}.")
    f = counts(c, dev, now)
    if not f:
        return say("सर, अभी मेरे पास गिनती के लिए कुछ नहीं है। कुछ फ़ैसले, आदतें या मूड लिखिए, फिर पूछिए।", "Sir, I have no numbers about you yet. Add a decision, a habit or a mood first, then ask again.")
    try:
        q, _ = ask([{"role": "user", "content": "Ask my one honest question."}], "hindi" if hindi else "english", "\n\n" + HQ_PROMPT + "\nCOUNTS:\n" + "\n".join("- " + x for x in f))
    except RuntimeError as e:
        return (say("सर, AI से जवाब नहीं मिला: ", "Sir, no answer from the AI: ") + str(e)[:150])  # not counted: the 14 days start only after a real question
    memory.setflag(c, dev, "honest_last", day)
    return q.strip() + "\n\n" + say("AI को सिर्फ़ यह गिनती गई: ", "Sent to the AI (counts only): ") + "; ".join(f)


def line(c, dev, now, hindi):
    """One briefing line (as a list) when the switch is on and 14 days have passed. It only tells you the question is ready; it does not ask the AI."""
    day = decisions._day(now)
    if not day or not memory.flag(c, dev, "honest") or day - memory.flag(c, dev, "honest_last") < EVERY or not counts(c, dev, now):
        return []
    return ["- आपका सच सवाल तैयार है। बोलिए: sach sawal" if hindi else "- Your honest question is ready. Say: sach sawal"]
