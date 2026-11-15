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
   so it is normal that it disappears from Downloads (the Files app may still show an empty ghost entry). The app header shows the result of the last update. The same zip twice is skipped by content (`scripts/sync.sh`). Name zips exactly `Jarvis_partN.zip`; a wrong name like `part114` once blocked all later zips (fixed in the catch-up zip, no number rule any more).
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
| 25 | **Mic inside the app + Hey Jarvis** (`Ears.java`, page changes): the app now uses the phone's own speech recognizer, so the mic button works in the app. "Hey Jarvis: off/on" button in the voice drawer: while the app stays open, it listens again and again; say "Hey Jarvis, <question>" or just "Hey Jarvis" and wait for "Yes sir?". It pauses while Jarvis speaks and when the app goes to the background (Android does not allow background listening). May beep and use battery; the phone's speech service (Google) hears the audio. "Jarvis, stop listening" or the button turns it off. Opt-in only | Built; app side not compiled or tried |
| 23 | **Screen reader** (`ScreenService.java`, `backend/screen.py`): Android app only. Say "read my screen" or "explain this screen". Jarvis asks you to turn on "Jarvis screen reader" in Accessibility settings (once), goes to the background, reads the text of the app you switch to after 6 seconds, and comes back with the answer. Reads text only (no screenshots), skips password fields, max 3000 characters, ignores all events and never reads by itself. The text goes to the AI provider for that one answer only and the answer is not saved. Screen text is treated as data, not orders | Built; app side not compiled or tried |
| 19 | **Calls and contacts** (`backend/calls.py` + `ContactsInfo.java`): in the Android app only, "missed calls", "recent calls today", "call history this week", "contact Faisal". Reads names, numbers and times only when you ask; the permission is asked at that moment. The answer is made on the phone (no AI sees it) and is NOT saved in chat history | Built, logic checked with fake data; app side not compiled |
| 3c | **Voice fix:** an old saved voice name left the voice list empty, so nothing was spoken and no error showed. Now it falls back to Madhur, and every voice failure shows a clear message | Built |
| 3b | **Voice in, voice out:** when you speak to the mic, the reply is spoken even if "Speak replies" is off | Built |
| 22 | **Camera** (`backend/see.py`): tap the camera button, take one photo, a vision AI describes it (groq, openrouter, mistral or nvidia). Photo is sent to the AI over the internet, not saved. Model names can change: set `MODEL_VISION_GROQ` etc. in `.env` if a model stops working. In the app the button opens the Android picker | Built, never tried with a real photo or key; app side not compiled |
| - | **Update status in the app header** (`~/.jarvis_last`, written by `sync.sh`): shows the last zip, time and result (pushed / skipped / PUSH FAILED). Note: the Android Files app can keep showing zips that Termux already moved away; those entries are empty ghosts | Built |
| 24 | **Phone check** (`backend/phone.py` + `PhoneInfo.java`): ask "why is my phone slow". Jarvis reads numbers only (RAM, storage, battery, heat, battery saver, days since restart) and gives simple advice. In Chrome only RAM and storage are checked | Built, rules checked with fake numbers; app side not compiled |
| - | **Catch-up zip** `Jarvis_part_24.zip`: Parts 15-21 and 24 were never pushed because of the `part114` zip name; this zip carries all of them plus the sync fix | Pushed? Check GitHub |
| 26 | **Security check and polish:** only the phone's own page may use the server (Host and Origin check); security headers and a strict page policy (no outside scripts or connections); error messages never show anything key-like; the app page cannot navigate away from the Jarvis address; file access off in the app; no cloud backup of the app data; new command "clear history" | Built; checked by a real local test of the server; app side not compiled |
| 17 | Build log is now saved on every run (artifact `build-log`). Real fixes need that log from the first build | Prepared; waiting for the first build |
| 18 | **Reminder notifications with the app closed:** `NotifyService.java` checks `/due` every 30 sec and shows a phone notification. The page hands the pairing token to the app. Termux must stay running | Built, never compiled or run |

## 7. Plan: finished (26 parts)
All planned parts are built. About 40 files and 2,650 lines of code. What is still open is TESTING on the phone, not building:
1. Download the zip, check the app header says "pushed". 2. Voice: Settings drawer, "Test voice". 3. APK: GitHub > Actions > Build APK > download `Jarvis-apk`; if it fails send `build-log`.
4. Try each feature once (cheat sheet below) and report what fails. Each fix is a small zip.
Ideas for later, not planned: wake word while the app is closed (needs a different Android method), real payments (never), WhatsApp messages (not allowed by WhatsApp).

## 8. Cheat sheet (type or say)
| Say or type | What happens |
|---|---|
| remember this: ... / what do you remember / forget 1 | Memory (no passwords or OTPs) |
| remind me tomorrow 9 am to ... / my reminders | Reminders (notification in the app) |
| I owe Faisal 5000, due 15 Nov / show ledger / paid 3 | Money ledger (notes only) |
| note about Faisal: old friend / who is Faisal / my people | People notes |
| briefing | Morning briefing |
| search: ... or paste a link | Internet read |
| why is my phone slow | Phone check (app: full, Chrome: memory and storage) |
| where am I / near me | Location, only for that message |
| missed calls / recent calls today / contact Faisal | Calls and contacts (app only, not saved) |
| read my screen | Screen reader (app only, Accessibility, not saved) |
| camera button | Describe one photo |
| Hey Jarvis (button in voice drawer) | Wake mode while the app is open |
| stop listening | Mic and voice off |
| clear history | Delete the chat history |

