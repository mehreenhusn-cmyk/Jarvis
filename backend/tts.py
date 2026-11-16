"""Jarvis neural awaaz (Part 7). Microsoft Edge ki free awaaz, `pip install edge-tts`. Internet chahiye."""
import base64, json, os, re, subprocess, sys, tempfile, urllib.error, urllib.request

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
