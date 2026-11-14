"""Jarvis backend - Part 1: chat + pairing + SQLite. Sirf Python stdlib, pip install nahi chahiye."""
import hashlib, json, os, re, secrets, sqlite3, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import tts

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("JARVIS_DB") or os.path.join(HERE, "jarvis.db")
KEYS = os.environ.get("JARVIS_KEYS") or os.path.join(HERE, "keys.json")  # app se daali keys (gitignored)
# naam: (base_url, key ka env naam, default model). Sab OpenAI-style API hain.
PROVIDERS = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "llama-3.3-70b-versatile"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "openai/gpt-4o-mini"),
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL_API_KEY", "mistral-small-latest"),
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY", "deepseek-chat"),
    "nvidia": ("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", "meta/llama-3.1-70b-instruct"),
}
SYSTEM = ("Tum Jarvis ho, Hussain ke personal AI dost. User jis bhasha mein likhe (Hindi, English ya Hinglish) "
          "usi mein jawab do. Hindi ko bhi Roman script mein likho, Devanagari nahi. Chhote, saaf jawab do. "
          "Personal baat tabhi yaad rakho jab user ne khud batayi ho. Kuch invent mat karo.")
FILES = {"/": ("index.html", "text/html; charset=utf-8"), "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
         "/icon-192.png": ("icon-192.png", "image/png"), "/icon-512.png": ("icon-512.png", "image/png")}
PAIR = {"code": "", "exp": 0, "fails": 0, "lock": 0}


