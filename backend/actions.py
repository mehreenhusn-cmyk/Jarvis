"""Jarvis command layer (Part 30). Turns "WhatsApp kholo" into ONE action from a FIXED list. The server only proposes; the Android app
(Java) checks the master switch, Stop and the real app list before anything happens. The AI never gives code, shell or package names."""
import json, re

ACTIONS = {"open_app"}  # what the AI fallback may return. Only open_app, nothing else.
SCREEN = {"click", "scroll", "swipe", "type", "back", "home", "current_app", "lock"}  # Part 34: only the user's own words can make these; the AI fallback never can.
SAFE = {"open_app"}  # Part 33: these run after the master switch. Anything else needs a preview and Hussain's own tap on Yes, every single time.
EN = {"open", "launch", "start", "run"}
HI = {"kholo", "khol", "kholna", "kholiye", "kholiyega", "kholen", "chalao", "chala", "chalu", "shuru", "खोलो", "खोल", "खोलना", "खोलिए", "खोलिये", "खोलें", "चलाओ", "चला", "चालू", "चालु", "शुरू"}
FILL = set("please plz pls jarvis जार्विस जारविस sir सर ko को app ap application ek एक zara jara जरा na ना kar karo kr कर करो do दो de दे dena dijiye दीजिए the my mera mere meri मेरा मेरे मेरी mujhe मुझे hai है hain chahiye चाहिए can could will you hey ok okay tum aap आप तुम bhai भाई जी ji phir fir अब ab".split())
QW = set("kya kaise kyun kyu kab kaun what why how when who which क्या कैसे क्यों कब कौन".split())
NEAR = EN | HI | {"jao", "jana", "jaana", "जाओ", "जाना"}  # words that make a message look like a command (for the AI fallback)

_key = lambda s: re.sub(r"[\s़.\-']", "", s.lower())
CANON = {
    "WhatsApp": "व्हाट्सएप व्हाट्सऐप वाट्सएप वॉट्सऐप whatsap watsapp whatsup", "Chrome": "क्रोम chrom गूगलक्रोम googlechrome", "YouTube": "यूट्यूब utube यू_ट्यूब",
    "Instagram": "इंस्टाग्राम इंस्टा insta", "Facebook": "फेसबुक fb", "Gmail": "जीमेल", "Maps": "मैप्स गूगलमैप्स googlemaps", "Camera": "कैमरा",
    "Phone": "फोन फ़ोन dialer डायलर", "Messages": "मैसेज मैसेजेस sms", "Settings": "सेटिंग्स सेटिंग", "Calculator": "कैलकुलेटर", "Clock": "घड़ी क्लॉक",
    "Gallery": "गैलरी", "Photos": "फोटोज फ़ोटोज", "Telegram": "टेलीग्राम", "Paytm": "पेटीएम", "PhonePe": "फोनपे", "Google Pay": "गूगलपे gpay",
    "Spotify": "स्पॉटिफाई", "Termux": "टर्मक्स", "Play Store": "प्लेस्टोर playstore", "Calendar": "कैलेंडर", "Contacts": "कॉन्टैक्ट्स", "Files": "फाइल्स",
    "Netflix": "नेटफ्लिक्स", "Amazon": "अमेज़न अमेजन", "Flipkart": "फ्लिपकार्ट", "Snapchat": "स्नैपचैट", "Twitter": "ट्विटर"}
ALIAS = {_key(a): c for c, v in CANON.items() for a in v.split() + [c]}


def _words(msg):
    return re.findall(r"[\w\u0900-\u097F]+", re.sub(r"[।॥]", " ", msg.lower()))


def _trim(w):
    while w and w[0] in FILL:
        w = w[1:]
    while w and w[-1] in FILL:
        w = w[:-1]
    return w


def parse(msg):
    """App name if the message is an open-app command ("" = no name given), else None. Short, no question words, so chat is not hijacked."""
    if "?" in msg or len(msg) > 80:
        return None
    w = _words(msg)
    if not w or len(w) > 7 or QW & set(w):
        return None
    w = _trim(w)
    if not w:
        return None
    if w[0] in EN or w[0] in HI:
        name = _trim(w[1:])
    elif w[-1] in HI or w[-1] in EN:
        name = _trim(w[:-1])
    else:
        return None
    return " ".join(name) if len(name) <= 4 else None


