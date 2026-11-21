"""Part 200a: a voice set for an own small copy of the Sarvam voice (personal use). Every sentence that Sarvam speaks for Jarvis is saved here WITH its text
(the normal saved audio has no text, so it cannot train anything). Only when the switch is ON. Stays on this phone until you tap Export, which writes ONE zip
to Downloads (wavs + metadata.csv, the usual `id|text` form) that you take to Colab (Part 200b). Nothing is sent anywhere by this file."""
import hashlib, os, re, shutil, subprocess, sys, tempfile, threading, time, wave, zipfile, io

SET = os.path.expanduser("~/.jarvis_voiceset")  # SET/<speaker>/<id>.wav and SET/index.tsv (id, speaker, seconds, text)
INDEX = os.path.join(SET, "index.tsv")
MAXB = 1024 * 1024 * 1024  # stop collecting at 1 GB
NEED_MIN = 30  # a rough guess of the audio needed for a fine-tuned voice; the page shows the minutes so far
LOCK = threading.Lock()


def _ok(text):
    """Only plain sentences: no long digit runs (OTP, card), nothing the memory filter calls a secret, 8 to 400 characters."""
    t = re.sub(r"[*_`#]", "", text or "").strip()
    if not 8 <= len(t) <= 400 or re.search(r"\d{4,}", t.replace(" ", "")):
        return ""
    try:
        import memory
        if memory.SECRET.search(t):
            return ""
    except Exception:
        pass
    return re.sub(r"[\t\r\n|]+", " ", t)


def _rows():
    try:
        with open(INDEX, encoding="utf-8") as fh:
            return [l.rstrip("\n").split("\t", 3) for l in fh if l.count("\t") >= 3]
    except OSError:
        return []


def add(text, speaker, audio):
    """Called by tts.cache_put after Sarvam made a NEW sentence and the switch is ON. Never raises."""
    try:
        t = _ok(text)
        if not t or not audio or len(audio) < 1000:
            return
        with wave.open(io.BytesIO(audio)) as w:
            sec = w.getnframes() / float(w.getframerate() or 1)
        if not 1.0 <= sec <= 40.0:
            return
        i = hashlib.sha1(("%s|%s" % (t, speaker)).encode("utf-8")).hexdigest()[:16]
        with LOCK:
            d = os.path.join(SET, speaker)
            p = os.path.join(d, i + ".wav")
            if os.path.exists(p):
                return  # this sentence is already in the set
            os.makedirs(d, exist_ok=True)
            if sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d)) > MAXB:
                return  # the set is full
            with open(p, "wb") as fh:
                fh.write(audio)
            with open(INDEX, "a", encoding="utf-8") as fh:
                fh.write("%s\t%s\t%.2f\t%s\n" % (i, speaker, sec, t))
    except Exception:
        pass


def info():
    r = _rows()
    sp = {}
    for _, s, sec, _t in r:
        try:
            a = sp.setdefault(s, [0, 0.0])
            a[0] += 1
            a[1] += float(sec)
        except ValueError:
            pass
    return {"n": len(r), "minutes": round(sum(x[1] for x in sp.values()) / 60, 1), "need": NEED_MIN,
            "speakers": {s: {"n": a[0], "minutes": round(a[1] / 60, 1)} for s, a in sp.items()}}


def export():
    """ONE zip in Downloads for the speaker with the most audio: wavs/<id>.wav and metadata.csv (id|text)."""
    inf = info()
    if not inf["speakers"]:
        return {"ok": False, "error": "Nothing is collected yet. Turn the switch ON and let Jarvis speak with Sarvam."}
    sp = max(inf["speakers"], key=lambda s: inf["speakers"][s]["minutes"])
    dl = os.environ.get("JARVIS_DL") or os.path.expanduser("~/storage/downloads")
    if not os.path.isdir(dl):
        return {"ok": False, "error": "Downloads folder not found. Run once in Termux: termux-setup-storage"}
    out = os.path.join(dl, "jarvis_voiceset_%s.zip" % sp)  # lower case, so the update sync (Jarvis_part*.zip) never touches it
    rows = [r for r in _rows() if r[1] == sp and os.path.exists(os.path.join(SET, sp, r[0] + ".wav"))]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        for i, _s, _sec, t in rows:
            z.write(os.path.join(SET, sp, i + ".wav"), "wavs/%s.wav" % i)
        z.writestr("metadata.csv", "".join("%s|%s\n" % (r[0], r[3]) for r in rows))
    return {"ok": True, "path": out, "n": len(rows), "minutes": inf["speakers"][sp]["minutes"], "speaker": sp}


