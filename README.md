# JARVIS - a personal AI assistant that runs on Hussain's phone (Termux + Chrome, then an Android app)

> **For any new Claude or AI (read this first):** Hussain only sends you this repo link. He has 2-3 Claude accounts and the chat limit
> runs out often. This README has the full plan: what we build, why, how, the rules, where we are, and what is next.
> Read it, then start the next part. Do not ask him to resend the old chat. Repo: https://github.com/mehreenhusn-cmyk/Jarvis

## 1. What we are building
A personal AI assistant like Jarvis from Iron Man. It talks, remembers things, sets reminders, keeps a money ledger, reads links and
searches the web. Final goal: one app on the phone, no PC needed.

## 2. Why
Hussain is a beginner and works on his phone in Termux. He wants everything to work by download only, with no copy-paste.
So: small code, runs on the phone, and says "working" only when it really works.

## 3. How it works
```
Chrome or Android app  -->  Python server in Termux (127.0.0.1:8787)  -->  AI provider (Groq, OpenRouter, ...)
   web/index.html             backend/app.py + helper files               SQLite: backend/jarvis.db
```
- Backend: plain Python (no FastAPI, it fails to build in Termux). Frontend: one file, `web/index.html`.
- AI: 5 providers (groq, openrouter, mistral, deepseek, nvidia). The first one that works answers.
- Keys: paste in Settings. Jarvis finds the company, tests the key, shows a green tick. Stored in `backend/keys.json` (gitignored).
- Pairing: 6-digit code in Termux, valid 10 minutes, one use. The phone gets a token. Only its hash is stored.
- Voice: free Microsoft neural voices through `edge-tts` (`pip install edge-tts`). Target: calm, deep Hindi-dub Iron Man Jarvis
  (Rajesh Khattar style). A real actor's voice cannot be cloned, so we get close with Madhur + lower pitch + slower speed.
- App (Part 16): a thin Android WebView shell in `android/`. It shows the same page from the Termux server. Built by GitHub Actions.

## 4. RULES
1. Each part is under 350 lines of code. New files only when really needed. Update this README after every part.
2. **Talk to Hussain in very simple English** (short, plain words, like WhatsApp). No Roman Hindi, but do not sound uneducated either.
   The app text is also simple English. Show files and lines in a table. He dictates by voice, so spelling mistakes are normal.
3. Output is **one zip**, `Jarvis_partN.zip`, with only the changed or new files. He only downloads it. `run.sh` checks Downloads every
   5 seconds, unzips it, pushes to GitHub, restarts the server, and the page reloads by itself. The zip moves from Downloads to `~/.jarvis_done`,
   so it is normal that it disappears from Downloads. The same zip twice is skipped by content (`scripts/sync.sh`). Name zips exactly `Jarvis_partN.zip`; a wrong name like `part114` once blocked all later zips (fixed in the catch-up zip, no number rule any more).
   Never change `run.sh` or `sync.sh` through a zip (running scripts). If you must, ask him to run `bash run.sh` once.
4. Only a syntax check unless a test is really needed. Never write "tested" for something that was not tested.
5. Ask him for as few Termux commands as possible. When he names the next parts, start building at once.
6. Never save passwords, OTPs, PINs or CVVs. Never put keys or tokens in chat, code or Git.
7. His OWL1 trading repo is separate. Never touch it.
8. After each part, tell him in a table: next files and lines, and totals so far vs remaining.

## 5. Setup (phone, Termux)
Once: `pkg install git python unzip && termux-setup-storage`, `pip install edge-tts`, GitHub login (`git config --global credential.helper store`).
The GitHub token must also allow **workflow** files (needed from Part 16, or the push is rejected).
Daily: `cd ~/Jarvis && bash run.sh`. Open **http://127.0.0.1:8787** (or the Jarvis app). First time: pairing code, then Settings for the key.
Auto-start (Part 11): Termux starts Jarvis when opened. Turn off with `JARVIS_NO_AUTOSTART=1` in `.env`.

