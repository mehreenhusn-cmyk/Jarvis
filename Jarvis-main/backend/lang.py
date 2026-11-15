"""Jarvis languages (Part 63) and app-name spelling (Part 62).
Idea: every Indian script is laid out the same way in Unicode, so Tamil, Telugu, Gujarati and the others can be moved onto the Devanagari
letters. Then the Hindi word lists in actions.py work for them too. Nothing is sent anywhere: this is plain text work."""
import re

BLOCKS = {"bn": 0x980, "pa": 0xA00, "gu": 0xA80, "or": 0xB00, "ta": 0xB80, "te": 0xC00, "kn": 0xC80, "ml": 0xD00}  # first letter of each script
NAMES = {"bn": "Bengali", "pa": "Punjabi", "gu": "Gujarati", "or": "Odia", "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam",
         "mr": "Marathi", "ur": "Urdu"}
CHILLU = {"ൺ": "ണ്", "ൻ": "ന്", "ർ": "ര്", "ൽ": "ല്", "ൾ": "ള്", "ൿ": "ക്"}  # Malayalam letters that carry no vowel
FIX = str.maketrans({"ऩ": "न", "ऱ": "र", "ऴ": "ल", "ऎ": "ए", "ऒ": "ओ", "ॆ": "े", "ॊ": "ो"})  # short e and o (Tamil, Telugu, Kannada, Malayalam) are plain e and o  # Tamil and South Indian letters with no Hindi twin
URDU = [(r"اوپن|اوپین", "open"), (r"کھولو|کھول دو|کھولیں|کھولئے", "kholo"), (r"ٹارچ", "torch"), (r"آن", "on"), (r"آف", "off"), (r"اور", "aur")]


def script_of(text):
    """'hi' for Devanagari, 'ta', 'gu' ... for the other scripts, 'ur' for Urdu, '' for Latin or nothing."""
    n = {}
    for ch in text or "":
        o = ord(ch)
        if 0x900 <= o <= 0x97F:
            n["hi"] = n.get("hi", 0) + 1
        elif 0x600 <= o <= 0x6FF:
            n["ur"] = n.get("ur", 0) + 1
        else:
            for k, s in BLOCKS.items():
                if s <= o < s + 0x80:
                    n[k] = n.get(k, 0) + 1
    return max(n, key=n.get) if n else ""


def detect(text):
    """Language code of what was said. Marathi shares the Devanagari script with Hindi, so a few Marathi words decide it."""
    s = script_of(text)
    if s == "hi" and re.search(r"उघड|आहे|आणि|नको|करा\b|मला|तुम्ही", text):
        return "mr"
    return s


def norm(text):
    """The same message with every Indian script moved to Devanagari, and Urdu command words turned into Latin ones. Hindi and English stay as they are."""
    if not text:
        return text
    s = script_of(text)
    if s == "ur":
        for rx, to in URDU:
            text = re.sub(rx, " " + to + " ", text)
        return text
    if s not in BLOCKS:
        return text
    base = BLOCKS[s]
    for k, v in CHILLU.items():
        text = text.replace(k, v)
    if s == "ml":
        text = text.replace("ം", "മ്")  # Malayalam "m" at the end of a word
    out = "".join(chr(ord(ch) - base + 0x900) if base <= ord(ch) < base + 0x80 else ch for ch in text)
    out = out.translate(FIX)
    return re.sub(r"्(?=[\s,.;!?।]|$)", "", out)  # a last "halant" only means "no vowel"; "ओपन्" is "ओपन"


# ---- Part 62: a Hindi-script name as Latin letters, so the phone's own app list can be searched ----
_C = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमयरलळवशषसह", "k kh g gh n ch chh j jh n t th d dh n t th d dh n p f b bh m y r l l v sh sh s h".split()))
_V = dict(zip("अआइईउऊऋएऐओऔऑ", "a aa i i u u ri e ai o au o".split()))
_M = dict(zip("ािीुूृेैोौॉ", "a i i u u ri e ai o au o".split()))


def romanize(text):
    """Rough Latin spelling of a Devanagari word ("ज़ोमैटो" gives "zomaito"). Only a search key for the app list, never shown as a fact."""
    t = (text or "").replace("ज़", "z").replace("फ़", "f").replace("ड़", "r").replace("ढ़", "rh").replace("क़", "q").replace("ख़", "kh").replace("ग़", "g")
    out, i = [], 0
    while i < len(t):
        ch = t[i]
        if ch in _C:
            out.append(_C[ch])
            nx = t[i + 1] if i + 1 < len(t) else ""
            if nx == "्":
                i += 1
            elif nx in _M:
                out.append(_M[nx])
                i += 1
            elif nx and re.match(r"[\w]", nx) and nx not in "ंँः":
                out.append("a")
        elif ch in _V:
            out.append(_V[ch])
        elif ch in "ंँ":
            out.append("n")
        elif ch == "ः":
            out.append("h")
        elif ch.isascii():
            out.append(ch)
        i += 1
    return "".join(out)


def is_latin(s):
    return all(ord(c) < 0x250 for c in s)


# ---- reply text for the page (the page owns the words it shows; the server only says which language) ----
CHAT_NOTE = "\n\nThe user wrote in {n}. Reply in {n}, in its own script, in short simple spoken sentences. Address the user as sir (in {n})."


def chat_note(text):
    """Extra instruction for the AI when the user wrote in a language other than Hindi or English. Empty for Hindi, English and Marathi-less cases."""
    code = detect(text)
    return CHAT_NOTE.format(n=NAMES[code]) if code in NAMES else ""
