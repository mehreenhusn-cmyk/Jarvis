"""Jarvis phone check (Part 24, 65): "why is my phone slow", "phone me kya problem hai", "bluetooth connected hai kya", "internet chal raha hai kya".
Reads numbers only (memory, storage, battery, heat, network, Bluetooth audio device name). No apps, no files, no messages. Nothing is saved."""
import calendar, json, os, re, shutil, time

ASK = re.compile(r"phone (?:is )?(?:slow|hang|lag)|why is my phone|phone health|phone check|slow phone|फ़ोन धीमा|फोन धीमा|phone slow"
                 r"|\b(?:phone|mobile)\b(?!.{0,12}\b(?:number|nambar)\b).{0,20}\b(?:problem|dikkat|issue|kharab|slow|hang|lag(?:ging)?|garam|gram|hot|heat(?:ing)?|health|check|theek|thik|wrong)\b"
                 r"|what'?s wrong with my (?:phone|mobile)|battery (?:health|kharab|jaldi|drain)|फोन में क्या|फोन गर्म", re.I)  # Part 65: Roman Hindi and English
DEEP = re.compile(r"phone doctor|deep (?:phone )?check|full phone check|phone performance|performance doctor|poori phone (?:ki )?jaanch|फोन डॉक्टर", re.I)  # Part 79
TREND = re.compile(r"storage trend|storage (?:kitna|kitni) (?:ghata|ghati|kam hua|kam hui)|storage kahan gaya|phone trend|trend of (?:my )?storage|स्टोरेज (?:ट्रेंड|कितना घटा)", re.I)  # Part 82
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phone_trend.json")  # {"2026-11-17": [free_bytes, total_bytes]}, last 40 days, numbers only
BT = re.compile(r"bluetooth|ब्लूटूथ|\bbt\b|earbuds?|airpods?|headphones?|हेडफोन", re.I)
NET = re.compile(r"wi-?fi|वाईफाई|internet|इंटरनेट|\bnet\b|network|mobile data|net data", re.I)
STORE = re.compile(r"storage|स्टोरेज|memory|मेमोरी|\bram\b|space", re.I)
STAT = re.compile(r"connected|connect (?:hai|hua|ho)|chal (?:raha|rha|rahi)|chalu hai|(?:on|off|band) hai|kis se|kisse|kaun ?sa|konsa|status|working|slow|kitna|kitni|bacha|कनेक्ट|चल रहा|चालू है|कौन|कितना|बचा", re.I)
HOWQ = re.compile(r"\b(?:how|kaise|kyun|kyu|why|what is|python|code|install|setup|tutorial|difference|meaning)\b|कैसे|क्यों", re.I)  # advice and coding questions stay normal chat
CMD = re.compile(r"\b(?:open|kholo|khol|turn|switch|on kar\w*|off kar\w*|band kar\w*|chalu kar\w*|enable|disable|connect kar\w*|jodo|laga\w*)\b|ओपन|खोलो|ऑन|ऑफ|बंद कर|चालू कर", re.I)  # "bluetooth on karo" is a settings command (actions.py), not a question


def _days():
    try:
        d = json.load(open(FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: v for k, v in d.items() if isinstance(d, dict) and re.fullmatch(r"\d{4}-\d\d-\d\d", str(k)) and isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) for x in v)}


def note(i):
    """Part 82: once a day (the last number of the day wins) keep the phone's free storage, ONLY when the numbers come from the Android app (Chrome would give Termux's disk, a different thing). Two numbers per day, nothing else."""
    if not isinstance(i, dict) or not isinstance(i.get("disk_free"), (int, float)) or not isinstance(i.get("disk_total"), (int, float)) or i["disk_total"] <= 0:
        return
    d = _days()
    d[time.strftime("%Y-%m-%d")] = [int(i["disk_free"]), int(i["disk_total"])]
    d = dict(sorted(d.items())[-40:])
    try:
        with open(FILE + ".tmp", "w", encoding="utf-8") as f:
            json.dump(d, f)
        os.replace(FILE + ".tmp", FILE)
    except OSError:
        pass  # a trend is nice to have; never break a chat for it


