#!/data/data/com.termux/files/usr/bin/bash
# Downloads mein Jarvis_part*.zip aaye to repo mein kholta hai aur GitHub par push karta hai.
# Safe: the same zip again (same content, any name) is skipped. No new content = no commit. (The old 'older part number' rule was removed: a zip named part114 blocked all later parts.)
# (Ye file scripts/sync.sh mein rakhi hai; server start par khud ./sync.sh ban jati hai.)
REPO="$(cd "$(dirname "$0")" && pwd)"
DL="${JARVIS_DL:-$HOME/storage/downloads}"
DONE="$HOME/.jarvis_done"; mkdir -p "$DONE"

main() {
  shopt -s nullglob
  [ -d "$DL" ] || { echo "Downloads nahi mila. Pehle: termux-setup-storage"; return 1; }
  while :; do
    for z in "$DL"/Jarvis_part*.zip; do
      b="$(basename "$z")"
      h="$(sha256sum "$z" | cut -d' ' -f1)"
      if sha256sum "$DONE"/*.zip </dev/null 2>/dev/null | grep -q "$h"; then
        echo "[sync] $b pehle ho chuka hai, skip (dobara push nahi)"; mv "$z" "$DONE/dup_$b"; continue
      fi
      echo "[sync] $b"
      unzip -oq "$z" -x sync.sh -d "$REPO" || { echo "[sync] unzip fail"; continue; }
      mv "$z" "$DONE/$b"
      cd "$REPO" && git add -A
      if git diff --cached --quiet; then echo "[sync] repo mein kuch naya nahi (commit nahi)"; else git commit -qm "Update from $b"; fi
      git pull --rebase -q origin main 2>/dev/null
      git push -q origin HEAD && echo "[sync] GitHub par push ho gaya / pehle se up-to-date" || echo "[sync] push fail (token/net check karo)"
    done
    [ "$1" = "watch" ] || return 0
    sleep 10
  done
}
main "$@"; exit $?
