"""Jarvis backend - Part 1: chat + pairing + SQLite. Sirf Python stdlib, pip install nahi chahiye."""
import hashlib, json, os, re, secrets, sqlite3, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import actions, assist, autostart, backup, brief, calls, capsule, clock, debate, decisions, dreams, drift, events, ghost, guest, handoff, habits, ledger, lens, lists, memory, modes, money, mood, notes, people, phone, place, placenote, progress, redteam, remind, replyideas, screen, search, see, signs, spend, sysinfo, tasks, touch, tts, voiceengine, web, whatsnew

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
# Part 57: how Jarvis talks when someone sounds sad or stressed (always added). Not a doctor, no diagnosis, nothing about the mood is saved.
MOOD = ("\n\n[If the user sounds sad, stressed or low: first show you understand, do not judge, and ask whether he wants to talk, wants a distraction, or wants a practical fix. "
        "Give at most two small, practical options. Never diagnose, never say you are a doctor or a human. If he speaks of hurting himself or being in danger, stay calm, "
        "tell him to call the emergency number 112 or Tele-MANAS 14416 or a trusted person right now, and ask him to stay with someone.]")
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
    notes.init(c)  # Part 71/72: voice notes (same database, one table)
    people.init(c)
    remind.init(c)
    ledger.init(c)
    lists.init(c)  # Part 83: shopping and packing lists
    habits.init(c)  # Part 83: habit and streak tracker
    spend.init(c)  # Part 84: quick expense logger
    decisions.init(c)  # Parts 93 + 94
    mood.init(c)  # Part 96
    touch.init(c)  # Part 95
    placenote.init(c)  # Parts 113 + 114
    capsule.init(c)  # Part 97
    dreams.init(c)  # Part 103
    signs.init(c)  # Part 104
    ghost.init(c)  # Part 107
    money.init(c)  # Part 110
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


CAN = ("\n\nWHAT JARVIS CAN DO (the app does these when Hussain's words fit, not you): open any app; scroll, click, back and home on the open app; call or dial a contact by name; alarm and timer; reminders; notes, lists, habits, expenses; read the screen when asked; look at a photo; search the web in Research mode. "
       "WHAT IT CANNOT DO: see inside another app's private data (like a trading watch list) unless it is on the screen, send a message or pay without his tap, or guess news. "
       "If he asks for something from the CAN list, never say you cannot: tell him the exact short words to say, for example: Ammi ko call karo, or: Chrome kholo aur neeche scroll karo. "
       "Use the earlier messages to understand words like usko, wahi, isko, that, it.")  # Part 126
