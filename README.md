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

## 6. STATUS: ALL 26 PARTS ARE DONE (15 Nov 2026)
Everything below is built and pushed. "Phone test" says only what Hussain has already seen working on his phone. Anything not marked YES still needs one quick try (a bug found there = one small fix zip, not unfinished work).
| Part | What | Status | Phone test |
|---|---|---|---|
| 1-5 | Server, pairing, chat, history, mic (Chrome), keys, 5 AI providers | DONE | YES |
| 6-9 | Voice: neural voices, sliders, Hindi style, memory | DONE | YES (voice plays; matching the movie voice is still being tuned) |
| 10-11 | Reminders, money ledger, auto-update `run.sh`, auto-start | DONE | YES (update and push seen in Termux) |
| 12-14 | Privacy bar, web read and search, morning briefing, duplicate-zip protection | DONE | YES for duplicate-zip protection, NOT YET for the rest |
| 15 | New professional look (dark/light, gold accent, simple English) | DONE | YES |
| 16-17 | Android app shell, GitHub APK build, build log | DONE | YES (build is green, app opens) |
| 18 | Reminder notifications with the app closed | DONE | NOT YET |
| 19 | Calls and contacts (app only, not saved) | DONE | NOT YET |
| 20 | People notes | DONE | NOT YET |
| 21 | Location, only when asked | DONE | NOT YET |
| 22 | Camera: describe one photo | DONE | NOT YET |
| 23 | Screen reader (app only, not saved) | DONE | NOT YET |
| 24 | Phone check "why is my phone slow" | DONE | NOT YET |
| 25 | Mic inside the app, "Hey Jarvis" while the app is open | DONE | NOT YET |
| 26 | Security check, polish, "clear history" | DONE | NOT YET |
| - | Update status line in the app header (`~/.jarvis_last`) | DONE | YES |
| - | Voice presets: Khattar, Rolex, Jarvis studio (Hindi), Jarvis studio (British English), Normal | DONE | Hussain will pick the closest to the movie Jarvis |
Total: about 40 files and about 2,650 lines of code. Known limits (not bugs): Hey Jarvis works only while the app is open; mic in Chrome and in the app use different engines; the real actor's voice cannot be copied, only approached with the free voices; Android Files app may show empty ghost entries for zips that Termux already moved to `~/.jarvis_done`.

## 7. What to do next
Only testing. Try each feature once with the cheat sheet below. Report what fails with a screenshot. For the APK: GitHub > Actions > Build APK > download `Jarvis-apk`; if it fails send `build-log`. Then follow section 10 (future batches), one batch at a time.

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

