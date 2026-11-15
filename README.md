# JARVIS - a personal AI assistant that runs on Hussain's phone (Termux + Chrome, then an Android app)

> **For any new Claude or AI (read this first):** Hussain only sends you this repo link. He has 2-3 Claude accounts and the chat limit
> runs out often. This README has the full plan: what we build, why, how, the rules, where we are, and what is next.
> Read it, then start the next part. Do not ask him to resend the old chat. Repo: https://github.com/mehreenhusn-cmyk/Jarvis

## 0. AT A GLANCE (updated 16 Nov 2026, after Part 47)
**What:** Jarvis, a personal AI assistant on Hussain's phone (Termux server + Android app). **Why:** one app on the phone, no PC, works by download only.
**Done:** 52 of 56 Parts built (about 4,460 lines of code, 74 files). Only Parts 1 to 26 were partly phone tested; Parts 27 to 39, 41 to 47, 50, 51, 52, 54, 55 and 56 are built but NOT phone tested. Java is still not compiled: the GitHub Build APK is the first compile test.
**Pending:** 4 Parts, about 850 lines (about 180 required: Part 48; about 120 only if needed: Part 53; about 550 optional: Parts 40 and 49). Next Part is **48**. Part 53 only if the two voices sound too alike. Full table in section 11.6, order in the "Build order" line.
| Group | Parts | Status |
|---|---|---|
| Base: server, chat, voice, reminders, app, privacy | 1 to 29 | DONE |
| Phone control: commands, apps, screen, confirm rules, lock phone | 30 to 35 | BUILT, not phone tested |
| App lock, chat times, conversation wait | 36 | BUILT |
| Settings by voice (pages, flashlight, volume), Quick Settings tile and shortcut | 37, 38 | BUILT |
| Background mic test (Settings card, 8 h limit) | 39 | BUILT (this zip) |
| Task engine (server) and task runner (app): several steps in one sentence | 41, 42 | BUILT (this zip) |
| Phone checklist (section 11.8 is now a table). No test file, Hussain's no-tests rule | 43 | BUILT (this zip) |
| Repeat reminders, birthdays, phone calendar | 44 | BUILT (this zip) |
| Richer briefing, suggestions, quiet hours | 45 | BUILT (this zip) |
| Routines (saved task sentences) | 46 | BUILT (this zip) |
| Backup (encrypted file, restore with preview, delete everything) | 47 | BUILT (this zip) |
| Share to Jarvis, handoff, lost phone | 48 | PENDING |
| Two voices (Tony and JARVIS): engine and Settings cards | 51, 52 | BUILT (this zip) |
| Second voice provider (Google), only if needed | 53 | PENDING |
| Home tab (orb, today, quick buttons, stats) | 56 | BUILT (this zip) |
| Optional: offline wake word, notification summary | 40, 49 | OPTIONAL |

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
2. **Talk to Hussain in simple Roman Hinglish or simple English (Roman script only, NEVER Devanagari), even when he writes or dictates in Hindi/Devanagari.** Short, plain words, like WhatsApp.
   The app text is simple English. Show files and lines in a table. He dictates by voice, so spelling mistakes are normal.
3. Output is **one zip**, `Jarvis_partN.zip`, with only the changed or new files. He only downloads it. `run.sh` checks Downloads every
   5 seconds, unzips it, pushes to GitHub, restarts the server, and the page reloads by itself. The zip moves from Downloads to `~/.jarvis_done`,
   so it is normal that it disappears from Downloads (the Files app may still show an empty ghost entry). The app header shows the result of the last update. The same zip twice is skipped by content (`scripts/sync.sh`). Name zips exactly `Jarvis_partN.zip`; a wrong name like `part114` once blocked all later zips (fixed in the catch-up zip, no number rule any more).
   Never change `run.sh` or `sync.sh` through a zip (running scripts). If you must, ask him to run `bash run.sh` once.
4. Only a syntax check unless a test is really needed. Never write "tested" for something that was not tested.
5. Ask him for as few Termux commands as possible. When he names the next parts, start building at once.
6. Never save passwords, OTPs, PINs or CVVs. Never put keys or tokens in chat, code or Git.
7. His OWL1 trading repo is separate. Never touch it.
8. After each part, tell him in a table: next files and lines, and totals so far vs remaining.
9. Zip content (from Part 27): each zip holds this Part's files PLUS every file changed in earlier Parts whose push the app header has not yet shown as "pushed". Never the whole repo. This stops the "see.py was missing" crash from happening again.
10. Before each Part, say first if it is WITH tests or WITHOUT tests, and why. Python logic is tested (it can be run). Android Java cannot be compiled by Claude: the GitHub build is its compile test and Hussain's phone is its real test. Anything not run is written as "Not run".
11. Phone control rules: see section 11. Plan first, code only after Hussain says OK to a Part. Every Part must list files, lines and benefit.

## 5. Setup (phone, Termux)
Once: `pkg install git python unzip openssl-tool && termux-setup-storage` (openssl-tool is for backups, Part 47), `pip install edge-tts`, GitHub login (`git config --global credential.helper store`).
The GitHub token must also allow **workflow** files (needed from Part 16, or the push is rejected).
Daily: `cd ~/Jarvis && bash run.sh`. Open **http://127.0.0.1:8787** (or the Jarvis app). First time: pairing code, then Settings for the key.
Auto-start (Part 11): Termux starts Jarvis when opened. Turn off with `JARVIS_NO_AUTOSTART=1` in `.env`.

