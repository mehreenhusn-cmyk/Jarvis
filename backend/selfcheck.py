"""Part 204: one tap self-check of the voice side of the phone server. Shows what works and what to do if not. Reads only; changes nothing, sends nothing
except one short connection test to the Sarvam host (no key, no text)."""
import importlib.util, os, shutil, socket, sys


def _has(mod):
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def run(sarvam_key, meter, cache_n, own_info, own_ready, own_model_mb):
    """List of {name, ok (True / False / None for just a note), say}. Never raises."""
    out = []

    def add(name, ok, say):
        out.append({"name": name, "ok": ok, "say": say})

    add("Python", sys.version_info >= (3, 8), "%d.%d.%d" % sys.version_info[:3] + ("" if sys.version_info >= (3, 8) else " is too old, use 3.8 or newer"))
    try:
        socket.create_connection(("api.sarvam.ai", 443), timeout=4).close()
        add("Internet (Sarvam host)", True, "reachable")
    except OSError:
        add("Internet (Sarvam host)", False, "not reachable. Check mobile data or Wi-Fi. Without it only saved audio and the own voice can speak")
    add("Sarvam key", bool(sarvam_key), "saved" if sarvam_key else "not saved. Settings > Voice > Sarvam: paste the key")
    lim, used = meter.get("limit") or 0, meter.get("used") or 0
    add("Sarvam credit limit", True if lim else None, ("%d of %d characters used this month" % (used, lim)) if lim else "no limit set; you can set one in the Sarvam card")
    add("Edge voice (edge-tts)", _has("edge_tts"), "installed" if _has("edge_tts") else "missing. In Termux: pip install edge-tts")
    add("Saved Sarvam sentences", True if cache_n else None, "%d saved" % cache_n if cache_n else "none yet; the common lines can be saved from the Sarvam card")
    dl = os.environ.get("JARVIS_DL") or os.path.expanduser("~/storage/downloads")
    add("Downloads folder", os.path.isdir(dl), "found" if os.path.isdir(dl) else "not found. In Termux run once: termux-setup-storage")
    add("Voice set (own copy)", True if own_info.get("n") else None, "%d sentences, %s minutes (about %d or more are needed)" % (own_info.get("n", 0), own_info.get("minutes", 0), own_info.get("need", 30)))
    add("Piper (own voice)", _has("piper"), "installed" if _has("piper") else "missing. In Termux: pip install piper-tts (only needed for the own voice copy)")
    add("Own voice file", own_ready, ("installed (%s MB)" % own_model_mb) if own_ready else "not installed yet (comes from Colab, Part 200b)")
    try:
        free = shutil.disk_usage(os.path.expanduser("~")).free // 1048576
        add("Free space", free >= 500, "%d MB free" % free + ("" if free >= 500 else ". Low: saved audio and the voice set need room"))
    except OSError:
        add("Free space", None, "could not read")
    return out