## 9. Security and privacy
- Server listens on 127.0.0.1 only. Only the page from that address may call it (Host and Origin are checked). Pairing code: 10 minutes, one use, locks after 5 wrong tries.
- Token is stored as a hash on the server. Keys are stored in `backend/keys.json` (owner-only file, never in Git, never sent back to the browser).
- Passwords, OTPs and PINs are never saved. Calls, contacts and screen text are never saved. Chat history is saved on the phone only; "clear history" deletes it.
- These go to the internet only when you use them: your question to the AI provider; voice text to Microsoft (online voice); photo to the vision AI; location to OpenStreetMap; screen text to the AI for that one answer.
- The Android app only opens the Jarvis address, has no file access, and is excluded from cloud backup. Accessibility is used only to read text when you ask.
- Zips: only put zips you trust in Downloads. A zip can replace any file in the repo, including scripts.

## 10. Future roadmap (NOT started, not part of the MVP)
Rules for all future work: (1) finish and TEST one batch on the phone before starting the next; (2) every feature is one handler in the existing chat chain in `backend/app.py` plus, if it needs Android, one method in the existing `JarvisApp` bridge: no new server, no second database, no second scheduler; (3) every feature that reads private data is opt-in, shows up in the privacy dashboard, and never saves what it reads unless stated; (4) sensitive text (OTP, passwords, card numbers) is filtered with the same filter as memory (`memory.SECRET`, extended); (5) nothing here uses OpenJarvis code today (it was never installed); if one of its ideas is reused later, check its license first and credit it in a NOTICE file.

**Shared services we already have, to be reused:** SQLite database and `messages` history; chat chain in `app.py`; `remind.py` (time parsing, due check, notifications through `NotifyService`); `people.py`; `memory.py` and its secret filter; `brief.py`; `phone.py` rules; the `JarvisApp` bridge pattern (`PhoneInfo`, `ContactsInfo`, `ScreenService`, `Ears`); privacy bar and "stop listening"; zip update and push pipeline.

| # | Wish | Decision | How (reuse) | Batch |
|---|---|---|---|---|
| 7 | Privacy and permission dashboard | Yes, FIRST: every later feature adds a permission | Settings card: one row per feature (mic, location, screen reader, notification access, accounts/keys) with ON/OFF and a button to Android settings; small log of sensitive reads (time and feature only, never content) | A |
| 9 | PC online/offline, safe reconnect | Reshaped: there is no PC part today. Build only server health and auto-reconnect in the app. PC monitoring only if a PC component is ever added | Existing `/status` plus header; app retries and shows "server offline" | A |
| 3 | Calendar, birthdays, recurring events | Yes, by extending, not by a new calendar | Add a repeat field to reminders (daily, weekly, monthly, yearly); "birthday" notes in people become yearly reminders; read the phone calendar with a bridge method (read permission, only when asked or in briefing) | B |
| 2 | Richer daily briefing | Yes, extend `brief.py` | Add calendar events and pending tasks (a task is a reminder without a time); dues and totals already there | C |
| 12 | Proactive suggestions, never intrusive | Yes, but small and capped | A few fixed rules (payment due tomorrow, birthday, low storage from phone check); each can be switched off; max 3 per day; quiet hours; shown in the app, optional notification; no AI needed | C |
| 5 | Multi-step routines, automation | Yes, as saved lists of EXISTING commands | A routine = a name plus commands run through the same chat chain (for example "good morning" = briefing + phone check). Only read-only or safe commands; anything that deletes, sends or pays is never allowed in a routine. Time triggers use reminders | D |
| 8 | Task history, failure report, recovery | Yes, small | One `jobs` table for long actions (web read, photo, routine): status, error, retry button; on server start show "restarted, missed reminders: N" (reminders already survive restarts) | D |
| 6 | Encrypted backup, export, restore, delete | Yes | Export memory, people, reminders and ledger (chat history optional) into one file encrypted with a passphrase; restore with a preview and merge; "delete everything" with a typed confirmation. Pick the encryption tool at build time (`openssl` from Termux is the likely choice); never write our own encryption | E |
| 1 | Notification intelligence and daily summaries | Maybe, high risk, opt-in, after A to E | Android notification access (special permission) only for apps the user picks; skip OTP and password text; keep only app name, time and a short title for a few days; summary made on request from that short list; the text is never stored in full | F |
| 10 | Clipboard assistance | Maybe, small | Only when the user taps a button (Android blocks background reads anyway); filter sensitive text; never monitor | F |
| 4 | Authorized Claude, ChatGPT, browser help | Reshaped: official ways only | (a) "Share to Jarvis" from the Android share menu (the user sends text or a link on purpose); (b) a "handoff summary" the user can paste into any chat app. No reading of logged-in sessions, cookies or private accounts, and no controlling other people's accounts | G |
| 11 | Lost-phone help | Guidance only | A card with steps and a link to Google's Find Hub and the SIM block steps. No remote control of the phone through Jarvis: that would need the server reachable from the internet, which is a bigger risk than the benefit | G |

**Batch size estimates (code only, each under 350 lines):** A about 250 lines, 2-3 files. B about 250, 1-2 files. C about 200, 1 file. D about 300, 2 files. E about 200, 1 file. F about 350, 3 files (optional). G about 180, 2 files. Total about 1,700 lines, about 12 files, spread over 7 tested batches.

**Not planned:** reading private accounts or sessions of other services; remote phone control; WhatsApp or SMS sending without a confirm tap; payments.

