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