## 6. STATUS (16 Nov 2026): Parts 1 to 39, 41 to 47, 50, 51, 52, 54, 55 and 56 are built
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
| 27 | Security: WebView permission checks, http only for 127.0.0.1, permissions asked when first used | BUILT | NOT YET (Java not compiled yet) |
| 28 | Real Stop kept in Java (`Privacy.java`), saved across restarts, restart only by a finger tap | BUILT | NOT YET |
| 29 | Privacy dashboard in Settings (allowed vs running, last used, activity log), server-offline banner | BUILT | NOT YET |
| 30 | Command layer: "WhatsApp kholo" (Hindi, English, Hinglish) becomes one action from a fixed list. Master switch "Phone control" OFF by default, only a finger tap turns it on, Stop turns it off. Limited AI fallback, checked by the server | BUILT | NOT YET (server tests pass; Java not compiled) |
| 31 | App launch: Java lists apps with a launcher icon, matches by name (Hindi names, small spelling mistakes), asks with buttons when two fit, never opens an app that is not on the phone | BUILT | NOT YET (Java not compiled) |
| 32 | Better screen reading: lines are tagged button, field, switch, scroll area; typed text in fields is never read; OTP, PIN, CVV, card, Aadhaar, PAN, bank account and password values are hidden before the AI sees them; honest message when an app shows nothing | BUILT | NOT YET (redaction tested in Python; Java not compiled) |
| 33 | Risk and confirm rules: send, pay, buy, delete, install, account need a preview and Hussain's own tap on Yes (script clicks ignored, 60 s timeout); typing a password, OTP, PIN or card number is always refused. No action can send or change anything yet; Part 34 plugs into this gate | BUILT | NOT YET |
| 34 | Safe screen actions: press a button by name, scroll, type in a text box, back, home, which app is open. Each step finds the control again on the live screen, never types in password/OTP/PIN/card boxes, checks after the step and says if nothing changed. Send, pay, delete type buttons need your Yes (and a real finger tap checked in Java). Swipe only as a confirmed fallback when nothing can scroll. Jarvis can now also answer "how far is the app" from this README | BUILT | NOT YET (server tests pass; Java not compiled) |
| 35 | Lock phone: "phone lock kar do" uses Android's own lock action (Android 9 or newer), then Java checks the real lock state and Jarvis says honestly if it could not confirm. There is no unlock command | BUILT | NOT YET (Java not compiled) |
| 36 | App lock with Android's own prompt (fingerprint, face, PIN; closes the app if cancelled; 1 minute grace; the bridge refuses while locked). WhatsApp-style time under every message and a date line (Today, Yesterday). Jarvis now knows the time and how long you were away. Mic waits 4 to 5 seconds of quiet before it ends your sentence. "Kitna kaam ho gaya" now answers progress. **Pairing fix:** one fixed signing key, so an update installs over the old app and keeps your pairing | BUILT | NOT YET (Java not compiled; install once with uninstall first, see section 7) |
| 37 | Settings help: "wifi settings kholo", "bluetooth", "location", "sound", "brightness" (opens Display page), "battery", "permissions", "notifications" open fixed Android pages. "torch on/off" switches the flashlight. "volume badhao/kam karo" changes the music volume and says what Android really did. Wi-Fi, Bluetooth, location and brightness are NEVER switched by Jarvis (Android does not allow it): Jarvis opens the page and says so. Needs Phone control ON | BUILT | NOT YET (Java not compiled) |
| 38 DONE | Quick Settings tile \"Jarvis\" (swipe down, edit tiles, add it) and an icon shortcut (long-press the Jarvis icon, \"Listen\"). One tap opens Jarvis and starts the mic. Never works while Jarvis is stopped or locked | BUILT | NOT YET (Java not compiled) |
| 39 | Background mic TEST (Settings > "Background listening test"): Start test, a notification with Stop stays visible, ends by itself after 8 h. It only COUNTS how often it heard "Jarvis", how often with the screen off and with the app closed. It keeps no words, sends nothing to the page or server, does no phone action. Starts only after your finger tap, never while Jarvis is stopped or locked. Stop everything ends it. Opening the mic in the app ends it (one listener at a time). The card also shows phone brand, Android version, battery limit and says if Android killed it | BUILT | NOT YET (Java not compiled; needs one day on the phone) |
| 56 | Home tab: a Chat / Home switch under the header. Home shows the orb (gold = ready, pulsing = listening, red = stopped), greeting and date, today's reminders and money entries due today or late, quick buttons (Talk, Briefing, Reminders, Ledger, Settings, Stop everything) and the phone and server numbers. New server route `/today` | BUILT | NOT YET (page syntax checked only) |
| 41 | Task engine (server): "Chrome kholo aur neeche scroll karo phir back jao" is split into up to 6 steps from the fixed action list (open app, back, home, scroll, click, torch, volume, settings page, which app is open, lock only as the last step). No AI is used to plan. Table `tasks` with the 10 states. Restart rule: when the server starts, RUNNING and VERIFYING tasks become FAILED with a note (also after 10 minutes of no news). Steps that need your Yes (send, pay, delete) or that type text or touch passwords are NEVER put in a task: Jarvis says so and does nothing | BUILT | NOT YET (server syntax checked only) |
| 42 | Task runner (app): runs the steps in Java one at a time with Jarvis in the background. Before every step it checks Stop, Phone control, app lock and Cancel. After every step it checks the step really did something (a click or scroll that changed nothing counts as failed). It stops at the first failed step. Notification with a Cancel button while it runs. Result (steps with tick or cross, and why it stopped) comes back to the chat when you return. The server then sets COMPLETED, PARTIAL, FAILED or CANCELLED from what the app really reported. Stop everything ends it at once | BUILT | NOT YET (Java not compiled) |
| 55 | Conversation mode (app only): button "Conversation" starts it. After each answer the phone mic opens by itself (0.5 s pause so it does not hear Jarvis). Ends after 2 silent rounds, on "bas" or "stop", after 20 turns, on Stop everything, or if the app goes to the background. Phone speech service may beep | BUILT | NOT YET (page and Java not run) |
| 54 | Smart memory: when you state a personal fact ("mere bhatije ka naam Arman hai") Jarvis answers and shows "Should I remember this?" Yes / No. Only your finger tap on Yes saves it (normal "yaad rakho" path, so passwords and OTPs are still refused). Questions are never offered | BUILT | NOT YET (server tests pass; page JS syntax checked only) |
| 43 | Phone checklist: section 11.8 is now one table, one row per Part (what to do, what you should see). Docs only, no code, no test file | BUILT | NOT YET (nothing to run) |
| 51 | Voice engine (server): new `voiceengine.py`. Two voices, TONY (conversation) and JARVIS (information, task result, reminder, briefing, alert). Six intents, a policy table, JARVIS when unsure. `/tts` without `voice` now takes `intent` or `profile` and sends the header `X-Voice` (who spoke). New routes `GET /voice` and `POST /voice/set`; settings live in `voice.json` (survives restart, gitignored). Old `/tts` with `voice` still works (classic). Hindi has only one male Edge voice (Madhur), so in Hindi the two differ by depth and speed; in English they are different voices (Tony: Prabhat, JARVIS: Ryan) | BUILT | NOT YET (Python syntax checked only) |
| 52 | Voice settings (page): Settings > "Voice personality" with a Tony card and a JARVIS card (Depth, Speed, Test, Use always), Auto routing switch, a switch for the classic voice, and a badge that shows the voice that really spoke (Tony, JARVIS, classic, or phone voice if the online voice failed). Changing a setting stops the voice that is speaking. Reminders, briefing, task results and photo answers now send an intent | BUILT | NOT YET (page JS syntax checked only) |
| 44 | Repeat reminders and birthdays (server): say "roz subah 9 baje chai yaad dilana", "har hafte", "har mahine", "har saal" (or daily, every week, monthly, yearly) and the reminder repeats; one new column `rep` in `reminders` (old rows untouched). "Faisal ka birthday 15 Nov" saves a yearly reminder at 09:00 and a note in People; "birthdays" lists them; "my reminders" now only lists (before it could create a new reminder by mistake). Phone calendar (app): "my calendar", "aaj ke events", "events tomorrow", "events this week" read title, time and place for up to 14 days through the new `CalendarInfo.java`; permission READ_CALENDAR asked when first used; a Calendar row in the privacy dashboard; never saved, not sent to the AI | BUILT | NOT YET (Python logic run here; Java not compiled; page JS syntax checked only) |
| 45 | Richer briefing: "briefing" now also shows today's phone calendar events (app only, only when you type or say briefing, never at the automatic morning briefing so no surprise permission prompt). Suggestions: up to 3 a day in total, three fixed rules (late ledger entries, a birthday in the next 3 days, reminders tomorrow), no AI. The automatic morning briefing stays silent in quiet hours (default 22:00 to 07:00). Switch by chat: `suggestions off/on`, `money|birthday|tomorrow suggestions off/on`, `quiet hours 22 to 7`, `briefing settings`. Settings live in `brief.json` (gitignored, survives restart). **Also in this zip:** battery bar is green when full and red only when low (20 percent or less; amber 40 or less); Settings > Privacy card now explains how to turn on "Jarvis screen reader" when Android greys it out (Restricted settings: Jarvis app info > 3 dots > Allow restricted settings) | BUILT | NOT YET (Python logic run here; page JS syntax checked only) |
| 46 | Routines: a routine is a name for a task sentence. `routine banao subah: Chrome kholo aur neeche scroll karo` saves it (2 to 6 steps, checked when saved: no send, pay, delete, typing; lock only last). Run it with `routine subah` (or `run routine subah`, `subah routine chalao`). `my routines` lists, `routine delete subah` removes; max 10; same name replaces. Running plans the sentence again through the task engine, so the Phone control switch, app-only rule, Stop, app lock and per-step checks apply every time and the run shows in task history. New table `routines` (name and sentence only). Home tab has a Routines button. No time trigger yet (use a reminder to remember it) | BUILT | NOT YET (Python logic run here; page JS syntax checked only; steps run by the Part 42 Java runner, not compiled) |
| 47 | Backup: Settings > Backup card. Type a passphrase (8+ characters), tap Make backup: memory, people, pending reminders (with repeat), open ledger entries and routines go into ONE file `Jarvis_backup_DATE.jbk` in Downloads, locked with OpenSSL AES-256 (pbkdf2, 200000 rounds), no home-made encryption. Chat history only if you tick the box. API keys, pairing, tasks and paid/old items are never in it. Restore: type the passphrase, tap Restore on a file, see a preview (how many NEW rows per kind), then tap Yes. It only ADDS what is new, never overwrites or deletes; password/OTP/PIN words are skipped; People and Memory keep their limits. Works on a new phone after pairing. Wrong passphrase or a damaged file is refused (a SHA-256 check inside the file catches damage, it is not protection against someone who knows your passphrase). Delete everything: say `delete everything`, Jarvis explains, then only the exact capital-letter phrase DELETE ALL MY JARVIS DATA wipes memory, people, reminders, ledger, routines, tasks and chat (keys and pairing stay). The passphrase is never typed in chat, never saved, never logged. Needs once: `pkg install openssl-tool` | BUILT | NOT YET (Python logic run here with real OpenSSL; page JS syntax checked only) |
| 50 | System card in Settings: phone RAM, storage, battery, heat, Jarvis server memory and CPU, uptime, internet. Server tests pass; page JS syntax checked only | BUILT | NOT YET |
Total: about 40 files and about 2,650 lines of code. Known limits (not bugs): Hey Jarvis works only while the app is open; mic in Chrome and in the app use different engines; the real actor's voice cannot be copied, only approached with the free voices; Android Files app may show empty ghost entries for zips that Termux already moved to `~/.jarvis_done`.