## 6. Status (15 Nov 2026)   Done on phone / Built, not tested on phone / Not started
| Part | What | State |
|---|---|---|
| 1-5 | Server, pairing, chat, history, mic, keys, 5 providers | Done on phone |
| 6-9 | Voice tuning, neural voice, Hindi-dub style, memory | Built, listen test pending |
| 10-11 | Reminders, money ledger, auto-update (`run.sh`), auto-start | Built, phone test pending |
| 12 | Privacy bar, "stop listening", voice styles (Khattar, Rolex) | Built, phone test pending |
| 13 | Read links, "search: ..." (`backend/web.py`) | Built, real internet test pending |
| 14 | Morning briefing (`backend/brief.py`) | Built |
| - | Duplicate-zip protection (`scripts/sync.sh`) | Done on fake GitHub test |
| 15 | **New look:** dark/light theme, gold accent, bubbles, big mic button, voice tools in a drawer, all text in simple English; replies from memory, reminders, ledger, briefing and web errors are now simple English too | Built, syntax-checked only |
| 16 | **Android app shell** (`android/`, `.github/workflows/apk.yml`): WebView of the Termux page, mic permission. Build: GitHub > Actions > Build APK > run > download `Jarvis-apk` | Built, never built yet |
| 20 | **People profiles** (`backend/people.py`): "note about Faisal: old friend", "who is Faisal", "my people", "forget person Faisal"; Settings > People list. When you name a saved person in chat, the AI gets those notes. No passwords or OTPs | Built, logic checked with a fake database only |
| 21 | **Location** (`backend/place.py`): only when you ask ("where am I", "near me"), the page sends the phone position for that one message. Never stored. Place name comes from OpenStreetMap over the internet. App asks for location permission | Built, not tested on phone |
| 24 | **Phone check** (`backend/phone.py` + `PhoneInfo.java`): ask "why is my phone slow". Jarvis reads numbers only (RAM, storage, battery, heat, battery saver, days since restart) and gives simple advice. In Chrome only RAM and storage are checked | Built, rules checked with fake numbers; app side not compiled |
| - | **Catch-up zip** `Jarvis_part_24.zip`: Parts 15-21 and 24 were never pushed because of the `part114` zip name; this zip carries all of them plus the sync fix | Pushed? Check GitHub |
| 17 | Build log is now saved on every run (artifact `build-log`). Real fixes need that log from the first build | Prepared; waiting for the first build |
| 18 | **Reminder notifications with the app closed:** `NotifyService.java` checks `/due` every 30 sec and shows a phone notification. The page hands the pairing token to the app. Termux must stay running | Built, never compiled or run |

## 7. Roadmap (about 26 parts, each under 350 lines; sizes are estimates)
Done so far (1-18, 20, 21, 24): about 31 files, about 1,900 lines of code. Part 19 was skipped on purpose for now.
| Part | What | New files | Lines |
|---|---|---|---|
| 19 | Contacts and call history (metadata only, skipped for now) | 2 | ~200 |
| 22 | Camera: understand surroundings | 2 | ~200 |
| 23 | Screen and app understanding | 3 | ~300 |
| 25 | "Hey Jarvis" wake word (uncertain on Android, test first) | 2 | ~150 |
| 26 | Security check and final polish | 0-1 | ~100 |
| **Remaining (19, 22, 23, 25, 26)** | | **~10 files** | **~950 lines** |
| **Final total** | | **~41 files** | **~2,850 lines** |

Safety rules for later parts: ask before sending a message, deleting or paying; never use mic or camera secretly; call log is metadata only;
"stop listening" turns the mic off at once.

## 8. Security so far
Server listens on 127.0.0.1 only. Token is stored as a hash. Pairing locks after 5 wrong tries. Keys never go back to the browser.
Location is sent to OpenStreetMap (internet) only when you ask a location question, and is never saved. Spoken text goes to Microsoft's voice service over the internet, so keep voice off for private talk.