def ai_name(msg, ask):
    """Limited AI fallback: only for command-looking phrases the grammar missed. The AI may only answer one JSON line; we check it."""
    w = _words(msg)
    if "?" in msg or len(msg) > 120 or len(w) > 12 or not (NEAR & set(w)):
        return None
    extra = ("\n\nCOMMAND MODE. Decide if the user message asks to open an app on the phone. Answer with ONE line of JSON and nothing else: "
             '{"action":"open_app","app":"<app name as a person would say it>"} or {"action":"none"}. No other keys, no explanation.')
    try:
        out, _ = ask([{"role": "user", "content": msg}], "english", extra)
    except RuntimeError:
        return None
    m = re.search(r"\{.*?\}", out or "", re.S)
    try:
        d = json.loads(m.group()) if m else None
    except ValueError:
        return None
    if not isinstance(d, dict) or d.get("action") not in ACTIONS or not isinstance(d.get("app"), str):
        return None
    name = re.sub(r"[^\w\u0900-\u097F .&+\-]", "", d["app"]).strip()[:40]
    return name or None


# ---- Part 33: risk and confirm rules. Only Hussain's own words decide this, never screen or web text. ----
RISK = [  # checked in this order; Hindi words have no \b because Devanagari marks break it
    ("pay", r"\b(?:pay|payment|transfer|upi|paise bhej\w*|paisa bhej\w*|rupe\w* bhej\w*)\b|भुगतान|पेमेंट|ट्रांसफर|पैसे भेज|पैसा भेज", "a payment or money transfer", "पैसे भेजना या भुगतान"),
    ("buy", r"\b(?:buy|purchase|order|kharid\w*|mangao|mangwao)\b|खरीद|ऑर्डर|मंगा", "buying or ordering something", "कुछ खरीदना या ऑर्डर करना"),
    ("install", r"\b(?:install|download)\b|इंस्टॉल|इंस्टाल|डाउनलोड", "installing or downloading an app", "ऐप इंस्टॉल या डाउनलोड करना"),
    ("delete", r"\b(?:delete|remove|uninstall|erase|hatao|hata do|mita do|mitao)\b|डिलीट|हटाओ|हटा दो|मिटा|अनइंस्टॉल", "deleting something", "कुछ डिलीट करना"),
    ("account", r"\b(?:log ?out|sign ?out|log ?in|sign ?in|account|password (?:change|badal\w*|reset))\b|लॉग ?आउट|साइन ?आउट|अकाउंट|पासवर्ड (?:बदल|रीसेट)", "an account change (login, logout, password)", "अकाउंट बदलना (लॉगिन, लॉगआउट, पासवर्ड)"),
    ("send", r"(?=.*(?:\b(?:bhej\w*|send|forward)\b|भेज))(?=.*(?:\b(?:message|msg|sms|whatsapp|mail|email|text|sandesh|photo|pic)\b|मैसेज|संदेश|ईमेल|व्हाट्सएप|फोटो))", "sending a message or file", "मैसेज या फ़ाइल भेजना"),
]
RISK = [(k, re.compile(rx, re.I | re.S), en, hi) for k, rx, en, hi in RISK]
NOTYPE = re.compile(r"(?=.*(?:\b(?:type|enter|fill|put|write|daal\w*|dal\w*|likho|likh|bharo|bhar)\b|डालो|डाल|भरो|लिखो))"
                    r"(?=.*(?:\b(?:password|passcode|otp|pin|cvv|card (?:number|no))\b|पासवर्ड|ओटीपी|पिन|कार्ड नंबर))", re.I | re.S)


def _command_like(msg):
    w = _words(msg)
    return "?" not in msg and len(msg) <= 120 and 0 < len(w) <= 12 and not (QW & set(w))


def risk_of(msg):
    """(kind, English label, Hindi label) if the message asks for a dangerous thing, else None."""
    if not _command_like(msg):
        return None
    for k, rx, en, hi in RISK:
        if rx.search(msg):
            return k, en, hi
    return None


def blocked(msg):
    """True if the message asks Jarvis to type a password, OTP, PIN or card number. Jarvis never does that, switch ON or OFF."""
    return _command_like(msg) and bool(NOTYPE.search(msg))