## 7. What to do next
0. **What to type on the pairing screen:** open the Termux app, find the last line `PAIRING CODE: 123456` and type those 6 numbers. The code works for 10 minutes. Old or missing? Tap "Show code in Termux" and look again.
   **Pairing keeps coming back because every GitHub build used a new random signing key, so Android refused the update and you had to uninstall (that wipes the pairing). Part 36 fixes it with one fixed key. Do this ONCE: uninstall the old Jarvis app, install the new APK, pair one last time. After that, updates install over the app and the pairing stays.**
   Termux closing by itself: Android kills it to save battery. Settings > Apps > Termux > Battery > No restriction; keep the Termux notification (wake lock) visible; install the Termux:Boot app for restarts.
1. Download the zip, wait for "pushed" in the app header, run **Build APK** on GitHub, install it. If the build fails, send `build-log`.
2. Test Parts 27, 28 and 29 with the list in section 11.8, plus the old cheat sheet. Report what fails with a screenshot.
3. Parts 30 to 39, 41 to 47, 50, 51, 52, 54, 55 and 56 are BUILT. Download the zip, wait for "pushed", run **Build APK**, install, then test with section 11.8. Next Part: **48**, then the rest in order (section 11.6, Build order line). Dual voice: Parts 51 and 52 are built, Part 53 is planned in section 11.6b. Section 11 is the full plan. Batches A to G in section 10 are merged into it.

## 8. Cheat sheet (type or say)
| Say or type | What happens |
|---|---|
| Chrome kholo aur neeche scroll karo phir back jao (2 to 6 steps joined by aur / and / phir / then) | One task: steps shown, run one by one with checks, Cancel in the notification, result in chat (app only, switch ON). Send, pay, delete or typing steps are refused inside a task |
| remember this: ... / what do you remember / forget 1 | Memory (no passwords or OTPs). Also: say "mere bhatije ka naam Arman hai" and tap Yes on "Should I remember this?" |
| phone lock kar do / lock the phone | Locks the phone (app only, switch ON). Never unlocks |
| Chrome kholo / go back / peeche jao / go home / neeche scroll karo / Settings dabao / type hello / kaun sa app khula hai | Phone control (app only, switch ON). Never types passwords, OTPs, PINs or card numbers |
| app ka kaam kahan tak pahuncha / next part kaun sa | Jarvis reads the plan in this README and tells you built, remaining and next Parts |
| remind me tomorrow 9 am to ... / my reminders | Reminders (notification in the app) |
| roz subah 9 baje chai yaad dilana / every week ... / har mahine ... / har saal ... | Repeating reminder (daily, weekly, monthly, yearly). `my reminders` shows a repeat mark |
| Faisal ka birthday 15 Nov / birthday of Sara on Mar 3 / birthdays | Yearly reminder at 09:00 plus a People note; list of birthdays |
| delete everything | Explains, then wipes your Jarvis data only after you type the exact capital-letter phrase it shows. Backups: Settings > Backup (never type the passphrase in chat) |
| routine banao subah: Chrome kholo aur neeche scroll karo / routine subah / my routines / routine delete subah | Saved multi-step task (app only, switch ON). Same safety checks on every run |
| suggestions off / money suggestions off / quiet hours 22 to 7 / briefing settings | Controls the 3-a-day suggestions in the briefing |
| my calendar / aaj ke events / events tomorrow / events this week | Phone calendar events (app only, permission asked first time, not saved) |
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
| stop listening (also: stop listening completely, mic band, sunna band) | Mic, Hey Jarvis, screen reading and photo picker off, saved. Tap "Turn mic on" to restart |
| clear history | Delete the chat history |