def load_env():
    p = os.path.join(HERE, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def db():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS devices(id INTEGER PRIMARY KEY, name TEXT, token_hash TEXT UNIQUE, ts REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, device INT, role TEXT, content TEXT, ts REAL)")
    return c


def new_code():
    PAIR.update(code=f"{secrets.randbelow(10**6):06d}", exp=time.time() + 600, fails=0)
    print(f"PAIRING CODE: {PAIR['code']}  (10 minute valid, ek baar use)", flush=True)


def saved():
    try:
        return json.load(open(KEYS))
    except (OSError, ValueError):
        return {}


def getkey(n):
    env = os.environ.get(PROVIDERS[n][1], "") if n in PROVIDERS else ""
    return env or saved().get(n, "")


def store(n, key):
    d = saved()
    if key:
        d[n] = key
    else:
        d.pop(n, None)
    with open(KEYS, "w") as f:
        json.dump(d, f)
    os.chmod(KEYS, 0o600)


def detect(k):
    """Key ka shuruaat dekh ke company pehchano. Pehchan na ho to None (key kisi aur ko nahi bhejte)."""
    for pre, n in (("mock_", "mock"), ("gsk_", "groq"), ("sk-or-", "openrouter"), ("nvapi-", "nvidia"), ("mstrl_", "mistral")):
        if k.startswith(pre):
            return n
    if re.fullmatch(r"sk-[0-9a-f]{32}", k):
        return "deepseek"
    return "mistral" if re.fullmatch(r"[A-Za-z0-9]{32}", k) else None


def mask(k):
    return k[:4] + "…" + k[-4:] if len(k) > 10 else "…"


def names():
    env = [n.strip().lower() for n in os.environ.get("PROVIDER", "").split(",") if n.strip()]
    return env or [n for n in [*PROVIDERS, "mock"] if getkey(n)]


def call(name, history, key=None):
    if name == "mock":  # sirf testing ke liye
        return "mock jawab: " + history[-1]["content"]
    base, key_env, model = PROVIDERS[name]
    key = key or getkey(name)
    body = json.dumps({"model": os.environ.get("MODEL_" + name.upper()) or model,
                       "messages": [{"role": "system", "content": SYSTEM}] + history}).encode()
    req = urllib.request.Request(base + "/chat/completions", body, {
        "Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "jarvis/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"error {e.code}: {e.read()[:150].decode(errors='ignore')}")
    except Exception as e:
        raise RuntimeError("connect nahi hua: " + type(e).__name__)


def check(n, k):
    try:
        call(n, [{"role": "user", "content": "Ek shabd mein jawab do: OK"}], k)
    except RuntimeError as e:
        return str(e)


def ask(history):
    """PROVIDER=groq,openrouter,... : pehla jo chale uska jawab. Return (jawab, provider)."""
    errs = []
    for n in names():
        if n != "mock" and n not in PROVIDERS:
            errs.append(f"{n}: naam galat")
        elif n != "mock" and not getkey(n):
            errs.append(f"{n}: key nahi")
        else:
            try:
                return call(n, history), n
            except RuntimeError as e:
                errs.append(f"{n}: {e}")
    raise RuntimeError(" | ".join(errs) or "koi key nahi - upar ⚙ Settings mein key paste karo")


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def device(self):
        m = re.match(r"Bearer (\S+)$", self.headers.get("Authorization", ""))
        if not m:
            return None
        row = db().execute("SELECT id FROM devices WHERE token_hash=?",
                           (hashlib.sha256(m.group(1).encode()).hexdigest(),)).fetchone()
        return row[0] if row else None

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 20000:
            return None
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return None

    def do_GET(self):
        if self.path in FILES:
            fn, ctype = FILES[self.path]
            try:
                page = open(os.path.join(HERE, "..", "web", fn), "rb").read()
            except OSError:
                return self.send(404, {"error": "file nahi mili"})
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            return self.wfile.write(page)
        if self.path == "/status":
            ok = any(n == "mock" or bool(getkey(n)) for n in names())
            return self.send(200, {"ok": True, "provider": ",".join(names()), "configured": ok})
        dev = self.device()
        if dev is None:
            return self.send(401, {"error": "pehle pair karo"})
        if self.path == "/keys":  # keys kabhi wapas nahi bhejte, sirf masked
            return self.send(200, {"providers": [{"name": n, "saved": bool(getkey(n)), "masked": mask(getkey(n)) if getkey(n) else ""} for n in PROVIDERS]})
        if self.path == "/history":
            rows = db().execute("SELECT role, content FROM messages WHERE device=? ORDER BY id DESC LIMIT 50", (dev,)).fetchall()
            return self.send(200, {"messages": [{"role": r, "content": c} for r, c in reversed(rows)]})
        self.send(404, {"error": "not found"})

    def do_POST(self):
        data = self.body()
        if not isinstance(data, dict):
            return self.send(400, {"error": "galat request"})
        if self.path == "/pair":
            if time.time() < PAIR["lock"]:
                return self.send(429, {"error": "kuch der baad try karo"})
            ok = time.time() < PAIR["exp"] and secrets.compare_digest(str(data.get("code", "")), PAIR["code"])
            if not ok:
                PAIR["fails"] += 1
                if PAIR["fails"] >= 5:
                    PAIR.update(fails=0, lock=time.time() + 60)
                return self.send(403, {"error": "code galat ya expire"})
            token = secrets.token_urlsafe(32)
            c = db()
            c.execute("INSERT INTO devices(name, token_hash, ts) VALUES(?,?,?)",
                      (str(data.get("name", "phone"))[:40], hashlib.sha256(token.encode()).hexdigest(), time.time()))
            c.commit()
            new_code()
            return self.send(200, {"token": token})
        dev = self.device()
        if dev is None:
            return self.send(401, {"error": "pehle pair karo"})
        if self.path == "/keys":
            k = str(data.get("key", "")).strip()
            n = detect(k)
            if not n:
                return self.send(200, {"ok": False, "error": "Ye key kis company ki hai, pehchana nahi gaya"})
            err = check(n, k)
            if err:
                return self.send(200, {"ok": False, "provider": n, "error": err})
            store(n, k)
            return self.send(200, {"ok": True, "provider": n, "masked": mask(k)})
        if self.path == "/keys/test":
            n = str(data.get("provider", ""))
            err = check(n, getkey(n)) if n in PROVIDERS else "naam galat"
            return self.send(200, {"ok": err is None, "error": err or ""})
        if self.path == "/keys/delete":
            store(str(data.get("provider", "")), "")
            return self.send(200, {"ok": True})
        if self.path == "/tts":  # Part 7: neural awaaz (mp3)
            try:
                audio = tts.speak(str(data.get("text", "")), str(data.get("voice", "")))
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(audio)))
            self.end_headers()
            return self.wfile.write(audio)
        if self.path == "/chat":
            msg = str(data.get("message", "")).strip()
            if not msg or len(msg) > 4000:
                return self.send(400, {"error": "message khali ya bahut bada"})
            c = db()
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "user", msg, time.time()))
            c.commit()
            rows = c.execute("SELECT role, content FROM messages WHERE device=? ORDER BY id DESC LIMIT 10", (dev,)).fetchall()
            try:
                reply, via = ask([{"role": r, "content": t} for r, t in reversed(rows)])
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", reply, time.time()))
            c.commit()
            return self.send(200, {"reply": reply, "via": via})
        self.send(404, {"error": "not found"})


if __name__ == "__main__":
    load_env()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8787"))
    new_code()
    print(f"Jarvis chal raha hai: http://{host}:{port}  provider={','.join(names())}", flush=True)
    ThreadingHTTPServer((host, port), H).serve_forever()
