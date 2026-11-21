"""Jarvis command layer (Part 30). Turns "WhatsApp kholo" into ONE action from a FIXED list. The server only proposes; the Android app
(Java) checks the master switch, Stop and the real app list before anything happens. The AI never gives code, shell or package names."""
import json, re
from difflib import get_close_matches
import lang
import appnames

ACTIONS = {"open_app"}  # what the AI fallback may return. Only open_app, nothing else.
SCREEN = {"click", "click_nth", "scroll", "swipe", "type", "back", "home", "current_app", "lock", "settings", "torch", "volume", "look", "tap"}  # Part 129 adds look and tap. Part 34: only the user's own words can make these; the AI fallback never can.
SAFE = {"open_app"}  # Part 33: these run after the master switch. Anything else needs a preview and Hussain's own tap on Yes, every single time.
EN = {"open", "launch", "start", "run", "ओपन", "ओपेन", "ओप्पण", "लॉन्च", "लांच", "स्टार्ट", "रन"}  # Part 59: Hindi-script spellings of the English words (phone dictation writes "open" as "ओपन")
HI = {"उघड", "उघडा", "उघडणे", "तिर", "तिरक्क", "तिरक्कवुम", "तिरक्कुम", "तेरुवु", "तेरवंडि", "तेरे", "तेरयिरि", "तुरक्कुक", "तुरक्कू", "खोल्हो", "खोल्हें", "kholo", "khol", "kholna", "kholiye", "kholiyega", "kholen", "chalao", "chala", "chalu", "shuru", "खोलो", "खोल", "खोलना", "खोलिए", "खोलिये", "खोलें", "चलाओ", "चला", "चालू", "चालु", "शुरू"}
FILL = set("please plz pls jarvis जार्विस जारविस sir सर ko को app ap application ek एक zara jara जरा na ना kar karo kr कर करो do दो de दे dena dijiye दीजिए the my mera mere meri मेरा मेरे मेरी mujhe मुझे hai है hain chahiye चाहिए can could will you hey ok okay tum aap आप तुम bhai भाई जी ji phir fir अब ab".split())
QW = set("kya kaise kyun kyu kab kaun what why how when who which क्या कैसे क्यों कब कौन".split())
LNOISE = set("main mai मैं मै yaar yar यार abhi अभी bhi भी ye यह wo वो".split())  # Part 139: filler the mic adds (was a local list in device_cmd)
PREPS = set("par pe pr पर पे ko को me mein में se से ka ki ke का की के to on le ले chal chalo चल चलो jana jaana जाना ho hona हो kijiye कीजिए karna करना".split())
NEAR = EN | HI | {"jao", "jana", "jaana", "जाओ", "जाना"}  # words that make a message look like a command (for the AI fallback)

_key = lambda s: re.sub(r"[\s़.\-'_]", "", s.lower()).translate(str.maketrans({"ू": "ु", "ी": "ि", "ॉ": "ो", "ँ": "ं", "्": ""}))  # Part 59: यूट्यूब and युटुब give a close key
CANON = {
    "WhatsApp": "वाट्सअप्प वाट्सऐप वाट्साप वाट्सप व्हाट्सएप व्हाट्सऐप वाट्सएप वॉट्सऐप whatsap watsapp whatsup", "Chrome": "क्रोम क्रोमे chrom गूगलक्रोम गूगल googlechrome", "YouTube": "यूट्यूब utube यू_ट्यूब युट्यूब युटुब यूटूब यूट्यूब यूट्यब यूटियूप यूटियूब यूटिऊब इउटिउब yt",
    "Instagram": "इंस्टाग्राम इंस्टा insta", "Facebook": "फेसबुक fb", "Gmail": "जीमेल", "Maps": "मैप्स गूगलमैप्स googlemaps", "Camera": "कैमरा",
    "Phone": "फोन फ़ोन dialer डायलर", "Messages": "मैसेज मैसेजेस sms", "Settings": "सेटिंग्स सेटिंग", "Calculator": "कैलकुलेटर", "Clock": "घड़ी क्लॉक",
    "Gallery": "गैलरी", "Photos": "फोटोज फ़ोटोज", "Telegram": "टेलीग्राम", "Paytm": "पेटीएम", "PhonePe": "फोनपे", "Google Pay": "गूगलपे gpay",
    "Spotify": "स्पॉटिफाई", "Termux": "टर्मक्स", "Play Store": "प्लेस्टोर playstore", "Calendar": "कैलेंडर", "Contacts": "कॉन्टैक्ट्स", "Files": "फाइल्स",
    "Netflix": "नेटफ्लिक्स", "Amazon": "अमेज़न अमेजन", "Flipkart": "फ्लिपकार्ट", "Snapchat": "स्नैपचैट", "Twitter": "ट्विटर"}
ALIAS = {_key(a): c for c, v in CANON.items() for a in v.split() + [c]}


APPS = []  # Part 201: the app names of the phone that is talking now; app.py sets them before each message (names only)


def set_apps(names):
    global APPS
    APPS = list(names or [])


def canon(name):
    """Known app name for what was said. Exact key first; then a close match (cutoff 0.84) so a small spelling slip still works. Else the words as said."""
    k = _key(name)
    if k in ALIAS:
        return ALIAS[k]
    from difflib import get_close_matches
    hit = get_close_matches(k, list(ALIAS), n=1, cutoff=0.84)
    return ALIAS[hit[0]] if hit else name


def _words(msg):
    return re.findall(r"[\w\u0900-\u097F]+", re.sub(r"[।॥]", " ", msg.lower()))


def _trim(w):
    while w and w[0] in FILL:
        w = w[1:]
    while w and w[-1] in FILL:
        w = w[:-1]
    return w


def _fuzzy(w, vocab, cutoff=0.8):
    """Part 73: nudge a slightly-misheard word (phone dictation writes 'alaam' for 'alarm', 'pazz' for 'pause') onto the
    closest word in vocab. Exact matches, short words (<4 letters) and numbers are left alone, so normal text never changes."""
    out = []
    for t in w:
        if t in vocab or len(t) < 4 or t.replace(".", "", 1).isdigit():
            out.append(t)
            continue
        hit = get_close_matches(t, vocab, n=1, cutoff=cutoff)
        out.append(hit[0] if hit else t)
    return out


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
    if name and set(name) <= PRON:
        return ""  # Part 139: only "it / usko / wahi": Jarvis asks which app instead of searching for an app called "usko"
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
AGAIN = set("aur और thoda थोड़ा thora again more phir फिर bhi भी baar बार once".split())  # Part 128: "thoda aur scroll karo", "aur neeche"
LOOSEF = FILL | GO | AGAIN | LNOISE | PREPS  # Part 139
ORD = {"pehla": 1, "pehle": 1, "first": 1, "पहला": 1, "dusra": 2, "doosra": 2, "second": 2, "दूसरा": 2, "teesra": 3, "tisra": 3, "third": 3, "तीसरा": 3, "chautha": 4, "chauthha": 4, "fourth": 4, "चौथा": 4,
       "panchva": 5, "paanchva": 5, "panchwa": 5, "fifth": 5, "पांचवा": 5, "पाँचवा": 5, "chatha": 6, "sixth": 6, "छठा": 6}
