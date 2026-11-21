"""Jarvis neural awaaz (Part 7). Microsoft Edge ki free awaaz, `pip install edge-tts`. Internet chahiye."""
import base64, hashlib, json, os, re, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request

VOICES = {"en-GB-RyanNeural", "en-IN-PrabhatNeural", "hi-IN-MadhurNeural", "en-IN-NeerjaNeural", "hi-IN-SwaraNeural"}


def speak(text, voice, pitch=-8, rate=-6):
    """mp3 bytes lautata hai. Kuch bhi galat ho to RuntimeError (page browser ki awaaz par lautega)."""
    try:
        pitch, rate = max(-50, min(50, int(pitch))), max(-30, min(30, int(rate)))
    except (TypeError, ValueError):
        pitch, rate = -8, -6
    if voice not in VOICES:
        raise RuntimeError("awaaz ka naam galat")
    text = re.sub(r"[*_`#]", "", text).strip()[:600]
    if not text:
        raise RuntimeError("no text to speak")
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        base = [sys.executable, "-m", "edge_tts", "--voice=" + voice, "--text=" + text, "--write-media=" + path]
        # Jarvis jaisa gehra, shaant andaaz: thoda dheema aur gehra. Na chale to seedhi awaaz.
        r = subprocess.run(base + ["--rate=%+d%%" % rate, "--pitch=%+dHz" % pitch], capture_output=True, timeout=40)
        if r.returncode != 0 and b"No module named" not in r.stderr:
            r = subprocess.run(base, capture_output=True, timeout=40)
        err = r.stderr.decode(errors="ignore")
        if "No module named" in err:
            raise RuntimeError("edge-tts is not installed. Run in Termux: pip install edge-tts")
        if r.returncode != 0 or os.path.getsize(path) < 100:
            hint = " In Termux run: pip install -U edge-tts  (old versions get NoAudioReceived), then restart run.sh." if "NoAudioReceived" in err or "No audio" in err else ""
            raise RuntimeError("voice failed (check internet): " + err.strip()[-120:] + hint)
        return open(path, "rb").read()
    except subprocess.TimeoutExpired:
        raise RuntimeError("awaaz banne mein bahut der lagi")
    finally:
        os.remove(path)


# Part 53: Sarvam (Indian company) voice for JARVIS. Key kept in keys.json. Male voices of Bulbul v3 (checked on docs.sarvam.ai, 16 Nov 2026).
SARVAM_SPEAKERS = {"shubh", "rahul", "aditya", "ratan", "amit", "rohan"}