CAN += (" Never write the label '(phone action)'. Never say you switched, opened, turned on or changed something on the phone yourself: only the app does that, and only when the user's words match a command. "
        "If he asks for such a thing and no action ran, say so plainly and give the exact short words to say, for example: torch chalu karo.")


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
            s = voiceengine.load()
            k = getkey("sarvam")
            s["sarvam_saved"], s["sarvam_masked"] = bool(k), mask(k) if k else ""
            return self.send(200, s)
        if self.path == "/stats":  # Part 50: system card numbers (login needed)
            return self.send(200, sysinfo.stats())
        if self.path == "/keys":  # keys kabhi wapas nahi bhejte, sirf masked
            return self.send(200, {"providers": [{"name": n, "saved": bool(getkey(n)), "masked": mask(getkey(n)) if getkey(n) else ""} for n in PROVIDERS]})
        if self.path == "/history":
            rows = db().execute("SELECT role, content, ts FROM messages WHERE device=? ORDER BY id DESC LIMIT 50", (dev,)).fetchall()
            return self.send(200, {"messages": [{"role": r, "content": (c.replace("(phone action) ", "", 1) if r == "assistant" else c), "ts": int(t or 0)} for r, c, t in reversed(rows)]})  # Part 36: ts so the page can show WhatsApp-style times
        if self.path == "/ledger":
            r = ledger.rows(db(), dev)
            dn, ln = ledger.totals(r)
            return self.send(200, {"items": [{"id": i, "text": ledger.line(i, w, a, d, du)} for i, w, a, d, du in r], "dena": dn, "lena": ln})
        if self.path == "/people":
            return self.send(200, {"people": people.all_people(db(), dev)})
        if self.path == "/memory":
            return self.send(200, {"memories": [{"id": i, "text": t} for i, t in memory.rows(db(), dev)]})
        if self.path == "/atlas":  # Part 88: everything Jarvis keeps (counts) and the notes; reading only
            return self.send(200, memory.atlas(db(), dev))
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
            now = str(data.get("now", ""))
            return self.send(200, {"due": remind.due(db(), dev, now), "routines": tasks.due_routines(db(), dev, now), "report": tasks.due_report(db(), dev, now), "follow": remind.followup(db(), dev, now), "capsule": capsule.due(db(), dev, now), "bd": modes.bd_due(dev, now)})  # Part 76: routine ka time hua to page ek-tap button dikhata hai
        if self.path == "/capsule/open":  # Part 97: the text is sent only after the tap, and only if its day has come
            try:
                t = capsule.open_text(db(), dev, int(data.get("id") or 0), str(data.get("now", "")))
            except ValueError:
                t = None
            return self.send(200 if t else 404, {"text": t} if t else {"error": "not ready"})
        if self.path == "/place/sync":  # Parts 113 + 114: the page hands this copy to the Android app (places and reminders only, never a position)
            return self.send(200, {"pw": placenote.sync(db(), dev)})
        if self.path == "/place/fired":  # Part 113: the app showed a once-only reminder, so remove it
            return self.send(200, {"ok": placenote.fired(db(), dev, int(data.get("id") or 0))})
        if self.path == "/bd/answer":  # Part 101: Haan / Nahi under the check-in
            modes.bd_answer(dev, data.get("yes") is True)
            return self.send(200, {"ok": True})
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
            try:
                n = remind.tm(now)
            except ValueError:
                n = None
            c = db()
            bd = [{"in": k, "text": t, "on": on} for k, t, on in remind.birthdays(c, dev, n, 7)] if n else []  # Part 75: Daily Life Manager = reminders + ledger + birthdays + notes
            nts = [{"id": i, "text": x[:120]} for i, x in c.execute("SELECT id, text FROM notes WHERE device=? ORDER BY id DESC LIMIT 3", (dev,))]
            return self.send(200, {"reminders": remind.today(c, dev, now), "ledger": led, "birthdays": bd, "notes": nts, "routines": tasks.scheduled(c, dev), "lens": lens.build(c, dev, now, data.get("phone"), str(data.get("lens") or "all")), "mission": progress.mission(), "away": brief.away(c, dev, now, data.get("phone"), False)})  # Part 108: card after 6+ hours away  # Part 85/86: next best move card and Now/Next/Later strip
        if self.path == "/timeline":  # Part 109: the Timeline tab (filter + "More" with `before`)
            return self.send(200, {"items": events.items(db(), dev, str(data.get("now", "")), str(data.get("kind", "all")), data.get("before"), 30)})
        if self.path == "/away/dismiss":  # Part 108: Dismiss or Review hides the card until you are away again
            try:
                memory.setflag(db(), dev, "away_seen", int(data.get("id", 0)))
            except (TypeError, ValueError):
                return self.send(400, {"error": "bad id"})
            return self.send(200, {"ok": True})
        if self.path == "/guest":  # Part 118: is a guest session on (the page shows the badge after a reload)
            return self.send(200, {"on": guest.on(dev)})
        if self.path == "/snooze":  # Part 82: the 10 min button under a reminder
            try:
                t2 = remind.snooze(db(), dev, int(data.get("id") or 0), int(data.get("mins") or 10), str(data.get("now", "")))
            except (TypeError, ValueError):
                t2 = None
            return self.send(200, {"ok": t2 is not None, "at": time.strftime("%H:%M", time.gmtime(t2)) if t2 else ""})
        if self.path == "/followup/answer":  # Part 77: 'ho gaya?' ka jawab. Haan = band, Nahi = 2 ghante baad ek baar phir
            try:
                ok = remind.follow_answer(db(), dev, int(data.get("id") or 0), data.get("yes") is True, str(data.get("now", "")))
            except ValueError:
                ok = False
            return self.send(200, {"ok": ok})
        if self.path == "/brief":  # page din mein ek baar apne aap maangta hai
            return self.send(200, {"text": brief.build(db(), dev, str(data.get("now", "")), data.get("style") == "hindi", bool(data.get("auto")), None, data.get("phone"))})
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
        if self.path == "/note/delete":  # Part 88: the Remove button in the Atlas
            c = db()
            c.execute("DELETE FROM notes WHERE id=? AND device=?", (int(data.get("id") or 0), dev))
            c.commit()
            return self.send(200, {"ok": True})
        if self.path == "/memory/delete":
            c = db()
            c.execute("DELETE FROM memories WHERE id=? AND device=?", (int(data.get("id") or 0), dev))
            c.commit()
            return self.send(200, {"ok": True})
        if self.path == "/voice/set":  # Part 51: save Tony/JARVIS settings in voice.json
            s = voiceengine.save(data)
            s["sarvam_saved"] = bool(getkey("sarvam"))
            return self.send(200, s)
        if self.path == "/voice/key":  # Part 53: Sarvam voice key. Tested with one short sentence, then saved in keys.json (never sent back)
            k = str(data.get("key", "")).strip()
            if not re.fullmatch(r"[A-Za-z0-9_\-]{16,120}", k):
                return self.send(200, {"ok": False, "error": "That does not look like a Sarvam key"})
            try:
                tts.sarvam("Hello sir", k)
            except RuntimeError as e:
                return self.send(200, {"ok": False, "error": str(e)})
            store("sarvam", k)
            return self.send(200, {"ok": True, "masked": mask(k)})
        if self.path == "/voice/key/delete":
            store("sarvam", "")
            voiceengine.save({"provider": "edge"})
            return self.send(200, {"ok": True})
        if self.path == "/tts":  # Part 7: neural awaaz. Part 51: intent se awaaz. Part 53: Sarvam pehle (agar chuna ho), na chale to Edge
            txt, mime, eng = str(data.get("text", "")), "audio/mpeg", "edge"
            try:
                if data.get("voice"):
                    audio, who = tts.speak(txt, str(data.get("voice", "")), data.get("pitch", -8), data.get("rate", -6)), "classic"
                else:
                    v = voiceengine.pick(txt, str(data.get("intent", "")), str(data.get("profile", "")), "english" if data.get("lang") == "english" else "hindi")
                    who, audio = v["profile"], None
                    if v["provider"] == "sarvam":  # Part 71: both personalities use Sarvam, each with its own speaker
                        try:
                            audio, mime, eng = tts.sarvam(txt, getkey("sarvam"), v["speaker"], "english" if data.get("lang") == "english" else "hindi", v["rate"]), "audio/wav", "sarvam"
                        except RuntimeError as e:
                            eng = "edge-fallback"
                            self.log_message("Sarvam failed: %s", e)
                    if audio is None:
                        audio = tts.speak(txt, v["voice"], v["pitch"], v["rate"])
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            self.send_response(200)
            self.send_header("X-Voice", who)
            self.send_header("X-Engine", eng)
            self.send_header("X-Distinct", "no" if (not data.get("voice") and eng != "sarvam" and not v["distinct"]) else "yes")  # "no" = Tony and JARVIS are the same voice with pitch/speed only
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(audio)))
            self.end_headers()
            return self.wfile.write(audio)
        if self.path == "/see":
            try:
                ans, via = see.look(data.get("image"), data.get("question"), data.get("style") == "hindi", PROVIDERS, getkey, names())
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            if not guest.on(dev):  # Part 118: a guest photo answer is not saved
                c = db()
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", "(photo) " + ans, time.time()))
                c.commit()
            return self.send(200, {"reply": ans, "via": via})
        if self.path == "/chat":
            msg = str(data.get("message", "")).strip()
            if not msg or len(msg) > 4000:
                return self.send(400, {"error": "message khali ya bahut bada"})
            hi = str(data.get("style", "")) == "hindi"
            g = guest.command(dev, msg, hi)  # Part 118: guest session words. Checked BEFORE anything is saved
            if g is not None:
                return self.send(200, {"reply": g[0], "via": "guest", "guest": g[1]})
            if guest.on(dev):  # guest turn: no database, no memory, no phone action, no web; RAM only, numbers masked
                a = assist.handle(msg, hi, ask, str(data.get("now", "")), guest.mask, guest.RULE)  # Part 119: translate / explain / plan / reliable info, still RAM only
                if a is not None:
                    guest.add(dev, "user", guest.mask(msg))
                    guest.add(dev, "assistant", a)
                    return self.send(200, {"reply": a, "via": "assist", "guest": True})
                try:
                    reply, via = ask(guest.add(dev, "user", guest.mask(msg)), str(data.get("style", "")), guest.RULE)
                except RuntimeError as e:
                    return self.send(502, {"error": str(e)})
                guest.add(dev, "assistant", reply)
                return self.send(200, {"reply": reply, "via": via, "guest": True})
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
            if re.search(r"[\u0900-\u097F]", msg):
                style = "hindi"  # Part 130: you spoke Hindi, so local replies (phone actions, notes, lists) answer in Hindi too
            if len(msg) < 25 and re.match(r"^\s*(?:का|की|के|से|को|पर|में|और|तो)\s+\S+(?:\s+\S+)?\s*$", msg):  # Part 130: a cut-off fragment from the mic gets no AI answer
                frag = "सर, पूरी बात नहीं सुनी, फिर से बोलिए।"
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", frag, time.time()))
                c.commit()
                return self.send(200, {"reply": frag, "via": "memory"})
            mode = str(data.get("mode", "normal"))
            mode = mode if mode in modes.MODES else "normal"
            tmd = modes.timed(msg, style == "hindi")  # Part 100: "meeting mode 45 minute" (the page keeps the clock)
            if tmd:
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", tmd[0], time.time()))
                c.commit()
                return self.send(200, dict({"reply": tmd[0], "via": "memory"}, **({"mode": "quiet", "timed": tmd[1]} if tmd[1] else {})))
            hit = modes.handle(msg, style == "hindi")  # Part 58: "research mode on" (a setting only, the page keeps it)
            if hit:
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", hit[0], time.time()))
                c.commit()
                return self.send(200, {"reply": hit[0], "via": "memory", "mode": hit[1]})
            msg, gnote, gapp = ghost.pre(c, dev, msg, style == "hindi")  # Part 107: "Chrome kholo research ke liye" keeps the reason; the open command goes on without it
            mem = memory.handle(c, dev, msg, style == "hindi")  # yaad rakho / bhool jao / kya yaad hai
            now = str(data.get("now", ""))
            if mem is None:  # Part 89: "sab jagah dhundo Bombay" (same words in notes, memories, people, lists, reminders; reads only, no AI)
                mem = search.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 72: "note karo ...", "meri notes", "notes me bijli dhundo" (saved only on your words, never sent to the AI)
                mem = notes.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 83: "list me doodh add karo", "list dikhao" (own words, never sent to the AI)
                mem = lists.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 83: "habit banao gym", "aaj gym gaya", "my habits" (only habits you made)
                mem = habits.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Parts 110 + 111: "kamai 40000 mahina", "bachat 50000", "paisa picture", "agar job chhod du" (your numbers, plain arithmetic, no AI). Before the expense logger.
                mem = money.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 84: "200 coffee", "kharcha" (what you spent; not the owe/get ledger)
                mem = spend.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 119: "translate to hindi: ...", "explain simply: ...", "make a plan: ...", "reliable info: ..." (fixed words only)
                mem = assist.handle(msg, style == "hindi", ask, now)
            if mem is None:  # Part 91: "red team: yeh phone kharidna hai" (the AI gets only your own Jarvis numbers)
                mem = redteam.handle(c, dev, msg, style == "hindi", ask, now)
            if mem is None:  # Part 105: "sach sawal on", "sach sawal" (one hard question per 14 days; the AI gets only counts and the reply lists them)
                mem = redteam.honest(c, dev, msg, style == "hindi", ask, now)
            if mem is None:  # Part 106: "drift on", "drift dikhao" (word counts of your own chat, no AI)
                mem = drift.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Parts 93 + 94: "sochenge baad mein: ...", "adhoora: ..." (your words only, never sent to the AI)
                mem = decisions.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 96: "mood 3", "mood history", "mood care on" (only when you say it)
                mem = mood.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 95: "ammi track karo", "ammi se baat hui" (only people you pick)
                mem = touch.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Parts 113 + 114: "is jagah ko ghar naam do", "jab ghar pahunchu doodh lena", "jab JBL bluetooth jude ..." (your words only, never sent to the AI; the position stays in the app)
                mem = placenote.handle(c, dev, msg, style == "hindi", data.get("loc"))
            if mem is None:  # Part 102: "thanda karo" (then the WhatsApp command waits 20 seconds with a Continue button)
                mem = actions.cool_cmd(dev, msg, style == "hindi")
            if mem is None:  # Part 97: "6 mahine baad yeh sunana: ...", "my capsules", "open capsule 3" (your words only, never sent to the AI)
                mem = capsule.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 103: "sapna: ...", "sapne dikhao", "sapne ka matlab" (only that one dream goes to the AI, and only when you ask)
                mem = dreams.handle(c, dev, msg, style == "hindi", now, ask)
            if mem is None:  # Part 104: "sign: 11:11 dekha", "signs dikhao" (only counts what you type)
                mem = signs.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 101: "body double 45 minute" / "body double stop"
                mem = modes.bd_command(dev, msg, style == "hindi", now)
            if mem is None:  # Part 92: "debate stop" ends it; "debate ruthless: ..." switches it on and the AI answers below
                mem = debate.command(dev, msg, style == "hindi")
            if mem is None:  # Part 109: "timeline", "timeline notes" (reads what Jarvis already keeps, no AI)
                mem = events.handle(c, dev, msg, style == "hindi", now)
            if mem is None:  # Part 107: "ghost dikhao", "ghost bhool jao"
                mem = ghost.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 83: "day report 9 baje" (the time at which the page offers a one-tap day summary)
                mem = tasks.report(c, dev, msg, style == "hindi")
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
                mem = brief.handle(c, dev, msg, style == "hindi", now, data.get("cal"), data.get("phone"))
            if mem is None:  # hisab: "Faisal ko 5000 dene hain"
                mem = ledger.handle(c, dev, msg, style == "hindi", ask, now)
            if mem is None:  # reminder: "kal 9 baje chai yaad dilana"
                mem = remind.handle(c, dev, msg, style == "hindi", ask, now)
            if mem is None:  # Part 117: "last update", "kya kya add hua" (from the zips on this phone and the README, no AI)
                mem = whatsnew.handle(msg, style == "hindi", sync_note())
            if mem is None:  # "app ka kaam kahan tak pahuncha" / "mission": three honest counts read from the README (Part 87)
                mem = progress.handle(msg, style == "hindi")
            action = None
            if mem is None:  # Part 30: "WhatsApp kholo" (only proposes; the app checks the switch and Stop)
                got = tasks.routine(c, dev, msg, style == "hindi", data.get("control") is True, data.get("app") is True) or tasks.make(c, dev, msg, style == "hindi", data.get("control") is True, data.get("app") is True) or actions.handle(msg, style == "hindi", data.get("control") is True, data.get("app") is True, ask)  # Part 41: several steps in one sentence become one task
                if got:
                    mem, action = got
            gq = ghost.ask(c, dev, action, gapp) if mem is not None else None  # Part 107: the saved reason, asked once
            if mem is not None and gnote and action:
                mem += "\n" + gnote
            if mem is not None:
                keep = "(call, contact and calendar info was shown, not saved)" if calls.private(msg) else mem
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", keep, time.time()))
                c.commit()
                cl = actions.cool_take(dev, action)  # Part 102: asked once, because it uses the switch up
                return self.send(200, dict({"reply": mem, "via": "memory"}, **({"action": action} if action else {}), **({"cool": cl} if cl else {}), **({"ghost": gq} if gq else {}), **({"pw": pwc} if (pwc := placenote.take(c, dev)) else {})))
            rows = c.execute("SELECT role, content, ts FROM messages WHERE device=? ORDER BY id DESC LIMIT 20", (dev,)).fetchall()  # Part 126: 20 turns, not 10
            tctx = clock.context([(r, t) for r, _, t in reversed(rows)], prev_ts)
            wtxt, srcs = web.lookup(msg, now, mode == "research" and len(msg) >= 8 and not screen.used(data.get("screen")))  # Part 57: in Research mode every question is searched
            try:
                reply, via = ask([{"role": r, "content": t} for r, t, _ in reversed(rows)], style, CAN + tctx + memory.context(c, dev) + people.context(c, dev, msg) + place.context(msg, data.get("loc")) + screen.context(data.get("screen")) + replyideas.context(data.get("notif")) + wtxt + MOOD + debate.extra(dev) + modes.extra(mode))
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            if srcs:  # the list of sites comes from the real search result, not from the AI
                reply += ("\n\nस्रोत: " if style == "hindi" else "\n\nSources: ") + ", ".join(srcs) + "\n" + web.label(srcs, style == "hindi")  # Part 90
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", "(answer about your screen was shown, not saved)" if screen.used(data.get("screen")) else "(reply ideas were shown, not saved)" if replyideas.used(data.get("notif")) else reply, time.time()))
            c.commit()
            sug = None if screen.used(data.get("screen")) or replyideas.used(data.get("notif")) else memory.suggest(msg)  # Part 54: only an offer, nothing is saved here
            return self.send(200, dict({"reply": reply, "via": via}, **({"remember": sug} if sug else {}), **({"debate": debate.label(dev)} if debate.label(dev) else {})))
        self.send(404, {"error": "not found"})


if __name__ == "__main__":
    load_env()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8787"))
    autostart.ensure(os.path.dirname(HERE))
    autostart.refresh_scripts(os.path.dirname(HERE))
    autostart.move_strays(os.path.dirname(HERE))  # Part 119: one-time cleanup of files that older zips left in the repo root
    try:
        srv = ThreadingHTTPServer((host, port), H)  # Part 131: bind FIRST, so a busy port stops here with one clear line (no traceback, no new pairing code every 5 seconds)
    except OSError as e:
        print(f"[app] port {port} is busy ({e.strerror}): an old Jarvis is still running. run.sh stops it by itself; by hand: pkill -f backend/app.py", flush=True)
        raise SystemExit(98)
    new_code()
    tasks.restart(db())  # Part 41 restart rule: a task that was RUNNING before this start is FAILED now
    print(f"Jarvis chal raha hai: http://{host}:{port}  provider={','.join(names())}", flush=True)
    srv.serve_forever()