# ---- Part 34: safe screen actions. Same rule: only Hussain's own words in this turn, never screen or web text. ----
GO = set("go jao ja जाओ जा chalo चलो press dabao दबाओ karo kar kr करो कर please plz the page screen स्क्रीन".split())
BACKW, HOMEW = {"back", "peeche", "piche", "पीछे", "wapas", "वापस"}, {"home", "होम"}
SCRW, DOWN, UP = {"scroll", "स्क्रॉल", "skrol"}, {"down", "neeche", "niche", "नीचे"}, {"up", "upar", "oopar", "ऊपर"}
CLICK_EN, CLICK_HI = {"click", "tap", "press"}, {"dabao", "dabaye", "dabaiye", "दबाओ", "दबाइए", "दबाएं"}
THIS = set("is isko ye yeh yah this it इस इसे यह ये".split())
BTN = {"button", "btn", "बटन", "tab", "option"}
LOCKW, PHONEW = {"lock", "लॉक"}, {"phone", "फोन", "फ़ोन", "mobile", "मोबाइल", "screen", "स्क्रीन"}  # Part 35: lock only. There is no unlock command and there never will be.
TYPE_RX = re.compile(r"^\s*(?:type|likho|लिखो|टाइप)\s*(?:karo|kar do|kar|करो|कर दो)?\s*[:,\-]?\s*(.+)$", re.I | re.S)
APP_RX = re.compile(r"(?:which|what|kaun ?sa|konsa|कौन ?सा).{0,20}(?:app|ऐप|एप).{0,20}(?:open|khula|chal|screen|खुला|चल|on)|current app", re.I)
LABEL_RISK = re.compile(r"\b(?:send|submit|pay|buy|order|delete|remove|uninstall|install|log ?out|sign ?out|transfer|confirm)\b|भेज|पेमेंट|भुगतान|खरीद|ऑर्डर|डिलीट|हटा|इंस्टॉल|लॉग ?आउट|कन्फर्म", re.I)


def secret_text(t):
    """True if the text to type looks like an OTP, PIN, card number or a password. Jarvis never types those."""
    d = re.sub(r"\D", "", t)
    return bool(re.search(r"password|passcode|\botp\b|\bpin\b|cvv|पासवर्ड|ओटीपी|पिन", t, re.I)) or (d == re.sub(r"[\s-]", "", t) and (4 <= len(d) <= 8 or 13 <= len(d) <= 19))


def screen_cmd(msg):
    """(action or None, English text, Hindi text) for back, home, scroll, click, type, current app. None = not a screen command."""
    m = msg.strip()
    if len(m) > 200:
        return None
    tm = TYPE_RX.match(m)
    if tm and "?" not in m and not (QW & set(_words(m))) and _words(tm.group(1))[:1] != ["of"]:
        t = tm.group(1).strip()[:200]
        if secret_text(t):
            return None, "Sir, I never type passwords, OTPs, PINs or card numbers. Please type it yourself.", "सर, मैं पासवर्ड, OTP, PIN या कार्ड नंबर कभी टाइप नहीं करता। कृपया आप खुद टाइप कीजिए।"
        return {"type": "type", "text": t}, f"Typing \"{t[:60]}\" in the text box, sir. It replaces what is in the box.", f"ठीक है सर, टेक्स्ट बॉक्स में \"{t[:60]}\" लिख रहा हूँ। बॉक्स में जो था वो बदल जाएगा।"
    if "?" in m and not APP_RX.search(m):
        return None
    if APP_RX.search(m) and len(m) <= 60:
        return {"type": "current_app"}, "Checking which app is open, sir.", "देखता हूँ सर, कौन सा ऐप खुला है।"
    w = _words(m)
    if not w or len(w) > 7:
        return None
    s = set(w)
    if s & BACKW and s <= BACKW | GO | FILL and s & GO - {"the", "page", "screen", "स्क्रीन", "please", "plz"}:
        return {"type": "back"}, "Going back, sir.", "ठीक है सर, पीछे जा रहा हूँ।"
    if s & HOMEW and s <= HOMEW | GO | FILL and s & GO - {"the", "page", "screen", "स्क्रीन", "please", "plz"}:
        return {"type": "home"}, "Going to the home screen, sir.", "ठीक है सर, होम स्क्रीन पर जा रहा हूँ।"
    if s & LOCKW and s & PHONEW and s <= LOCKW | PHONEW | GO | FILL and not s & {"app", "ऐप", "एप"}:
        return {"type": "lock"}, "Locking the phone, sir. I can lock it, but I never unlock it.", "ठीक है सर, फ़ोन लॉक कर रहा हूँ। अनलॉक मैं कभी नहीं करता।"
    if s & SCRW and s <= SCRW | DOWN | UP | GO | FILL and bool(s & DOWN) != bool(s & UP):
        d = "down" if s & DOWN else "up"
        return {"type": "scroll", "dir": d}, f"Scrolling {d}, sir.", ("नीचे" if d == "down" else "ऊपर") + " स्क्रॉल कर रहा हूँ सर।"
    x = _trim(w)
    name = None
    if x and (x[0] in CLICK_EN or x[0] in CLICK_HI):
        name = x[1:]
    elif x and x[-1] in CLICK_HI | CLICK_EN:
        name = x[:-1]
    if name is None:
        return None
    name = [i for i in _trim(name) if i not in BTN]
    if not name or set(name) <= THIS or len(name) > 4:
        return None, "Which button, sir? Please say its name, like \"click Settings\".", "कौन सा बटन सर? उसका नाम बोलिए, जैसे \"Settings दबाओ\"।"
    n = " ".join(name)
    act = {"type": "click", "name": n}
    if LABEL_RISK.search(n):  # a button like Send, Pay, Delete: the page must get Hussain's own tap on Yes first
        return {"type": "confirm", "risk": "click", "then": act}, f"Sir, this needs your Yes first: pressing \"{n}\". I will do nothing until you tap Yes.", f"सर, यह आपकी हाँ मांगता है: \"{n}\" दबाना। आपके Yes दबाने तक मैं कुछ नहीं करूँगा।"
    return act, f"Pressing \"{n}\", sir.", f"ठीक है सर, \"{n}\" दबा रहा हूँ।"


