"""Jarvis auto-start (Part 11): Termux khulte hi aur phone restart par run.sh khud chale. Ek baar app.py chalne par set ho jata hai.
Band karna ho: .env mein JARVIS_NO_AUTOSTART=1 (aur ~/.bashrc se '# JARVIS autostart' wali 2 lines hata do)."""
import os

MARK = "# JARVIS autostart"


def ensure(root):
    if os.environ.get("JARVIS_NO_AUTOSTART"):
        return
    home = os.path.expanduser("~")
    try:
        rc = os.path.join(home, ".bashrc")
        t = open(rc, encoding="utf-8").read() if os.path.exists(rc) else ""
        if MARK not in t:  # server pehle se chal raha ho to dobara nahi chalata
            with open(rc, "a", encoding="utf-8") as f:
                f.write(f"\n{MARK}\npython -c \"import socket;socket.create_connection(('127.0.0.1',8787),1)\" 2>/dev/null || (cd \"{root}\" && bash run.sh)\n")
            print("[autostart] ab Termux kholte hi Jarvis khud chalega (~/.bashrc)", flush=True)
        d = os.path.join(home, ".termux", "boot")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "jarvis.sh")  # Termux:Boot app install ho to phone restart par bhi chalega
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"#!/data/data/com.termux/files/usr/bin/sh\ntermux-wake-lock\ncd \"{root}\" && bash run.sh\n")
            os.chmod(p, 0o755)
    except OSError as e:
        print("[autostart] set nahi hua:", e, flush=True)


def refresh_scripts(root):
    """scripts/sync.sh (zip se aayi nayi copy) ko sync.sh bana deta hai, taaki sync.sh khud update ho (Hussain ko command nahi)."""
    src, dst = os.path.join(root, "scripts", "sync.sh"), os.path.join(root, "sync.sh")
    try:
        if os.path.exists(src) and open(src, "rb").read() != open(dst, "rb").read():
            import shutil
            shutil.copyfile(src, dst)
            print("[update] sync.sh nayi version se badal diya", flush=True)
    except OSError as e:
        print("[update] sync.sh nahi badla:", e, flush=True)
