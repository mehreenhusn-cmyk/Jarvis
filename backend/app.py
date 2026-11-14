"""Jarvis backend - Part 1: chat + pairing + SQLite. Sirf Python stdlib, pip install nahi chahiye."""
import hashlib, json, os, re, secrets, sqlite3, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("JARVIS_DB") or os.path.join(HERE, "jarvis.db")
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


def ask(history):
    name = os.environ.get("PROVIDER", "groq").lower()
    if name == "mock":  # sirf testing ke liye
        return "mock jawab: " + history[-1]["content"]
    if name not in PROVIDERS:
        raise RuntimeError("PROVIDER galat hai: " + name)
    base, key_env, model = PROVIDERS[name]
    key = os.environ.get(key_env, "")
    if not key:
        raise RuntimeError(f"{key_env} .env file mein nahi mili")
    body = json.dumps({"model": os.environ.get("MODEL", model),
                       "messages": [{"role": "system", "content": SYSTEM}] + history}).encode()
    req = urllib.request.Request(base + "/chat/completions", body, {
        "Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "jarvis/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"provider error {e.code}: {e.read()[:200].decode(errors='ignore')}")
    except Exception as e:
        raise RuntimeError("provider se connect nahi hua: " + type(e).__name__)


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
        if self.path == "/status":
            name = os.environ.get("PROVIDER", "groq").lower()
            ok = name == "mock" or bool(os.environ.get(PROVIDERS.get(name, ("", "X"))[1], ""))
            return self.send(200, {"ok": True, "provider": name, "configured": ok})
        dev = self.device()
        if dev is None:
            return self.send(401, {"error": "pehle pair karo"})
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
        if self.path == "/chat":
            msg = str(data.get("message", "")).strip()
            if not msg or len(msg) > 4000:
                return self.send(400, {"error": "message khali ya bahut bada"})
            c = db()
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "user", msg, time.time()))
            c.commit()
            rows = c.execute("SELECT role, content FROM messages WHERE device=? ORDER BY id DESC LIMIT 10", (dev,)).fetchall()
            try:
                reply = ask([{"role": r, "content": t} for r, t in reversed(rows)])
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", reply, time.time()))
            c.commit()
            return self.send(200, {"reply": reply})
        self.send(404, {"error": "not found"})


if __name__ == "__main__":
    load_env()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8787"))
    new_code()
    print(f"Jarvis chal raha hai: http://{host}:{port}  provider={os.environ.get('PROVIDER', 'groq')}", flush=True)
    ThreadingHTTPServer((host, port), H).serve_forever()