ITEMW = set("video vedio item result chart link card post song option row videos result photo reel वीडियो आइटम चार्ट लिंक रिज़ल्ट रिजल्ट".split())
OPENW = set("kholo khol open dabao click tap press play chalao खोलो खोल दबाओ चलाओ".split())
NTHFILL = set("ooper upar oopar se from top the a wala wali number no nambar ka ki ke jo hai ko ऊपर से वाला वाली नंबर नम्बर".split())
THIS = set("is isko ye yeh yah this it इस इसे यह ये".split())
PRON = THIS | set("usko use उसको उसे wahi wahin वही वहीं dobara दोबारा that them isse again wo वो".split())  # Part 139: "usko open karo" is not an app called usko
BTN = {"button", "btn", "बटन", "tab", "option"}
LOCKW, PHONEW = {"lock", "लॉक"}, {"phone", "फोन", "फ़ोन", "mobile", "मोबाइल", "screen", "स्क्रीन"}  # Part 35: lock only. There is no unlock command and there never will be.
TYPE_RX = re.compile(r"^\s*(?:type|likho|लिखो|टाइप)\s*(?:karo|kar do|kar|करो|कर दो)?\s*[:,\-]?\s*(.+)$", re.I | re.S)
APP_RX = re.compile(r"(?:which|what|kaun ?sa|konsa|कौन ?सा).{0,20}(?:app|ऐप|एप).{0,20}(?:open|khula|chal|screen|खुला|चल|on)|current app", re.I)
LABEL_RISK = re.compile(r"\b(?:send|submit|pay|buy|order|delete|remove|uninstall|install|log ?out|sign ?out|transfer|confirm)\b|भेज|पेमेंट|भुगतान|खरीद|ऑर्डर|डिलीट|हटा|इंस्टॉल|लॉग ?आउट|कन्फर्म", re.I)


def secret_text(t):
    """True if the text to type looks like an OTP, PIN, card number or a password. Jarvis never types those."""
    d = re.sub(r"\D", "", t)
    return bool(re.search(r"password|passcode|\botp\b|\bpin\b|cvv|पासवर्ड|ओटीपी|पिन", t, re.I)) or (d == re.sub(r"[\s-]", "", t) and (4 <= len(d) <= 8 or 13 <= len(d) <= 19))


# ---- Part 129: look and tap. Only this grammar, only the person's own words. ONE screenshot, a vision AI points, you see a number on it, and only your finger tap on Yes taps. ----
LOOK_RX = re.compile(r"^\s*(?:look\s*(?:and|n|&)\s*tap|look\s*tap|dekh\s*(?:ke|kar|kr)\s*(?:dabao|dabaao|tap\s*karo|click\s*karo|press\s*karo)|देख\s*(?:के|कर)\s*(?:दबाओ|टैप\s*करो))\s*[:,\-]?\s*(.{2,80}?)\s*[.!]?\s*$", re.I | re.S)


def look_cmd(msg):
    """The thing to find on the screen (text), or None if this is not a look-and-tap sentence."""
    m = LOOK_RX.match(msg.strip()) if len(msg) <= 160 and "?" not in msg else None
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


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
    nth = None  # Part 127: "ooper se teesra video kholo", "3rd item kholo", "number 3 result kholo"
    for x in w:
        if x in ORD:
            nth = ORD[x]
        elif re.fullmatch(r"\d{1,2}(?:st|nd|rd|th)?", x) and (s & ITEMW or s & {"number", "no", "nambar", "नंबर"}):
            nth = int(re.match(r"\d+", x).group())
    if nth and 1 <= nth <= 12 and s & OPENW and s <= set(ORD) | ITEMW | OPENW | NTHFILL | FILL | GO | {x for x in w if re.fullmatch(r"\d{1,2}(?:st|nd|rd|th)?", x)}:
        return {"type": "click_nth", "n": nth}, f"Opening item number {nth} from the top, sir.", f"ऊपर से {nth} नंबर का आइटम खोल रहा हूँ सर।"
    one = bool(s & DOWN) != bool(s & UP)
    if one and s <= SCRW | DOWN | UP | GO | FILL | AGAIN and (s & SCRW or s & GO or s & AGAIN):  # Part 128: "upar jao", "aur neeche", "scroll karo neeche"
        d = "down" if s & DOWN else "up"
        return {"type": "scroll", "dir": d}, f"Scrolling {d}, sir.", ("नीचे" if d == "down" else "ऊपर") + " स्क्रॉल कर रहा हूँ सर।"
    if s & SCRW and not (s & DOWN or s & UP) and s & AGAIN and s <= SCRW | AGAIN | GO | FILL:  # "thoda aur scroll karo": the page repeats the last direction
        return {"type": "scroll", "dir": "again"}, "Scrolling again, sir.", "फिर से स्क्रॉल कर रहा हूँ सर।"
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


# ---- Part 139: loose commands. The command word may sit anywhere, filler and ONE stray word are ignored. Only safe steps: home, back, scroll. Never click, type, send, pay or delete. ----
MOVE = set("aa aao आ आओ go jao ja jaa jana jaana chalo chal le जाओ जा जाना चलो चल ले".split())
VERBS = MOVE | set("open ओपन ओपेन kholo khol खोलो खोल dikhao दिखाओ show".split())
SCREENW = {"screen", "स्क्रीन", "page"}
# Part 186: loose words. "minimize" has many spellings, the mic writes them in Hindi letters too, so only the start of the word is compared. Seedha / aa / aao are filler like "seedha home screen par aa jao".
MINI_PRE = ("minim", "mimim", "minem", "मिनिम", "मिनीम", "मिनम", "मीनीम")
MORE186 = {"seedha", "seedhe", "direct", "सीधा", "सीधे", "aa", "aao", "आ", "आओ", "ab", "अब", "wapas", "वापस", "phir", "फिर", "to", "तो", "bas", "बस", "kar", "do", "दो"}
FRONTW = {"front", "frnt", "selfie", "फ्रंट", "फ्रण्ट", "सेल्फी", "सेल्फ़ी"}
CAMW = {"camera", "cam", "kaimara", "कैमरा", "कैमेरा", "कैमरे", "कैमरा"}


