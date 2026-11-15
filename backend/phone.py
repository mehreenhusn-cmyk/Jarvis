"""Jarvis phone check (Part 24, 65): "why is my phone slow", "phone me kya problem hai", "bluetooth connected hai kya", "internet chal raha hai kya".
Reads numbers only (memory, storage, battery, heat, network, Bluetooth audio device name). No apps, no files, no messages. Nothing is saved."""
import os, re, shutil

ASK = re.compile(r"phone (?:is )?(?:slow|hang|lag)|why is my phone|phone health|phone check|slow phone|फ़ोन धीमा|फोन धीमा|phone slow"
                 r"|\b(?:phone|mobile)\b(?!.{0,12}\b(?:number|nambar)\b).{0,20}\b(?:problem|dikkat|issue|kharab|slow|hang|lag(?:ging)?|garam|gram|hot|heat(?:ing)?|health|check|theek|thik|wrong)\b"
                 r"|what'?s wrong with my (?:phone|mobile)|battery (?:health|kharab|jaldi|drain)|फोन में क्या|फोन गर्म", re.I)  # Part 65: Roman Hindi and English
BT = re.compile(r"bluetooth|ब्लूटूथ|\bbt\b|earbuds?|airpods?|headphones?|हेडफोन", re.I)
NET = re.compile(r"wi-?fi|वाईफाई|internet|इंटरनेट|\bnet\b|network|mobile data|net data", re.I)
STORE = re.compile(r"storage|स्टोरेज|memory|मेमोरी|\bram\b|space", re.I)
STAT = re.compile(r"connected|connect (?:hai|hua|ho)|chal (?:raha|rha|rahi)|chalu hai|(?:on|off|band) hai|kis se|kisse|kaun ?sa|konsa|status|working|slow|kitna|kitni|bacha|कनेक्ट|चल रहा|चालू है|कौन|कितना|बचा", re.I)
HOWQ = re.compile(r"\b(?:how|kaise|kyun|kyu|why|what is|python|code|install|setup|tutorial|difference|meaning)\b|कैसे|क्यों", re.I)  # advice and coding questions stay normal chat
CMD = re.compile(r"\b(?:open|kholo|khol|turn|switch|on kar\w*|off kar\w*|band kar\w*|chalu kar\w*|enable|disable|connect kar\w*|jodo|laga\w*)\b|ओपन|खोलो|ऑन|ऑफ|बंद कर|चालू कर", re.I)  # "bluetooth on karo" is a settings command (actions.py), not a question


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
    if i.get("battery") is not None and i["battery"] <= 15 and not i.get("charging"):
        out.append((say(f"बैटरी सिर्फ़ {i['battery']}% है।", f"Battery is only {i['battery']}%."), say("चार्जर लगाइए।", "Plug in the charger.")))
    hl = {3: ("बैटरी ज़्यादा गर्म है।", "The battery is overheating.", "चार्जिंग रोकिए और फ़ोन को ठंडा होने दीजिए।", "Stop charging and let it cool."),
          4: ("बैटरी खराब (dead) बताई गई है।", "Android reports the battery as dead.", "सर्विस सेंटर पर दिखाइए।", "Show it at a service centre."),
          5: ("बैटरी में ओवर-वोल्टेज की रिपोर्ट है।", "Android reports battery over-voltage.", "दूसरा चार्जर आज़माइए।", "Try another charger."),
          6: ("बैटरी में फ़ेल्योर की रिपोर्ट है।", "Android reports a battery failure.", "सर्विस सेंटर पर दिखाइए।", "Show it at a service centre."),
          7: ("बैटरी बहुत ठंडी है।", "The battery is too cold.", "फ़ोन को सामान्य तापमान में लाइए।", "Bring the phone to room temperature.")}
    if i.get("health") in hl:
        h = hl[i["health"]]
        out.append((say(h[0], h[1]), say(h[2], h[3])))
    if i.get("airplane"):
        out.append((say("Airplane mode चालू है, इसलिए नेटवर्क नहीं है।", "Airplane mode is ON, so there is no network."), say("इसे बंद कीजिए।", "Turn it off.")))
    elif i.get("net") == "none":
        out.append((say("कोई इंटरनेट कनेक्शन नहीं है।", "There is no internet connection."), say("Wi-Fi या मोबाइल डेटा चालू कीजिए, या सिग्नल देखिए।", "Turn on Wi-Fi or mobile data, or check the signal.")))
    elif i.get("net") in ("wifi", "mobile", "ethernet") and i.get("net_ok") is False:
        w = "Wi-Fi" if i["net"] == "wifi" else "मोबाइल डेटा" if hindi else "Mobile data"
        out.append((say(f"{w} जुड़ा है, पर Android कहता है इंटरनेट काम नहीं कर रहा।", f"{w} is connected, but Android says the internet is not working."),
                    say("राउटर रीस्टार्ट कीजिए या नेटवर्क बदलिए।", "Restart the router or switch network.")))
    if i.get("uptime_h", 0) >= 168:
        out.append((say(f"फ़ोन {i['uptime_h'] // 24} दिन से बंद नहीं हुआ।", f"The phone has not restarted for {i['uptime_h'] // 24} days."), say("एक बार रीस्टार्ट कीजिए।", "Restart it once.")))
    return out