## 9. Security and privacy
- Server listens on 127.0.0.1 only. Only the page from that address may call it (Host and Origin are checked). Pairing code: 10 minutes, one use, locks after 5 wrong tries.
- Token is stored as a hash on the server. Keys are stored in `backend/keys.json` (owner-only file, never in Git, never sent back to the browser).
- Passwords, OTPs and PINs are never saved. Calls, contacts and screen text are never saved. Chat history is saved on the phone only; "clear history" deletes it.
- These go to the internet only when you use them: your question to the AI provider; voice text to Microsoft (online voice); photo to the vision AI; location to OpenStreetMap; screen text to the AI for that one answer.
- Part 27: the page can use only the microphone, only from the Jarvis address, only after Android allowed it. Camera and other requests are denied. Plain http works only for 127.0.0.1. Microphone, location and notification permissions are asked when first used, not at app start.
- Part 28: Stop is stored in Java. While stopped, the app will not listen, read the screen or open the photo picker, even if the page asks. Only a real finger tap on "Turn mic on" can switch Jarvis on again. A photo or camera app that is already open cannot be closed by Jarvis.
- The Android app only opens the Jarvis address, has no file access, and is excluded from cloud backup. Accessibility is used only to read text when you ask.
- Zips: only put zips you trust in Downloads. A zip can replace any file in the repo, including scripts.

## 10. Future roadmap (NOT started, not part of the MVP)
> Update 15 Nov 2026: the batches A to G below are now Parts 27 to 49 in section 11 (map in 11.7). Section 11 is the plan to follow.
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

## 11. MASTER PLAN: real phone control (Parts 27, 28 and 29 are built, not phone tested. The rest is plan only)
Audit date: 15 Nov 2026. Written from the real repo files, not from old README claims.

### 11.1 Goal in simple words
Hussain speaks in Hindi, English or Hinglish. Jarvis understands the request, opens apps, reads the screen, taps, scrolls, types, goes back, locks the phone, opens settings, and runs safe multi-step jobs. It always says what really happened. It never bypasses Android security. One Stop command switches everything off. Everything reuses the existing server, database and app. No second server, no second database, no second scheduler.

### 11.2 Audit: what exists today (file and line)
Read in full: `app.py`, `memory.py`, `web.py`, `screen.py`, `MainActivity.java`, `ScreenService.java`, `Ears.java`, `NotifyService.java`, `AndroidManifest.xml`, `screen_service.xml`, `build.gradle`, `apk.yml`, `run.sh`, `scripts/sync.sh`, and the stop, privacy, wake and screen parts of `index.html`. Only skimmed (will be read in full before the Part that touches them): `calls.py`, `place.py`, `phone.py`, `see.py`, `remind.py`, `ledger.py`, `brief.py`, `tts.py`, `autostart.py`, `PhoneInfo.java`, `ContactsInfo.java`, `test_app.py`.
| Wish | Real state | Evidence |
|---|---|---|
| Open an app | MISSING | The page bridge has only calls, contact, listen, stopListen, screen, phoneInfo, saveToken (`MainActivity.java` 70-99) |
| Read screen | Built, NOT phone tested | `ScreenService.java` 19-47; password fields skipped at line 37; 3000 characters max; the app goes to the background and waits 6 seconds (`MainActivity.java` 88-96) |
| Tap, scroll, type, back, swipe | MISSING | `ScreenService` ignores all events (line 15) and has no click, scroll, text or global action. `screen_service.xml` has only window-change events and read access |
| Lock phone | MISSING | No lock code. Android lock-screen action needs Android 9 (API 28). App minSdk is 24 (`app/build.gradle` line 5) |
| Lock the Jarvis app | MISSING | No biometric code, no androidx.biometric |
| Settings, volume, flashlight, brightness | MISSING | Nothing in any Java file |
| Stop listening completely | PARTIAL | Only page JavaScript (`index.html` 81 and `stopAll` 235). The native `listen` (`MainActivity.java` 82) never checks a stop flag. The 6 second screen wait (line 94) cannot be cancelled. No camera or screen state exists |
| Privacy bar | Built, shows page flags only | `index.html` `pv()`. It shows what the page thinks, not what services really do |
| Permission dashboard | MISSING | No permission status code |
| Hey Jarvis | Built, works only while app is open, NOT phone tested | `onPause` stops it (`MainActivity.java` 119-122). It uses the Google recognizer, not a wake-word engine |
| Background microphone | MISSING | No microphone foreground service (`AndroidManifest.xml` 12-13 has only data-sync) |
| Understand natural speech | PARTIAL | Chat chain is keyword handlers (`app.py` 323-338). The AI only answers chat. It cannot choose an action |
| Multi-step tasks | MISSING | No task table, no states, no cancel |
| Memory, people, calls, location, camera, phone check, ledger, reminders, briefing, web | Built, NOT phone tested (see section 6) | `app.py` 311-351 and helper files |
| Line count claim | README was wrong | README said about 2,650 lines. The repo has about 2,000 lines in about 30 files (README, gradle files and images not counted). Plan numbers below use the real count |

### 11.3 Security findings (to fix, in order)
| # | Finding | Evidence | Fixed in |
|---|---|---|---|
| S1 | WebView grants every permission request and always grants location | `MainActivity.java` 67 and 60 | Part 27 (BUILT, not phone tested) |
| S2 | Plain http allowed for the whole app | `AndroidManifest.xml` 15 | Part 27 (BUILT, not phone tested) |
| S3 | Mic, notification and location asked at app start, not when used | `MainActivity.java` 36 | Part 27 (BUILT, not phone tested) |
| S4 | Stop exists only in page JavaScript. Native code can still listen | `index.html` 235, `MainActivity.java` 82 | Part 28 (BUILT, not phone tested) |
| S5 | Bridge methods have no stop or lock check. New power (click, lock) must be checked in Java, not in the page | `MainActivity.java` 70-99 | Part 28 (stop flag checked in Java, BUILT); Part 36 for app lock |
| S6 | Screen text goes to the AI with only password fields skipped and a prompt rule. No OTP or card removal in code. `memory.SECRET` has only words (password, otp, pin, cvv), no card number pattern | `ScreenService.java` 37, `screen.py` 13-14, `memory.py` 4 | Part 32 |
| S7 | ANY file named `Jarvis_part*.zip` in Downloads is unzipped into the repo and the server restarts. Another app with storage access could drop a zip and run code in Termux | `run.sh` 16-22, `scripts/sync.sh` 14-21 | Not by zip (scripts cannot change by zip). Owner decision D5 |
| S8 | Pairing token is in plain app storage (backup is off, so risk is low) | `MainActivity.java` 99, `NotifyService.java` 44 | Part 36 (optional) |
| S9 | `ScreenService` will gain click power. It is exported as every accessibility service is, protected by the Android bind permission | `AndroidManifest.xml` 17 | Parts 33-34 rules |
| S10 | A request with no Origin header is allowed (needed by the reminder service, token still required). A changed HOST turns the check off | `app.py` 162-165 | Keep, document |
| S11 | `web.py` checks the address, then opens it again. Small DNS gap | `web.py` 9-28 | Later, low |

