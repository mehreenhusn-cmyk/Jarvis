"""Jarvis neural awaaz (Part 7). Microsoft Edge ki free awaaz, `pip install edge-tts`. Internet chahiye."""
import os, re, subprocess, sys, tempfile

VOICES = {"en-GB-RyanNeural", "en-IN-PrabhatNeural", "hi-IN-MadhurNeural", "en-IN-NeerjaNeural", "hi-IN-SwaraNeural"}


def speak(text, voice):
    """mp3 bytes lautata hai. Kuch bhi galat ho to RuntimeError (page browser ki awaaz par lautega)."""
    if voice not in VOICES:
        raise RuntimeError("awaaz ka naam galat")
    text = re.sub(r"[*_`#]", "", text).strip()[:600]
    if not text:
        raise RuntimeError("bolne ke liye text nahi")
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        r = subprocess.run([sys.executable, "-m", "edge_tts", "--voice=" + voice, "--text=" + text, "--write-media=" + path],
                           capture_output=True, timeout=40)
        err = r.stderr.decode(errors="ignore")
        if "No module named" in err:
            raise RuntimeError("edge-tts install nahi hai: Termux mein chalao  pip install edge-tts")
        if r.returncode != 0 or os.path.getsize(path) < 100:
            raise RuntimeError("awaaz nahi bani (internet check karo): " + err.strip()[-120:])
        return open(path, "rb").read()
    except subprocess.TimeoutExpired:
        raise RuntimeError("awaaz banne mein bahut der lagi")
    finally:
        os.remove(path)