def _trend(d):
    """(gb_change, days_between, free_gb_now, days_until_full or None) from the saved days, or None if there are fewer than 2 days. Compares today with the oldest day within the last 7 (else the oldest saved)."""
    ds = sorted(d)
    if len(ds) < 2:
        return None
    day = lambda k: calendar.timegm(time.strptime(k, "%Y-%m-%d")) // 86400
    last = ds[-1]
    ref = next((k for k in ds[:-1] if day(last) - day(k) <= 7), ds[0])
    span = max(1, day(last) - day(ref))
    ch = (d[last][0] - d[ref][0]) / 1e9
    full = d[last][0] / 1e9 / (-ch / span) if ch < -0.05 * span else None
    return ch, span, d[last][0] / 1e9, full


def trend_text(hindi):
    say = lambda hi, en: hi if hindi else en
    d = _days()
    t = _trend(d)
    if not t:
        return say(f"सर, ट्रेंड के लिए कम से कम 2 दिन के नंबर चाहिए। अभी {len(d)} दिन का है। रोज़ briefing या phone doctor बोलिए (Jarvis ऐप में)।",
                   f"Sir, a trend needs numbers from at least 2 days. I have {len(d)} so far. Say briefing or phone doctor once a day (in the Jarvis app).")
    ch, span, now_gb, full = t
    s = (say(f"सर, खाली स्टोरेज अभी {now_gb:.1f} GB है, {span} दिन पहले से {abs(ch):.1f} GB कम।", f"Sir, free storage is {now_gb:.1f} GB now, {abs(ch):.1f} GB less than {span} day(s) ago.") if ch < -0.05
         else say(f"सर, खाली स्टोरेज अभी {now_gb:.1f} GB है, {span} दिन पहले से {ch:.1f} GB ज़्यादा।", f"Sir, free storage is {now_gb:.1f} GB now, {ch:.1f} GB more than {span} day(s) ago.") if ch > 0.05
         else say(f"सर, खाली स्टोरेज अभी {now_gb:.1f} GB है, {span} दिन में लगभग वही।", f"Sir, free storage is {now_gb:.1f} GB now, about the same as {span} day(s) ago."))
    if full is not None and full < 365:
        s += say(f" इसी रफ़्तार से लगभग {full:.0f} दिन में भर जाएगा।", f" At this speed it will be full in about {full:.0f} days.")
    return s + say("\n(सिर्फ़ उन दिनों के नंबर जब आपने ऐप में briefing या phone check बोला।)", "\n(Only the days when you said briefing or phone check in the app.)")


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
    if TREND.search(m):
        return "trend"
    if DEEP.search(m):
        return "deep"
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
    note(info)  # Part 82
    t = topic(msg)
    if not t:
        return None
    say = lambda hi, en: hi if hindi else en
    if t == "trend":
        return trend_text(hindi)
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
    if t == "deep":
        found += deep(i, hindi)
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
    if t == "deep":  # Part 79: honest list of what Android does not give
        body += "\n" + deep_info(i, hindi) + "\n" + say("उपलब्ध नहीं: CPU लोड, हर ऐप की बैटरी/RAM/स्टोरेज और भारी ऐप के नाम। Android आम ऐप को ये नहीं देता और Jarvis Usage Access माँगता नहीं। ऐप देखने के लिए Settings > Battery या Storage खोलिए।",
                                                   "Unavailable: CPU load, per-app battery/RAM/storage and heavy-app names. Android does not give these to normal apps and Jarvis does not ask for Usage Access. To see apps, open Settings > Battery or Storage.")
    if not found:
        return body + say("\nकोई दिक्कत नहीं दिख रही। धीमेपन की वजह शायद कोई भारी ऐप है।", "\nNo problem found. A heavy app may be the cause if it feels slow.") + src
    return body + say("\nदिक्कतें:\n", "\nProblems found:\n") + "\n".join(f"- {p} {a}" for p, a in found) + src