def loose_cmd(msg):
    """(action or None, English text, Hindi text) for home, back and scroll said in a loose way, else None."""
    m = msg.strip()
    if "?" in m or len(m) > 80 or risk_of(msg) or LABEL_RISK.search(m):
        return None
    w = _words(m)
    s = set(w)
    if not w or len(w) > 9 or s & QW or s & (CLICK_EN | CLICK_HI | BTN | CALLW | {"app", "ऐप", "एप", "type", "लिखो"}):
        return None
    mini = [x for x in w if x.startswith(MINI_PRE)]  # Part 186: "YouTube minimize karo" = the app goes away and the home screen shows (same as the home step)
    if mini and not (s & (BACKW | SCRW | DOWN | UP)):
        rest = [x for x in w if x not in mini and x not in LOOSEF and x not in VERBS and x not in HOMEW and x not in SCREENW and x not in PREPS and x not in MORE186]
        if len(rest) <= 2:
            return {"type": "home"}, "Minimizing, going to the home screen, sir.", "ठीक है सर, ऐप को छोटा करके होम स्क्रीन पर जा रहा हूँ।"
    known = HOMEW | BACKW | SCRW | DOWN | UP | SCREENW | LOOSEF | VERBS | MORE186  # Part 186: MORE186 = extra filler
    stray = [x for x in w if x not in known]
    if len(stray) > 1:
        return None
    home, back = bool(s & HOMEW), bool(s & BACKW)
    if home != back and s & VERBS and not (s & (SCRW | DOWN | UP)):
        if home:
            return {"type": "home"}, "Going to the home screen, sir.", "ठीक है सर, होम स्क्रीन पर जा रहा हूँ।"
        if s & MOVE:
            return {"type": "back"}, "Going back, sir.", "ठीक है सर, पीछे जा रहा हूँ।"
    if not (home or back) and s & SCRW and bool(s & DOWN) != bool(s & UP):
        d = "down" if s & DOWN else "up"
        return {"type": "scroll", "dir": d}, f"Scrolling {d}, sir.", ("नीचे" if d == "down" else "ऊपर") + " स्क्रॉल कर रहा हूँ सर।"
    return None


# ---- Part 154: reading scroll. "padhte hue scroll karo", "scroll karte raho": ONE screenful, a pause to read, the next one. "scroll ruko" stops it. Only scrolling, never a tap. ----
READW = set("padhte padhta padhke padh padhna पढ़ते पढ़ता पढ़कर पढ़ना पढ़ read reading auto khud खुद lagatar लगातार continuous continuously keep karte करते raho rahe रहो रहे rehna".split())
STOPS = set("ruko roko ruk रुको रोको रुक band बंद bas बस stop".split())
HUE = set("hue huye hue हुए ke saath sath with while".split())


def read_cmd(msg):
    """(action, English text, Hindi text) for the reading scroll or its stop, else None. The word `scroll` must be in the sentence."""
    m = msg.strip()
    if "?" in m or len(m) > 80 or risk_of(msg) or LABEL_RISK.search(m):
        return None
    w = _words(m)
    s = set(w)
    if not w or len(w) > 8 or not s & SCRW or s & QW or s & (CLICK_EN | CLICK_HI | BTN | CALLW | {"app", "ऐप", "एप", "type", "लिखो"}):
        return None
    if len(s - (SCRW | DOWN | UP | GO | FILL | AGAIN | LNOISE | PREPS | HUE | READW | STOPS)) > 1:
        return None
    if s & STOPS and not s & READW:
        return {"type": "scroll", "mode": "stop"}, "Stopping the scroll, sir.", "ठीक है सर, स्क्रॉल रोक रहा हूँ।"
    if s & READW and not (s & DOWN and s & UP):
        d = "up" if s & UP else "down"
        return ({"type": "scroll", "dir": d, "mode": "read"},
                f"Scrolling {d}, one screen at a time, sir. I wait a little after each one so you can read. Say: scroll ruko, to stop.",
                ("ऊपर" if d == "up" else "नीचे") + " की तरफ़ एक-एक स्क्रीन स्क्रॉल कर रहा हूँ सर, हर बार थोड़ा रुककर। रोकने के लिए बोलिए: स्क्रॉल रुको।")
    return None


# ---- Part 163: YouTube Shorts / Reels. "agla video", "pichla video", "next short", "next reel": ONE swipe that moves to the next or the previous video. Only a swipe, never a tap. ----
V_NEXT = {"agla", "agli", "next", "nxt", "अगला", "अगली", "नेक्स्ट"}
V_PREV = {"pichla", "pichhla", "pichli", "pichhli", "previous", "prev", "पिछला", "पिछली"}
V_NOUN = {"video", "videos", "vedio", "short", "shorts", "reel", "reels", "वीडियो", "शॉर्ट", "शॉर्ट्स", "रील", "रील्स"}
V_FILL = {"dikhao", "dikha", "lagao", "laga", "chalao", "chala", "dekho", "dekhna", "चलाओ", "दिखाओ", "लगाओ", "dekhao", "wala", "wali", "वाला", "वाली"}


def short_cmd(msg):
    """(action, English text, Hindi text) for the next or previous Short, else None. A video word (video, short, reel) must be in the sentence."""
    m = msg.strip()
    if "?" in m or len(m) > 60 or risk_of(msg) or LABEL_RISK.search(m):
        return None
    w = _words(m)
    s = set(w)
    if not w or len(w) > 6 or s & QW or not s & V_NOUN or bool(s & V_NEXT) == bool(s & V_PREV):
        return None
    if s - (V_NEXT | V_PREV | V_NOUN | V_FILL | FILL | GO | LNOISE | PREPS):
        return None  # something else in the sentence (a title, an app name): not a plain Shorts command
    if s & V_NEXT:
        return {"type": "scroll", "dir": "down", "mode": "video"}, "Next video, sir.", "अगला वीडियो सर।"
    return {"type": "scroll", "dir": "up", "mode": "video"}, "Previous video, sir.", "पिछला वीडियो सर।"


# Part 37: settings help. Only a FIXED list: open a settings page, flashlight, music volume. Wi-Fi, Bluetooth and location are never switched
# by Jarvis (Android does not allow it): the page is opened and Jarvis says so.
PAGES = {"wifi": ("wifi", "वाईफाई वायफाय वाईफ़ाई"), "bluetooth": ("bluetooth", "ब्लूटूथ ब्लूटुथ"), "location": ("location gps", "लोकेशन"),
         "sound": ("sound awaaz", "आवाज़ आवाज"), "display": ("brightness display", "ब्राइटनेस डिस्प्ले चमक"), "battery": ("battery", "बैटरी"),
         "network": ("network airplane flight", "नेटवर्क"), "notifications": ("notification notifications", "नोटिफिकेशन"),
         "permissions": ("permission permissions", "परमिशन"), "accessibility": ("accessibility", "एक्सेसिबिलिटी")}
PAGEOF = {w: k for k, (en, hi) in PAGES.items() for w in (en + " " + hi).split()}
SETW = {"settings", "setting", "सेटिंग", "सेटिंग्स", "page"}
ONW, OFFW = {"on", "ऑन", "ओन", "chalu", "चालू", "चालु", "jalao", "jala", "जलाओ", "start", "shuru", "enable"}, {"off", "ऑफ", "ओफ", "band", "बंद", "bujhao", "बुझाओ", "disable"}
OPENW = {"open", "ओपन", "ओपेन", "टर्न", "स्विच", "kholo", "khol", "खोलो", "खोल", "show", "dikhao", "दिखाओ", "turn", "switch", "kar", "karo", "करो", "कर", "do", "दो", "me", "mein", "में"}
TORCHW = {"flashlight", "torch", "flash", "टॉर्च", "टार्च", "टोर्च", "टार्च", "फ्लैशलाइट", "फ्लैश", "light", "लाइट"}
VOLW = {"volume", "vol", "awaaz", "आवाज़", "आवाज", "sound"}
VUP = {"up", "badhao", "badha", "बढ़ाओ", "बढ़ा", "increase", "zyada", "jyada", "ज़्यादा", "tez", "तेज़", "तेज", "louder", "more", "full"}
VDOWN = {"down", "kam", "कम", "decrease", "lower", "dheere", "धीरे", "low", "less", "halka", "slow"}
NICE = {"wifi": "Wi-Fi", "bluetooth": "Bluetooth", "location": "Location", "sound": "Sound", "display": "Display and brightness", "battery": "Battery",
        "network": "Network", "notifications": "Notifications", "permissions": "App permissions", "accessibility": "Accessibility"}


