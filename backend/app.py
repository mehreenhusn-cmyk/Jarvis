"""Jarvis backend - Part 1: chat + pairing + SQLite. Sirf Python stdlib, pip install nahi chahiye."""
import hashlib, json, os, re, secrets, sqlite3, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import actions, autostart, backup, brief, calls, clock, handoff, ledger, memory, people, phone, place, progress, remind, screen, see, sysinfo, tasks, tts, voiceengine, web

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
SYSTEM = ("You are Jarvis, a calm and polite personal AI assistant. Reply in simple, clear English, in 1 to 3 short sentences. "
          "Call the user sir. No emoji or markdown. Use personal facts only if the user told you. Never invent facts.")
# Part 8: Iron Man (Hindi dub) wala Jarvis - shaant, vinamra, "sir" kehne wala. Page tab bhejta hai jab Hindi awaaz chuni ho.
PERSONA = {"english": SYSTEM, "hindi": (
    "You are JARVIS, like the calm, polite, witty AI butler from the Hindi dub of Iron Man. Address the user as 'सर'. "
    "Always reply in pure, simple spoken Hindi in Devanagari script (English words only when really needed). "
    "Keep answers short: 1 to 3 sentences, with a light dry wit when it fits. No emoji, markdown, stars or hashes, "
    "because your reply will be spoken aloud. Remember personal things only if the user told you. Never invent facts.")}
FILES = {"/": ("index.html", "text/html; charset=utf-8"), "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
         "/icon-192.png": ("icon-192.png", "image/png"), "/icon-512.png": ("icon-512.png", "image/png")}
BOOT = str(int(time.time()))  # server ka restart pehchanne ke liye: page khud refresh hota hai
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
    memory.init(c)
    people.init(c)
    remind.init(c)
    ledger.init(c)
    tasks.init(c)  # Part 41: tracked multi-step tasks
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


def call(name, history, key=None, style="english", extra=""):
    if name == "mock":  # sirf testing ke liye
        return "mock jawab: " + history[-1]["content"]
    base, key_env, model = PROVIDERS[name]
    key = key or getkey(name)
    body = json.dumps({"model": os.environ.get("MODEL_" + name.upper()) or model,
                       "messages": [{"role": "system", "content": PERSONA.get(style, SYSTEM) + extra}] + history}).encode()
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


def ask(history, style="english", extra=""):
    """PROVIDER=groq,openrouter,... : pehla jo chale uska jawab. Return (jawab, provider)."""
    errs = []
    for n in names():
        if n != "mock" and n not in PROVIDERS:
            errs.append(f"{n}: naam galat")
        elif n != "mock" and not getkey(n):
            errs.append(f"{n}: key nahi")
        else:
            try:
                return call(n, history, None, style, extra), n
            except RuntimeError as e:
                errs.append(f"{n}: {e}")
    raise RuntimeError(" | ".join(errs) or "koi key nahi - upar ⚙ Settings mein key paste karo")


def sync_note():
    """Last zip update, written by sync.sh: 'name|time|result'."""
    try:
        return open(os.path.expanduser("~/.jarvis_last")).read().strip()[:120]
    except OSError:
        return ""


