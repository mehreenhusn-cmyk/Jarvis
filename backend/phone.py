"""Jarvis phone check (Part 24): "why is my phone slow". Reads numbers only (memory, storage, battery, heat). No apps, no files, no messages."""
import os, re, shutil

ASK = re.compile(r"phone (?:is )?(?:slow|hang|lag)|why is my phone|phone health|phone check|slow phone|फ़ोन धीमा|फोन धीमा|phone slow", re.I)


def local_info():
    """Fallback when the page is in Chrome (not the app): what Termux itself can read."""
    o = {}
    try:
        m = dict(re.findall(r"(\w+):\s+(\d+) kB", open("/proc/meminfo").read()))
        o["ram_total"], o["ram_free"] = int(m["MemTotal"]) * 1024, int(m["MemAvailable"]) * 1024
    except Exception:
        pass
    try:
        d = shutil.disk_usage(os.path.expanduser("~"))
        o["disk_total"], o["disk_free"] = d.total, d.free
    except Exception:
        pass
    return o


def analyze(i, hindi):
    """List of (problem, advice) found. Simple rules, no AI needed."""
    def say(hi, en):
        return hi if hindi else en
    out = []
    pct = lambda a, b: 100.0 * a / b if b else 100.0
    if i.get("ram_total"):
        f = pct(i["ram_free"], i["ram_total"])
        if f < 12 or i.get("ram_low"):
            out.append((say(f"मेमोरी कम है, सिर्फ़ {f:.0f}% खाली।", f"Memory is low: only {f:.0f}% free."),
                        say("बैकग्राउंड ऐप्स बंद कीजिए।", "Close apps running in the background.")))
    if i.get("disk_total"):
        f = pct(i["disk_free"], i["disk_total"])
        if f < 12:
            out.append((say(f"स्टोरेज लगभग भर गया है, {f:.0f}% खाली ({i['disk_free'] / 1e9:.1f} GB)।", f"Storage is almost full: {f:.0f}% free ({i['disk_free'] / 1e9:.1f} GB)."),
                        say("बड़े वीडियो, डाउनलोड और पुरानी ज़िप फ़ाइलें हटाइए।", "Delete big videos, downloads and old zip files.")))
    if i.get("temp_c", 0) >= 41 or i.get("thermal", 0) >= 2:
        out.append((say(f"फ़ोन गर्म है ({i.get('temp_c', '?')}°C), इसलिए धीमा हो सकता है।", f"The phone is hot ({i.get('temp_c', '?')}°C), so it may slow itself down."),
                    say("कवर हटाइए, धूप से दूर रखिए, कुछ देर आराम दीजिए।", "Remove the case, keep it out of the sun, and let it rest.")))
    if i.get("power_save"):
        out.append((say("बैटरी सेवर चालू है, इससे फ़ोन धीमा चलता है।", "Battery saver is on. It slows the phone."), say("इसे बंद कीजिए।", "Turn it off.")))
    if i.get("uptime_h", 0) >= 168:
        out.append((say(f"फ़ोन {i['uptime_h'] // 24} दिन से बंद नहीं हुआ।", f"The phone has not restarted for {i['uptime_h'] // 24} days."), say("एक बार रीस्टार्ट कीजिए।", "Restart it once.")))
    return out


def handle(msg, info, hindi):
    """Reply if the message asks about phone health, else None."""
    if not ASK.search(msg):
        return None
    i = info if isinstance(info, dict) else local_info()
    src = "" if isinstance(info, dict) else ("\n(Chrome mode: only memory and storage are checked. Use the Jarvis app for battery and heat.)" if not hindi else "\n(Chrome में सिर्फ़ मेमोरी और स्टोरेज देखे गए। पूरी जाँच के लिए Jarvis ऐप चलाइए।)")
    if not i:
        return "सर, मैं फ़ोन की जानकारी नहीं पढ़ पाया।" if hindi else "Sir, I could not read the phone numbers."
    found = analyze(i, hindi)
    bits = []
    if i.get("ram_total"):
        bits.append(f"RAM {pct_free(i['ram_free'], i['ram_total'])}% {'खाली' if hindi else 'free'}")
    if i.get("disk_total"):
        bits.append(f"{'स्टोरेज' if hindi else 'Storage'} {pct_free(i['disk_free'], i['disk_total'])}% {'खाली' if hindi else 'free'}")
    if "battery" in i:
        bits.append(f"{'बैटरी' if hindi else 'Battery'} {i['battery']}%")
    head = ("सर, फ़ोन की जाँच: " if hindi else "Sir, phone check: ") + ", ".join(bits) + "."
    if not found:
        return head + (" सब ठीक दिख रहा है। धीमेपन की वजह शायद कोई भारी ऐप है।" if hindi else " Everything looks fine. A heavy app may be the cause.") + src
    return head + "\n" + "\n".join(f"- {p} {a}" for p, a in found) + src


def pct_free(a, b):
    return int(100 * a / b) if b else 0
