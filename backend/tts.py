"""Jarvis neural awaaz (Part 7). Microsoft Edge ki free awaaz, `pip install edge-tts`. Internet chahiye."""
import os, re, subprocess, sys, tempfile

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
            raise RuntimeError("voice failed (check internet): " + err.strip()[-120:])
        return open(path, "rb").read()
    except subprocess.TimeoutExpired:
        raise RuntimeError("awaaz banne mein bahut der lagi")
    finally:
        os.remove(path)
