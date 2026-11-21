"""Jarvis backend - Part 1: chat + pairing + SQLite. Sirf Python stdlib, pip install nahi chahiye."""
import hashlib, json, os, re, secrets, socket, sqlite3, threading, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import actions, appnames, assist, attach, autolearn, autostart, backup, brief, calls, capsule, chathist, chatsum, clock, cutoff, debate, decisions, deep, dreams, drift, events, ghost, guest, habits, handoff, learn, ledger, lens, lists, memory, modes, money, mood, notes, nudge, people, phone, phonetest, place, placenote, progress, redteam, remind, replyideas, screen, search, see, signs, spend, sysinfo, tasks, touch, tts, unknown, voiceengine, voices, web, whatsnew

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


def own(c):
    """Part 138: chat and data belong to the owner, not to one pairing. Old extra devices are folded into the oldest one once."""
    if "owner" in [r[1] for r in c.execute("PRAGMA table_info(devices)")]:
        return
    try:
        c.execute("ALTER TABLE devices ADD COLUMN owner INT")
    except sqlite3.OperationalError:
        return  # another request just did it
    ids = [r[0] for r in c.execute("SELECT id FROM devices ORDER BY id")]
    if ids:
        for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            if "device" not in [r[1] for r in c.execute(f'PRAGMA table_info("{t}")')]:
                continue
            for old in ids[1:]:
                try:
                    c.execute(f'UPDATE "{t}" SET device=? WHERE device=?', (ids[0], old))
                except sqlite3.Error:
                    pass  # a table with one row per device keeps the older row
        c.execute("UPDATE devices SET owner=?", (ids[0],))
    c.commit()


_bg = threading.Lock()


def after_chat(dev):
    """Part 158: fold older chat into a short summary. Part 155: every 8th chat pick up facts. Runs in the background, one at a time, and never raises."""
    if not _bg.acquire(False):
        return
    c = None
    try:
        c = db()
        chatsum.update(c, dev, ask)
        autolearn.note(c, dev, ask)
    except Exception:
        pass
    finally:
        if c is not None:
            c.close()
        _bg.release()


def db():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS devices(id INTEGER PRIMARY KEY, name TEXT, token_hash TEXT UNIQUE, ts REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, device INT, role TEXT, content TEXT, ts REAL)")
    memory.init(c)
    notes.init(c)  # Part 71/72: voice notes (same database, one table)
    people.init(c)
    voices.init(c)  # Part 144: voice prints (numbers only)
    appnames.init(c)  # Part 201: app names of the phone (names only)
    remind.init(c)
    ledger.init(c)
    lists.init(c)  # Part 83: shopping and packing lists
    habits.init(c)  # Part 83: habit and streak tracker
    learn.init(c)  # Part 143: what Jarvis learned (counts only)
    chatsum.init(c)  # Part 158: short summary of older chat
    autolearn.init(c)  # Part 155: facts picked up from what you say
    nudge.init(c)  # Part 157: answers to Jarvis's offers
    unknown.init(c)  # Part 146: sentences it could not understand
    phonetest.init(c)  # Part 136: Table A answers (pass / fail / skip, date, note)
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
    own(c)  # Part 138
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


LAST = {"ai": "", "cool": {}}  # Part 195: the provider that answered last, and providers resting after error 429 (name -> until when)


def names():
    env = [n.strip().lower() for n in os.environ.get("PROVIDER", "").split(",") if n.strip()]
    if env:
        return env  # an order you wrote in PROVIDER is kept
    ns = [n for n in [*PROVIDERS, "mock"] if getkey(n)]
    if LAST["ai"] in ns:  # Part 195: the one that worked last goes first
        ns.remove(LAST["ai"])
        ns.insert(0, LAST["ai"])
    return ns


def ai_busy():
    """Part 194: True when every saved AI key is resting after error 429 (about 60 seconds)."""
    real = [n for n in names() if n != "mock"]
    return bool(real) and all(LAST["cool"].get(n, 0) > time.time() for n in real)


def ask_cmd(*a, **k):
    """Part 194: a phone command never waits for an AI that is at its limit. The grammar needs no AI; only an unclear sentence asks the AI for an app name."""
    if ai_busy():
        raise RuntimeError("AI is resting")
    return ask(*a, **k)


