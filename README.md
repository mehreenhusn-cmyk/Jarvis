# JARVIS - Hussain's personal AI on his phone (Termux + Android app)

> **For any new Claude:** Hussain only sends this repo link (https://github.com/mehreenhusn-cmyk/Jarvis). Read section 0 and section 3 only, then your Part's row and files. Do not ask him to resend the old chat. The long old README is in `docs/README_OLD_FULL.md`: do NOT read it unless he asks.

## 0. FAST READ

**What it is.** A Python server in Termux (port 8787) plus an Android app (a WebView and some Java). Hussain speaks or types in any Indian language or English. Jarvis answers, opens apps, calls, sets alarms, runs steps, reminds, remembers, and keeps the phone safe. Data lives in the phone's own SQLite database.

**Goal (Hussain, 18 Nov).** The film Jarvis in a safe phone form: it understands loose speech, remembers, learns his daily routine (visible and editable), knows people by voice (with their yes), answers where he taps it, suggests things, and never acts alone. Risky steps (send, pay, delete) always wait for his tap.

**How to read this file (save his chat limit).**
1. Read sections 0 and 3. Stop.
2. Your Part's row: `grep -n "^| 130 " README.md`. Open only the files in that row.
3. Rules: section 8. Safety: section 6. Phone tests: section 7.
4. Chat commands: in `backend/app.py` run `grep -n "if mem is None" backend/app.py` (one line per handler, in order; the guest check comes first).
5. Page code: `grep -n "function NAME" web/index.html` (one big script; `doAct` = phone actions, `homeLoad` = Home, `voiceLoad` = voice panel, `const BB=` = bottom bar).

**Zip rules (real bugs happened).**
- Name: `Jarvis_partN.zip`, N = a Part number. A README-only update reuses the last built number.
- Layout: real paths only (`backend/x.py`, `web/index.html`, `android/app/src/main/java/com/hussain/jarvis/X.java`, `README.md`). Never flat, never a `Jarvis-main/` folder. Run `unzip -l` before sending.
- Import check: `py_compile` is not enough. Really `import app` from a temp copy of `backend/` with the new files on top.
- Never change `run.sh` or `sync.sh` through a zip.

**Start and stop (Termux).** `cd ~/Jarvis && bash run.sh` (inside `~/Jarvis`). It starts by itself when Termux opens. Stop: Ctrl+C. Port busy (`Address already in use`): `pkill -f run.sh; pkill -f backend/app.py; cd ~/Jarvis && bash run.sh`. Open http://127.0.0.1:8787 or the Jarvis app. Setup, once: `pkg install git python unzip openssl-tool`, `pip install edge-tts`, GitHub token with workflow access.

**Where things are (backend).**

| File | What it does |
|---|---|
| `app.py` | Server and the `/chat` handler chain (the heart) |
| `actions.py`, `tasks.py` | Phone commands (fixed grammar, never the AI) and multi-step tasks |
| `guest.py` | Guest session: RAM only, numbers masked |
| `memory.py`, `people.py`, `notes.py`, `lists.py`, `habits.py`, `spend.py`, `ledger.py`, `remind.py` | What Jarvis keeps (list of stores: `memory.STORES`) |
| `brief.py`, `lens.py`, `progress.py`, `whatsnew.py`, `search.py` | Briefing, Home card, honest counts, what's new, search |
| `voiceengine.py`, `tts.py`, `see.py`, `screen.py`, `web.py` | Voice, speech, photo and screenshot helper, screen text, internet answers |
| `modes.py`, `clock.py`, `phone.py`, `calls.py`, `place.py`, `backup.py`, `lang.py`, `autostart.py` | Modes, time, phone doctor, calls, place, backup, languages, auto start |
| Java | `MainActivity` (page to phone bridge), `ScreenService` (read, click, scroll, screenshot), `TaskRunner`, `Ears`, `CallByName`, `Apps`, `QuickSet`, `PaymentGuard`, `Privacy`, `ListenService`, `WakeEngine`. Claude cannot compile Java: the GitHub build is its compile test |

## 1. WHAT JARVIS IS

1. A personal assistant on Hussain's phone. Everything he gets is ONE zip: he downloads it, `run.sh` unzips it, pushes it to GitHub and restarts the server. GitHub Actions builds the APK.
2. It understands Hindi, Hinglish, other Indian languages and English.
3. Jarvis never sends, pays, deletes or runs anything on its own.
4. Voice: Sarvam `Shubh` (Hindi and English), Edge as backup. Speech to text: the phone's recognizer (one language at a time).
5. Privacy: no cloud sync, no silent recording, every feature has an OFF word.

## 2. ALL PARTS IN ONE TABLE (Part 1 to 149)

One row per Part, plain numbers only. Keep each row to ONE line. A new idea gets the NEXT number (now 150). When a Part is built, fill the real lines and change the status. Status words are read by `mission`: `Built, not phone tested`, `Built, phone tested`, `Built, partly tested`, `Planned`. `*` = new file. A range like `1 to 5` means the old notes did not split them.

| Part | What it does | Files | Lines | New APK? | Status |
|---|---|---|---|---|---|
| 1 to 5 | Server, pairing code, chat, history, mic in Chrome, keys, 5 AI providers | - | - | No | Built, phone tested |
| 6 to 9 | Neural voices, voice sliders, Hindi style, memory | - | - | No | Built, phone tested |
| 10 to 11 | Reminders, money ledger | - | - | No | Built, phone tested |
| 12 to 14 | Privacy bar, web read and search, morning briefing, duplicate-zip protection | - | - | No | Built, partly tested |
| 15 | Professional look | - | - | No | Built, phone tested |
| 16 to 17 | Android app shell, GitHub APK build, build log | - | - | Yes | Built, phone tested |
| 18 | Reminder notifications with the app closed | - | - | Yes | Built, not phone tested |
| 19 | Calls and contacts | - | - | Yes | Built, not phone tested |
| 20 | People notes | `people.py` | - | No | Built, not phone tested |
| 21 | Location, only when asked | - | - | Yes | Built, not phone tested |
| 22 | Camera | - | - | Yes | Built, not phone tested |
| 23 | Screen reader | `ScreenService.java` | - | Yes | Built, not phone tested |
| 24 | Phone check | `phone.py` | - | Yes | Built, not phone tested |
| 25 | Mic inside the app, Hey Jarvis while the app is open | `Ears.java` | - | Yes | Built, not phone tested |
| 26 | Security check, polish, `clear history` | - | - | No | Built, not phone tested |
| 27 | WebView security | `MainActivity.java` | 36 | Yes | Built, not phone tested |
| 28 | Real Stop that cannot be undone by voice | `Privacy.java` | 94 | Yes | Built, not phone tested |
| 29 | Privacy dashboard in Settings | `Privacy.java`, `index.html` | 109 | Yes | Built, not phone tested |
| 30 | Command layer | `actions.py` | 120 | No | Built, not phone tested |
| 31 | Open an app by name | `Apps.java` | 128 | Yes | Built, not phone tested |
| 32 | Better screen reading | `screen.py` | 63 | Yes | Built, not phone tested |
| 33 | Risk and confirm rules | `actions.py` | 52 | No | Built, not phone tested |
| 34 | Safe screen actions | `ScreenService.java`, `progress.py` | 355 | Yes | Built, not phone tested |
| 35 | Lock the phone by voice | `ScreenService.java` | 22 | Yes | Built, not phone tested |
| 36 | App lock with Android's prompt, fixed signing key, chat times | `AppLock.java`, `clock.py` | 176 | Yes | Built, not phone tested |
| 37 | Settings by voice | `PhoneSettings.java` | 152 | Yes | Built, not phone tested |
| 38 | Quick Settings tile and shortcut | `JarvisTile.java` | 46 | Yes | Built, not phone tested |
| 39 | Background listening test | `ListenService.java` | 216 | Yes | Built, not phone tested |
| 40 | Offline wake word | `WakeEngine.java` | 230 | Yes | Built, not phone tested |
| 41 | Task engine | `tasks.py` | 133 | No | Built, not phone tested |
| 42 | Task runner in the app | `TaskRunner.java` | 181 | Yes | Built, not phone tested |
| 43 | Phone checklist table | README only | 40 | No | Built, not phone tested |
| 44 | Repeat reminders, birthdays, phone calendar | `remind.py`, `CalendarInfo.java` | 130 | Yes | Built, not phone tested |
| 45 | Richer briefing, suggestions, quiet hours | `brief.py` | 140 | No | Built, not phone tested |
| 46 | Routines | `tasks.py` | 75 | No | Built, not phone tested |
| 47 | Encrypted backup, restore with preview, delete everything | `backup.py` | 210 | No | Built, not phone tested |
| 48 | Share to Jarvis, handoff summary, lost-phone card, new Home look | `handoff.py`, `index.html` | 215 | Yes | Built, not phone tested |
| 49 | Clipboard button and notification summary | `NotifySummary.java`, `index.html` | - | Yes | Built, not phone tested |
| 50 | System card in Settings | `sysinfo.py` | - | No | Built, not phone tested |
| 51 | Two voices engine | `voiceengine.py` | 90 | No | Built, not phone tested |
| 52 | Voice personality cards in Settings | `index.html` | 46 | No | Built, not phone tested |
| 53 | Sarvam voice provider and neon chat look | `voiceengine.py`, `index.html` | - | No | Built, not phone tested |
| 54 | Smart memory | `memory.py` | 41 | No | Built, not phone tested |
| 55 | Conversation mode | `index.html` | 31 | No | Built, not phone tested |
| 56 | Home tab | `index.html` | 75 | No | Built, not phone tested |
| 57 | Research answers with sources, mood-support rules | `web.py` | - | No | Built, not phone tested |
| 58 | Voice modes | `modes.py` | - | No | Built, not phone tested |
| 59 | Hindi-script spelling of English words, clean message bar | `actions.py`, `index.html` | 70 | No | Built, not phone tested |
| 60 | Search inside an app | `actions.py`, `QuickSet.java` | 114 | Yes | Built, not phone tested |
| 61 | Smart interrupt | `Ears.java`, `index.html` | 68 | Yes | Built, not phone tested |
| 62 | Open any app in any script | `actions.py`, `lang.py` | 60 | Yes | Built, not phone tested |
| 63 | Any Indian language | `lang.py` | 85 | No | Built, not phone tested |
| 64 | Call by name | `CallByName.java` | 199 | Yes | Built, not phone tested |
| 65 | Phone health questions in Hindi or English | `phone.py`, `PhoneInfo.java` | 147 | Yes | Built, not phone tested |
| 66 | Alarm and timer by voice | `QuickSet.java` | 150 | Yes | Built, not phone tested |
| 67 | Weather on Home | - | - | No | DROPPED by Hussain |
| 68 | Music control by voice | `QuickSet.java` | 62 | Yes | Built, not phone tested |
| 69 | WhatsApp message by contact name | `CallByName.java` | 95 | Yes | Built, not phone tested |
| 70 | Fixes after phone test round 1 | `Apps.java`, `Ears.java` | - | Yes | Built, not phone tested |
| 71 | Dual voice fix | `voiceengine.py` | - | No | Built, not phone tested |
| 72 | Voice notes and recall | `notes.py` | - | No | Built, not phone tested |
| 73 | Misheard-word matching, pause for payment apps, screen wake | `PaymentGuard.java` | - | Yes | Built, not phone tested |
| 74 | Settings redesign | `index.html` | - | No | Built, not phone tested |
| 75 | Daily life | `remind.py`, `brief.py` | - | No | Built, not phone tested |
| 76 | Routine at a fixed time | `tasks.py` | - | No | Built, not phone tested |
| 77 | Smart follow-up | `remind.py` | - | No | Built, not phone tested |
| 78 | Privacy timeline and missed-reminders summary | `Privacy.java` | - | Yes | Built, not phone tested |
| 79 | Deep phone doctor | `phone.py`, `PhoneInfo.java` | - | Yes | Built, not phone tested |
| 80 | Phone problems in briefing, weekly summary, weekday routines | `brief.py`, `tasks.py` | - | No | Built, not phone tested |
| 81 | No separate record in the old notes | - | - | No | Unknown |
| 82 | Snooze, night summary, Hindi routine words, storage trend, payment apps list, backup of | `PaymentGuard.java`, `phone.py` | 250 | Yes | Built, not phone tested |
| 83 | Shopping lists, habit tracker, explain screen, battery guardian, day report | `lists.py`, `habits.py` | 297 | No | Built, not phone tested |
| 84 | Expense logger, clipboard buttons, reply ideas | `spend.py`, `replyideas.py` | 162 | No | Built, not phone tested |
| 85 | Home card next best move | `lens.py`*, `app.py`, `index.html` | about 80 | No | Built, not phone tested |
| 86 | Now / Next / Later | `lens.py`, `index.html` | about 43 | No | Built, not phone tested |
| 87 | Honest Mission view | `progress.py`, `app.py`, `index.html` | 39 | No | Built, not phone tested |
| 88 | Memory Atlas | `memory.py`, `app.py`, `index.html` | 30 | No | Built, not phone tested |
| 89 | Search everywhere | `search.py`*, `app.py`, `index.html` | 39 | No | Built, not phone tested |
| 90 | Source label | `web.py`, `app.py` | 14 | No | Built, not phone tested |
| 91 | Red Team | `redteam.py`, `app.py`, `index.html` | ~60 | No | Built, not phone tested |
| 92 | Debate Jarvis | `debate.py`, `app.py`, `index.html` | ~80 | No | Built, not phone tested |
| 93 | Decision Debt | `decisions.py`, `brief.py`, `backup.py`, `app.py` | ~90 | No | Built, not phone tested |
| 94 | Unfinished business | `decisions.py`, `app.py` | ~50 | No | Built, not phone tested |
| 95 | Last talked | `touch.py`, `brief.py`, `backup.py`, `app.py` | ~90 | No | Built, not phone tested |
| 96 | Mood check-in | `mood.py`, `brief.py`, `backup.py`, `app.py` | ~80 | No | Built, not phone tested |
| 97 | Time Capsule | `capsule.py`, `backup.py`, `app.py`, `index.html` | ~85 | No | Built, not phone tested |
| 98 | Conditional capsule | `capsule.py`, `touch.py`, `app.py` | ~70 | No | Built, not phone tested |
| 99 | Habit Contract | `habits.py`, `app.py` | ~80 | No | Built, not phone tested |
| 100 | Timed modes | `modes.py`, `index.html` | ~70 | No | Built, not phone tested |
| 101 | Body Double | `modes.py`, `index.html` | ~60 | No | Built, not phone tested |
| 102 | Cool-down | `actions.py`, `index.html` | ~60 | No | Built, not phone tested |
| 103 | Dream journal | `dreams.py`, `backup.py`, `app.py`, `index.html` | ~90 | No | Built, not phone tested |
| 104 | Signs log | `signs.py`, `backup.py`, `app.py` | ~40 | No | Built, not phone tested |
| 105 | One honest question | `redteam.py`, `brief.py`, `app.py`, `memory.py`, `backup.py` | 52 + 2 + 4 + 8 + 1 = 67 | No | Built, not phone tested |
| 106 | Topic drift | `drift.py*`, `app.py` | 68 + 4 = 72 | No | Built, not phone tested |
| 107 | Context Ghost | `ghost.py*`, `app.py`, `index.html` | 76 + 8 + 3 = 87 | No | Built, not phone tested |
| 108 | Recovery card | `brief.py`, `app.py`, `index.html` | 20 + 8 + 12 = 40 | No | Built, not phone tested |
| 109 | Life Timeline | `events.py*`, `app.py`, `index.html` | 63 + 5 + 24 = 92 | No | Built, not phone tested |
| 110 | Money picture | `money.py*`, `brief.py`, `backup.py`, `memory.py`, `app.py` | 100 + 5 + 2 + 1 + 4 = 112 | No | Built, not phone tested |
| 111 | What-if | `money.py` | 30 | No | Built, not phone tested |
| 112 | Note after a call | `CallNote.java*`, `MainActivity.java`, manifest, `Privacy.java` | about 95 | Yes | Built, not phone tested |
| 113 | Reminders by place | `placenote.py*`, `PlaceWatch.java*`, `MainActivity.java`, manifest | about 430 (shared base for | Yes | Built, not phone tested |
| 114 | Bluetooth triggers | `placenote.py`, `PlaceWatch.java`, `MainActivity.java`, manifest | about 75 | Yes | Built, not phone tested |
| 115 | Anti-Doomscroll | `UsageWatch.java*`, `MainActivity.java`, manifest, `Privacy.java` | about 215 (shared base for | Yes | Built, not phone tested |
| 116 | App habit map | `UsageWatch.java`, `MainActivity.java`, `index.html` | about 40 | Yes | Built, not phone tested |
| 117 | What's new answers | `whatsnew.py`*, `app.py` | 81 | No | Built, not phone tested |
| 118 | Assist mode: guest session core | `guest.py`*, `app.py`, `index.html` | 56 + 18 + 13 = 87 | No | Built, not phone tested |
| 119 | Assist tools | `assist.py`, `see.py`, `app.py`, `index.html` | 43 + 12 + 24 + 8 = 87 | No | Built, not phone tested |
| 120 | Lens rail | `lens.py`, `app.py`, `index.html` | about 33 | No | Built, not phone tested |
| 121 | Glass skin 1 of 2 | `index.html` | about 90 (CSS 65, JavaScript | No | Built, not phone tested |
| 132 | Glass skin 2 of 2 | `index.html` | about 70 (CSS 54, JavaScript | No | Built, not phone tested |
| 133 | New app logo | 5 logo pictures (mipmap folders) | 0 | No | Built, not phone tested |
| 122 | Bottom bar | `index.html` | 20 added, 4 changed | No | Built, not phone tested |
| 123 | Mic keeps going | `Ears.java`, `ScreenService.java`, `index.html` | 17 + 22 + 4 = 43 | Yes | Built, not phone tested |
| 124 | One default voice | `voiceengine.py`, `index.html` | 3 + 4 = 7 | No | Built, not phone tested |
| 125 | Call by name, dictation tolerant | `actions.py` | 2 | No | Built, not phone tested |
| 126 | Better context and word match | `app.py` | - | No | Built, not phone tested |
| 127 | Click by number | `ScreenService.java` 42, `actions.py` 14, `index.html` 1 | 58 | Yes | Built, not phone tested |
| 128 | Keep going words | `actions.py` 5, `index.html` 2 | 7 | No | Built, not phone tested |
| 129 | Look and tap | ScreenService.java, MainActivity.java, see.py, actions.py, app.py, index.html | 253 | Yes | Built, not phone tested |
| 130 | Voice fixes from the 17 Nov screenshots | `actions.py`, `MainActivity.java`, `index.html` | ~60 | Yes | Built, not phone tested |
| 131 | Port busy fix | `run.sh`, `app.py` | 9 + 6 = 15 | No | Built, not phone tested |
| 134 | Conversation pauses, not ends: resumes when you return, retries speech error 2, ignores Jarvis's own voice | `index.html`, `MainActivity.java` | ~60 | Yes | Planned |
| 135 | Wake word to Conversation: tap the `Jarvis heard you` notification and Conversation starts (needs Parts 39 and 40 phone tested) | `MainActivity.java`, `index.html` | ~45 | Yes | Planned |
| 136 | Table A runner: `table a next`, tap PASS / FAIL / Skip, saved with date and note; feeds the Verified count | `*phonetest.py`, `app.py`, `progress.py`, `index.html` | ~130 | No | Planned |
| 137 | Quiet mode exceptions: `quiet mode 2 hours except namaz, Ammi` | `modes.py`, `index.html` | ~100 | No | Planned |
| 138 | Chat never lost, no fake done: every new pairing joins the oldest device, so chat and data survive a re-pair (old devices merged once); a short AI answer that claims a phone action is replaced by "I did nothing"; old `(phone action)` lines are not sent to the AI | `app.py`, `test_app.py` | 66 | No | Built, not phone tested |
| 139 | Loose commands, round two: after retesting 125, 126, 130: command word anywhere, filler and misheard words ignored | `actions.py`, `test_app.py` | ~120 | No | Planned |
| 140 | One Voice mode: Off / Hey Jarvis / Conversation instead of three switches; Interrupt becomes automatic | `index.html` | ~50 | No | Planned |
| 141 | Talk on Home: tap Jarvis on Home and it listens and answers there, no jump to Chat | `index.html` | ~50 | No | Planned |
| 142 | Simple screens: fewer cards on Home and Settings, the rest under More (needs Hussain's Home screenshots) | `index.html` | ~80 | No | Planned |
| 143 | What Jarvis learned: daily routine from his own data (counts only), a card to edit or delete, suggestions only | `*learn.py`, `app.py`, `index.html` | ~150 | No | Planned |
| 144 | Know people by voice: Vosk speaker model (about 13 MB); Jarvis asks aloud and saves only after a yes; greets and remembers the last talk | `*SpeakerId.java`, `*voices.py`, `MainActivity.java`, `app.py`, `index.html` | ~250 | Yes | Planned |
| 145 | Samjha probe: `samjha: <sentence>` shows what Jarvis understood without doing anything | `app.py`, `actions.py` | ~30 | No | Planned |
| 146 | Unknown sentences list: sentences it could not understand are saved on the phone; one tap teaches it | `*unknown.py`, `app.py`, `index.html` | ~80 | No | Planned |
| 147 | Real tick: a tick or cross after a phone action only when the phone's own result says so | `index.html`, `app.py` | ~40 | No | Planned |
| 148 | More Jarvis mishearings: more misheard forms of the name (हिसारिस्ट, जरवेस, जरवेश ...) count as the wake word | `ListenService.java`, `index.html` | ~10 | Yes | Planned |
| 149 | Screenshot sentences as tests: torch, call Ammi, scroll, back, home, last update are locked. 5 sentences still FAIL and print KNOWN-FAIL: three home screen wordings, `मैं अम्मी को कॉल कर`, `usko open karo`. Part 139 must fix them | `test_app.py` | 13 | No | Built, not phone tested |

## 3. WHAT HUSSAIN DOES NOW

1. GitHub > Actions > **Build APK** > Run. Red? Send a screenshot of the error. Java (Parts 112 to 116, 129, 133 and others) was never compiled before.
2. Install the APK. Then Accessibility > `Jarvis screen reader` OFF and ON once (Part 129 needs the screenshot permission; Android 11 or newer).
3. **Retest the voice problems first.** The 17 Nov screenshots show old versions (headers say Part 89 to 122). Parts 125, 126 and 130 already target them (call by name, context, torch words). Try the same sentences again. Send screenshots only of what still fails.
4. Try Table A (section 7). Write PASS or FAIL for each row.
5. Then name the next Part from the plan (section 4).

**Done 19 Nov: 138 and 149 (built, not phone tested). Next in the order below is 149 done, so start at 148.**

**Build order (18 Nov):** 138, 149, 148, 139, 134, 140, 141, 142, 143, 135, 136, 137, 145, 146, 147, 144.

Why this order: Parts 18 to 90, 97 to 133 are built but not phone tested. A new feature on an untested base makes bugs hard to find, so small fixes and tests come first and the risky voice-ID Part (144) comes last.

## 4. THE PLAN (Parts 134 to 149)

The rows are in section 2. Lines are realistic (the first guess is usually 1.5 times too small).

| Group | Parts | Lines | Java / new APK |
|---|---|---|---|
| Voice and conversation | 134, 135, 140, 141, 148 | about 215 | 134, 135, 148 |
| Understanding | 138, 139, 145, 146, 147, 149 | about 345 | none |
| Learning and people | 143, 144 | about 400 | 144 |
| Screens and tests | 136, 137, 142 | about 310 | none |
| **Total** | **16 Parts** | **about 1,270** | **4 Parts** |

**Voice mode (Part 140).** Today Settings shows three switches. Conversation = after each answer the mic opens by itself. Hey Jarvis = it waits for the name, then takes one question. Interrupt = you can speak while Jarvis speaks and it stops. New: one choice `Off / Hey Jarvis / Conversation`. Interrupt is automatic (on with earphones, off without).

**Daily learning (Part 143).** Learns only from data Jarvis already has: which commands at which time, app usage (if tracking is on), reminders, namaz times. It keeps COUNTS, never speech or screen. A card `What Jarvis learned` lists each item with Keep and Delete. OFF word: `seekhna band karo`. It only suggests (`Sir, around this time you usually call Ammi. Shall I?`) and needs his Yes.

**Know people by voice (Part 144).**
- Owner: `meri awaaz yaad rakho` (3 short samples, saved as numbers, not as a recording).
- A new voice talks to Jarvis: Jarvis says aloud who it is, asks the name, and says what it would keep (name, voice numbers, date of last talk, short notes of the talk). Only after the person says YES is anything saved. No yes means a plain guest and nothing is saved (as today).
- Next time: `Haan Faisal, pehchan gaya. Pichhli baar 3 din pehle humne ... pe baat ki thi.` Jarvis continues from the last talk.
- Delete: `Faisal ko bhool jao` or Settings > People you know. It is in Backup and wiped by `delete everything`.
- A voice match is a guess and a recording can fool it: it is NEVER used to pay, send, delete or unlock.
- Technical: Vosk speaker model (about 13 MB, downloaded only after a tap like Part 40), raw audio through `AudioRecord`. The phone's recognizer and Vosk cannot hold the mic together, so a design check and a phone test come first. Hindi accuracy of the small Vosk model is weaker.

## 5. IDEAS WE WILL NOT BUILD

| Idea | Why not |
|---|---|
| Unlock the phone by voice, or any lock-screen bypass | REFUSED: banking trojans use this pattern |
| Voice commands with the screen locked or off | REFUSED; Android does not allow it either |
| Always-on "Hey Jarvis" as the default assistant | NOT PLANNED: big and risky; the background test (Parts 39, 40) is the safe version |
| Saving Aadhaar, card or bank numbers, passwords, OTPs, PINs | REFUSED |
| Recording the screen or "everything I say and do" | REFUSED: it records other people's chats, voices and OTPs |
| Detecting mood or anger from chats, typing, voice or heart rate | REFUSED: a mood is noted only when Hussain says it (Part 96) |
| A personality that appears by itself when he is alone or low | REFUSED: needs mood detection |
| Sending messages to people automatically | REFUSED: Jarvis never sends on its own |
| Silently saving a guest's voice, name or chat | REFUSED: a voice is personal data. Part 144 asks aloud and saves only after a yes |
| Routines that run with no tap | NOT PLANNED: the one-tap Run is the safety design |
| Blocking apps, or watching the screen all the time | NOT PLANNED |
| Moving real money as a penalty (Part 99 is only a number) | REFUSED |
| Emergency guide or medical steps written by the AI | NOT PLANNED: a wrong guide could harm |
| Splitting `index.html` into files | NOT NOW: biggest regression risk before Table A passes. Part 142 only hides cards |
| Weather on Home (Part 67), car mode | DROPPED by Hussain |

## 6. SAFETY RULES (every Part must keep these)

1. Only real data from Jarvis's own tables. No fake percentages or "confidence" scores.
2. Nothing is saved that Hussain did not say or tap. Passwords, OTPs, PINs, CVVs and card numbers are refused everywhere (`memory.SECRET`).
3. Personal data (mood, last talked, decisions, dreams, money, known people, learned routines) stays in the phone's database, is in Backup, is wiped by `delete everything`, and is not sent to the AI except where a Part says so in its reply.
4. Jarvis only suggests. Sending, paying, deleting and running steps need Hussain's tap.
5. Every feature has an OFF word and a delete word. Heavy emotional features are opt-in with a visible badge and never start on their own.
6. Guest session (Parts 118, 119): started by Hussain; nothing is saved; numbers are masked; End and erase wipes the chat.
7. Known people (Part 144): saved only after that person says yes aloud; deletable by name; never used for security.
8. Learning (Part 143): counts from his own data only, visible, editable, suggestions only.
9. A voice or face match is never proof of identity.

## 7. PHONE TESTS (TABLE A)

Nothing here is phone tested unless the Result says PASS. Build the APK first for the Java rows. Write PASS, FAIL or not tested in the last column. Part 87 and Part 136 read this column, so keep the table format. Every new Part adds rows when it is built.

| # | Try this | Expected | Needs new APK | Result |
|---|---|---|---|---|
| 1 | Open a payment app, close it, then Settings > Privacy | Timeline shows 'Paused for a payment app' (no app name) | Yes (Parts 73, 78) | not tested |
| 2 | `routine <name> 7 baje` with a time 2 minutes ahead, page open | Message with a Run button; runs only after your tap | No | not tested |
| 3 | `routine <name> 7 baje sirf weekdays` then `my routines` | Shows the time and weekdays | No | not tested |
| 4 | A reminder in 1 minute, wait 3 hours | Once 'ho gaya?' with Haan / Nahi abhi | No | not tested |
| 5 | Let 3 reminders wait, then open the page | ONE message and ONE short voice line | Yes (Part 78) | not tested |
| 6 | `phone doctor` | Normal check plus Deep check; 'unavailable' for what Android hides | Yes (Part 79) | not tested |
| 7 | `briefing`, `weekly summary`, `aaj ka summary` | Real numbers, no invented lines | No | not tested |
| 8 | A reminder comes: tap `⏰ 10 min` | Same text again 10 minutes later, no extra question | No | not tested |
| 9 | Say `storage trend` on day 1, then again on day 3 | Day 1: asks for 2 days. Day 3: change in GB | No | not tested |
| 10 | Settings > Privacy & Security > Payment apps > Add an app | Your app is listed; Remove works; 'Payment app list changed' in the timeline | Yes (Part 82) | not tested |
| 11 | Make a backup, delete a routine's time, restore | Time and weekdays come back | No | not tested |
| 12 | Settings > Background listening (test) | Optional. Needs the 40 MB model once on Wi-Fi; ends after 8 hours | Yes | not tested |
| 13 | `list me doodh bread add karo`, `list dikhao`, `list se doodh hatao`; then Backup and Restore | The list shows, the item goes, and the list comes back after a restore | No | not tested |
| 14 | `habit banao gym`, `aaj gym gaya`, `my habits`, `habit report` | Streak grows by 1 a day; saying it twice the same day does not count twice | No | not tested |
| 15 | With battery at 16 to 19 percent and not charging, say `briefing` | A 'Phone:' line with a calm suggestion (at 15 or less the Phone Doctor line shows instead) | No | not tested |
| 16 | `day report 9 baje`, wait for that time with the page open | A message with a Show day report button; the summary shows only after your tap | No | not tested |
| 17 | Home > Explain screen, then switch to another app | Jarvis waits a few seconds, reads that app and explains it in simple words | No (needs the screen reader from Part 23 switched ON) | not tested |
| 18 | `200 coffee`, `kharcha 50 auto`, `kharcha`, `kharcha hatao` | Each entry is noted with a category; `kharcha` shows today, 7 days, this month; `hatao` removes the last one. `10 baje alarm` is NOT taken as spending | No | not tested |
| 19 | Copy a text, Home > Clipboard, tap Save as note, then copy a short word and tap Add to list | `meri notes` shows the note; `list dikhao` shows the item | No | not tested |
| 20 | Notification summary ON, Home > Notifications > Reply ideas > pick one | 3 short options with Copy buttons; nothing is sent; the chat history shows a placeholder, not the notification text | No (notification access from the older Part) | not tested |
| 21 | Home tab: look at the Next best move card while a reminder is due in the next hour | The card shows that reminder with Why and Later; Show types `my reminders` in chat; nothing runs by itself | No | not tested |
| 22 | Home tab: look at the Now / Next / Later strip with a late money item, a habit not done and a reminder for tomorrow | Each item sits in its column (late money and reminders you were not told about are in NOW); with nothing planned the card says `Nothing needs you right now` | No | not tested |
| 23 | Home tab: look at the Honest progress card, then type `mission` in chat | The card and the chat show the same three counts: Code built, Phone tested, Verified (Table A). With nothing marked PASS yet, Verified says 0 of 24 | No | not tested |
| 24 | Type `last update`, then `last 3 updates`, then `kya kya add hua` | Last update: the newest zip name, its time, what that Part does, its files and lines, and the files inside the zip. The list shows Part numbers with one line each. No `I cannot access GitHub` | No | not tested |
| 25 | Settings > Your Data (Memory Atlas): look at the counts, add a note with `note karo test`, reopen the panel, press Remove on that note | The counts list 12 kinds of data with how to remove each; the test note appears under Notes and disappears after Remove; counts match what you know you saved | No | not tested |
| 26 | Save a note with `note karo Bombay trip`, then say `sab jagah dhundo Bombay`; also tap Home > Search all | The answer lists the note under Notes and any memory, person, list item or reminder with that word; a word you never saved says `nowhere`; nothing is sent to the AI | No | not tested |
| 27 | Type `search: Bombay population` (needs internet) | The answer ends with `Sources: ...` and a bracket line saying how many sites were seen. One site gives `One site only`. No word `agree` | No | not tested |
| 28 | Home > Guest session (or type `guest session start`), ask a question with a made-up phone number in it, then tap End & erase, then `my notes` and `sab jagah dhundo` that question's word | The gold badge `Guest: temporary, Memory saved: No` shows; the guest chat disappears on End & erase; reopening the page shows none of it; nothing appears in notes, memories or chat history | No | not tested |
| 29 | Settings > Voice (the speaker button) while the mic is listening, and look at the Home Honest progress card | The voice panel says `Mic ON` while listening and `Mic off` after; the Honest progress card keeps its counts | No | not tested |
| 30 | Open YouTube or Chrome, then say `Jarvis neeche scroll karo` (Phone control and screen reader ON) | The page moves down; if no scroll area exists Jarvis swipes by itself; the chat says what changed | Yes (Part 123) | not tested |
| 31 | Conversation on, stay silent 3 times | Conversation stays on until 4 silent rounds; a `speech error 2` with the internet off retries and then says `no internet right now` | Yes (Part 123) | not tested |
| 32 | Settings > Voice: look at the speaker list and Voice maker; tap Test JARVIS | Only `Shubh` is listed; Sarvam is the first choice; with the Sarvam key removed Edge speaks | No | not tested |
| 33 | Say `call ammi at anyhow last mein 5895` and `Ammi ko call karo` | Both start the Ammi call (or ask which Ammi if two fit); the AI does not say `I cannot call` | No | not tested |
| 34 | Open YouTube home, say `ooper se teesra video kholo`; then in Settings say `2nd item kholo` | The 3rd video card opens (the 2nd row opens in Settings). In a drawn chart (TradingView) Jarvis says it sees only N big items: that is expected | Yes (Part 127) | not tested |
| 35 | Say `neeche scroll karo`, then `thoda aur scroll karo`, then `upar jao` | The first goes down, the second goes down again (same direction), the third goes up | No for the words, Yes for the scroll (Part 123) | not tested |
| 36 | Say `translate to hindi: where is the bus station`, then `explain simply: this is a prepaid mobile plan`, then `make a plan: learn typing in 2 weeks`, then `reliable info: capital of Australia` | Each gives a short answer. The last one adds `Sources:` and a one line site label. Inside `guest session start` all four also work and nothing is saved | No | not tested |
| 37 | Tap the camera, send a photo of a bill or a medicine strip with the words `translate`, then type `photo: what is the total?`. Then say `big text` | The photo is read, the follow-up answer comes without a new photo, a medicine answer ends with `doctor ya pharmacist se confirm karo`. Big text makes the letters large and reads the last answer aloud; `big text off` goes back | No | not tested |
| 38 | Type `red team: yeh phone kharidna hai` | 3 hard questions, 2 counter-points, last line `Decision tumhara hai`. Numbers only from your own spending, habits and memories; none invented. Not available inside a guest session | No | not tested |
| 39 | Say `sochenge baad mein: phone lena hai`, `adhoora: Faisal se baat`, then `pending decisions`, `adhoora dikhao`, `decision ho gaya 1`, `adhoora khatam 1` | Each is saved or closed with its number. After 3 days the briefing shows the open decision and (once in 3 days) the unfinished item | No | not tested |
| 40 | Say `mood 3`, `aaj mood low`, `mood history`, `mood care on` | The mood is noted (one per day), history lists the days, care on is confirmed. After 4 low days in a row with care on, the briefing has one gentle line | No | not tested |
| 41 | Type `debate ruthless: main job chhod du`, then `debate stop` | A badge `Debate: ruthless` shows, the answer argues hard but without insults, `debate stop` removes the badge. After 10 minutes it ends by itself | No | not tested |
| 42 | Say `ammi track karo`, `ammi se baat hui`, `ammi track 10 din`, `tracked people`, `ammi track band karo` | Each is confirmed. With a tracked person silent for the limit days, the briefing says `Haven't talked to Ammi for N days`. Nothing is read from calls or WhatsApp | No | not tested |
| 43 | Say `habit banao gym`, `contract gym 7 din penalty 100`, then `my habits` the next days without `aaj gym gaya` | `my habits` shows `contract: day k/7, penalty pot Rs N` (100 per closed day without a check-in). It says no real money moves. `contract hatao gym` removes it | No | not tested |
| 44 | Say `30 din baad yeh sunana: test message`, then `my capsules`. (To test fast, change the phone date by 30 days, or wait.) | It says sealed and the opening date, and shows NO text. On that day a card appears once; `Open and read aloud` shows and speaks the text; `Later` keeps it for `open capsule N` | No | not tested |
| 45 | Say `body double 15 minute` and wait | After 15 minutes the chat shows `abhi bhi kaam par?` with Haan / Nahi (text only, no voice). Right after that the end card shows `15 minutes, N of 1 check-ins on task`. `body double stop` ends it early and shows the count | No | not tested |
| 46 | Say `meeting mode 2 minute` is too short (min 5), so say `meeting mode 5 minute`. Then a reminder in that time, then wait | A purple bar `meeting mode, until HH:MM` shows. No voice, one short sentence, the reminder is text only. After 5 minutes the bar goes and `Back to normal` shows. `normal mode` or the End button ends it sooner. Also try `sleep mode`, `namaz mode`, `focus 45 minute` | No | not tested |
| 47 | Say `main torch chalu kar`, `torch band kar yaar`, then `torch chalu karo` while another app holds the camera. Speak in Hindi and watch the language of the reply | The torch really switches (check the quick-settings tile). Extra words like `main` or a misheard `Jarvis` no longer lose the command. If Android says the torch did not change, Jarvis says so instead of `torch is off`. Hindi words get Hindi replies. A cut-off `का करियर` gets `phir se boliye` | Yes | not tested |
| 48 | Say `phrase capsule himmat chahiye: tu kar lega`, then `ammi track karo`, then `ammi se 30 din baat na ho to yeh sunana: ab call kar`, then `my capsules` | `my capsules` lists both with their condition and NO text. Typing a message with `himmat chahiye` opens the first one (shown as the reply). The second shows its card once, after 30 days without `ammi se baat hui`; `open capsule N` is refused before the condition is met | No | not tested |
| 49 | Say `thanda karo`, then `Ammi ko whatsapp pe hello bhejo` | A card shows `Your message to Ammi: "hello"` and a 20 second wait; Continue is greyed until it ends; Cancel opens nothing. Only after Continue does WhatsApp open (you still press send yourself). Without `thanda karo` the command works as before | No | not tested |
| 50 | Say `sapna: main udd raha tha aur Ammi neeche thi`, `sapne dikhao`, `sapno me Ammi kitni baar`, `sapne ka matlab`, `sapna hatao 1` | The dream is saved word for word, listed with a date, the word is counted, the reflection is gentle, says dreams have no fixed meaning and is only about that one dream. A dream holding a password or card number is refused | No | not tested |
| 51 | Say `sign: 11:11 dekha` three times (also `sign: 11:11 phir dekha`), then `signs dikhao`, then `sign hatao 11:11` | The count goes 1, 2, 3 (`dekha` and `phir` are ignored when matching), the list shows the count and last date, hatao removes it. Nothing is guessed or explained | No | not tested |
| 52 | Install the new APK (Build APK green first). At home say `is jagah ko ghar naam do` | Android asks for location once; reply says `saved as 'Ghar' (radius 150 m)`. If the position is worse than 200 m it asks you to stand in the open | Yes (Part 113) | not tested |
| 53 | Say `jab ghar pahunchu doodh lena yaad dilana`. Allow location. Leave home (500 m or more), come back | A phone notification `Ghar: doodh lena` within a few minutes of arriving; it comes only once. The silent `Jarvis place watch` notification is visible while it runs | Yes (Part 113) | not tested |
| 54 | Say `jab ghar se niklu chabi lena har baar`, then walk out of the 150 m circle twice (30 minutes apart) | A notification each time you leave; `place reminders` lists it as `every time` | Yes (Part 113) | not tested |
| 55 | Say `place reminders`, `place reminder hatao 1`, `place watch off`, then `place watch on` | List shows places and notes; the note is removed; with the switch off the silent notification goes away, with it on it comes back | No (Part 113) | not tested |
| 56 | Say `bluetooth devices`, then `jab <word from your earbuds name> bluetooth jude to music chalu karna` and connect the earbuds | Android asks for Nearby devices; the names are listed; on connect a notification `Bluetooth: <name>` shows the note | Yes (Part 114) | not tested |
| 57 | Settings > Privacy: look for `Place and Bluetooth watch`, then say `delete everything` (typed phrase) | The row shows the last time it was used; after deleting, `place reminders` says there is nothing | Yes (Part 113) | not tested |
| 58 | Say `scroll alert 5`, switch Jarvis on in the Usage access page, come back, then stay in one app (for example YouTube) for 5 minutes with the screen on | One notification `You have been in <app> for 5 min. A short break may feel good.` shows once; nothing is blocked; going home and back starts a new count. `scroll alert off` stops it | Yes (Part 115) | not tested |
| 59 | Say `app map on`, then open YouTube for 30 seconds, then Instagram, and repeat 2 times; later say `app map` | A line like `YouTube ke baad usually Instagram (2 times)`. `app map reset` erases it. Settings > Privacy shows `Scroll alert and app map` with Usage access allowed | Yes (Part 116) | not tested |
| 60 | Say `call note on`, allow Phone, then make or take a call of 30 seconds or more and hang up | A notification `Call ended. Kuch yaad rakhna hai?` shows. Tap it: Jarvis asks, you type `milk lena hai`, and `meri notes` lists it. A call under 30 seconds shows nothing. `call note off` stops it | Yes (Part 112) | not tested |
| 61 | On Home tap the chips Project, Phone, Life, All under Next best move | The card and the strip change with the chip. Project shows README counts, Phone only the battery, Life only reminders, money, birthdays and habits. Nothing is saved: Home starts on All again | No (Part 120) | not tested |
| 62 | On a phone in dark mode open Home. Then say `glass off`, look again, then `glass on` | Home shows frosted glass cards, a glass orb and gradient headings; `glass off` gives the old flat look; `glass on` brings the glass back. The orb still turns red when Jarvis is stopped and blue when listening. A phone in light mode keeps the old look | No (Part 121) | not tested |
| 63 | On Home look at the AI tools tiles, the buttons and the progress bars. Then open Settings > Look and tick `Reduce effects` | Tiles are glass squares with a glowing icon, main buttons are blue to purple, bars glow. After ticking Reduce effects Home goes back to the old flat look; unticking brings the glass back. `glass off` and the tick stay in sync. Phone setting `Remove animations` stops the orb from moving | No (Part 132) | not tested |
| 64 | Turn Phone control ON. Open any app (not a bank app). Say `look and tap the search button` (or `dekh ke dabao <a button name>`) | The app goes back, Jarvis comes to the front with a notification, shows a small picture of that screen with a red number 1 and asks `should I tap the red number 1?` with Yes and No. Yes taps once and the chat says if the screen changed; No or 60 seconds taps nothing. On a screen with a password box, or a bank/payment app, Jarvis says it took no picture. Nothing is saved. Android 10 or older says it needs Android 11 | Yes | not tested |

## 8. RULES FOR EVERY CLAUDE

1. Each Part is under 350 lines. New files only when really needed. After each Part update this README: its row in section 2 (real lines and status) and its Table A rows.
2. Talk to Hussain in simple Roman Hinglish or simple English. Roman script only, NEVER Devanagari, even when he dictates in Hindi. Short plain words, like WhatsApp. He dictates by voice, so spelling mistakes are normal. Show files and lines in a table.
3. Output is ONE zip (see section 0 zip rules) with this Part's files plus every earlier file whose push the app header has not yet shown as "pushed". Never the whole repo.
4. Before a Part say its number, files, lines and WITH or WITHOUT tests. After it say the real lines and offer 3 or 4 next Parts in a table. He may pick 2 or 3 at once.
5. Tests: Python logic is run. Java cannot be compiled by Claude: write "Not run". Never write "tested" for something that was not tested.
6. Ask for as few Termux commands as possible. When he names the next Parts, build at once.
7. Never save passwords, OTPs, PINs or CVVs. Never put keys or tokens in chat, code or Git.
8. His OWL1 trading repo is separate. Never touch it.
9. App lock stays OFF unless he turns it on himself.
10. Read less: sections 0 and 3, your Part's row, its files. Use `grep -n`. Say in one line which files you read.
11. Keep this README short and simple: one Parts table, one line per Part, no pasted chat text. Old detail goes to `docs/`.
12. After a Part, if it was only checked by syntax, its status is `Built, not phone tested`.

## 9. KNOWN LIMITS

- The phone recognizes ONE language at a time. Choose it in Settings > Voice > `Speak:`. Sarvam speaks only Hindi and English; other languages use Edge voices.
- Android does not let an app open itself from the background, switch Wi-Fi, Bluetooth or location, or delete alarms. Jarvis opens the right page or shows a notification.
- While another app is open Jarvis cannot hear you unless the background listener (Parts 39, 40) runs and you tap its notification.
- Interrupt works best with earphones; a Bluetooth speaker may echo.
- Contacts in non-Latin, non-Hindi scripts are not found by `call` (Part 64). Unknown Urdu app names are not matched.
- Place and Bluetooth reminders use the mobile or Wi-Fi position (50 to 200 m) and can be 2 to 10 minutes late.
- Termux may be killed by Android: Settings > Apps > Termux > Battery > No restriction, keep its notification, install Termux:Boot.
- Screenshots (Part 129) work only on Android 11 or newer, never on a screen with a password box or in a payment app, and the AI can point wrong, so you see the spot first.
- The pairing code is in Termux (`PAIRING CODE: ...`, valid 10 minutes). Pairing stays after updates because one fixed signing key is used; uninstalling the app makes a new pairing.
