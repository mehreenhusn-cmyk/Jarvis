#!/data/data/com.termux/files/usr/bin/bash
# EK BAAR chalao:  bash run.sh   (Termux khula rakho)
# Ye server chalata hai. Downloads mein naya Jarvis_part*.zip aate hi (5 sec mein): zip kholta hai, GitHub par push karta hai,
# purana server band karke naya chalu karta hai. Tum bas browser mein page dekho (wo khud refresh ho jata hai).
cd "$(dirname "$0")" || exit 1
DL="${JARVIS_DL:-$HOME/storage/downloads}"
mkdir -p "$HOME/.jarvis_done"
termux-wake-lock 2>/dev/null
PID=""
start() { python backend/app.py & PID=$!; }
stop() { [ -n "$PID" ] && kill "$PID" 2>/dev/null && wait "$PID" 2>/dev/null; PID=""; }
trap 'stop; exit 0' INT TERM
start
while :; do
  sleep 5
  if ls "$DL"/Jarvis_part*.zip >/dev/null 2>&1; then
    echo "[run] naya zip mila, update ho raha hai..."
    bash sync.sh once
    mv "$DL"/Jarvis_part*.zip "$HOME/.jarvis_done/" 2>/dev/null && echo "[run] zip fail hua tha, dobara download karo"
    stop; start; echo "[run] server naya chalu ho gaya"
  elif ! kill -0 "$PID" 2>/dev/null; then
    echo "[run] server band mila, dobara chalu"; start
  fi
done