### 11.4 Android limits (honest list, to be verified on the phone)
| Wish | Android reality | What Jarvis will do |
|---|---|---|
| Lock phone | Accessibility global lock action, Android 9+. Needs the Jarvis accessibility switch ON. Some makers may block it | Call it, then check the screen state. If still on, say it failed. Never unlock |
| Tap, scroll, type, back | Accessibility node actions. Work only if the app shows its controls. Banking apps, games and some apps show nothing | Use controls by meaning, re-find them before acting. If not found, ask Hussain. Say "this app does not allow it" |
| Swipe | Needs a gesture permission, fragile | Fallback only, with a confirm |
| Wi-Fi and Bluetooth on/off | Apps cannot switch them silently on new Android | Open the right settings or panel and explain the one tap |
| Brightness | Needs the special "modify system settings" permission | Default: open Display settings (decision D1) |
| Flashlight, volume | Allowed without risky permission | Do it, then check the state |
| Do Not Disturb | Needs notification-policy access | Open the access page and explain |
| Close other apps | Android does not allow it | Say so, show the safe steps |
| Background microphone | Android 14+: needs a microphone foreground service, a visible notification, and it must start while the app is visible. Makers may kill it | Test first (Part 39). No promise until it works on this phone |
| Wake word with screen off | The Google recognizer may not run there | Part 39 measures it. Alternative: Quick Settings tile and shortcut (Part 38) |
| Voice on lock screen | Jarvis may listen, but must not do sensitive actions while locked | Check lock state first |
Phone brand and Android version are NOT known yet (decision D4).

### 11.5 Architecture (reuse, no duplicates)
- New `backend/actions.py`: first a cheap Hindi, English, Hinglish grammar ("WhatsApp kholo", "neeche scroll karo"). If nothing matches and it looks like a command, the AI may only return a JSON action from a FIXED list. The server checks the action name and arguments. The AI never gives code, shell, coordinates or package names that were not found on the phone.
- `/chat` returns an optional `action` next to `reply`. The page runs it through ONE new bridge method, `JarvisApp.act(json)`. Java checks stop, lock and permission flags itself.
- Risk levels: READ (open app, open settings page, read screen when asked) runs. CHANGE (scroll, type, tap normal button) runs after the plan is shown. SENSITIVE (send message, delete, pay, buy, install, permission, account change) needs a preview and an explicit yes. BLOCKED (password field, OTP, PIN, banking data) never runs.
- Screen text and web text are DATA. An action may only come from Hussain's own message in the same turn.
- Master switch "Phone control" starts OFF. It is shown on the privacy dashboard.
- Task engine `tasks.py` uses the same SQLite file (one new table, nothing removed). Page runs the steps because the phone actions are in the app. Each step is verified before the next.
- Task states: CREATED, PLANNING, WAITING_FOR_PERMISSION, WAITING_FOR_CONFIRMATION, RUNNING, VERIFYING, COMPLETED, PARTIAL, FAILED, CANCELLED. After a server or phone restart a RUNNING task becomes FAILED with a note. A risky step is never repeated by itself.