def voice_state():
    """Part 197 and 198: everything the Sarvam card shows."""
    m = tts.meter()
    n, mb = tts.cache_info()
    return {"ok": True, "used": m["used"], "limit": m["limit"], "pct": tts.pct(m), "silent": m["silent"], "short": m["short"], "edge": bool(m.get("edge")), "files": n, "mb": mb, "warm": dict(tts.WARM)}


WARM_CMDS = ["home jao", "peeche jao", "neeche scroll karo", "upar scroll karo", "scroll ruko", "minimize karo", "phone lock karo", "torch on karo"]
WARM_APPS = ["YouTube", "WhatsApp", "Chrome", "Camera", "Instagram", "Gmail", "Maps", "Settings", "Calculator", "Clock", "Phone", "Messages"]
WARM_FIXED = ["Good morning, sir. How can I help you?", "Good afternoon, sir. How can I help you?", "Good evening, sir. How can I help you?", "Good night, sir. How can I help you?",
              "Yes, sir?", "I am listening, sir.", "Done, sir.", "Sorry sir, I did not catch that. Could you say it again?",
              "सर, मैं आपके लिए हमेशा यहाँ हूँ।", "जी सर?", "ठीक है सर।", "सर, मैं सुन रहा हूँ।", "सर, माफ़ कीजिए, मैं समझ नहीं पाया। क्या आप फिर से कह सकते हैं?"]


def warm_jobs():
    """Part 197: the sentences Jarvis says all day, in both languages, for Tony and JARVIS. Only the ones not saved yet are made."""
    def no_ai(*a, **k):
        raise RuntimeError("no AI")
    lines = list(WARM_FIXED)
    for hindi in (True, False):
        for c in WARM_CMDS:
            try:
                got = actions.handle(c, hindi, True, True, no_ai)
            except Exception:
                got = None
            if got and got[0]:
                lines.append(got[0])
    for x in WARM_APPS:
        lines += [f"Opening {x}, sir.", f"ठीक है सर, {x} खोल रहा हूँ।"]
    jobs, seen = [], set()
    for line in lines:
        lang = "hindi" if re.search(r"[\u0900-\u097F]", line) else "english"
        for prof in ("tony", "jarvis"):
            v = voiceengine.pick(line, "", prof, lang)
            if v["provider"] != "sarvam":
                return []
            key = (line, v["speaker"], lang, v["rate"])
            if key not in seen and not tts.cached(*key):
                seen.add(key)
                jobs.append(key)
    return jobs


def limit_msg(style, errs):
    wait = max([int(LAST["cool"].get(n, 0) - time.time()) for n in names()] + [0])
    tail = " | ".join(errs)
    if style == "hindi":
        return "सर, आपकी सारी AI key की free limit अभी पूरी है। एक मिनट रुकिए या Settings में एक और key डालिए। (" + tail + ")"
    return "Sir, every AI key is at its limit right now" + (f" (about {wait} seconds to wait)" if wait > 0 else "") + ". Wait a minute or add one more key in Settings. (" + tail + ")"


OFFLINE = "No internet right now, so I cannot answer this one. Phone commands, notes, lists, reminders and habits still work."  # Part 170
OFFLINE_HI = "सर, अभी इंटरनेट नहीं है, इसलिए इसका जवाब नहीं दे सकता। फ़ोन कमांड, नोट्स, लिस्ट, रिमाइंडर और आदतें चलती हैं।"
NET = {"at": 0.0, "up": True, "ai": 0.0}  # Part 170: last check time, last result, last time an AI call worked


def online():
    """Part 170: a quick yes/no (cached 20 s) so nothing waits 60 s for the internet. A working AI call in the last 2 minutes counts as online."""
    now = time.time()
    if now - NET["ai"] < 120:
        return True
    if now - NET["at"] < 20:
        return NET["up"]
    up = False
    for host in ("1.1.1.1", "8.8.8.8"):
        try:
            socket.create_connection((host, 53), timeout=1.2).close()
            up = True
            break
        except OSError:
            pass
    NET["at"], NET["up"] = now, up
    return up