def clear():
    with LOCK:
        n = 0
        try:
            for d in os.listdir(SET):
                p = os.path.join(SET, d)
                if os.path.isdir(p):
                    for x in os.listdir(p):
                        os.remove(os.path.join(p, x))
                        n += 1
                    os.rmdir(p)
            if os.path.exists(INDEX):
                os.remove(INDEX)
        except OSError:
            pass
    return n


# ---- Part 200c: speak with the trained copy (Piper ONNX from Colab, Part 200b) as a backup after the saved audio and Sarvam ----
MODEL_DIR = os.path.expanduser("~/.jarvis_ownvoice")
MODEL = os.path.join(MODEL_DIR, "jarvis_voice.onnx")  # the .onnx.json file must sit next to it


def ready():
    return os.path.exists(MODEL) and os.path.exists(MODEL + ".json")


def model_info():
    return {"model": ready(), "model_mb": round(os.path.getsize(MODEL) / 1048576, 1) if ready() else 0}


def install():
    """Take jarvis_voice.zip (the Colab download) or jarvis_voice.onnx + .onnx.json from Downloads and put them in MODEL_DIR."""
    dl = os.environ.get("JARVIS_DL") or os.path.expanduser("~/storage/downloads")
    if not os.path.isdir(dl):
        return {"ok": False, "error": "Downloads folder not found. Run once in Termux: termux-setup-storage"}
    try:
        os.makedirs(MODEL_DIR, exist_ok=True)
        z = os.path.join(dl, "jarvis_voice.zip")
        if os.path.exists(z):
            with zipfile.ZipFile(z) as zf:
                for n in ("jarvis_voice.onnx", "jarvis_voice.onnx.json"):
                    with zf.open(n) as a, open(os.path.join(MODEL_DIR, n), "wb") as b:
                        shutil.copyfileobj(a, b)
        elif os.path.exists(os.path.join(dl, "jarvis_voice.onnx")) and os.path.exists(os.path.join(dl, "jarvis_voice.onnx.json")):
            for n in ("jarvis_voice.onnx", "jarvis_voice.onnx.json"):
                shutil.copy(os.path.join(dl, n), os.path.join(MODEL_DIR, n))
        else:
            return {"ok": False, "error": "jarvis_voice.zip not found in Downloads. Take it from Colab (Part 200b) first."}
    except (OSError, KeyError, zipfile.BadZipFile) as e:
        return {"ok": False, "error": "Could not read the voice files: " + type(e).__name__}
    return dict(model_info(), ok=True)


def speak(text):
    """wav bytes from the trained voice. RuntimeError if anything is missing or slow (the caller then goes on to the next backup)."""
    if not ready():
        raise RuntimeError("own voice file is not installed")
    t = re.sub(r"[*_`#\r\n]+", " ", text or "").strip()[:400]
    if not t:
        raise RuntimeError("no text to speak")
    fd, out = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        r = subprocess.run([sys.executable, "-m", "piper", "-m", MODEL, "-f", out], input=t.encode("utf-8"), capture_output=True, timeout=60)
        err = r.stderr.decode(errors="ignore")
        if "No module named" in err:
            raise RuntimeError("Piper is not installed. In Termux run: pip install piper-tts")
        if r.returncode != 0 or os.path.getsize(out) < 200:
            raise RuntimeError("own voice failed: " + err.strip()[-120:])
        with open(out, "rb") as fh:
            return fh.read()
    except subprocess.TimeoutExpired:
        raise RuntimeError("own voice took too long")
    except OSError as e:
        raise RuntimeError("own voice failed: " + type(e).__name__)
    finally:
        try:
            os.remove(out)
        except OSError:
            pass


# ---- Part 203: quick fill. The sentences of voicelines.py are spoken once by Sarvam and saved WITH their text (a sentence that is already saved is only paired with its text, no credit) ----
FILL = {"running": False, "done": 0, "total": 0, "stop": ""}


def fill_start(key, jobs):
    """jobs: [(text, speaker, lang, rate)]. Runs in the background, one after the other. Stops at the first limit or key error."""
    import tts
    if FILL["running"]:
        return
    tts.meter_set(collect=True)  # the set is filled by sarvam_cached, so the switch must be ON
    FILL.update(running=True, done=0, total=len(jobs), stop="")

    def run():
        try:
            for text, speaker, lang, rate in jobs:
                audio = tts.cached(text, speaker, lang, rate)
                try:
                    if audio:
                        add(text, speaker, audio)
                    else:
                        tts.sarvam_cached(text, key, speaker, lang, rate)
                except RuntimeError as e:
                    FILL["stop"] = str(e)
                    break
                FILL["done"] += 1
                if not audio:
                    time.sleep(0.4)
        finally:
            FILL["running"] = False

    threading.Thread(target=run, daemon=True).start()
