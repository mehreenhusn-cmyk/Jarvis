"""Jarvis subah ka briefing (Part 14): aaj ke reminders + paas ki tareekh wale hisab. Seedha database se, AI ki zaroorat nahi."""
import re, time

import ledger, remind

TRIG = re.compile(r"briefing|brief karo|aaj ka plan|aaj kya hai|my plan today|good morning jarvis|ब्रीफिंग|सुप्रभात", re.I)


def build(c, dev, now, hindi, auto=False):
    """Text lautata hai. auto=True aur kuch na ho to '' (page ko chup rehna hai)."""
    try:
        n = remind.tm(now)
    except ValueError:
        return ""
    end = n - n % 86400 + 86400
    rem = c.execute("SELECT text, due FROM reminders WHERE device=? AND sent=0 AND due<? ORDER BY due", (dev, end)).fetchall()
    L = ledger.rows(c, dev)
    soon = time.strftime("%Y-%m-%d", time.gmtime(n + 2 * 86400))
    near = [x for x in L if x[4] and x[4] <= soon]
    if not rem and not near and auto:
        return ""
    say = (lambda hi, ro: hi if hindi else ro)
    out = [say("सुप्रभात सर।", "Suprabhat sir.") + " " + time.strftime("%d %b", time.gmtime(n))]
    if rem:
        out.append(say("आज के रिमाइंडर:", "Today's reminders:"))
        out += [f"- {time.strftime('%H:%M', time.gmtime(d))} {t}" for t, d in rem]
    if near:
        out.append(say("पास की तारीख़ वाला हिसाब:", "Paas ki tareekh wala hisab:"))
        out += ["- " + ledger.line(*x) for x in near]
    if L:
        dn, ln = ledger.totals(L)
        out.append(f"{say('कुल देना', 'You owe')}: {ledger.money(dn)} | {say('कुल लेना', 'You get')}: {ledger.money(ln)}")
    if not rem and not near:
        out.append(say("आज कुछ ज़रूरी बाकी नहीं है।", "Nothing important is pending today."))
    return "\n".join(out)


def handle(c, dev, msg, hindi, now):
    return build(c, dev, now, hindi) if TRIG.search(msg) and len(msg) < 50 else None