def deep_info(i, hindi):
    """Part 79: extra real numbers, only the ones Android gave. Missing ones are named, never guessed."""
    say = lambda hi, en: hi if hindi else en
    L = []
    if i.get("volt_mv"):
        L.append(f"{say('बैटरी वोल्टेज', 'Battery voltage')} {i['volt_mv'] / 1000:.2f} V")
    L.append(f"{say('चार्ज साइकल', 'Charge cycles')} {i['cycles']}" if "cycles" in i else say("चार्ज साइकल: उपलब्ध नहीं (Android 14 और फ़ोन की रिपोर्ट चाहिए)", "Charge cycles: unavailable (needs Android 14 and a phone that reports it)"))
    if i.get("charge_mah"):
        L.append(f"{say('अभी बैटरी में', 'Charge now')} ~{i['charge_mah']} mAh")
    if i.get("ram_total"):
        L.append(f"RAM {i['ram_free'] / 1e9:.1f} / {i['ram_total'] / 1e9:.1f} GB {say('खाली', 'free')}")
    if i.get("uptime_h") is not None:
        L.append(f"{say('बिना रीस्टार्ट', 'Up for')} {i['uptime_h'] // 24} {say('दिन', 'd')} {i['uptime_h'] % 24} h")
    if "bright_pct" in i:
        L.append(f"{say('ब्राइटनेस', 'Brightness')} {i['bright_pct']}%" + (f" ({say('ऑटो', 'auto')})" if i.get("auto_bright") else ""))
    if i.get("screen_timeout_s"):
        L.append(f"{say('स्क्रीन टाइमआउट', 'Screen timeout')} {i['screen_timeout_s']} s")
    t = _trend(_days())  # Part 82: only when 2 or more days are saved
    if t:
        L.append(f"{say('खाली स्टोरेज बदलाव', 'Free storage change')} {t[0]:+.1f} GB / {t[1]} {say('दिन', 'd')}")
    return say("गहरी जाँच:\n", "Deep check:\n") + "\n".join(f"- {x}" for x in L)


def deep(i, hindi):
    """Part 79: advice only from real numbers."""
    say = lambda hi, en: hi if hindi else en
    out = []
    if i.get("screen_timeout_s", 0) > 60:
        out.append((say(f"स्क्रीन {i['screen_timeout_s']} सेकंड जलती रहती है, बैटरी जाती है।", f"The screen stays on for {i['screen_timeout_s']} s, which drains the battery."), say("टाइमआउट 30 सेकंड रखिए।", "Set the timeout to 30 s.")))
    if i.get("bright_pct", 0) >= 80 and not i.get("auto_bright"):
        out.append((say(f"ब्राइटनेस {i['bright_pct']}% पर है।", f"Brightness is at {i['bright_pct']}%."), say("ऑटो ब्राइटनेस चालू कीजिए।", "Turn on auto brightness.")))
    if i.get("cycles", 0) >= 800:
        out.append((say(f"बैटरी के {i['cycles']} चार्ज साइकल हो चुके हैं।", f"The battery has done {i['cycles']} charge cycles."), say("बैटरी पुरानी हो गई है, बदलवाने का सोचिए।", "It is ageing; think about replacing it.")))
    t = _trend(_days())  # Part 82: a real number, a real warning
    if t and t[3] is not None and t[3] < 30:
        out.append((say(f"खाली स्टोरेज रोज़ लगभग {abs(t[0]) / t[1]:.1f} GB घट रहा है, लगभग {t[3]:.0f} दिन में भर जाएगा।", f"Free storage is falling about {abs(t[0]) / t[1]:.1f} GB a day, so it may be full in about {t[3]:.0f} days."),
                    say("बड़े वीडियो, डाउनलोड और पुरानी फ़ाइलें हटाइए।", "Delete big videos, downloads and old files.")))
    return out


def pct_free(a, b):
    return int(100 * a / b) if b else 0
