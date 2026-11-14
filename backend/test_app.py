"""Chalao: python backend/test_app.py   (mock provider, internet/API key nahi chahiye)"""
import json, os, re, subprocess, sys, tempfile, time, urllib.error, urllib.request

import stat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as A

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
    check("khali message reject", call("/chat", {"message": " "}, token)[0] == 400)
    check("history mein 4 message", len(call("/history", token=token)[1]["messages"]) == 4)
finally:
    p.terminate()
    p.wait()
p2, _ = start()
try:
    check("restart ke baad token + history bachi", len(call("/history", token=token)[1]["messages"]) == 4)
finally:
    p2.terminate()
    p2.wait()
try:
    call("/status")
    check("band server offline dikhta hai", False)
except Exception:
    check("band server offline dikhta hai", True)
print("Sab test pass")