def device_cmd(msg):
    """(action or None, English text, Hindi text) for settings pages, flashlight and volume. None = not such a command."""
    m = re.sub(r"wi[\s\-]?fi", "wifi", msg.strip(), flags=re.I)
    if "?" in m or len(m) > 70:
        return None
    w = _words(m)
    s = set(w)
    if not w or len(w) > 8 or s & QW:
        return None
    OPENON = {"open", "ओपन", "ओपेन", "kholo", "khol", "खोलो", "खोल"}  # Part 59: "open torch" / "ओपन टॉर्च" means switch it on
    NOISE = LNOISE  # Part 130: filler the mic adds (Part 139: shared list)
    extra = [x for x in w if x not in TORCHW | ONW | OFFW | GO | FILL | OPENW | NOISE]  # a misheard "Jarvis" or one stray word must not lose the command
    strong = TORCHW - {"light", "लाइट", "flash", "फ्लैश"}
    dirs = [x for x in w if x in ONW or x in OPENON or x in OFFW]
    if dirs and ((s & (TORCHW - {"light", "लाइट"}) and not extra) or (s & strong and len(extra) == 1)):
        on = dirs[-1] not in OFFW  # "abhi bhi chalu hai switch off kar": the LAST direction word wins
        return {"type": "torch", "on": on}, ("Switching the flashlight on, sir." if on else "Switching the flashlight off, sir."), ("टॉर्च चालू कर रहा हूँ सर।" if on else "टॉर्च बंद कर रहा हूँ सर।")
    if s & VOLW and s <= VOLW | VUP | VDOWN | GO | FILL | OPENW | LNOISE | PREPS and bool(s & VUP) != bool(s & VDOWN):
        d = "up" if s & VUP else "down"
        return {"type": "volume", "dir": d}, f"Turning the volume {d}, sir.", ("आवाज़ बढ़ा रहा हूँ सर।" if d == "up" else "आवाज़ कम कर रहा हूँ सर।")
    pages = {PAGEOF[x] for x in s if x in PAGEOF}
    more = (VUP | VDOWN) if pages == {"display"} else set()  # "brightness kam karo": Jarvis cannot change it, so it opens the Display page
    if len(pages) == 1 and s <= set(PAGEOF) | SETW | ONW | OFFW | OPENW | GO | FILL | more and (s & (SETW | OPENW | ONW | OFFW | more)):
        p = pages.pop()
        n = NICE[p]
        if s & (ONW | OFFW | more) and p in ("wifi", "bluetooth", "location", "network", "display"):
            return {"type": "settings", "page": p}, f"Sir, Android does not let any app switch {n} on or off by itself. I opened the {n} page, please tap the switch yourself.", f"सर, Android किसी ऐप को {n} खुद चालू या बंद नहीं करने देता। मैंने {n} का पेज खोल दिया है, स्विच आप दबा दीजिए।"
        return {"type": "settings", "page": p}, f"Opening the {n} settings, sir.", f"{n} की सेटिंग खोल रहा हूँ सर।"
    return None


# ---- Part 64: "Ammi ko call karo". Only the person's own words make a call. The app finds the contact in the phone's own contacts. ----
CALLW = {"call", "कॉल", "काल", "कौल", "कोल", "dial", "डायल"}
LAGW = {"lagao", "laga", "lagana", "lagaiye", "लगाओ", "लगा", "लगाना", "लगाइए", "milao", "mila", "milana", "मिलाओ", "मिला", "मिलाना"}
PHW = {"phone", "फोन", "फ़ोन", "mobile", "मोबाइल"}
CALLFILL = {"to", "on", "se", "से", "pe", "पे", "par", "पर", "for", "via", "ne", "ने", "तो", "एक", "a", "पण्णु", "पन्नु", "पण्णुं", "माडि", "माडु", "चेयि", "चेयु", "चेय", "चेयंडि", "cheyi", "cheyyi", "cheyandi", "pannu", "panni", "madi", "maadi", "maadu"}  # last 7: "do" in Tamil, Kannada, Telugu
CALLNO = set("missed miss log history recent last today yesterday aaj kal kitne kitni number nambar नंबर नम्बर मिस्ड लॉग हिस्ट्री called calls kab कब time टाइम".split())
ASK_WHO = (None, 'Whom should I call, sir? Say the name, like "call Ammi".', 'किसे कॉल करूँ सर? नाम बोलिए, जैसे "अम्मी को कॉल करो"।')


def call_cmd(msg):
    """(action or None, English text, Hindi text) for a call command, else None. (None, ...) = a call word but no name, so Jarvis asks.
    A typed number only opens the dialer (raw): the green call button is the person's own tap."""
    m = msg.strip()
    m = re.sub(r"\s+(?:at\s+\w+\s+)?(?:last|ending|end|aakhri)\s*(?:mein|me|in|with|digits?)?\s*\d{2,6}\s*[.!]?$", "", m, flags=re.I)  # Part 125: dictation noise "call ammi at anyhow last mein 5895": the name is what counts; the app asks which contact if two fit
    if "?" in m or len(m) > 80:
        return None
    w = _words(m)
    if not w or len(w) > 7:
        return None
    s = set(w)
    if s & QW or s & CALLNO:
        return None
    drop = FILL | CALLFILL | LNOISE  # Part 139: "मैं अम्मी को कॉल कर" is Ammi, not "main ammi"
    while w and w[0] in drop:
        w = w[1:]
    while w and w[-1] in drop:
        w = w[:-1]
    if not w:
        return None
    # the call word must be at an edge ("Ammi ko call", "call Ammi", "Ammi ko phone lagao"), so a normal sentence that only contains "call" stays chat
    edge = (w[0] in CALLW or w[-1] in CALLW) or (len(w) >= 2 and w[-1] in LAGW and w[-2] in PHW) or (len(w) >= 2 and w[0] in PHW and w[1] in LAGW)
    if not edge:
        return None
    rest = [x for x in w if not (x in CALLW or x in LAGW or x in PHW)]
    while rest and rest[0] in drop:
        rest = rest[1:]
    while rest and rest[-1] in drop:
        rest = rest[:-1]
    if not rest:
        return ASK_WHO
    nm = re.search(r"\+?\d[\d \-]{2,}\d", m)
    if nm and all(x.isdigit() for x in rest):
        num = re.sub(r"[ \-]", "", nm.group())
        return {"type": "call", "number": num, "raw": True}, f"Opening the dialer with {num}, sir. Please press the green call button yourself.", f"डायलर में {num} खोल रहा हूँ सर। हरा कॉल बटन आप खुद दबाइए।"
    if "at" in rest[1:]:
        rest = rest[:rest.index("at", 1)]  # Part 139: "call ammi at anyhow": the name is what comes before "at"
    if len(rest) > 3 or "of" in rest or any(x.isdigit() for x in rest):
        return None
    name = " ".join(rest)
    if lang.is_latin(name):
        name = name.title()  # the words were lower-cased for matching; show a proper name
    act = {"type": "call", "name": name} if lang.is_latin(name) else {"type": "call", "name": lang.romanize(name) or name, "said": name}
    return act, f"Calling {name}, sir.", f"ठीक है सर, {name} को कॉल कर रहा हूँ।"


