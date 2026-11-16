"""Part 91: Red Team. `red team: yeh phone kharidna hai`. The AI gets ONLY your own Jarvis numbers (this month's spending, habit streaks, things you asked it to remember),
asks 3 hard questions and gives 2 counter-points. Only when you say the words. Not for guest sessions (they never reach this). Nothing is saved."""
import re
import sqlite3
import habits, ledger, memory, spend

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
