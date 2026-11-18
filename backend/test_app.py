"""Chalao: python backend/test_app.py   (mock provider, internet/API key nahi chahiye)"""
import json, os, re, subprocess, sys, tempfile, time, urllib.error, urllib.request

import stat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as A

import screen as SC, actions as AC, progress as PG
_r = lambda t: SC.redact(t)[0]
def _unit():
    ok = lambda n, c: print(("PASS " if c else "FAIL ") + n) or (c or sys.exit(1))
    ok("32: OTP chhupta hai", "483921" not in _r("Your OTP is 483921. Do not share."))
    ok("32: OTP agli line mein bhi chhupta hai", "123456" not in _r("Verification code\n123 456").replace(" ", ""))
    ok("32: card number chhupta hai", "4111" not in _r("Card 4111 1111 1111 1111 exp 12/29") and "12/29" in _r("Card 4111 1111 1111 1111 exp 12/29"))
    ok("32: Aadhaar aur PAN chhupte hain", "2345" not in _r("Aadhaar 2345 6789 0123") and "ABCDE1234F" not in _r("PAN ABCDE1234F"))
    ok("32: password value chhupti hai", "hunter2" not in _r("Password: hunter2"))
    ok("32: UPI PIN chhupta hai", "1234" not in _r("UPI PIN\n1234"))
    ok("32: normal paise aur phone number nahi chhupte", _r("Total Rs 4500 for 3 items") == "Total Rs 4500 for 3 items" and "9876543210" in _r("Call 9876543210 now"))
    ok("32: khali screen par imaandar sandesh", "no readable text" in SC.context({"app": "com.bank", "text": "  "}))
    ok("32: context mein secret nahi jata", "483921" not in SC.context({"app": "a.b", "text": "OTP 483921 Send"}))
    a = lambda m, ctl=True: AC.handle(m, False, ctl, True, lambda h, s, e: ("x", "y"))
    ok("33: message bhejo -> confirm", a("message bhejo")[1] == {"type": "confirm", "risk": "send"})
    ok("33: paise bhejo -> pay confirm", a("paise bhejo Faisal ko")[1] == {"type": "confirm", "risk": "pay"})
    ok("33: delete / buy / install / logout -> confirm", all((a(m) or (0, {}))[1].get("type") == "confirm" for m in ("delete this chat", "buy shoes", "install Telegram", "logout karo")))
    ok("33: switch OFF par confirm nahi, chat chalti hai", a("delete this chat", False) is None)
    import see as SE
    ok("129: look and tap -> look action", a("look and tap the chart")[1] == {"type": "look", "target": "the chart"} and a("dekh ke dabao subscribe")[1]["type"] == "look")
    ok("129: switch OFF, password target, question are not look", a("look and tap chart", False)[1] is None and a("look and tap password box")[1] is None and a("what does look and tap do?") is None)
    ok("129: AI answer parser: good, out of range, garbage", SE.parse_loc('{"found":true,"x":500,"y":250,"label":"Chart"}') == {"found": True, "x": 0.5, "y": 0.25, "label": "Chart"} and SE.parse_loc('{"found":true,"x":1500,"y":5}') == {"found": False} and SE.parse_loc("no") == {"found": False})
    import clock as CK
    ok("66: subah 6 baje alarm -> 6:00 AM", a("subah 6 baje alarm laga")[1] == {"type": "alarm", "hour": 6, "minute": 0})
    ok("66: bina AM/PM ke 6 baje -> Java agla wala chunta hai", a("alarm laga do 6:30 baje")[1] == {"type": "alarm", "hour": 6, "minute": 30, "ambiguous": True})
    ok("66: raat 1 baje = 1 AM, shaam 5 baje = 5 PM, 18:30 = 6:30 PM", (a("raat 1 baje alarm")[1]["hour"], a("shaam 5 baje alarm")[1]["hour"], a("alarm 18:30")[1]["hour"]) == (1, 17, 18))
    ok("66: 5 minute ka timer = 300 sec, 1 hour 30 minute = 5400", a("5 minute ka timer laga do")[1] == {"type": "timer", "seconds": 300} and a("1 hour 30 minute timer")[1]["seconds"] == 5400)
    ok("66: bina samay ke poochta hai, action nahi", a("alarm laga do")[1] is None and a("timer laga do")[1] is None)
    ok("66: sawal chat rehta hai", a("alarm kya hota hai?") is None)
    ok("66: switch OFF par kuch nahi chalta", "OFF" in a("subah 6 baje alarm laga", False)[0] and a("subah 6 baje alarm laga", False)[1] is None)
    ok("60: YouTube par search -> search action", a("YouTube par Arijit ke gaane search karo")[1] == {"type": "search", "app": "youtube", "query": "arijit gaane"})
    ok("60: play X on YouTube", a("play Kesariya on YouTube")[1] == {"type": "search", "app": "youtube", "query": "kesariya"})
    ok("60: Hindi script", a("यूट्यूब पर अरिजीत सिंह सर्च करो")[1]["query"] == "अरिजीत सिंह")
    ok("60: sirf 'YouTube kholo' ab bhi app kholta hai", a("YouTube kholo")[1] == {"type": "open_app", "name": "YouTube"})
    ok("60: Google Maps alag, weather in Mumbai poora rehta hai", a("Google Maps par Mumbai airport search karo")[1]["app"] == "maps" and a("Chrome par weather in Mumbai search karo")[1]["query"] == "weather in mumbai")
    ok("68: gaana pause / next song / pichla gaana", (a("gaana pause karo")[1], a("next song")[1], a("pichla gaana")[1]) == ({"type": "media", "cmd": "pause"}, {"type": "media", "cmd": "next"}, {"type": "media", "cmd": "prev"}))
    ok("68: volume, torch, 'band karo' akela media nahi banta", a("volume up")[1]["type"] == "volume" and a("torch band karo")[1]["type"] == "torch" and a("band karo") is None and a("gaane ki awaaz badhao") is None)
    ok("68: 'play X on YouTube' search rehta hai, bina naam ke 'play' media nahi", a("play Kesariya on YouTube")[1]["type"] == "search" and a("Kesariya play karo") is None)
    ok("69: Ammi ko WhatsApp pe hello -> chat khulti hai, text bhara", a("Ammi ko WhatsApp pe hello bhejo")[1] == {"type": "call", "via": "whatsapp", "name": "Ammi", "text": "hello"})
    ok("69: send hello to Ammi on WhatsApp", a("send hello to Ammi on WhatsApp")[1]["text"] == "hello" and a("Ammi ko whatsapp karo")[1]["text"] == "")
    ok("69: bina naam 'message bhejo' ab bhi Yes maangta hai, 'whatsapp kholo' sirf app kholta hai", a("message bhejo")[1]["type"] == "confirm" and a("whatsapp kholo")[1]["type"] == "open_app")
    ok("73: thoda misheard alarm/timer word bhi chalta hai (alram, tiemr)", a("subah 6 baje alram laga")[1] == {"type": "alarm", "hour": 6, "minute": 0} and a("5 minute ka tiemr laga do")[1] == {"type": "timer", "seconds": 300})
    ok("73: misheard music word bhi chalta hai (agli gaana -> next)", a("agli gaana")[1] == {"type": "media", "cmd": "next"} and a("gaana playy karo")[1] == {"type": "media", "cmd": "play"})
    ok("73: exact galat shabd (random typo) action nahi banata, chat hi rehta hai", a("xyz123 kuch bhi") is None)
    import voiceengine as _ve, notes as _nt, sqlite3 as _sq, tempfile as _tf, os as _os
    _ve.FILE = _os.path.join(_tf.mkdtemp(), "voice.json")  # a throw-away settings file, the real voice.json is never touched
    _p = lambda t, i="": _ve.pick(t, i)["profile"]
    ok("71: normal baat-cheet = TONY", _p("kaise ho sir") == "tony")
    ok("71: jaankari, task, reminder, briefing, alert = JARVIS", (_p("battery 42 percent hai"), _p("x", "TASK_CONFIRMATION"), _p("x", "REMINDER"), _p("x", "BRIEFING"), _p("low battery warning")) == ("jarvis",) * 5)
    ok("71: na samajh aane wala intent = JARVIS", _p("kuch", "WHATEVER") == "jarvis")
    ok("71: Edge par Hindi mein dono ek hi awaaz (sach bataya jata hai), English mein alag", _ve.pick("hi")["distinct"] is False and _ve.pick("hi", "", "", "english")["distinct"] is True)
    _ve.save({"provider": "sarvam"})
    ok("71: Sarvam par dono ke alag speaker, restart ke baad bhi", _ve.pick("hi", "", "tony")["speaker"] != _ve.pick("hi", "", "jarvis")["speaker"] and _ve.pick("hi")["distinct"] is True and _ve.load()["provider"] == "sarvam")
    _db = _sq.connect(":memory:"); _nt.init(_db)
    _n = lambda m: _nt.handle(_db, 1, m, False)
    ok("72: note karo -> save, meri notes -> list, dhundo -> search", "saved" in _n("note karo ki kal bijli ka bill bharna hai") and "bijli" in _n("meri notes") and "bijli" in _n("notes me bijli dhundo"))
    ok("72: password / OTP / card wala note save nahi hota", "do not save" in _n("note karo mera password 1234 hai") and "do not save" in _n("note karo card 4111111111111111"))
    ok("72: 'note about Faisal: ...' aur sawal notes ko nahi chhuate (people/AI ke paas jate hain)", _n("note about Faisal: loves cricket") is None and _n("note kya hota hai") is None)
    ok("72: delete note 1 hata deta hai", "deleted" in _n("delete note 1") and "no note" in _n("delete note 1"))
    ok("36: gap shabd sahi", CK.gap(40) == "40 seconds" and CK.gap(300) == "5 minutes" and CK.gap(7200) == "2 hours")
    ok("36: AI ko gap aur time rule milta hai", "5 minutes ago" in CK.context([("user", time.time() - 300)], time.time() - 300) and "Never write timestamps" in CK.context([], None))
    ok("36: 1 ghante se purani baat par naya shuru", "fresh start" in CK.context([], time.time() - 7200) and "fresh start" not in CK.context([], time.time() - 60))
    ok("36: 'kitna kaam ho gaya' samjha jata hai", PG.handle("bhai kitna kaam ho gaya short me", False) is not None)
    d = lambda m: (AC.device_cmd(m) or (None,))[0]
    ok("37: wifi on karo -> Wi-Fi page + imaandar note", d("wifi on karo") == {"type": "settings", "page": "wifi"} and "does not let any app" in AC.device_cmd("wifi on karo")[1])
    ok("37: bluetooth / battery / permissions pages", d("bluetooth settings") == {"type": "settings", "page": "bluetooth"} and d("battery settings kholo")["page"] == "battery" and d("permissions kholo")["page"] == "permissions")
    ok("37: torch on aur off", d("torch on") == {"type": "torch", "on": True} and d("flashlight band karo") == {"type": "torch", "on": False} and d("torch") is None)
    ok("37: volume badhao / kam karo", d("volume badhao") == {"type": "volume", "dir": "up"} and d("awaaz kam karo") == {"type": "volume", "dir": "down"} and d("volume kam aur zyada") is None)
    ok("37: brightness kam -> Display page (Jarvis badalta nahi)", d("brightness kam karo") == {"type": "settings", "page": "display"})
    ok("37: normal chat nahi pakda jata", all(d(m) is None for m in ("wifi password kya hai", "what is bluetooth", "mera wifi slow hai", "how do I turn on torch?")))
    ok("37: switch OFF par settings action nahi", "OFF" in AC.handle("torch on", False, False, True, lambda h, s, e: ("x", "y"))[0] and AC.handle("torch on", False, True, True, lambda h, s, e: ("x", "y"))[1] == {"type": "torch", "on": True})
    ok("33: sawaal par confirm nahi", a("how to delete a file?") is None and a("send me a joke") is None)
    ok("33: password type karna hamesha mana", a("mera password type karo", False)[1] is None and "never type" in a("enter my OTP 1234")[0])
    ok("33: Chrome kholo ab bhi bina confirm", a("Chrome kholo")[1]["type"] == "open_app")
    ok("34: peeche jao / go back -> back, go home -> home", a("peeche jao")[1] == {"type": "back"} and a("go back")[1] == {"type": "back"} and a("go home")[1] == {"type": "home"})
    ok("34: neeche scroll karo / scroll up", a("neeche scroll karo")[1] == {"type": "scroll", "dir": "down"} and a("scroll up")[1] == {"type": "scroll", "dir": "up"})
    ok("34: Hindi (पीछे जाओ, नीचे स्क्रॉल करो)", a("पीछे जाओ")[1] == {"type": "back"} and a("नीचे स्क्रॉल करो")[1]["dir"] == "down")
    ok("34: Settings dabao -> click, is button ko dabao -> naam poochho", a("Settings dabao")[1] == {"type": "click", "name": "settings"} and a("is button ko dabao")[1] is None)
    ok("34: Send/Delete button par pehle Yes (then ke saath)", a("send button dabao")[1] == {"type": "confirm", "risk": "click", "then": {"type": "click", "name": "send"}} and a("delete button dabao")[1]["then"]["name"] == "delete")
    ok("34: type hello chalta hai, par OTP/PIN/card number kabhi nahi", a("type hello")[1] == {"type": "type", "text": "hello"} and a("type 1234")[1] is None and "never type" in a("type 1234")[0] and a("type 4111 1111 1111 1111")[1] is None)
    ok("34: switch OFF par type chat hai, back par OFF bataya", a("type hello", False) is None and "OFF" in a("go back", False)[0])
    ok("34: sawaal chat hi rehte hain", a("type of food kya hai") is None and a("how to go back?") is None and a("which app is best?") is None)
    ok("34: kaun sa app khula hai -> current_app", a("kaun sa app khula hai")[1] == {"type": "current_app"})
    import memory as MM
    ok("54: fact par offer (bhatija, wife, Hindi)", all(MM.suggest(x) for x in ("mere bhatije ka naam Arman hai", "my wife's name is Sara", "मेरे भतीजे का नाम अरमान है", "meri behan ka birthday 5 May ko hai")))
    ok("54: sawaal, secret aur yaad rakho par offer nahi", not any(MM.suggest(x) for x in ("mere bhatije ka naam kya hai", "what is my wife's name?", "my password name is abc", "yaad rakho: mere bhatije ka naam Arman hai", "weather kaisa hai", "mera pin 1234 hai naam")))
    ok("35: phone lock kar do / lock the phone / फोन लॉक करो -> lock", all(a(m)[1] == {"type": "lock"} for m in ("phone lock kar do", "lock the phone", "फोन लॉक करो", "lock screen")))
    ok("35: unlock, app lock, sawaal par lock nahi", all((a(m) or (0, None))[1] != {"type": "lock"} for m in ("unlock phone", "app lock lagao", "how to lock my phone?", "lock kar do")))
    ok("35: switch OFF par lock nahi, OFF bataya", "OFF" in a("phone lock kar do", False)[0] and a("phone lock kar do", False)[1] is None)
    pr = PG.handle("bhai app ka kaam kahan tak pahuncha", False)
    ok("34: progress README se aata hai (done, baaki, next)", "built" in pr and "34" in pr and "Next:" in pr and PG.handle("my fitness progress", False) is None)
