"""Part 48: handoff summary (paste into Claude or ChatGPT) and the lost-phone card. Text only. Jarvis sends nothing anywhere: Hussain copies or shares it himself."""
import re
import memory

HAND = re.compile(r"^\s*(?:handoff|hand off|hand-off)(?:\s+summary)?\s*$|summary for (?:claude|chatgpt|gemini)|chat summary for|handoff summary", re.I)
LOST = re.compile(r"phone (?:kho|gum|chori|lost|stolen)|(?:kho|gum) gaya|lost (?:my )?phone|phone (?:khoya|chura)|mera phone chori|stolen phone|lost phone", re.I)


def summary(c, dev, n=12):
    """Last chat lines, cleaned: passwords/OTPs removed, markers of private answers skipped, each line short."""
    rows = c.execute("SELECT role, content FROM messages WHERE device=? ORDER BY id DESC LIMIT ?", (dev, n)).fetchall()
    out = []
    for role, text in reversed(rows):
        t = " ".join(str(text).split())
        if not t or t.startswith("(") or memory.SECRET.search(t) or (role == "user" and HAND.search(t)):
            continue
        out.append(("Me: " if role == "user" else "Jarvis: ") + (t[:280] + "..." if len(t) > 280 else t))
    if not out:
        return None
    return ("Handoff from my phone assistant Jarvis. This is the end of my recent chat with it. "
            "Please read it, then help me continue from here.\n\n" + "\n".join(out) + "\n\n(Lines with passwords, OTPs or private phone data were left out.)")


def handle(c, dev, msg, hindi=False):
    m = (msg or "").strip()
    if len(m) > 80:
        return None
    if HAND.search(m):
        s = summary(c, dev)
        if not s:
            return "Sir, there is no chat to summarize yet." if not hindi else "Sir, abhi summary ke liye chat nahi hai."
        return s + "\n\nTap Copy or Share below, then paste it in Claude or ChatGPT."
    if LOST.search(m):
        return ("Sir, I am sorry. Do these in order. I cannot find, lock or erase the phone myself (by design, that needs the internet, which is a bigger risk).\n"
                "1. From another phone or PC open Google Find Hub (Find My Device) and sign in with your Google account. Play sound, then Secure device. Erase only as the last step.\n"
                "2. Call your SIM company from another phone and block the SIM. Ask for a duplicate SIM.\n"
                "3. Change your Google password. In your Google account: Security > Manage all devices > Sign out the lost phone.\n"
                "4. Block UPI and cards in your bank app or by calling the bank. WhatsApp: log in on the new SIM, the old phone is logged out.\n"
                "5. Make a police complaint (FIR) and keep a copy. Then block the phone's IMEI on Sanchar Saathi (CEIR). The IMEI is on the phone box or bill.\n"
                "Use the buttons below to open Find Hub or Sanchar Saathi.")
    return None