### 11.6 Parts (plan; * = new file). "With tests" = Python logic run in Termux. "Without tests" = Android Java: GitHub build plus Hussain's phone.
| Part | What | Files | Lines | Tests | Benefit |
|---|---|---|---|---|---|
| 27 DONE | Close WebView and manifest holes: permission checks, local-only http, ask permissions when used | MainActivity, AndroidManifest, res/xml/network_security_config.xml* | ~50 | Without | The page cannot get mic, camera or location by tricks |
| 28 DONE | Real Stop: one `Privacy.java` holds mic, wake, screen, camera state. Stop cancels all in Java. Voice cannot turn mic back on, only a visible button | Privacy.java*, MainActivity, Ears, index.html | ~140 | Without | "Stop listening completely" really stops everything |
| 29 DONE | Privacy dashboard: ON/OFF per feature, permission given vs service running, last used, small log (feature and time only), settings buttons, server-offline banner and auto-reconnect | index.html, Privacy.java, app.py, MainActivity | ~140 | Without | One screen shows what Jarvis can do and is doing |
| 30 DONE | Command layer: Hindi/English/Hinglish grammar plus limited AI fallback, master switch OFF by default | actions.py*, app.py, index.html | ~150 | With | Jarvis understands "WhatsApp kholo" without guessing |
| 31 DONE | App launch: list launchable apps, fuzzy name, ask when two match, never open unknown | Apps.java*, MainActivity, AndroidManifest, index.html, actions.py | ~110 | Without | "Chrome open karo" works safely |
| 32 DONE | Better screen reading: visible buttons, fields, scroll areas; remove OTP, card, PIN text before sending; honest message when an app shows nothing | ScreenService, screen.py, screen_service.xml, index.html, MainActivity | ~90 | With (redaction), Java without | Screen help without leaking secrets |
| 33 DONE | Risk and confirm rules: preview and explicit yes for send, delete, pay, buy, install, account; block password fields | actions.py, index.html | ~100 | With | No dangerous action without Hussain's yes |
| 34 DONE | Safe screen actions: click, scroll, type in a field, back, home, current app; re-find the control before acting; verify the result; swipe only as confirmed fallback | ScreenService, MainActivity, index.html, screen_service.xml | ~165 | Without | "Is button ko dabao", "neeche scroll karo", "peeche jao" |
| 35 DONE | Lock phone with the Android lock action, check the result, honest failure | ScreenService, MainActivity, index.html, actions.py | ~60 | Without | "Phone lock kar do". Never unlocks |
| 36 DONE | Lock the Jarvis app with the real Android fingerprint, face or phone PIN prompt. Bridge refuses while locked. Turn off only after authenticating. Optional: token in Android Keystore | AppLock.java*, MainActivity, app/build.gradle, index.html | ~140 | Without | Nobody else can use Jarvis on your phone |
| 37 DONE | Settings help: open Wi-Fi, Bluetooth, location, sound, battery, app permissions, notifications pages; flashlight, volume; explain when Android blocks a change | PhoneSettings.java*, MainActivity, actions.py, index.html | ~140 | Without | Settings by voice, no hacks, no false "done" |
| 38 DONE | Quick Settings tile and app shortcut to start listening | JarvisTile.java*, AndroidManifest, res/xml/shortcuts.xml*, MainActivity | ~70 | Without | Hands-free start even if wake word is weak |
| 39 DONE | Background mic test: microphone foreground service, notification with Stop button, battery check, no sensitive action while locked | ListenService.java*, AndroidManifest, MainActivity, Privacy, index.html, Ears | ~140 | Without, plus one day phone test | We learn if "Hey Jarvis" works with the app closed |
| 40 | OPTIONAL: offline wake-word engine, only if Part 39 shows the Google recognizer is not enough | decided after 39 | ~200 | decided later | Reliable hands-free. Bigger app and more battery, needs Hussain's OK |
| 41 DONE | Task engine backend: tasks table, 10 states, steps, restart rule | tasks.py*, app.py | ~180 | With | Multi-step jobs are tracked honestly |
| 42 DONE | Task runner in the page: shows steps, runs them through the bridge, verifies each, Cancel button, stops on failure | index.html, MainActivity, ScreenService, Privacy | ~120 | Without | "Chrome kholo aur ..." sequences, cancel any time |
| 43 DONE | Phone checklist table, regression list of old features. No test_app.py (Hussain's no-tests rule, 16 Nov 2026) | README | ~40 | Without | We know what to check on the phone before more features |
| 44 DONE | (old Batch B) Repeat reminders, birthdays, phone calendar | remind.py, people.py, calls.py, app.py, CalendarInfo.java*, MainActivity, Privacy, AndroidManifest, index.html | ~250 (real: about 130) | Python logic run, Java without | Birthdays and repeat jobs are remembered |
| 45 DONE | (old Batch C) Richer briefing, max 3 suggestions a day, quiet hours, each can be switched off | brief.py, app.py, index.html | ~200 (real: about 140) | With | One useful morning summary, not noise |
| 46 DONE | (old Batch D, smaller) Routines = saved task lists. Uses the task engine, no second system | tasks.py, app.py, index.html | ~115 (real: about 75) | With | One command runs a safe set of steps |
| 47 DONE | (old Batch E) Encrypted backup, restore with preview, delete everything | backup.py*, app.py, index.html | ~210 (real: about 210) | With | Memory is safe and can move to a new phone |
| 48 | (old Batch G) Share to Jarvis, handoff summary for Claude or ChatGPT, lost-phone steps card | AndroidManifest, MainActivity, index.html, app.py | ~180 | Without | Official sharing only, no private sessions |
| 49 | OPTIONAL, risky (old Batch F) Notification summary for chosen apps, clipboard button | NotifySummary.java*, MainActivity, AndroidManifest, index.html, app.py | ~350 | Without | Day summary. Needs special notification access |
| 50 DONE | Live system card (like the PC screenshot): RAM used/free, storage, battery and heat, Jarvis server own memory and CPU, uptime, net online. New `/stats` route, refreshed every 5 s only while the card is open. Honest "not available" if Android blocks a number | sysinfo.py*, app.py, index.html | ~110 | With (Python) | Hussain sees what Jarvis and the phone are using |
| 51 DONE | Voice Personality Engine, backend: intent classifier (CONVERSATION, INFORMATION, TASK_CONFIRMATION, REMINDER, BRIEFING, ALERT), policy table, JARVIS fallback, two voice profiles, `/tts` takes `intent` or `profile` | voiceengine.py*, tts.py, app.py | ~170 | With | The right voice is chosen by intent, not by keywords |
| 52 DONE | Voice Personality settings: Tony and JARVIS cards, Auto routing ON, manual override, Test Tony, Test JARVIS, active-voice badge, saved in `voice.json` on the server (survives restart), stop and switch while speaking | index.html, app.py | ~160 | Without (page) plus Python route tests | One clear place to control both voices |
| 53 | Second voice provider only if the Edge test shows the two voices are too alike: Google Cloud Chirp 3 HD, key kept in `keys.json`, Edge stays as fallback | tts.py, app.py, backend/.env.example | ~120 | With, needs Hussain's key | Two truly different voices |
| 54 DONE | Smart memory: when you say a personal fact ("mere bhatije ka naam Arman hai"), Jarvis answers and shows "Yaad rakhun? Yes / No". Only your own tap on Yes saves it, in the existing `memories` table (limit 100, never passwords, OTPs, PINs). Later "mera bhatija kaun hai" is answered from memory. Needed because today Jarvis saves only after "yaad rakho: ..." | memory.py, app.py, index.html, test_app.py | ~75 | With | Jarvis learns names and facts without typing "yaad rakho" |
| 56 DONE | Home dashboard (inspired by the PC Jarvis screenshot): a Home tab with the orb, today's reminders and events, phone and server stats, quick buttons. Chat stays the main screen. Phone layout: one column, cards that scroll | index.html, app.py | ~130 | Without (page) | One glance shows the day and the phone |
| 55 DONE | Conversation mode: after Jarvis finishes speaking, the mic opens by itself, so you can answer without tapping the mic. Visible "Conversation ON" bar. Ends after 2 silent rounds, on "bas" or "stop", or on Stop everything. Works only while the app is open (background listening is tested in Part 39) | index.html, Ears.java, MainActivity | ~80 | Without | Natural back and forth talk |

**Totals** (code lines added or changed, README excluded):
| Group | Parts | New files | Lines |
|---|---|---|---|
| Phone control core | 27 to 39, 41 to 43 (16 Parts, 43 is docs only) | 10 | about 1,900 |
| Old batches B to E and G | 44 to 48 (5 Parts) | 2 | about 950 |
| Required total | 21 Parts | 12 | about 2,800 |
| Optional (40 and 49) | 2 Parts | about 4 | about 550 |
| Stats card and dual voice (Parts 50 to 53) | 4 Parts | 2 or 3 (sysinfo.py, voiceengine.py, voice.json is data) | about 560 |
| Repo today | - | - | about 2,000 lines, about 30 files |
| Repo after required Parts | - | - | about 4,800 lines, about 42 files |
| Repo after everything | - | - | about 5,400 lines, about 46 files |
Estimates are rough (plus or minus 25 percent). Real numbers go into this table after each Part.


**Build order (next first):** 48, 47, 48, then 53 only if the two voices sound too alike. Optional: 40, 49 (40 is decided after the Part 39 phone test). Optional: 40, 49 (40 is decided after the Part 39 phone test).

### 11.6b Dual voice personality plan (added 15 Nov 2026; Parts 51 and 52 built 16 Nov 2026, Part 53 not built)
Goal: two default voices that switch by themselves. Default from the first start: Tony and JARVIS with Auto routing ON (Hussain asked for this on 16 Nov 2026); the classic voice is only used if he switches it on in Settings. TONY = conversation (confident, witty, Hinglish). JARVIS = information, tasks, reminders, briefings, alerts (calm, deep, precise). No cloning of Rajesh Khattar or Atul Kapoor. Original or licensed voices only.
**What exists today (read from the repo):** `backend/tts.py` (35 lines) runs `edge_tts` with a fixed list `VOICES` (line 4): en-GB-Ryan, en-IN-Prabhat, hi-IN-Madhur, en-IN-Neerja, hi-IN-Swara. `app.py` route `POST /tts` (line 292) returns mp3. `index.html`: `neural()` (line 147) plays it, `speak()` (156) falls back to the browser voice, `#voice` and `#pre` select a voice and a preset (lines 41 to 42), `stopAll()` (262) stops sound, saved in `localStorage` (`jvoice`). There is no intent routing and no server-side voice settings.
**Two real profiles today? NO.** Edge has only one Hindi male voice (Madhur). Khattar, Rolex and Jarvis studio are Madhur with different pitch and speed. That is one voice in two moods, not two voices. Prabhat is male but Indian-English and reads Hindi badly.
**Rules for Parts 51 to 53:** reuse `tts.py` and `/tts`; no second server, no new database table, no new Android permission; keys only in `keys.json`; JARVIS is the fallback when intent is unclear; the voice that speaks is the voice that is shown; if a provider fails, fall back to Edge, then to the browser voice, and show which one spoke.
**Provider choice:** step 1 (Part 51 and 52) uses Edge only: Tony = Madhur, normal pitch, a little faster; JARVIS = Madhur, lower and slower. Free, but the two will sound related. Step 2 (Part 53), only if Hussain agrees: Google Cloud Chirp 3 HD, which has several male Hindi voices. List price checked 15 Nov 2026: about 30 USD per 1 million characters, and free monthly amounts differ by source, so check the account before using. It needs internet, billing enabled and an API key. Must be tested for Hinglish before it is chosen.
**Cost and internet:** Edge is free and needs internet. Google is pay as you go (a 200 character reply is about 0.006 USD at list price). Offline fallback is the browser voice, not Tony or JARVIS.

### 11.7 Order and map of old batches
Why this order: Parts 27 to 29 come first because every later power needs a safe base and a real Stop. 30 before 31 and 37 because they use the command layer. 32 and 33 before 34 because clicking needs safe reading and confirm rules first. 35 and 36 before background voice. 41 and 42 only after single actions work. Real phone tests between groups.
| Old name | Now |
|---|---|
| Batch A (privacy dashboard, server health) | Parts 28, 29 |
| Batch B (recurring, birthdays) | Part 44 |
| Batch C (briefing, suggestions) | Part 45 |
| Batch D (routines, task history) | Parts 41, 42 and 46 |
| Batch E (backup) | Part 47 |
| Batch F (notifications, clipboard) | Part 49 (optional) |
| Batch G (share, handoff, lost phone) | Part 48 |

### 11.8 Phone checklist (Part 43). Try each row once on the phone. A bug = one small fix zip.
| Part | Do this | You should see |
|---|---|---|
| 27 | Open the app, tap mic the first time | Android asks for the mic only now; the page cannot open another site |
| 28 | Say "stop listening completely" | Mic icon off; saying "Jarvis" does nothing; tap Restart and it works |
| 29 | Accessibility OFF; then stop Termux, then start it | Dashboard shows OFF; red offline banner, then it clears |
| 30 | Say "WhatsApp kholo", then a nonsense phrase | WhatsApp opens; nonsense does nothing |
| 31 | "Chrome kholo", "xyz app kholo", a name that fits two apps | Chrome opens; "not found"; Jarvis asks which one |
| 32 | Open a screen that shows a code, ask Jarvis to read it | The code is hidden |
| 33 | "message bhejo" | Preview shown, waits for your Yes |
| 34 | In Settings: "neeche scroll karo", "peeche jao" | Scrolls, goes back |
| 35 | "phone lock kar do" | Screen locks, or an honest failure |
| 36 | App lock ON, close and open the app | Real Android fingerprint, face or PIN prompt |
| 37 | "Bluetooth settings kholo", "torch on karo" | Page opens; light is on |
| 38 | Quick Settings tile | Opens Jarvis and starts the mic |
| 39 | Background test, screen off for 10 min | Card shows counts and battery use |
| 41-42 | "Chrome kholo aur neeche scroll karo phir back jao" | Chat lists 3 steps; notification has Cancel; ticks and crosses when you return |
| 41-42 | Same task, tap Cancel; then kill the server; then "Chrome kholo aur send dabao" | Cancelled; marked failed; refused |
| 50 | Settings, System card | RAM, storage, battery, heat, uptime |
| 51-52 | Settings > Voice personality: tap Test Tony, then Test JARVIS | Two different sounds; the badge says TONY or JARVIS. In Hindi the difference is depth and speed only |
| 51-52 | Say "hello" in chat with Speak replies ON, then set a reminder for 1 minute | Chat reply = Tony; reminder = JARVIS |
| 51-52 | Auto routing OFF, tap Use always on Tony, ask something; then switch Tony and JARVIS OFF | Tony speaks every reply; then the classic voice and presets work as before |
| 54 | "mere bhatije ka naam Arman hai" | Asks "Should I remember this?"; saves only on Yes |
| 55 | Tap Conversation | Mic reopens by itself; ends on "bas" |
| 56 | Open Home tab | Orb, today's list, quick buttons, numbers |
| 47 | Settings > Backup: type a passphrase, tap Make backup; then type it again and tap Restore... on the file | "Saved in Downloads: Jarvis_backup_...jbk" with counts; restore shows "0 new" because everything is already here; a wrong passphrase is refused. (Do not test "delete everything" unless you have a backup.) First time may say openssl is missing: run `pkg install openssl-tool` |
| 46 | Turn Phone control ON. Say "routine banao subah: Chrome kholo aur neeche scroll karo", then "my routines", then "routine subah" | Saved; listed; Chrome opens and scrolls, result in chat. With the switch OFF it says so and does nothing |
| 45 | Say "briefing", then "briefing settings", then "suggestions off" | Calendar events and up to 3 suggestions; settings reply; no suggestions after off. Home > Phone and server: battery bar is not red when high |
| 44 | Say "roz subah 9 baje chai yaad dilana", then "my reminders"; say "Faisal ka birthday 15 Nov", then "birthdays"; then "my calendar" | Reminder shows a repeat mark; birthday listed; first calendar ask shows the Android calendar permission, then your events or "no events" |
| All | After every build: chat, 5 providers, memory, reminders, ledger, voice, APK build | Nothing old is broken |

### 11.9 Decisions (a default is set; say OK or change it)
- D1 Brightness: default is to open Display settings (no extra permission). Alternative: allow "modify system settings".
- D2 App lock: default is Android's own prompt only. Jarvis will not keep its own PIN.
- D3 Phone control master switch starts OFF.
- D4 Needed before Part 35 and 39: phone brand and Android version (Settings > About phone).
- D5 Zip trap (S7): later, Hussain decides if he wants a one-time script that checks zips.

### 11.10 Risks and rollback
Every Part is its own zip and its own commit. To undo a Part: GitHub > the commit > Revert. Older APKs stay in Actions artifacts. The only database change is one new `tasks` table (Part 41), nothing is removed. Phone control can be switched OFF without removing code. Rules that never change: no root, no lock-screen bypass, no hidden recording, no secret saving, no payments, no messages without a confirm tap, no OWL1 changes.

### 11.11 Progress (estimated vs actual lines, code only)
| Part | Status | Estimated | Actual | Phone test |
|---|---|---|---|---|
| 27 | BUILT | ~50 | 36 (`MainActivity` 26, manifest 2, new `network_security_config.xml` 8) | NOT YET. Java not compiled here, so the GitHub build is the first compile test |
| 28 | BUILT | ~140 | 94 (`Privacy.java` 58 new, `MainActivity` 19, `index.html` 14, `Ears` 3) | NOT YET |
Checks that were run for 27 and 28: XML parse, Java bracket balance, page script syntax, Python syntax. Nothing else was run (Not run: Java compile, phone test).
What changes for Hussain: the first mic tap asks for the microphone; the first "where am I" asks for location and may answer "unavailable" once, so ask again; the notification question comes once after pairing.
| 29 | BUILT | ~140 | 109 (`Privacy.java` +43, `index.html` 35, `MainActivity` 22, `NotifyService` 6, `app.py` 2, `Ears` 1) | NOT YET. Only the `/status` uptime field was run (server started, field checked: PASS). Java and page are Not run on a phone |
| 30 | BUILT | ~150 | about 120 (`actions.py` 91 new, `app.py` 10, `index.html` about 8, tests 12) | NOT YET |
| 31 | BUILT | ~110 | about 128 (`Apps.java` 74 new, `Privacy.java` 16 incl. the Part 30 switch, `MainActivity` 15, manifest 4, `index.html` about 19) | NOT YET. Java not compiled here, GitHub build is the first compile test |
| 32 | BUILT | ~90 | 63 (`screen.py` +49, `ScreenService.java` +14; `screen_service.xml` and `MainActivity` needed no change) | NOT YET. Java not compiled here |
| 33 | BUILT | ~100 | 52 (`actions.py` +42, `index.html` +10). Tests for 32 and 33 together: 23 lines in `test_app.py` | NOT YET |
| 34 | BUILT | ~165 | 355 in all: Java 169 (`ScreenService` 130, `MainActivity` 34, `Privacy` 4, `screen_service.xml` 1), Python 130 (`actions.py` 75, `progress.py` 52 new, `app.py` 3), page 42, tests 14 | NOT YET. Java not compiled here, GitHub build is the first compile test. After installing, switch the Jarvis accessibility switch OFF and ON once so Android accepts the new gesture permission |
| 54 | BUILT | ~75 | 41 (`memory.py` +15, `app.py` +3, `index.html` +13, `test_app.py` +10) | NOT YET. Page buttons not run on a phone |
| 35 | BUILT | ~60 | 22 (`ScreenService` 11, `actions.py` 4, `index.html` about 3, tests 3, `MainActivity` 1) | NOT YET. Java not compiled. Needs Android 9+ (decision D4: phone brand and Android version still not known) |
| 37 | BUILT | ~140 | 152 (`PhoneSettings.java` 77 new, `actions.py` 46, `MainActivity` 13, `index.html` 9, tests 7) | NOT YET. Java not compiled. Python tests: 75 PASS, 0 FAIL |
| 38 | BUILT | ~70 | 46 (`JarvisTile.java` 24 new, `shortcuts.xml` 7 new, `MainActivity` 8, manifest 6, strings 1) | NOT YET. Java not compiled |
| Pairing helper | BUILT | - | 15 (`app.py` /newcode 9, `index.html` 6): the pairing screen now tells you the 3 steps, asks Termux to print a fresh code by itself, and has a "Show code in Termux" button. The code is never shown in the page | NOT YET |
| 36 | BUILT | ~140 | 176 (`AppLock.java` 56 new, `MainActivity` 43, `Ears` 2, `index.html` 17, `clock.py` 38 new, `app.py` 8, `progress.py` 1, `build.gradle` 6, tests 5; plus the fixed key file `android/jarvis-debug.keystore`) | NOT YET. Java not compiled here. Python tests: 68 PASS, 0 FAIL |
| 55 | BUILT | ~80 | 31 (`index.html` about 29, `Ears.java` 2) | NOT YET. Page and Java not run on a phone |
| 39 | BUILT | ~140 | about 216 (`ListenService.java` 157 new, `MainActivity` 19, `Privacy` 6, `Ears` 1, manifest 2, `index.html` about 31) | NOT YET. Java not compiled. Not run: phone test |
| 41 | BUILT | ~180 | 133 (`tasks.py` 115 new, `app.py` 18) | NOT YET. Not run: nothing, syntax check only |
| 42 | BUILT | ~120 | 181 (`TaskRunner.java` 129 new, `index.html` 34, `MainActivity` 15, `Privacy` 3). `ScreenService` needed no change | NOT YET. Java not compiled |
| 43 | BUILT | ~80 | about 40 (README only: checklist table and status lines; no test file) | NOT YET |
| 51 | BUILT | ~170 | 90 (`voiceengine.py` 76 new, `app.py` 13, `.gitignore` 1). `tts.py` needed no change | NOT YET. Python syntax checked only. Not run: server, voice |
| 52 | BUILT | ~160 | 46 (`index.html` only; the routes were already in Part 51) | NOT YET. Page JS syntax checked only. Not run: phone |
| 47 | BUILT | ~210 | about 210 (`backup.py` 170 new, `index.html` +22, `app.py` +17, README setup line) | NOT YET. Python logic run here with real OpenSSL (lock, wrong passphrase, damage, path trick, merge, wipe); page not run |
| 46 | BUILT | ~115 | about 75 (`tasks.py` +70, `app.py` 1, `index.html` 1) | NOT YET. Python logic run here (save, run, refusals, limit 10, switch OFF); Java runner not compiled |
| 45 | BUILT | ~200 | about 140 (`brief.py` +100, `index.html` +4, `app.py` 1, `.gitignore` 1) | NOT YET. Python logic run here (cap, quiet hours, next day, settings); page not run |
| 44 | BUILT | ~250 | about 130 (`remind.py` +85, `calls.py` +22, `people.py` +14, `CalendarInfo.java` 39 new, `index.html` +3, `MainActivity` +6, `Privacy` +2, `app.py` 2, manifest 1) | NOT YET. Python logic run here (repeat, month end, 29 Feb, duplicate birthday, calendar text); Java not compiled |
| 56 | BUILT | ~130 | about 75 (`index.html` about 46, `remind.py` 11, `app.py` 4, plus fixes below) | NOT YET. Page syntax checked only |
Fixes in the same zip: (1) the Settings system card used a helper (`el`) that only existed inside another function, so it would have stayed empty; it is global now. (2) Durations over 60 minutes now show as hours and minutes everywhere (page and `clock.py`, for example "1 h 15 min", never "75 minutes").

How the dashboard works (Part 29): open Settings (gear), the first card is "Privacy and permissions". Each row shows three separate things: permission (Allowed or Not allowed, from Android), running now (from Java, not from the page), and last used. A permission being allowed never means a feature is running. Screen reader shows "Accessibility ON" only when the Jarvis accessibility service is really connected. "Reminder service ON" means the background service is really up. The activity log keeps only the feature name and time (max 30 lines, one entry per feature per minute) and never any content. "Open settings" buttons open one fixed Android page each. If the server stops, a red banner appears after about 10 seconds and Jarvis retries every 5 seconds; it clears by itself when the server is back. Chrome shows only the server line, because Android permissions exist only in the app.