_unit()

PORT = "8799"
URL = "http://127.0.0.1:" + PORT
env = dict(os.environ, PROVIDER="bogus,mock", PORT=PORT, JARVIS_DB=os.path.join(tempfile.mkdtemp(), "t.db"), PYTHONUNBUFFERED="1", JARVIS_KEYS=os.path.join(tempfile.mkdtemp(), "k.json"))
app = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def call(path, data=None, token=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(URL + path, json.dumps(data).encode() if data is not None else None, h)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def start():
    p = subprocess.Popen([sys.executable, app], env=env, stdout=subprocess.PIPE, text=True)
    code = re.search(r"PAIRING CODE: (\d{6})", p.stdout.readline()).group(1)
    time.sleep(0.5)
    return p, code


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        sys.exit(1)


p, code = start()
try:
    check("status chalta hai", call("/status")[1]["ok"])
    check("manifest khulta hai", b"Jarvis" in urllib.request.urlopen(URL + "/manifest.webmanifest").read())
    check("chat page (/) khulta hai", b"Jarvis" in urllib.request.urlopen(URL + "/").read())
    check("bina token chat band (401)", call("/chat", {"message": "hi"})[0] == 401)
    check("galat code band (403)", call("/pair", {"code": "000000" if code != "000000" else "111111"})[0] == 403)
    s, r = call("/pair", {"code": code, "name": "test"})
    token = r.get("token", "")
    check("sahi code se token mila", s == 200 and len(token) > 20)
    check("code dobara use nahi hota", call("/pair", {"code": code})[0] == 403)
    check("chat ka jawab aaya", call("/chat", {"message": "namaste"}, token)[1].get("reply", "").endswith("namaste"))
    check("pehla provider fail to agla chalta hai (fallback)", call("/chat", {"message": "x"}, token)[1].get("via") == "mock")
    check("key pehchan: groq/openrouter/nvidia/deepseek/mistral", [A.detect(k) for k in ("gsk_a", "sk-or-v1-a", "nvapi-a", "sk-" + "a1" * 16, "mstrl_a", "A" * 32)] == ["groq", "openrouter", "nvidia", "deepseek", "mistral", "mistral"] and A.detect("hello") is None)
    check("keys bina token band (401)", call("/keys", {"key": "mock_x"})[0] == 401)
    check("nakli key reject", call("/keys", {"key": "hello"}, token)[1]["ok"] is False)
    s, r = call("/keys", {"key": "mock_secret123"}, token)
    check("sahi key save hui (green)", r.get("ok") is True and r["provider"] == "mock" and "secret123" not in json.dumps(r))
    check("keys list mein key wapas nahi aati", "secret123" not in json.dumps(call("/keys", token=token)[1]))
    check("keys file sirf owner ke liye (600)", stat.S_IMODE(os.stat(env["JARVIS_KEYS"]).st_mode) == 0o600)
    check("key hatane se file se nikli", call("/keys/delete", {"provider": "mock"}, token)[1]["ok"] and "secret123" not in open(env["JARVIS_KEYS"]).read())
    st = call("/stats", token=token)
    check("stats: login ke bina band", call("/stats")[0] == 401)
    check("stats: login ke baad numbers", st[0] == 200 and st[1].get("srv_ram", 1) > 0 and "disk_total" in st[1])
    check("khali message reject", call("/chat", {"message": " "}, token)[0] == 400)
    check("history mein 4 message", len(call("/history", token=token)[1]["messages"]) == 4)
finally:
    p.terminate()
    p.wait()
p2, _ = start()
try:
    check("restart ke baad token + history bachi", len(call("/history", token=token)[1]["messages"]) == 4)
    cc = lambda m, ctl=True, ap=True: call("/chat", {"message": m, "control": ctl, "app": ap}, token)[1]
    r = cc("WhatsApp kholo")
    check("30: WhatsApp kholo -> open_app action", r.get("action") == {"type": "open_app", "name": "WhatsApp"})
    check("30: Hindi naam (व्हाट्सएप खोलो) -> WhatsApp", cc("व्हाट्सएप खोलो").get("action", {}).get("name") == "WhatsApp")
    check("30: switch OFF -> koi action nahi, OFF bataya", "action" not in cc("open chrome", False) and "OFF" in cc("open chrome", False)["reply"])
    check("30: Chrome (browser) mein action nahi", "action" not in cc("open chrome", True, False))
    check("30: bakwas phrase par action nahi", "action" not in cc("blah blah nonsense"))
    check("30: sawaal (open source kya hai) par action nahi", "action" not in cc("open source kya hai"))
    check("34: chat route par peeche jao -> back action", cc("peeche jao").get("action") == {"type": "back"})
    check("34: chat route par progress sawaal ka jawab", "planned Parts" in cc("app ka kaam kahan tak pahuncha")["reply"])
    r54 = cc("mere bhatije ka naam Arman hai")
    check("54: chat jawab ke saath remember offer, par abhi save nahi", r54.get("remember") == "mere bhatije ka naam Arman hai" and "Arman" not in cc("kya yaad hai")["reply"])
    check("54: Yes ke baad (yaad rakho) save hota hai", "saved" in cc("yaad rakho: " + r54["remember"])["reply"] and "Arman" in cc("kya yaad hai")["reply"])
    check("30: AI ne bakwas diya -> action nahi", "action" not in cc("please start the day with a joke now ok"))
finally:
    p2.terminate()
    p2.wait()
try:
    call("/status")
    check("band server offline dikhta hai", False)
except Exception:
    check("band server offline dikhta hai", True)
print("Sab test pass")