SECURE = {  # Part 26: the page may only talk to this server; no outside scripts, no framing
    "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                               "img-src 'self' data: blob:; media-src 'self' blob: data:; connect-src 'self'; base-uri 'none'; "
                               "form-action 'none'; frame-ancestors 'none'"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def allowed(self):
        """Part 26: only this phone's own page may talk to the server (stops other websites using it, e.g. DNS rebinding)."""
        host, port = self.server.server_address[:2]
        if host != "127.0.0.1":
            return True  # someone chose another HOST in .env: they accept the risk
        ok = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
        return self.headers.get("Host", "").lower() in {f"127.0.0.1:{port}", f"localhost:{port}"} and self.headers.get("Origin", next(iter(ok))) in ok

    def send(self, code, obj):
        if code >= 400 and isinstance(obj, dict) and "error" in obj:  # never show anything that looks like a key
            obj["error"] = re.sub(r"[A-Za-z0-9_\-]{24,}", "***", str(obj["error"]))
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def device(self):
        m = re.match(r"Bearer (\S+)$", self.headers.get("Authorization", ""))
        if not m:
            return None
        row = db().execute("SELECT id FROM devices WHERE token_hash=?",
                           (hashlib.sha256(m.group(1).encode()).hexdigest(),)).fetchone()
        return row[0] if row else None

    def body(self, lim=20000):
        n = int(self.headers.get("Content-Length") or 0)
        if n > lim:
            return None
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return None

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {"error": "blocked"})
        if self.path in FILES:
            fn, ctype = FILES[self.path]
            try:
                page = open(os.path.join(HERE, "..", "web", fn), "rb").read()
            except OSError:
                return self.send(404, {"error": "file nahi mili"})
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(page)))
            for k, v in SECURE.items():
                self.send_header(k, v)
            self.end_headers()
            return self.wfile.write(page)
        if self.path == "/status":
            ok = any(n == "mock" or bool(getkey(n)) for n in names())
            return self.send(200, {"ok": True, "provider": ",".join(names()), "configured": ok, "boot": BOOT, "sync": sync_note(), "uptime": int(time.time()) - int(BOOT)})
        dev = self.device()
        if dev is None:
            return self.send(401, {"error": "pehle pair karo"})
        if self.path == "/backup/list":  # Part 47: backup files in Downloads (names only)
            return self.send(200, {"files": backup.files(), "dir": backup.DIR})
        if self.path == "/tasks":  # Part 41: the last few tasks and how they ended
            return self.send(200, {"tasks": tasks.recent(db(), dev)})
        if self.path == "/voice":  # Part 51: Tony and JARVIS settings (login needed)
            return self.send(200, voiceengine.load())
        if self.path == "/stats":  # Part 50: system card numbers (login needed)
            return self.send(200, sysinfo.stats())
        if self.path == "/keys":  # keys kabhi wapas nahi bhejte, sirf masked
            return self.send(200, {"providers": [{"name": n, "saved": bool(getkey(n)), "masked": mask(getkey(n)) if getkey(n) else ""} for n in PROVIDERS]})
        if self.path == "/history":
            rows = db().execute("SELECT role, content, ts FROM messages WHERE device=? ORDER BY id DESC LIMIT 50", (dev,)).fetchall()
            return self.send(200, {"messages": [{"role": r, "content": c, "ts": int(t or 0)} for r, c, t in reversed(rows)]})  # Part 36: ts so the page can show WhatsApp-style times
        if self.path == "/ledger":
            r = ledger.rows(db(), dev)
            dn, ln = ledger.totals(r)
            return self.send(200, {"items": [{"id": i, "text": ledger.line(i, w, a, d, du)} for i, w, a, d, du in r], "dena": dn, "lena": ln})
        if self.path == "/people":
            return self.send(200, {"people": people.all_people(db(), dev)})
        if self.path == "/memory":
            return self.send(200, {"memories": [{"id": i, "text": t} for i, t in memory.rows(db(), dev)]})
        self.send(404, {"error": "not found"})

    def do_POST(self):
        if not self.allowed():
            return self.send(403, {"error": "blocked"})
        data = self.body(1500000 if self.path == "/see" and self.headers.get("Authorization") else 20000)
        if not isinstance(data, dict):
            return self.send(400, {"error": "galat request"})
        if self.path == "/newcode":  # Part 37: the pairing screen asks Termux to show the code again (the code is NEVER sent to the page)
            if time.time() < PAIR["lock"] or time.time() - PAIR.get("last", 0) < 5:
                return self.send(429, {"error": "kuch der baad try karo"})
            PAIR["last"] = time.time()
            if time.time() > PAIR["exp"] - 60:
                new_code()
            else:
                print(f"PAIRING CODE: {PAIR['code']}  (abhi bhi valid)", flush=True)
            return self.send(200, {"ok": True})
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
        if self.path == "/due":  # page har 10 sec poochta hai: kisi reminder ka time hua?
            return self.send(200, {"due": remind.due(db(), dev, str(data.get("now", "")))})
        if self.path == "/task/update":  # Part 41/42: the page tells how a task is going (RUNNING, WAITING_FOR_PERMISSION, ...)
            try:
                ok = tasks.update(db(), dev, int(data.get("id") or 0), str(data.get("state", "")), data.get("cur") if isinstance(data.get("cur"), int) else None, data.get("note", ""))
            except (TypeError, ValueError):
                ok = False
            return self.send(200, {"ok": ok})
        if self.path == "/task/done":  # Part 42: what the app really reported for every step; the server decides COMPLETED, PARTIAL, FAILED or CANCELLED
            try:
                st = tasks.finish(db(), dev, int(data.get("id") or 0), data.get("results"), data.get("cancelled") is True)
            except (TypeError, ValueError):
                st = ""
            return self.send(200, {"ok": bool(st), "state": st})
        if self.path == "/today":  # Part 56: Home tab. Aaj ke reminders aur jin hisab ki tareekh aaj ya pehle ki hai
            now = str(data.get("now", ""))
            led = [{"id": i, "text": ledger.line(i, w, a, d, du), "late": du < now[:10]} for i, w, a, d, du in ledger.rows(db(), dev) if du and du <= now[:10]]
            return self.send(200, {"reminders": remind.today(db(), dev, now), "ledger": led})
        if self.path == "/brief":  # page din mein ek baar apne aap maangta hai
            return self.send(200, {"text": brief.build(db(), dev, str(data.get("now", "")), data.get("style") == "hindi", bool(data.get("auto")))})
        if self.path == "/ledger/paid":
            c = db()
            c.execute("UPDATE ledger SET paid=1 WHERE id=? AND device=?", (int(data.get("id") or 0), dev))
            c.commit()
            return self.send(200, {"ok": True})
        if self.path in ("/backup/make", "/backup/preview", "/backup/restore"):  # Part 47: the passphrase is used once and never kept
            try:
                pw = str(data.get("pass", ""))
                if self.path == "/backup/make":
                    return self.send(200, backup.make(db(), dev, pw, data.get("chat") is True))
                if self.path == "/backup/preview":
                    return self.send(200, {"preview": backup.preview(db(), dev, str(data.get("name", "")), pw)})
                if data.get("confirm") is not True:
                    return self.send(400, {"error": "restore needs your confirm tap"})
                return self.send(200, {"added": backup.restore(db(), dev, str(data.get("name", "")), pw)})
            except RuntimeError as e:
                return self.send(400, {"error": str(e)})
        if self.path == "/people/delete":
            c = db()
            return self.send(200, {"ok": bool(people.delete(c, dev, str(data.get("name", ""))))})
        if self.path == "/memory/delete":
            c = db()
            c.execute("DELETE FROM memories WHERE id=? AND device=?", (int(data.get("id") or 0), dev))
            c.commit()
            return self.send(200, {"ok": True})
        if self.path == "/voice/set":  # Part 51: save Tony/JARVIS settings in voice.json
            return self.send(200, voiceengine.save(data))
        if self.path == "/tts":  # Part 7: neural awaaz (mp3). Part 51: voice na diya ho to Tony/JARVIS intent se chunta hai
            txt = str(data.get("text", ""))
            try:
                if data.get("voice"):
                    audio, who = tts.speak(txt, str(data.get("voice", "")), data.get("pitch", -8), data.get("rate", -6)), "classic"
                else:
                    v = voiceengine.pick(txt, str(data.get("intent", "")), str(data.get("profile", "")), "english" if data.get("lang") == "english" else "hindi")
                    audio, who = tts.speak(txt, v["voice"], v["pitch"], v["rate"]), v["profile"]
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            self.send_response(200)
            self.send_header("X-Voice", who)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(len(audio)))
            self.end_headers()
            return self.wfile.write(audio)
        if self.path == "/see":
            try:
                ans, via = see.look(data.get("image"), data.get("question"), data.get("style") == "hindi", PROVIDERS, getkey, names())
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            c = db()
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", "(photo) " + ans, time.time()))
            c.commit()
            return self.send(200, {"reply": ans, "via": via})
        if self.path == "/chat":
            msg = str(data.get("message", "")).strip()
            if not msg or len(msg) > 4000:
                return self.send(400, {"error": "message khali ya bahut bada"})
            c = db()
            last = c.execute("SELECT ts FROM messages WHERE device=? AND role='user' ORDER BY id DESC LIMIT 1", (dev,)).fetchone()  # Part 36: when did the user last write?
            prev_ts = last[0] if last else None
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "user", msg, time.time()))
            c.commit()
            if re.match(r"^\s*(?:clear|delete|erase)\s+(?:my\s+)?(?:chat\s+)?history\s*$", msg, re.I):
                c.execute("DELETE FROM messages WHERE device=?", (dev,))
                c.commit()
                return self.send(200, {"reply": "Okay sir, the chat history is deleted. Saved memories, people and reminders are not touched.", "via": "memory"})
            style = str(data.get("style", ""))
            mem = memory.handle(c, dev, msg, style == "hindi")  # yaad rakho / bhool jao / kya yaad hai
            now = str(data.get("now", ""))
            if mem is None:  # Part 47: "backup", "delete everything" (typed phrase). Never takes a passphrase
                mem = backup.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 48: "handoff" (summary for Claude or ChatGPT) and "phone kho gaya" (steps)
                mem = handoff.handle(c, dev, msg, style == "hindi")
            if mem is None:  # missed calls / contact Faisal (made here, no AI)
                mem = calls.handle(msg, data.get("calls"), data.get("contact"), style == "hindi", data.get("cal"))
            if mem is None:  # note about Faisal: ... / who is Faisal
                mem = people.handle(c, dev, msg, style == "hindi")
            if mem is None:  # why is my phone slow
                mem = phone.handle(msg, data.get("phone"), style == "hindi")
            if mem is None:  # where am I
                mem = place.handle(msg, data.get("loc"), style == "hindi")
            if mem is None:  # "briefing" / "aaj ka plan"
                mem = brief.handle(c, dev, msg, style == "hindi", now, data.get("cal"))
            if mem is None:  # hisab: "Faisal ko 5000 dene hain"
                mem = ledger.handle(c, dev, msg, style == "hindi", ask, now)
            if mem is None:  # reminder: "kal 9 baje chai yaad dilana"
                mem = remind.handle(c, dev, msg, style == "hindi", ask, now)
            if mem is None:  # "app ka kaam kahan tak pahuncha": read from the README plan
                mem = progress.handle(msg, style == "hindi")
            action = None
            if mem is None:  # Part 30: "WhatsApp kholo" (only proposes; the app checks the switch and Stop)
                got = tasks.routine(c, dev, msg, style == "hindi", data.get("control") is True, data.get("app") is True) or tasks.make(c, dev, msg, style == "hindi", data.get("control") is True, data.get("app") is True) or actions.handle(msg, style == "hindi", data.get("control") is True, data.get("app") is True, ask)  # Part 41: several steps in one sentence become one task
                if got:
                    mem, action = got
            if mem is not None:
                keep = "(call, contact and calendar info was shown, not saved)" if calls.private(msg) else ("(phone action) " + mem if action else mem)
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", keep, time.time()))
                c.commit()
                return self.send(200, dict({"reply": mem, "via": "memory"}, **({"action": action} if action else {})))
            rows = c.execute("SELECT role, content, ts FROM messages WHERE device=? ORDER BY id DESC LIMIT 10", (dev,)).fetchall()
            tctx = clock.context([(r, t) for r, _, t in reversed(rows)], prev_ts)
            try:
                reply, via = ask([{"role": r, "content": t} for r, t, _ in reversed(rows)], style, tctx + memory.context(c, dev) + people.context(c, dev, msg) + place.context(msg, data.get("loc")) + screen.context(data.get("screen")) + web.context(msg))
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", "(answer about your screen was shown, not saved)" if screen.used(data.get("screen")) else reply, time.time()))
            c.commit()
            sug = None if screen.used(data.get("screen")) else memory.suggest(msg)  # Part 54: only an offer, nothing is saved here
            return self.send(200, dict({"reply": reply, "via": via}, **({"remember": sug} if sug else {})))
        self.send(404, {"error": "not found"})


if __name__ == "__main__":
    load_env()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8787"))
    autostart.ensure(os.path.dirname(HERE))
    autostart.refresh_scripts(os.path.dirname(HERE))
    new_code()
    tasks.restart(db())  # Part 41 restart rule: a task that was RUNNING before this start is FAILED now
    print(f"Jarvis chal raha hai: http://{host}:{port}  provider={','.join(names())}", flush=True)
    ThreadingHTTPServer((host, port), H).serve_forever()