def lookup_safe(*a):
    """Part 170: the internet lookup is skipped when the phone is offline."""
    return web.lookup(*a) if online() else ("", [])


def call(name, history, key=None, style="english", extra="", full=False):
    if name == "mock":  # sirf testing ke liye
        return "mock jawab: " + history[-1]["content"]
    base, key_env, model = PROVIDERS[name]
    key = key or getkey(name)
    system = (deep.DEEP.get(style, deep.DEEP["english"]) if full else PERSONA.get(style, SYSTEM)) + extra  # Part 169: a full answer uses its own prompt
    payload = {"model": os.environ.get("MODEL_" + name.upper()) or model, "messages": [{"role": "system", "content": system}] + history}
    if full:
        payload["max_tokens"] = 3000
    body = json.dumps(payload).encode()
    req = urllib.request.Request(base + "/chat/completions", body, {
        "Authorization": "Bearer " + key, "Content-Type": "application/json", "User-Agent": "jarvis/0.1"})
    for tries in (0, 1):  # Part 185: a busy or limited answer (429, 503) gets ONE more try after a short wait, then the next provider
        try:
            with urllib.request.urlopen(req, timeout=120 if full else 60) as r:
                return json.load(r)["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            raw = e.read()[:150].decode(errors="ignore")
            if e.code in (429, 503) and tries == 0:
                try:
                    wait = min(4, max(1, int(e.headers.get("Retry-After", "2"))))
                except (TypeError, ValueError):
                    wait = 2
                time.sleep(wait)
                continue
            raise RuntimeError(nice_err(e.code, raw))
        except Exception as e:
            raise RuntimeError("connect nahi hua: " + type(e).__name__)


def nice_err(code, raw):
    """Part 185: one plain sentence for the usual HTTP errors. The start stays 'error CODE:' so older code that reads it still works."""
    why = {429: "this key is at its limit (free quota or too many requests). Wait a minute or add another key",
           402: "this key has no credit left",
           401: "this key is not accepted", 403: "this key is not accepted",
           500: "the AI service has a problem, try again later", 502: "the AI service has a problem, try again later",
           503: "the AI service is busy, try again in a minute"}.get(code)
    return f"error {code}: {why}" if why else f"error {code}: {raw}"


def check(n, k):
    try:
        call(n, [{"role": "user", "content": "Ek shabd mein jawab do: OK"}], k)
    except RuntimeError as e:
        return str(e)


CAN = ("\n\nWHAT JARVIS CAN DO (the app does these when Hussain's words fit, not you): open any app; scroll, click, back and home on the open app; call or dial a contact by name; alarm and timer; reminders; notes, lists, habits, expenses; read the screen when asked; look at a photo; search the internet BY ITSELF for live questions (price, news, score, weather) and when he says: net par search karke batao. "
       "You DO have internet: when a block named INTERNET SE MILA TEXT is below, answer from it. Never say you have no permission to search. If a live question has no such block, the lookup failed: say so in one sentence and tell him to say: search karo <topic>. "
       "WHAT IT CANNOT DO: see inside another app's private data (like a trading watch list) unless it is on the screen, send a message or pay without his tap, or guess news. "
       "If he asks for something from the CAN list, never say you cannot: tell him the exact short words to say, for example: Ammi ko call karo, or: Chrome kholo aur neeche scroll karo. "
       "Use the earlier messages to understand words like usko, wahi, isko, that, it.")  # Part 126
CAN += (" Never write the label '(phone action)'. Never say you switched, opened, turned on or changed something on the phone yourself: only the app does that, and only when the user's words match a command. "
        "If he asks for such a thing and no action ran, say so plainly and give the exact short words to say, for example: torch chalu karo.")


FAKE = re.compile(r"\(phone action\)|\b(?:switch|turn|open|launch|call|dial|scroll|click)(?:ed|ing)\b|\bgoing to\b|kar diya|kar di\b|khol diya|ja raha|jaa raha|कर दिया|कर दी|खोल दिया|खोल रहा|जा रहा|कर रहा", re.I)
THING = re.compile(r"torch|flash ?light|wi-?fi|bluetooth|volume|brightness|alarm|timer|home|screen|chrome|youtube|whatsapp|\bapp\b|\bcall|scroll|टॉर्च|वाईफाई|ब्लूटूथ|वॉल्यूम|अलार्म|टाइमर|होम|स्क्रीन|ऐप|कॉल|स्क्रॉल", re.I)


TICKS = re.compile(r"^[\s\u2714\u2716\u2705\u274c\u2713\u2717\u2611\ufe0f]+")


def untick(reply):
    """Part 147: a tick or cross at the start of a short answer may only come from the phone's own result (the page adds it). The AI or the server never writes one there."""
    return TICKS.sub("", reply) if isinstance(reply, str) and len(reply) <= 240 else reply


def honest(reply, style):
    """Part 138: this runs only when NO phone action ran. A short AI answer that says it did a phone thing is a lie, so it is replaced."""
    if len(reply) > 240 or not (FAKE.search(reply) and (THING.search(reply) or "(phone action)" in reply)):
        return reply
    if style == "hindi":
        return "सर, मैंने फ़ोन पर कुछ नहीं किया, कोई एक्शन चला ही नहीं। छोटे शब्द बोलिए, जैसे: टॉर्च चालू करो, होम जाओ, क्रोम खोलो।"
    return "Sir, I did nothing on the phone: no action ran. Say the short words, for example: torch chalu karo, home jao, or Chrome kholo."


def ask(history, style="english", extra="", full=False):
    """PROVIDER=groq,openrouter,... : pehla jo chale uska jawab. Return (jawab, provider)."""
    errs = []
    if "mock" not in names() and not online():
        raise RuntimeError(OFFLINE)  # Part 170: one clear line at once, no 60 second wait
    order = names()
    rest = [n for n in order if LAST["cool"].get(n, 0) > time.time()]  # Part 195: a key that just said 429 goes to the end of the line for 60 seconds
    if rest and len(rest) == len(order) and "mock" not in order:
        raise RuntimeError(limit_msg(style, [f"{n}: error 429: resting" for n in rest]))  # all of them are resting: answer at once, no waiting
    for n in [x for x in order if x not in rest] + rest:
        if n != "mock" and n not in PROVIDERS:
            errs.append(f"{n}: naam galat")
        elif n != "mock" and not getkey(n):
            errs.append(f"{n}: key nahi")
        else:
            try:
                out = call(n, history, None, style, extra, full)
                NET["ai"] = time.time()  # Part 170
                LAST["ai"] = n  # Part 195
                return out, n
            except RuntimeError as e:
                errs.append(f"{n}: {e}")
                if "error 429" in str(e):
                    LAST["cool"][n] = time.time() + 60
    if errs and all("error 429" in e for e in errs):  # Part 185: every key is at its limit
        raise RuntimeError(limit_msg(style, errs))
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
        row = db().execute("SELECT COALESCE(owner, id) FROM devices WHERE token_hash=?",
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
            return self.send(200, {"ok": True, "provider": ",".join(names()), "configured": ok, "offline": not online(), "boot": BOOT, "sync": sync_note(), "uptime": int(time.time()) - int(BOOT)})
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
        data = self.body(1500000 if self.path in ("/see", "/lookat", "/attach") and self.headers.get("Authorization") else 60000 if self.path == "/chat" and self.headers.get("Authorization") else 20000)  # Parts 168 + 169
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
            first = c.execute("SELECT MIN(COALESCE(owner, id)) FROM devices").fetchone()[0]  # Part 138: a new pairing joins the owner, so the chat is not empty again
            c.execute("INSERT INTO devices(name, token_hash, ts, owner) VALUES(?,?,?,?)",
                      (str(data.get("name", "phone"))[:40], hashlib.sha256(token.encode()).hexdigest(), time.time(), first))
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
        if self.path == "/learn":  # Part 143: the \"What Jarvis learned\" card and the one offer for this hour (reading only)
            c = db()
            return self.send(200, {"on": learn.is_on(c, dev), "items": learn.rows(c, dev), "suggest": learn.suggest(c, dev) or nudge.suggest(c, dev),  # Part 157: more offers
                                   "facts": [{"id": i, "text": t} for i, t in autolearn.saved(c, dev)], "today": autolearn.today(c, dev), "facts_on": autolearn.is_on(c, dev)})  # Part 156: facts picked up, and the last 24 hours
        if self.path == "/learn/act":  # Part 143: Keep, Delete, or the answer to an offer (yes / later)
            wh, i = str(data.get("act")), data.get("id")
            if isinstance(i, int) and wh == "fact_delete":  # Part 156: one picked-up fact
                autolearn.forget(db(), dev, i)
            elif isinstance(i, int) and i < 0 and wh in ("yes", "later", "never"):  # Part 157: an offer from nudge.py (its ids are negative)
                nudge.act(db(), dev, i, wh)
            elif isinstance(i, int) and i >= 0 and wh in ("keep", "delete", "yes", "later"):
                learn.act(db(), dev, i, wh)
            return self.send(200, {"ok": True})
        if self.path == "/unknown":  # Part 146: the list for Settings > Your Data (reading only)
            c = db()
            return self.send(200, {"on": unknown.is_on(c, dev), "items": unknown.rows(c, dev)})
        if self.path == "/unknown/act":  # Part 146: Teach, Forget or Delete one sentence
            if str(data.get("act")) in ("teach", "forget", "delete") and isinstance(data.get("id"), int):
                unknown.act(db(), dev, data["id"], str(data["act"]))
            return self.send(200, {"ok": True})
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
            return self.send(200, {"reminders": remind.today(c, dev, now), "ledger": led, "birthdays": bd, "notes": nts, "routines": tasks.scheduled(c, dev), "lens": lens.build(c, dev, now, data.get("phone"), str(data.get("lens") or "all")), "mission": progress.mission(c, dev), "away": brief.away(c, dev, now, data.get("phone"), False)})  # Part 108: card after 6+ hours away  # Part 85/86: next best move card and Now/Next/Later strip
        if self.path == "/timeline":  # Part 109: the Timeline tab (filter + "More" with `before`)
            return self.send(200, {"items": events.items(db(), dev, str(data.get("now", "")), str(data.get("kind", "all")), data.get("before"), 30)})
        if self.path == "/away/dismiss":  # Part 108: Dismiss or Review hides the card until you are away again
            try:
                memory.setflag(db(), dev, "away_seen", int(data.get("id", 0)))
            except (TypeError, ValueError):
                return self.send(400, {"error": "bad id"})
            return self.send(200, {"ok": True})
        if self.path == "/appnames":  # Part 201: the page sends the launcher app names when the list changed (names only, never sent to the AI)
            if data.get("names") is not None:
                n = appnames.save(db(), dev, data.get("names"))
                return self.send(200, {"ok": n is not None, "n": n or 0})
            return self.send(200, {"n": len(appnames.load(db(), dev))})
        if self.path == "/voices":  # Part 144: names of the voices Jarvis knows (never the numbers)
            return self.send(200, {"voices": voices.rows(db(), dev), "guest": guest.on(dev)})
        if self.path == "/voices/match":  # Part 144: who spoke? The page sends the 128 voice numbers; nothing is saved here
            return self.send(200, {"state": "guest"} if guest.on(dev) else voices.match(db(), dev, data.get("vec")))
        if self.path == "/voices/limit":  # Part 192: how strict the voice match is (1 strict, 2 normal, 3 loose); no level = just tell the current one
            if data.get("level") is not None:
                try:
                    voices.set_level(db(), dev, int(data.get("level")))
                except (TypeError, ValueError):
                    return self.send(400, {"error": "bad level"})
            return self.send(200, {"level": voices.level(db(), dev)})
        if self.path == "/voices/save":  # Part 144: only after a yes. Refused in a guest session
            if guest.on(dev):
                return self.send(200, {"ok": False, "why": "guest session: nothing is saved"})
            ok = voices.save(db(), dev, str(data.get("name", "")), data.get("vec"), data.get("owner") is True, str(data.get("note", "")))
            return self.send(200, {"ok": ok is True, "why": "" if ok is True else ok})
        if self.path == "/hist":  # Part 174: all saved messages by day, or a word search over them (reading only)
            return self.send(200, chathist.query(db(), dev, data))
        if self.path == "/tablea":  # Part 177: the phone-test checklist screen (same table as the chat words `table a pass 12`)
            return self.send(200, phonetest.api(db(), dev, data))
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
        if self.path == "/voice/meter":  # Part 198: the numbers, and your limit and two switches
            if any(k in data for k in ("limit", "silent", "short", "edge")):
                try:
                    tts.meter_set(data.get("limit"), data.get("silent"), data.get("short"), data.get("edge"))
                except (TypeError, ValueError):
                    return self.send(200, {"ok": False, "error": "That is not a number"})
            return self.send(200, voice_state())
        if self.path == "/voice/warm":  # Part 197: make and save the common lines once (uses Sarvam credit one time)
            k = getkey("sarvam")
            if not k:
                return self.send(200, {"ok": False, "error": "Add your Sarvam key first"})
            if not tts.WARM["running"]:
                jobs = warm_jobs()
                if not jobs:
                    return self.send(200, {"ok": False, "error": "Choose the Sarvam voice first"})
                tts.warm_start(k, jobs)
            return self.send(200, voice_state())
        if self.path == "/tts":  # Part 7: neural awaaz. Part 51: intent se awaaz. Part 53: Sarvam pehle (agar chuna ho), na chale to Edge
            txt, mime, eng = str(data.get("text", "")), "audio/mpeg", "edge"
            if tts.meter()["short"] and not data.get("voice"):
                txt = tts.first_sentences(txt)  # Part 198: long replies speak only their first 2 sentences
            try:
                if data.get("voice"):
                    audio, who = tts.speak(txt, str(data.get("voice", "")), data.get("pitch", -8), data.get("rate", -6)), "classic"
                else:
                    v = voiceengine.pick(txt, str(data.get("intent", "")), str(data.get("profile", "")), "english" if data.get("lang") == "english" else "hindi")
                    who, audio = v["profile"], None
                    if v["provider"] == "sarvam":  # Part 71: both personalities use Sarvam, each with its own speaker
                        try:
                            audio, was = tts.sarvam_cached(txt, getkey("sarvam"), v["speaker"], "english" if data.get("lang") == "english" else "hindi", v["rate"])  # Part 197: saved audio first
                            mime, eng = "audio/wav", "sarvam-saved" if was else "sarvam"
                        except RuntimeError as e:
                            if tts.meter()["silent"]:  # Part 198: Sarvam voice or silence, never the Edge voice
                                return self.send(502, {"error": "Sarvam voice is not available (" + str(e) + "). Text only.", "silent": True})
                            self.log_message("Sarvam failed: %s", e)
                            if not tts.meter().get("edge"):  # Part 193: the Edge voice only if you allowed it; otherwise the phone speaks (the page asks Android for its own voice)
                                return self.send(502, {"error": "Sarvam voice is not available (" + str(e) + ")", "phone": True})
                            eng = "edge-fallback"
                    if audio is None:
                        audio = tts.speak(txt, v["voice"], v["pitch"], v["rate"])
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            self.send_response(200)
            self.send_header("X-Voice", who)
            self.send_header("X-Engine", eng)
            self.send_header("X-Sarvam-Pct", str(tts.pct(tts.meter())) if eng.startswith("sarvam") else "0")  # Part 198
            self.send_header("X-Distinct", "no" if (not data.get("voice") and not eng.startswith("sarvam") and not v["distinct"]) else "yes")  # "no" = Tony and JARVIS are the same voice with pitch/speed only
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(audio)))
            self.end_headers()
            return self.wfile.write(audio)
        if self.path == "/lookat":  # Part 129: where is the thing on the screen picture. Nothing is saved, nothing is tapped here
            try:
                res, via = see.locate(data.get("image"), data.get("target"), PROVIDERS, getkey, names())
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            return self.send(200, dict(res, via=via))
        if self.path == "/attach":  # Part 168: one file from the paperclip (text, code, PDF, Word, image). RAM only; never saved as a file
            if guest.on(dev):
                return self.send(400, {"error": "Attachments are off in a guest session."})
            q, nm, kind = str(data.get("question", "")).strip()[:600], attach.clean(data.get("name")), str(data.get("kind", ""))
            try:
                if kind == "image":
                    ans, via = see.look(data.get("data"), q, data.get("style") == "hindi", PROVIDERS, getkey, names(), True)
                else:
                    ans, via = attach.answer(dev, nm, kind, data.get("data"), q, str(data.get("style", "")), ask)
            except RuntimeError as e:
                return self.send(502, {"error": str(e)})
            c = db()
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "user", "(file) " + nm + (": " + q if q else ""), time.time()))
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", ans, time.time()))
            c.commit()
            return self.send(200, {"reply": ans, "via": via, "deep": True})
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
            if not msg or len(msg) > 12000:  # Part 169: pasted code is allowed
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
                reply = untick(honest(reply, str(data.get("style", ""))))  # Part 138 + 147
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
                chatsum.wipe(c, dev)  # Part 158: the short summary of the old chat goes too
                attach.clear(dev)  # Part 168: and the file you sent
                return self.send(200, {"reply": "Okay sir, the chat history and its short summary are deleted. Saved memories, people and reminders are not touched.", "via": "memory"})
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
            msg = unknown.expand(c, dev, msg)  # Part 146: a sentence you taught becomes its plain command (all the normal checks still run)
            mem = actions.probe(msg, style == "hindi")  # Part 145: "samjha: <sentence>" shows what Jarvis understood, does nothing
            if mem is None:  # Part 136: "table a next", "table a pass 12" (your test answers; nothing runs on the phone)
                mem = phonetest.handle(c, dev, msg, style == "hindi")
            if mem is None:
                mem = memory.handle(c, dev, msg, style == "hindi")  # yaad rakho / bhool jao / kya yaad hai
            now = str(data.get("now", ""))
            if mem is None:  # Part 89: "sab jagah dhundo Bombay" (same words in notes, memories, people, lists, reminders; reads only, no AI)
                mem = search.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 72: "note karo ...", "meri notes", "notes me bijli dhundo" (saved only on your words, never sent to the AI)
                mem = notes.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 83: "list me doodh add karo", "list dikhao" (own words, never sent to the AI)
                mem = lists.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 143: "seekha dikhao", "seekhna band karo", "seekha bhool jao" (counts only, never your words)
                mem = learn.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 155: "kya samjha", "galat hai #3", "auto seekhna band karo", "auto seekha bhool jao" (facts picked up from your words)
                mem = autolearn.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 157: "sujhav band karo" / "sujhav chalu karo" (Jarvis only asks, never acts alone)
                mem = nudge.handle(c, dev, msg, style == "hindi")
            if mem is None:  # Part 146: "unknown dikhao", "unknown teach 2", "unknown band karo", "unknown saaf karo" (the sentence only, never the AI)
                mem = unknown.handle(c, dev, msg, style == "hindi")
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
            if mem is None:  # Part 144: known voices list / awaaz bhoolo (the voice check itself is started by the page)
                mem = voices.handle(c, dev, msg, style == "hindi")
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
                mem = progress.handle(msg, style == "hindi", c, dev)
            action = None
            teach_off = None  # Part 165
            if mem is None:  # Part 30: "WhatsApp kholo" (only proposes; the app checks the switch and Stop)
                actions.set_apps(appnames.load(c, dev))  # Part 201
                got = tasks.routine(c, dev, msg, style == "hindi", data.get("control") is True, data.get("app") is True) or tasks.make(c, dev, msg, style == "hindi", data.get("control") is True, data.get("app") is True) or actions.handle(msg, style == "hindi", data.get("control") is True, data.get("app") is True, ask_cmd)  # Part 41: several steps in one sentence become one task
                if got:
                    mem, action = got
                    learn.note(c, dev, action)  # Part 143: one more count for this call or app, in this hour
                    teach_off = unknown.pair(c, dev, msg, action)  # Parts 146 + 165: this clear command may be what the last unclear sentence meant
            gq = ghost.ask(c, dev, action, gapp) if mem is not None else None  # Part 107: the saved reason, asked once
            if mem is not None and gnote and action:
                mem += "\n" + gnote
            if mem is not None:
                keep = "(call, contact and calendar info was shown, not saved)" if calls.private(msg) else mem
                c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", keep, time.time()))
                c.commit()
                cl = actions.cool_take(dev, action)  # Part 102: asked once, because it uses the switch up
                return self.send(200, dict({"reply": mem, "via": "memory"}, **({"action": action} if action else {}), **({"cool": cl} if cl else {}), **({"ghost": gq} if gq else {}), **({"teach": teach_off} if teach_off else {}), **({"pw": pwc} if (pwc := placenote.take(c, dev)) else {}), **({"tablea": tq} if (tq := phonetest.take(dev)) else {})))
            unknown.note(c, dev, msg, data.get("app") is True)  # Part 146: no command matched and it goes to the AI, so the sentence is kept for you to teach
            rows = c.execute("SELECT role, content, ts FROM messages WHERE device=? ORDER BY id DESC LIMIT 20", (dev,)).fetchall()  # Part 126: 20 turns, not 10
            rows = deep.trim([x for x in rows if not (x[0] == "assistant" and x[1].startswith("(phone action)"))])  # Part 169: old long answers are cut  # Part 138: the AI must not copy an old fake label
            tctx = clock.context([(r, t) for r, _, t in reversed(rows)], prev_ts)
            prev_q = next((x[1] for x in rows[1:] if x[0] == "user"), "")  # Part 153: the question before this one ("net par search karke batana" means that one)
            wtxt, srcs = lookup_safe(msg, now, mode == "research" and len(msg) >= 8 and not screen.used(data.get("screen")), data.get("webauto") is not False and not screen.used(data.get("screen")), prev_q)  # Part 57 + 153: Research mode searches everything; live questions (price, news, score, weather) are searched by themselves
            full = deep.wants(msg, data.get("deep"))  # Part 169: code, audit, long question: one full answer
            try:
                reply, via = ask([{"role": r, "content": t} for r, t, _ in reversed(rows)], style, CAN + tctx + memory.context(c, dev) + people.context(c, dev, msg) + place.context(msg, data.get("loc")) + screen.context(data.get("screen")) + replyideas.context(data.get("notif")) + wtxt + MOOD + debate.extra(dev) + modes.extra(mode) + cutoff.context(data.get("interrupted")) + chatsum.context(c, dev) + autolearn.context(c, dev) + attach.context(dev), full)  # Parts 160 + 168: what Jarvis was saying when you cut in
            except RuntimeError as e:
                if str(e) == OFFLINE:  # Part 170: not an error, just no internet: say it clearly in his language
                    return self.send(502, {"error": OFFLINE_HI if style == "hindi" else OFFLINE, "offline": True})
                return self.send(502, {"error": str(e)})
            reply = untick(honest(reply, style))  # Part 138 + 147: no action ran on this path, so "done" from the AI is replaced
            if srcs:  # the list of sites comes from the real search result, not from the AI
                reply += ("\n\nस्रोत: " if style == "hindi" else "\n\nSources: ") + ", ".join(srcs) + "\n" + web.label(srcs, style == "hindi")  # Part 90
            c.execute("INSERT INTO messages(device, role, content, ts) VALUES(?,?,?,?)", (dev, "assistant", "(answer about your screen was shown, not saved)" if screen.used(data.get("screen")) else "(reply ideas were shown, not saved)" if replyideas.used(data.get("notif")) else reply, time.time()))
            c.commit()
            quiet_turn = screen.used(data.get("screen")) or replyideas.used(data.get("notif"))
            sug = None if quiet_turn else (memory.suggest(msg) or autolearn.pending(c, dev))  # Part 54 + 155: only an offer (Yes / No), nothing is saved here
            if not quiet_turn:
                threading.Thread(target=after_chat, args=(dev,), daemon=True).start()  # Parts 155 + 158: after the answer is ready, so the chat is never slower
            return self.send(200, dict({"reply": reply, "via": via}, **({"deep": True} if full else {}), **({"remember": sug} if sug else {}), **({"debate": debate.label(dev)} if debate.label(dev) else {})))
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
