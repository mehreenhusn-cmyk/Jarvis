#!/data/data/com.termux/files/usr/bin/bash
# Downloads mein Jarvis_part*.zip aaye to repo mein kholta hai aur GitHub par push karta hai.
# Use:  bash sync.sh once  (ek baar)   |   bash sync.sh watch  (har 10 sec check)
REPO="$(cd "$(dirname "$0")" && pwd)"
DL="${JARVIS_DL:-$HOME/storage/downloads}"
DONE="$HOME/.jarvis_done"; mkdir -p "$DONE"

main() {
  shopt -s nullglob
  [ -d "$DL" ] || { echo "Downloads nahi mila. Pehle: termux-setup-storage"; return 1; }
  while :; do
    for z in "$DL"/Jarvis_part*.zip; do
      echo "[sync] $(basename "$z")"
      unzip -oq "$z" -x sync.sh -d "$REPO" || { echo "[sync] unzip fail"; continue; }
      mv "$z" "$DONE/"
      cd "$REPO" && git add -A
      if git diff --cached --quiet; then echo "[sync] kuch naya nahi"; continue; fi
      git commit -qm "Update from $(basename "$z")"
      git pull --rebase -q origin main
      git push -q origin HEAD && echo "[sync] GitHub par push ho gaya" || echo "[sync] push fail (token/net check karo)"
    done
    [ "$1" = "watch" ] || return 0
    sleep 10
  done
}
main "$@"; exit $?