# ---- Part 66: alarm and timer by voice. Part 60: search inside an app. Only the person's own words; the app (Java) sets the alarm or opens the search page. ----
NUMW = {"ek": 1, "एक": 1, "do": 2, "दो": 2, "teen": 3, "तीन": 3, "char": 4, "chaar": 4, "चार": 4, "panch": 5, "paanch": 5, "पांच": 5, "पाँच": 5, "chhe": 6, "che": 6, "chah": 6, "छह": 6, "छः": 6, "saat": 7, "सात": 7, "aath": 8, "आठ": 8, "nau": 9, "नौ": 9, "das": 10, "दस": 10,
        "gyarah": 11, "ग्यारह": 11, "barah": 12, "बारह": 12, "pandrah": 15, "पंद्रह": 15, "bees": 20, "बीस": 20, "tees": 30, "तीस": 30, "aadha": 0.5, "adha": 0.5, "आधा": 0.5, "dedh": 1.5, "derh": 1.5, "डेढ़": 1.5, "डेढ": 1.5}
BAJE = {"baje", "bje", "बजे", "o'clock", "oclock"}
UNIT = {"sec": 1, "secs": 1, "second": 1, "seconds": 1, "सेकंड": 1, "सेकेंड": 1, "min": 60, "mins": 60, "minute": 60, "minutes": 60, "मिनट": 60, "मिनिट": 60,
        "hour": 3600, "hours": 3600, "hr": 3600, "hrs": 3600, "ghanta": 3600, "ghante": 3600, "ghanta.": 3600, "घंटा": 3600, "घंटे": 3600, "घण्टा": 3600, "घण्टे": 3600}
ALW = {"alarm", "अलार्म", "alaram", "alarams", "alarms"}
TMW = {"timer", "टाइमर", "taimar"}
AFILL = set("laga lagao lagana laga do de dena dijiye karo kar kr kardo set a an the for at on to ka ki ke ko ke liye me mein में par पर please plz pls jarvis जार्विस sir सर bhai भाई ji जी mere meri mera mujhe मुझे ek एक chahiye चाहिए hai है aur phir fir ab".split()) | FILL
AMW = {"subah", "सुबह", "savere", "morning", "am", "a.m", "a.m."}
PMW = {"shaam", "शाम", "sham", "evening", "pm", "p.m", "p.m.", "raat", "रात", "night"}
NOONW = {"dopahar", "दोपहर", "afternoon", "dophar"}
SHOWW = {"band", "बंद", "cancel", "delete", "hata", "hatao", "हटा", "हटाओ", "off", "dikhao", "दिखाओ", "show", "list", "dismiss", "rok", "roko", "ruk", "kholo", "खोलो", "open", "ओपन", "check"}
SAADE = {"saade": 0.5, "साढ़े": 0.5, "साढे": 0.5, "sava": 0.25, "सवा": 0.25, "paune": -0.25, "पौने": -0.25, "paun": -0.25}
MAXT = 86400


def _num(tok):
    if re.fullmatch(r"\d+(\.\d+)?", tok):
        return float(tok)
    return NUMW.get(tok)


def _clock(w, raw=""):
    """(hour, minute, ambiguous) from the words, or None. 24-hour times and am/pm/subah/shaam are exact; a bare 6 is ambiguous and Java picks the next one on the phone's own clock."""
    s = set(w)
    h = mi = None
    txt = " ".join(w)
    m = re.search(r"(?<![\d:.])(\d{1,2})[:.](\d{2})(?![\d:])", raw)
    if m and int(m.group(2)) < 60:
        h, mi = int(m.group(1)), int(m.group(2))
    else:
        m = re.search(r"\b(\d{1,2}) (\d{2})\b(?! ?(?:min|sec|hour|hr|मिनट|सेकंड|घंटे))", txt)
        if m and int(m.group(2)) < 60 and (set(w[w.index(m.group(2)) + 1:w.index(m.group(2)) + 2]) & (BAJE | AMW | PMW | NOONW) or s & (AMW | PMW | BAJE)):
            h, mi = int(m.group(1)), int(m.group(2))
    if h is None:
        for i, t in enumerate(w):
            n = _num(t)
            nxt = w[i + 1] if i + 1 < len(w) else ""
            prv = w[i - 1] if i else ""
            if n is None or n != int(n) or not 0 <= n <= 24:
                continue
            if nxt in BAJE or nxt in AMW | PMW or (t.isdigit() and not (nxt in UNIT)):
                if prv in SAADE:
                    h, mi = int(n), 30 if SAADE[prv] == 0.5 else 15
                    if SAADE[prv] < 0:
                        h, mi = int(n) - 1, 45
                else:
                    h, mi = int(n), 0
                break
    if h is None or h > 24 or mi > 59:
        return None
    if h == 24:
        h = 0
    if h > 12 or h == 0:
        return h, mi, False  # a 24-hour time such as 18:30 or 0:15
    if s & NOONW:
        return (12 if h == 12 else h + 12 if h <= 6 else h), mi, False
    if s & PMW - {"raat", "रात", "night"}:
        return (h if h == 12 else h + 12), mi, False
    if s & {"raat", "रात", "night"}:
        return (0 if h == 12 else h + 12 if h >= 5 else h), mi, False  # raat 1 baje is 1 AM, raat 10 baje is 10 PM
    if s & AMW:
        return (0 if h == 12 else h), mi, False
    return h, mi, True


def _span(w):
    """Seconds from words like \"5 minute\", \"1 hour 30 minute\", \"aadha ghanta\", else None."""
    tot, hit = 0.0, False
    for i, t in enumerate(w[:-1]):
        n = _num(t)
        if n is not None and w[i + 1] in UNIT:
            tot += n * UNIT[w[i + 1]]
            hit = True
    return int(tot) if hit else None