def _bt(i, say):
    if "bt_on" not in i:
        return None
    if not i["bt_on"]:
        return say("Bluetooth बंद है।", "Bluetooth is OFF.")
    names = [str(x) for x in (i.get("bt_audio") or []) if x]
    if names:
        return say("Bluetooth चालू है। जुड़ा हुआ ऑडियो डिवाइस: " + ", ".join(names) + "।", "Bluetooth is ON. Connected audio device: " + ", ".join(names) + ".")
    return say("Bluetooth चालू है, पर कोई ऑडियो डिवाइस (ईयरबड्स, स्पीकर, कार) जुड़ा नहीं दिख रहा। घड़ी या माउस जैसे डिवाइस मैं नहीं देख सकता।",
               "Bluetooth is ON, but no audio device (earbuds, speaker, car) is connected. I cannot see other devices like a watch or mouse.")


def _net(i, say):
    if "net" not in i:
        return None
    if i.get("airplane"):
        return say("Airplane mode चालू है, इसलिए इंटरनेट नहीं है।", "Airplane mode is ON, so there is no internet.")
    k, ok = i["net"], i.get("net_ok")
    nm = {"wifi": "Wi-Fi", "mobile": say("मोबाइल डेटा", "Mobile data"), "ethernet": "Ethernet", "other": say("नेटवर्क", "Network")}
    if k == "none":
        return say("कोई इंटरनेट कनेक्शन नहीं है। Wi-Fi या मोबाइल डेटा चालू कीजिए।", "There is no internet connection. Turn on Wi-Fi or mobile data.")
    if ok:
        return say(f"{nm[k]} से जुड़ा है और इंटरनेट चल रहा है।", f"Connected through {nm[k]} and the internet works.")
    return say(f"{nm[k]} जुड़ा है, पर Android कहता है इंटरनेट काम नहीं कर रहा। राउटर या सिग्नल देखिए।", f"{nm[k]} is connected, but Android says the internet is not working. Check the router or signal.")


def topic(msg):
    """'bt', 'net', 'store', 'all' or '' (not about the phone). Questions only: a command like "bluetooth on karo" is not handled here."""
    m = msg.strip()
    if len(m) > 90:
        return ""
    short = STAT.search(m) and not CMD.search(m) and not HOWQ.search(m)
    if BT.search(m) and short:
        return "bt"
    if NET.search(m) and short:
        return "net"
    if STORE.search(m) and short and re.search(r"kitna|kitni|bacha|free|khali|full|bhar|कितना|खाली|भरा", m, re.I):
        return "store"
    return "all" if ASK.search(m) else ""


def handle(msg, info, hindi):
    """Reply if the message asks about phone health, Bluetooth, internet or storage, else None."""
    t = topic(msg)
    if not t:
        return None
    say = lambda hi, en: hi if hindi else en
    i = info if isinstance(info, dict) else local_info()
    src = "" if isinstance(info, dict) else say("\n(Chrome में सिर्फ़ मेमोरी और स्टोरेज देखे गए। पूरी जाँच के लिए Jarvis ऐप चलाइए।)", "\n(Chrome mode: only memory and storage are checked. Use the Jarvis app for battery, Bluetooth and internet.)")
    if not i:
        return say("सर, मैं फ़ोन की जानकारी नहीं पढ़ पाया।", "Sir, I could not read the phone numbers.")
    if t in ("bt", "net"):
        r = (_bt if t == "bt" else _net)(i, say)
        if r is None:  # Chrome page: these are known only to the Android app
            return say("सर, यह जानकारी सिर्फ़ Jarvis Android ऐप से मिलती है, Chrome से नहीं।", "Sir, this is available only in the Jarvis Android app, not in Chrome.")
        return say("सर, ", "Sir, ") + r
    if t == "store":
        bits = []
        if i.get("disk_total"):
            bits.append(f"{say('स्टोरेज', 'Storage')} {pct_free(i['disk_free'], i['disk_total'])}% {say('खाली', 'free')} ({i['disk_free'] / 1e9:.1f} GB)")
        if i.get("ram_total"):
            bits.append(f"RAM {pct_free(i['ram_free'], i['ram_total'])}% {say('खाली', 'free')}")
        return say("सर, ", "Sir, ") + ", ".join(bits) + "." + src if bits else say("सर, मैं स्टोरेज नहीं पढ़ पाया।", "Sir, I could not read the storage.")
    found = analyze(i, hindi)
    bits = []
    if i.get("ram_total"):
        bits.append(f"RAM {pct_free(i['ram_free'], i['ram_total'])}% {'खाली' if hindi else 'free'}")
    if i.get("disk_total"):
        bits.append(f"{'स्टोरेज' if hindi else 'Storage'} {pct_free(i['disk_free'], i['disk_total'])}% {'खाली' if hindi else 'free'}")
    if "temp_c" in i and i["temp_c"]:
        bits.append(f"{i['temp_c']:.0f}°C")
    if "battery" in i:
        bits.append(f"{'बैटरी' if hindi else 'Battery'} {i['battery']}%" + ((" (चार्ज हो रहा)" if hindi else " (charging)") if i.get("charging") else ""))
    head = (say("सर, फ़ोन की जाँच: ", "Sir, phone check: ")) + ", ".join(bits) + "."
    extra = [x for x in (_net(i, say), _bt(i, say)) if x]
    body = head + ("\n" + "\n".join(f"- {x}" for x in extra) if extra else "")
    if not found:
        return body + say("\nकोई दिक्कत नहीं दिख रही। धीमेपन की वजह शायद कोई भारी ऐप है।", "\nNo problem found. A heavy app may be the cause if it feels slow.") + src
    return body + say("\nदिक्कतें:\n", "\nProblems found:\n") + "\n".join(f"- {p} {a}" for p, a in found) + src


def pct_free(a, b):
    return int(100 * a / b) if b else 0