def handle(msg, hindi, control, in_app, ask):
    """None = not a command. Else (reply text, action dict or None). The page shows what REALLY happened after the app answers."""
    say = lambda hi, en: hi if hindi else en
    if blocked(msg):
        return say("सर, मैं पासवर्ड, OTP, PIN या कार्ड नंबर कभी टाइप नहीं करता। कृपया आप खुद टाइप कीजिए।", "Sir, I never type passwords, OTPs, PINs or card numbers. Please type it yourself."), None
    sc = screen_cmd(msg)  # Part 34
    if sc and sc[0] and sc[0]["type"] == "type" and not (control and in_app):
        sc = None  # "type hello" is only a command when phone control is ON in the app; otherwise it is normal chat
    rk = risk_of(msg) if (control and in_app) else None
    if rk:  # never runs by itself: the page shows the preview and waits for a real tap on Yes
        k, en, hi = rk
        then = (sc[0].get("then") or sc[0]) if sc and sc[0] and sc[0]["type"] in ("click", "type", "confirm") else None  # a concrete step that Yes may run
        return say(f"सर, यह आपकी हाँ मांगता है: {hi}। आपने कहा: \"{msg.strip()[:120]}\"। आपके Yes दबाने तक मैं कुछ नहीं करूँगा।",
                   f"Sir, this needs your Yes first: {en}. You said: \"{msg.strip()[:120]}\". I will do nothing until you tap Yes."), dict({"type": "confirm", "risk": k}, **({"then": then} if then else {}))
    if sc:
        if not in_app:
            return say("सर, फ़ोन कंट्रोल सिर्फ़ Jarvis ऐप में चलता है।", "Sir, phone control works only in the Jarvis Android app."), None
        if not control:
            return say("फ़ोन कंट्रोल बंद है सर। Settings में \"Phone control\" चालू कीजिए।", "Phone control is OFF, sir. Turn it on in Settings, under Phone control."), None
        return say(sc[2], sc[1]), sc[0]
    name = parse(msg)
    if name is None:
        name = ai_name(msg, ask) if (control and in_app) else None
        if name is None:
            return None
    if not in_app:
        return say("सर, फ़ोन कंट्रोल सिर्फ़ Jarvis ऐप में चलता है।", "Sir, phone control works only in the Jarvis Android app."), None
    if not control:
        return say("फ़ोन कंट्रोल बंद है सर। Settings में \"Phone control\" चालू कीजिए।", "Phone control is OFF, sir. Turn it on in Settings, under Phone control."), None
    if not name:
        return say("कौन सा ऐप खोलूँ सर?", "Which app should I open, sir?"), None
    label = ALIAS.get(_key(name), name)
    return say(f"ठीक है सर, {label} खोल रहा हूँ।", f"Opening {label}, sir."), {"type": "open_app", "name": label}