def alarm_cmd(msg):
    """(action, English text, Hindi text) for \"subah 6 baje alarm laga\" or \"5 minute ka timer\", else None. Never a question, never part of a task."""
    m = msg.strip()
    if "?" in m or len(m) > 80:
        return None
    w = _words(m)
    w = _fuzzy(w, ALW | TMW)  # Part 73: "alaam"/"taimr" etc. still trigger
    s = set(w)
    if not w or len(w) > 10 or s & QW:
        return None
    if s & TMW:
        if s & SHOWW and not _span(w):
            return {"type": "alarm", "show": True}, "Android does not let me stop a timer. I opened your alarms and timers, sir, please stop it there.", "सर, Android मुझे टाइमर बंद नहीं करने देता। मैंने अलार्म खोल दिया है, वहाँ से बंद कर दीजिए।"
        sec = _span(w)
        if not sec:
            return None, "How long should the timer be, sir? For example \"5 minute ka timer\".", "कितनी देर का टाइमर सर? जैसे \"5 मिनट का टाइमर\"।"
        if sec > MAXT:
            return None, "Sir, a timer can be 24 hours at most.", "सर, टाइमर ज़्यादा से ज़्यादा 24 घंटे का हो सकता है।"
        mm, ss = divmod(sec, 60)
        hh, mm = divmod(mm, 60)
        nice = " ".join(x for x in (f"{hh} hour" + ("s" if hh > 1 else "") if hh else "", f"{mm} min" if mm else "", f"{ss} sec" if ss else "") if x)
        nice_hi = " ".join(x for x in (f"{hh} घंटे" if hh else "", f"{mm} मिनट" if mm else "", f"{ss} सेकंड" if ss else "") if x)
        return {"type": "timer", "seconds": sec}, f"Starting a {nice} timer, sir.", f"{nice_hi} का टाइमर चालू कर रहा हूँ सर।"
    if not s & ALW:
        return None
    if s & SHOWW:
        return {"type": "alarm", "show": True}, "Android does not let me delete or switch off alarms. I opened your alarms, sir, please do it there.", "सर, Android मुझे अलार्म हटाने या बंद करने नहीं देता। मैंने आपके अलार्म खोल दिए हैं, वहाँ से कर लीजिए।"
    t = _clock(w, m)
    if not t:
        return None, 'What time should the alarm be, sir? For example "subah 6 baje alarm laga".', 'कितने बजे का अलार्म सर? जैसे "सुबह 6 बजे अलार्म लगा"।'
    h, mi, amb = t
    act = {"type": "alarm", "hour": h, "minute": mi}
    if amb:
        act["ambiguous"] = True
    shown = f"{h if amb else (h % 12 or 12)}:{mi:02d}" + ("" if amb else " AM" if h < 12 else " PM")
    return act, f"Setting an alarm for {shown}, sir.", f"{shown} का अलार्म लगा रहा हूँ सर।"


# search inside an app: only these apps, and Java builds the web address itself from its own fixed list (the page never sends a link)
SEARCHAPPS = {"YouTube": "youtube", "Google": "google", "Chrome": "google", "Maps": "maps", "Play Store": "play", "Amazon": "amazon", "Flipkart": "flipkart", "Spotify": "spotify"}
SEARCHW = {"search", "serch", "सर्च", "dhundo", "dhoondo", "dhundna", "dhoondna", "ढूंढो", "ढूँढो", "ढूंढ", "खोजो", "khojo", "play", "प्ले", "chalao", "chala", "चलाओ", "चला", "laga", "lagao", "लगाओ", "sunao", "सुनाओ", "dikhao", "दिखाओ", "dekho", "देखो", "find", "look", "lookup", "navigate"}
SFILL = FILL | {"par", "pe", "पर", "पे", "me", "mein", "में", "ke", "liye", "लिए", "के", "का", "ki", "की", "ka", "se", "से", "ya", "karke", "kar", "karo", "kro", "करके", "app", "ऐप"}
SEDGE = {"on", "in", "for", "to", "a", "the", "some", "i", "want", "of", "about", "mujhe"}


def search_cmd(msg):
    """(action, English text, Hindi text) for \"YouTube par Arijit ke gaane search karo\" or \"play Kesariya on YouTube\", else None.
    There must be an app name from the fixed list AND a search or play word AND something to search for, so \"YouTube kholo\" stays a plain open."""
    m = msg.strip()
    if "?" in m or len(m) > 120:
        return None
    w = _words(m)
    if not w or len(w) > 14 or QW & set(w):
        return None
    app, used = None, ()
    for i, t in enumerate(w):
        two = canon(t + w[i + 1]) if i + 1 < len(w) else None  # "google maps"
        if two in SEARCHAPPS and two != t + w[i + 1]:
            app, used = two, (i, i + 1)
        elif t in ("google", "गूगल"):
            app, used = "Google", (i,)
        elif canon(t) in SEARCHAPPS:
            app, used = canon(t), (i,)
        if app:
            break
    if not app or not set(w) & SEARCHW:
        return None
    rest = [x for j, x in enumerate(w) if j not in used]
    rest = [x for x in rest if x not in SEARCHW and x not in SFILL and x not in EN and x not in HI]
    while rest and rest[0] in SEDGE:  # little English words (on, in, for, the) are dropped only at the two ends, so \"weather in Mumbai\" stays whole
        rest = rest[1:]
    while rest and rest[-1] in SEDGE:
        rest = rest[:-1]
    q = " ".join(rest).strip()
    if not q or len(q) > 100:
        return None
    return {"type": "search", "app": SEARCHAPPS[app], "query": q}, f"Searching {app} for \"{q}\", sir.", f"{app} पर \"{q}\" ढूँढ रहा हूँ सर।"

# ---- Part 68: music control by voice. Part 69: WhatsApp message by contact name. Only the person's own words; nothing is sent by Jarvis. ----
MEDW = {"gaana", "gana", "gaane", "gane", "song", "songs", "music", "musik", "track", "गाना", "गाने", "गान", "म्यूजिक", "म्यूज़िक", "संगीत"}
M_PAUSE = {"pause", "pose", "पॉज", "ruko", "roko", "rok", "ruk", "band", "bandh", "stop", "बंद", "रोको", "रुको", "रोक"}
M_PLAY = {"play", "resume", "continue", "chalu", "chalao", "chala", "shuru", "start", "चालू", "चलाओ", "प्ले", "शुरू"}
M_NEXT = {"next", "agla", "agli", "अगला", "अगली", "नेक्स्ट", "skip", "badlo", "badal", "बदलो", "बदल"}
M_PREV = {"previous", "prev", "pichla", "pichhla", "पिछला", "पिछली", "पिछले"}
MFILL = FILL | GO | {"ka", "ki", "ke", "ko", "ye", "yeh", "isko", "wala", "wali", "वाला", "वाली", "abhi", "अभी", "thoda", "थोड़ा", "bas", "बस", "ho", "hota"}