def sarvam(text, key, speaker="shubh", lang="hindi", rate=-10):
    """wav bytes lautata hai. Kuch bhi galat ho to RuntimeError (app.py phir Edge awaaz par jata hai)."""
    if not key:
        raise RuntimeError("Sarvam key not saved")
    text = re.sub(r"[*_`#]", "", text).strip()[:600]
    if not text:
        raise RuntimeError("no text to speak")
    try:
        pace = max(0.7, min(1.3, 1 + int(rate) / 100))
    except (TypeError, ValueError):
        pace = 0.9
    body = json.dumps({"text": text, "target_language_code": "en-IN" if lang == "english" else "hi-IN", "model": "bulbul:v3",
                       "speaker": speaker if speaker in SARVAM_SPEAKERS else "shubh", "pace": pace}).encode()
    req = urllib.request.Request("https://api.sarvam.ai/text-to-speech", body, {"api-subscription-key": key, "Content-Type": "application/json", "User-Agent": "jarvis/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            parts = json.load(r).get("audios") or []
    except urllib.error.HTTPError as e:
        raise RuntimeError("Sarvam error %d%s" % (e.code, " (key not accepted)" if e.code in (401, 403) else " (limit reached)" if e.code == 429 else ""))
    except Exception as e:
        raise RuntimeError("Sarvam not reachable: " + type(e).__name__)
    if len(parts) != 1:
        raise RuntimeError("Sarvam sent no audio")
    try:
        audio = base64.b64decode(parts[0])
    except ValueError:
        raise RuntimeError("Sarvam sent bad audio")
    if len(audio) < 100:
        raise RuntimeError("Sarvam sent no audio")
    return audio


# ---- Part 197 and Part 198: Sarvam voice saved on the phone, credit meter, "Sarvam voice or silence", short speaking ----
CACHE = os.path.expanduser("~/.jarvis_voicecache")  # one .wav per sentence, named by a hash of (text, speaker, language, speed)
METER = os.path.expanduser("~/.jarvis_sarvam.json")  # characters sent to Sarvam this month, your limit, the two switches
CACHE_MAX = 300 * 1024 * 1024  # when the saved audio is bigger than this the least used files go first
LOCK = threading.Lock()
WARM = {"running": False, "done": 0, "total": 0, "stop": ""}  # progress of "save the common lines"


def meter():
    """The numbers of this month. A new month starts again at 0 used."""
    m = {"month": time.strftime("%Y-%m"), "used": 0, "limit": 0, "silent": False, "short": False, "edge": False, "collect": False}  # Part 200a: collect = save text + audio of new Sarvam sentences for an own voice set (off by default). Part 193: edge = the Edge voice may speak when Sarvam fails (off by default)
    try:
        with open(METER) as fh:
            m.update(json.load(fh))
    except (OSError, ValueError):
        pass
    if m.get("month") != time.strftime("%Y-%m"):
        m["month"], m["used"] = time.strftime("%Y-%m"), 0
    return m


def meter_save(m):
    try:
        with open(METER, "w") as fh:
            json.dump(m, fh)
    except OSError:
        pass


def meter_set(limit=None, silent=None, short=None, edge=None, collect=None):
    with LOCK:
        m = meter()
        if limit is not None:
            m["limit"] = max(0, min(100000000, int(limit)))
        if silent is not None:
            m["silent"] = bool(silent)
        if short is not None:
            m["short"] = bool(short)
        if edge is not None:
            m["edge"] = bool(edge)
        if collect is not None:
            m["collect"] = bool(collect)
        meter_save(m)
        return m


def meter_add(n):
    with LOCK:
        m = meter()
        m["used"] = int(m.get("used", 0)) + int(n)
        meter_save(m)


def pct(m):
    return min(999, int(100 * m["used"] / m["limit"])) if m.get("limit") else 0


def _clean(text):
    return re.sub(r"[*_`#]", "", text).strip()[:600]


def _path(text, speaker, lang, rate):
    sp = speaker if speaker in SARVAM_SPEAKERS else "shubh"
    try:
        rt = int(rate)
    except (TypeError, ValueError):
        rt = -10
    h = hashlib.sha256(("%s|%s|%s|%d|bulbul:v3" % (_clean(text), sp, "en" if lang == "english" else "hi", rt)).encode()).hexdigest()[:40]
    return os.path.join(CACHE, h + ".wav")


def cached(text, speaker, lang, rate):
    """The saved audio of this sentence, or None."""
    p = _path(text, speaker, lang, rate)
    try:
        with open(p, "rb") as fh:
            audio = fh.read()
        os.utime(p, None)  # remember it was used now
        return audio if len(audio) > 100 else None
    except OSError:
        return None


def cache_put(text, speaker, lang, rate, audio):
    try:
        os.makedirs(CACHE, exist_ok=True)
        with open(_path(text, speaker, lang, rate), "wb") as fh:
            fh.write(audio)
        files = [(os.path.getmtime(os.path.join(CACHE, x)), os.path.getsize(os.path.join(CACHE, x)), os.path.join(CACHE, x)) for x in os.listdir(CACHE)]
        total = sum(x[1] for x in files)
        for _, size, p in sorted(files):
            if total <= CACHE_MAX:
                break
            os.remove(p)
            total -= size
    except OSError:
        pass


def cache_info():
    """(number of saved sentences, megabytes)"""
    try:
        sizes = [os.path.getsize(os.path.join(CACHE, x)) for x in os.listdir(CACHE)]
    except OSError:
        return 0, 0.0
    return len(sizes), round(sum(sizes) / 1048576, 1)


def sarvam_cached(text, key, speaker="shubh", lang="hindi", rate=-10):
    """(audio, was_saved). A saved sentence costs nothing. A new one goes to Sarvam, is counted and saved. Over your own limit: no new Sarvam call."""
    hit = cached(text, speaker, lang, rate)
    if hit:
        return hit, True
    m = meter()
    if m.get("limit") and m["used"] >= m["limit"]:
        raise RuntimeError("Sarvam limit that you set is used up (limit reached)")
    audio = sarvam(text, key, speaker, lang, rate)
    meter_add(len(_clean(text)))
    cache_put(text, speaker, lang, rate, audio)
    if m.get("collect"):  # Part 200a: a NEW Sarvam sentence goes into the voice set, with its text
        import ownvoice
        ownvoice.add(text, speaker if speaker in SARVAM_SPEAKERS else "shubh", audio)
    return audio, False


def first_sentences(text, n=2, over=160):
    """Part 198: a long reply is spoken only up to its first n sentences (the whole text stays on the screen)."""
    t = (text or "").strip()
    if len(t) <= over:
        return t
    parts = re.findall(r"[^.!?\u0964\n]+[.!?\u0964]*", t)
    return " ".join(p.strip() for p in parts[:n]).strip() or t[:over]


def warm_start(key, jobs):
    """Part 197: make and save the audio of the common lines, one after the other, in the background. Stops at the first limit or key error."""
    WARM.update(running=True, done=0, total=len(jobs), stop="")

    def run():
        try:
            for text, speaker, lang, rate in jobs:
                if cached(text, speaker, lang, rate):
                    WARM["done"] += 1
                    continue
                try:
                    sarvam_cached(text, key, speaker, lang, rate)
                except RuntimeError as e:
                    WARM["stop"] = str(e)
                    break
                WARM["done"] += 1
                time.sleep(0.4)
        finally:
            WARM["running"] = False

    threading.Thread(target=run, daemon=True).start()