def media_cmd(msg):
    """(action, English text, Hindi text) for "gaana pause karo", "next song", "agla gaana", "music band karo", else None.
    Needs a music word (gaana, song, music) except for a lone "pause" or "resume". Volume words belong to Part 37, so they are left alone."""
    m = msg.strip()
    if "?" in m or len(m) > 60:
        return None
    w = _words(m)
    w = _fuzzy(w, MEDW | M_PAUSE | M_PLAY | M_NEXT | M_PREV)  # Part 73: "pazz"/"gaanaa" etc. still trigger
    s = set(w)
    if not w or len(w) > 6 or s & QW or s & VOLW:
        return None
    noun = bool(s & MEDW)
    cats = [c for c, ws in (("pause", M_PAUSE), ("play", M_PLAY), ("next", M_NEXT), ("prev", M_PREV)) if s & ws]
    if len(cats) != 1:
        return None
    c = cats[0]
    if any(x not in MEDW | MFILL | M_PAUSE | M_PLAY | M_NEXT | M_PREV for x in w):
        return None  # something else in the sentence (a song title, an app): not a plain music command
    if not noun and not (c == "pause" and s & {"pause", "pose", "पॉज"}) and not (c == "play" and s & {"resume", "continue"}):
        return None
    en = {"pause": "Pausing the music", "play": "Playing the music", "next": "Next song", "prev": "Previous song"}[c]
    hi = {"pause": "गाना रोक रहा हूँ", "play": "गाना चला रहा हूँ", "next": "अगला गाना लगा रहा हूँ", "prev": "पिछला गाना लगा रहा हूँ"}[c]
    return {"type": "media", "cmd": c}, f"{en}, sir.", f"{hi} सर।"


WAKO = {"ko", "को"}
WAFILL = FILL | {"pe", "par", "पर", "पे", "on", "me", "mein", "में", "se", "से", "via", "using", "through", "ek", "a"}
WAVERB = set("bhejo bhej bhejna bhejiye bhej do de dena karo kar kr likho likh bolo bol batao bata message msg sms text send ki ke ka that say tell please plz jarvis sir bhai ji".split()) | {"भेजो", "भेज", "भेजना", "भेजिए", "करो", "कर", "लिखो", "बोलो", "बोल", "बता", "बताओ", "मैसेज", "की", "के", "दो", "दे", "सर", "जी", "भाई"}
_TOK = r"[\w\u0900-\u097F']+"


def wa_cmd(msg):
    """(action, English text, Hindi text) for "Ammi ko WhatsApp pe hello bhejo", "Ammi ko whatsapp karo", "send hello to Ammi on WhatsApp".
    It only OPENS the chat with the words filled in. The send button is the person's own tap. Java finds the number in the phone's contacts."""
    m = msg.strip()
    if "?" in m or len(m) > 200:
        return None
    toks = re.findall(_TOK, m)
    low = [x.lower() for x in toks]
    wi = [i for i, x in enumerate(low) if x == "whatsapp" or canon(x) == "WhatsApp"]
    if not wi or len(toks) > 30:
        return None
    name = text = None
    en = re.match(r"^(?:please\s+)?(?:send|text|message|msg)\s+(.+?)\s+to\s+([\w\u0900-\u097F]+(?: [\w\u0900-\u097F]+)?)\s+(?:on|via|in|using|through)\s+\S+\s*$", m, re.I)
    if en:
        text, name = en.group(1).strip(), en.group(2).strip()
    else:
        ko = [i for i, x in enumerate(low) if x in WAKO]
        if not ko:
            return None
        k = ko[0]
        nm = [toks[i] for i in range(k) if low[i] not in WAFILL and i not in wi and low[i] not in WAVERB]
        if not nm or len(nm) > 3 or any(x.isdigit() for x in nm):
            return None
        name = " ".join(nm)
        rest = [toks[i] for i in range(k + 1, len(toks)) if i not in wi]
        rl = [x.lower() for x in rest]
        while rest and rl[0] in WAFILL | WAVERB:
            rest, rl = rest[1:], rl[1:]
        while rest and rl[-1] in WAFILL | WAVERB:
            rest, rl = rest[:-1], rl[:-1]
        text = " ".join(rest).strip()
    if not name or len(text or "") > 300:
        return None
    if lang.is_latin(name):
        name = name.title()
    act = {"type": "call", "via": "whatsapp", "name": name, "text": text or ""}
    if not lang.is_latin(name):
        act = {"type": "call", "via": "whatsapp", "name": lang.romanize(name) or name, "said": name, "text": text or ""}
    shown = f' with "{text}"' if text else ""
    shown_hi = f' में "{text}" लिखकर' if text else ""
    return act, f"Opening the WhatsApp chat with {name}{shown}, sir. Please press send yourself.", f"{name} की WhatsApp चैट{shown_hi} खोल रहा हूँ सर। भेजने का बटन आप खुद दबाइए।"


def handle(msg, hindi, control, in_app, ask):
    """None = not a command. Else (reply text, action dict or None). The page shows what REALLY happened after the app answers."""
    say = lambda hi, en: hi if hindi else en
    code = lang.detect(msg)  # Part 63: Tamil, Gujarati, Telugu... are moved onto Devanagari so the Hindi word lists work
    msg = lang.norm(msg)
    if blocked(msg):
        return say("सर, मैं पासवर्ड, OTP, PIN या कार्ड नंबर कभी टाइप नहीं करता। कृपया आप खुद टाइप कीजिए।", "Sir, I never type passwords, OTPs, PINs or card numbers. Please type it yourself."), None
    lk = look_cmd(msg)  # Part 129: "look and tap the chart". Needs the app and the switch, and later your own Yes tap on the picture
    if lk:
        if secret_text(lk) or blocked(lk):
            return say("सर, मैं पासवर्ड, OTP, PIN या कार्ड वाली चीज़ें नहीं दबाता। आप खुद कीजिए।", "Sir, I do not tap password, OTP, PIN or card things. Please do that yourself."), None
        if not in_app:
            return say("सर, फ़ोन कंट्रोल सिर्फ़ Jarvis ऐप में चलता है।", "Sir, phone control works only in the Jarvis Android app."), None
        if not control:
            return say("फ़ोन कंट्रोल बंद है सर। Settings में \"Phone control\" चालू कीजिए।", "Phone control is OFF, sir. Turn it on in Settings, under Phone control."), None
        return say(f"ठीक है सर, स्क्रीन की एक फोटो लेकर \"{lk}\" ढूँढता हूँ। आपकी हाँ के बिना कुछ नहीं दबाऊँगा।", f"Okay sir, I will take one picture of the screen and look for \"{lk}\". I will tap nothing until you tap Yes."), {"type": "look", "target": lk}
    for fn in (wa_cmd, media_cmd, alarm_cmd, search_cmd):  # Part 66 (alarm, timer) and Part 60 (search inside an app). Only the person's own words, never the AI, never a task step.
        got = fn(msg)
        if got:
            if not in_app:
                return say("सर, फ़ोन कंट्रोल सिर्फ़ Jarvis ऐप में चलता है।", "Sir, phone control works only in the Jarvis Android app."), None
            if not control:
                return say("फ़ोन कंट्रोल बंद है सर। Settings में \"Phone control\" चालू कीजिए।", "Phone control is OFF, sir. Turn it on in Settings, under Phone control."), None
            return say(got[2], got[1]), got[0]
    sc = short_cmd(msg) or read_cmd(msg) or screen_cmd(msg) or device_cmd(msg) or loose_cmd(msg)  # Part 163 puts short_cmd first. Part 154 read_cmd. Part 139 adds loose_cmd last. Part 34 (screen steps) and Part 37 (settings pages, flashlight, volume)
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
    cc = call_cmd(msg)  # Part 64: "Ammi ko call karo". Not in a task and never from the AI: only this grammar, only the person's own words
    if cc:
        if not in_app:
            return say("सर, फ़ोन कंट्रोल सिर्फ़ Jarvis ऐप में चलता है।", "Sir, phone control works only in the Jarvis Android app."), None
        if not control:
            return say("फ़ोन कंट्रोल बंद है सर। Settings में \"Phone control\" चालू कीजिए।", "Phone control is OFF, sir. Turn it on in Settings, under Phone control."), None
        if cc[0] and code in lang.NAMES:
            cc[0]["lang"] = code
        return say(cc[2], cc[1]), cc[0]
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
    ws = set(_words(msg))
    if ws & FRONTW and ws & CAMW:  # Part 186 + 202: "front camera", "selfie camera" opens the camera already on the front side (Java; a camera app that ignores it opens on the back)
        return say("ठीक है सर, front camera खोल रहा हूँ। अगर पीछे वाला खुले तो flip बटन दबा दीजिए।",
                   "Opening the front camera, sir. If the back one opens, tap the flip button."), {"type": "open_app", "name": "Camera", "front": True}
    label = canon(name)
    if APPS and _key(label) not in {_key(x) for x in APPS}:  # Part 201: not an installed name as it is, so look in the list of this phone
        hit = appnames.resolve(APPS, name)
        if hit:
            label = hit
    act = {"type": "open_app", "name": label}
    if not lang.is_latin(label):  # Part 62: not one of the known names, so search the phone's app list with a Latin spelling (Java also matches by consonants)
        act = {"type": "open_app", "name": lang.romanize(label) or label, "said": label}
    if code in lang.NAMES:
        act["lang"] = code
    return say(f"ठीक है सर, {label} खोल रहा हूँ।", f"Opening {label}, sir."), act



# ---- Part 145: Samjha probe. `samjha: <sentence>` shows what Jarvis understood from the phone-command grammar and does NOTHING (no action, no note, no AI, nothing saved).
# It assumes Phone control is ON and the app is open. Only the phone-command part is probed; notes, lists, reminders and the AI are not run.
PROBE = re.compile(r"^\s*(?:samjha|samjhaa|समझा|समझ)\s*[:\uff1a]\s*(.{1,200}?)\s*$", re.I | re.S)
KEYS = {"type": "type", "name": "name", "target": "target", "text": "text", "risk": "needs your Yes for", "dir": "direction", "said": "you said", "lang": "language", "to": "to", "query": "search", "minutes": "minutes", "level": "level"}


def _noai(*a, **k):
    raise RuntimeError("probe: the AI is never asked")


def probe(msg, hindi):
    """Plain-words report, or None if the message is not `samjha: ...`."""
    g = PROBE.match(msg or "")
    if not g:
        return None
    s, say = g.group(1), (lambda hi, en: hi if hindi else en)
    if blocked(lang.norm(s)) or secret_text(s):  # never repeat a password, OTP, PIN or card back into the chat
        return say("सर, जाँच (कुछ किया नहीं): इसमें पासवर्ड/OTP/PIN/कार्ड है, मैं इसे कभी टाइप नहीं करूँगा और यहाँ दोहराऊँगा भी नहीं।", "Sir, probe (nothing was done): it has a password, OTP, PIN or card. I never type that, and I will not repeat it here.")
    head = say(f"सर, जाँच (कुछ किया नहीं): \"{s}\"", f"Sir, probe (nothing was done): \"{s}\"")
    code = lang.detect(s)
    heard = lang.norm(s)
    lines = [head, say("भाषा", "Language") + ": " + (lang.NAMES.get(code) or {"hi": "Hindi", "en": "English"}.get(code) or "Hindi/English"), say("समझा हुआ पाठ", "Understood as") + ": " + heard]
    if blocked(heard):
        lines.append(say("नतीजा: पासवर्ड/OTP/PIN/कार्ड वाली बात, मैं इसे कभी टाइप नहीं करूँगा।", "Result: it has a password, OTP, PIN or card. I never type that."))
    else:
        try:
            got = handle(s, hindi, True, True, _noai)
        except RuntimeError:
            got = None
        if not got:
            lines.append(say("नतीजा: फ़ोन कमांड नहीं। यह नोट, लिस्ट, रिमाइंडर या सामान्य बातचीत में जाएगा।", "Result: not a phone command. It would go to notes, lists, reminders or normal chat."))
        else:
            reply, act = got
            if act:
                lines.append(say("नतीजा: फ़ोन कमांड", "Result: phone command") + " - " + ", ".join(f"{KEYS.get(k, k)}: {v}" for k, v in act.items() if isinstance(v, (str, int, float)) and str(v)))
                lines.append(say("यह आपकी हाँ मांगेगा।", "It will wait for your Yes.") if act.get("type") == "confirm" else say("यह तभी चलेगा जब आप सीधा बोलें।", "It runs only when you say it as a normal command."))
            lines.append(say("जवाब होता", "Reply would be") + ": " + reply)
    return "\n".join(lines) + "\n" + say("कुछ नहीं चलाया। (फ़ोन कंट्रोल चालू और ऐप खुला मानकर जाँचा।)", "Nothing was run. (Checked as if Phone control is ON and the app is open.)")


# ---- Part 102: Cool-down before a message. `thanda karo` first, then the WhatsApp command. The page shows your text with a 20 second countdown and a Continue button.
# Only when you ask for it, only for the next WhatsApp message (or 5 minutes), nothing is sent by Jarvis. RAM only.
import time as _time

COOL_ON = re.compile(r"^\s*(?:thanda\s+karo|thanda\s+ho\s+jao|cool\s*down(?:\s+on)?|ठंडा\s+करो)\s*[.!]?\s*$", re.I)
COOL_OFF = re.compile(r"^\s*(?:thanda\s+band|cool\s*down\s+off|ठंडा\s+बंद)\s*$", re.I)
COOL = {}  # device -> until (time.time())


def cool_cmd(dev, msg, hindi):
    if COOL_OFF.match(msg):
        COOL.pop(dev, None)
        return "ठीक है, कूल-डाउन बंद।" if hindi else "Okay, cool-down is off."
    if COOL_ON.match(msg):
        COOL[dev] = _time.time() + 300
        return ("ठीक है। अगला WhatsApp कमांड बोलिए, जैसे: Ammi ko whatsapp pe hello bhejo। मैं 20 सेकंड रुककर आपका टेक्स्ट दिखाऊँगा, फिर Continue दबाइए।" if hindi else
                "Okay. Now say the WhatsApp command, for example: Ammi ko whatsapp pe hello bhejo. I will show your text with a 20 second wait, then tap Continue. This lasts for the next message or 5 minutes.")
    return None


def cool_take(dev, action):
    """20 (seconds) once, if cool-down is on and the action opens a WhatsApp chat; the switch is used up. Else 0."""
    if isinstance(action, dict) and action.get("via") == "whatsapp" and COOL.get(dev, 0) > _time.time():
        COOL.pop(dev, None)
        return 20
    return 0
