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
| `memory.py`, `people.py`, `notes.py`, `lists.py`, `habits.py`, `learn.py`, `spend.py`, `ledger.py`, `remind.py` | What Jarvis keeps (list of stores: `memory.STORES`) |
| `brief.py`, `lens.py`, `progress.py`, `phonetest.py`, `whatsnew.py`, `search.py` | Briefing, Home card, honest counts, Table A runner (Part 136), what's new, search |
| `voiceengine.py`, `tts.py`, `see.py`, `screen.py`, `web.py` | Voice, speech, photo and screenshot helper, screen text, internet answers |
| `modes.py`, `clock.py`, `phone.py`, `calls.py`, `place.py`, `backup.py`, `lang.py`, `autostart.py` | Modes, time, phone doctor, calls, place, backup, languages, auto start |
| Java | `MainActivity` (page to phone bridge), `ScreenService` (read, click, scroll, screenshot), `TaskRunner`, `Ears`, `CallByName`, `Apps`, `QuickSet`, `PaymentGuard`, `Privacy`, `ListenService`, `WakeEngine`. Claude cannot compile Java: the GitHub build is its compile test |

## 1. WHAT JARVIS IS

1. A personal assistant on Hussain's phone. Everything he gets is ONE zip: he downloads it, `run.sh` unzips it, pushes it to GitHub and restarts the server. GitHub Actions builds the APK.
2. It understands Hindi, Hinglish, other Indian languages and English.
3. Jarvis never sends, pays, deletes or runs anything on its own.
4. Voice: Sarvam `Shubh` (Hindi and English), Edge as backup. Speech to text: the phone's recognizer (one language at a time).
5. Privacy: no cloud sync, no silent recording, every feature has an OFF word.

## 2. ALL PARTS IN ONE TABLE (Part 1 to 170)

One row per Part, plain numbers only. Keep each row to ONE line. A new idea gets the NEXT number (now 171). When a Part is built, fill the real lines and change the status. Status words are read by `mission`: `Built, not phone tested`, `Built, phone tested`, `Built, partly tested`, `Planned`. `*` = new file. A range like `1 to 5` means the old notes did not split them.

| Part | What it does | Files | Lines | New APK? | Status |
|---|---|---|---|---|---|
| 1 to 5 | Server, pairing code, chat, history, mic in Chrome, keys, 5 AI providers | - | - | No | Built, phone tested 🟢 |
| 6 to 9 | Neural voices, voice sliders, Hindi style, memory | - | - | No | Built, phone tested 🟢 |
| 10 to 11 | Reminders, money ledger | - | - | No | Built, phone tested 🟢 |
| 12 to 14 | Privacy bar, web read and search, morning briefing, duplicate-zip protection | - | - | No | Built, partly tested 🟢 |
| 15 | Professional look | - | - | No | Built, phone tested 🟢 |
| 16 to 17 | Android app shell, GitHub APK build, build log | - | - | Yes | Built, phone tested 🟢 |
| 18 | Reminder notifications with the app closed | - | - | Yes | Built, not phone tested 🟢 |
| 19 | Calls and contacts | - | - | Yes | Built, not phone tested 🟢 |
| 20 | People notes | `people.py` | - | No | Built, not phone tested 🟢 |
| 21 | Location, only when asked | - | - | Yes | Built, not phone tested 🟢 |
| 22 | Camera | - | - | Yes | Built, not phone tested 🟢 |
| 23 | Screen reader | `ScreenService.java` | - | Yes | Built, not phone tested 🟢 |
| 24 | Phone check | `phone.py` | - | Yes | Built, not phone tested 🟢 |
| 25 | Mic inside the app, Hey Jarvis while the app is open | `Ears.java` | - | Yes | Built, not phone tested 🟢 |
| 26 | Security check, polish, `clear history` | - | - | No | Built, not phone tested 🟢 |
| 27 | WebView security | `MainActivity.java` | 36 | Yes | Built, not phone tested 🟢 |
| 28 | Real Stop that cannot be undone by voice | `Privacy.java` | 94 | Yes | Built, not phone tested 🟢 |
| 29 | Privacy dashboard in Settings | `Privacy.java`, `index.html` | 109 | Yes | Built, not phone tested 🟢 |
| 30 | Command layer | `actions.py` | 120 | No | Built, not phone tested 🟢 |
| 31 | Open an app by name | `Apps.java` | 128 | Yes | Built, not phone tested 🟢 |
| 32 | Better screen reading | `screen.py` | 63 | Yes | Built, not phone tested 🟢 |
| 33 | Risk and confirm rules | `actions.py` | 52 | No | Built, not phone tested 🟢 |
| 34 | Safe screen actions | `ScreenService.java`, `progress.py` | 355 | Yes | Built, not phone tested 🟢 |
| 35 | Lock the phone by voice | `ScreenService.java` | 22 | Yes | Built, not phone tested 🟢 |
| 36 | App lock with Android's prompt, fixed signing key, chat times | `AppLock.java`, `clock.py` | 176 | Yes | Built, not phone tested 🟢 |
| 37 | Settings by voice | `PhoneSettings.java` | 152 | Yes | Built, not phone tested 🟢 |
| 38 | Quick Settings tile and shortcut | `JarvisTile.java` | 46 | Yes | Built, not phone tested 🟢 |
| 39 | Background listening test | `ListenService.java` | 216 | Yes | Built, not phone tested 🟢 |
| 40 | Offline wake word | `WakeEngine.java` | 230 | Yes | Built, not phone tested 🟢 |
| 41 | Task engine | `tasks.py` | 133 | No | Built, not phone tested 🟢 |
| 42 | Task runner in the app | `TaskRunner.java` | 181 | Yes | Built, not phone tested 🟢 |
| 43 | Phone checklist table | README only | 40 | No | Built, not phone tested 🟢 |
| 44 | Repeat reminders, birthdays, phone calendar | `remind.py`, `CalendarInfo.java` | 130 | Yes | Built, not phone tested 🟢 |
| 45 | Richer briefing, suggestions, quiet hours | `brief.py` | 140 | No | Built, not phone tested 🟢 |
| 46 | Routines | `tasks.py` | 75 | No | Built, not phone tested 🟢 |
| 47 | Encrypted backup, restore with preview, delete everything | `backup.py` | 210 | No | Built, not phone tested 🟢 |
| 48 | Share to Jarvis, handoff summary, lost-phone card, new Home look | `handoff.py`, `index.html` | 215 | Yes | Built, not phone tested 🟢 |
| 49 | Clipboard button and notification summary | `NotifySummary.java`, `index.html` | - | Yes | Built, not phone tested 🟢 |
| 50 | System card in Settings | `sysinfo.py` | - | No | Built, not phone tested 🟢 |
| 51 | Two voices engine | `voiceengine.py` | 90 | No | Built, not phone tested 🟢 |
| 52 | Voice personality cards in Settings | `index.html` | 46 | No | Built, not phone tested 🟢 |
| 53 | Sarvam voice provider and neon chat look | `voiceengine.py`, `index.html` | - | No | Built, not phone tested 🟢 |
| 54 | Smart memory | `memory.py` | 41 | No | Built, not phone tested 🟢 |
| 55 | Conversation mode | `index.html` | 31 | No | Built, not phone tested 🟢 |
| 56 | Home tab | `index.html` | 75 | No | Built, not phone tested 🟢 |
| 57 | Research answers with sources, mood-support rules | `web.py` | - | No | Built, not phone tested 🟢 |
| 58 | Voice modes | `modes.py` | - | No | Built, not phone tested 🟢 |
| 59 | Hindi-script spelling of English words, clean message bar | `actions.py`, `index.html` | 70 | No | Built, not phone tested 🟢 |
| 60 | Search inside an app | `actions.py`, `QuickSet.java` | 114 | Yes | Built, not phone tested 🟢 |
| 61 | Smart interrupt | `Ears.java`, `index.html` | 68 | Yes | Built, not phone tested 🟢 |
| 62 | Open any app in any script | `actions.py`, `lang.py` | 60 | Yes | Built, not phone tested 🟢 |
| 63 | Any Indian language | `lang.py` | 85 | No | Built, not phone tested 🟢 |
| 64 | Call by name | `CallByName.java` | 199 | Yes | Built, not phone tested 🟢 |
| 65 | Phone health questions in Hindi or English | `phone.py`, `PhoneInfo.java` | 147 | Yes | Built, not phone tested 🟢 |
| 66 | Alarm and timer by voice | `QuickSet.java` | 150 | Yes | Built, not phone tested 🟢 |
| 67 | Weather on Home | - | - | No | DROPPED by Hussain |
| 68 | Music control by voice | `QuickSet.java` | 62 | Yes | Built, not phone tested 🟢 |
| 69 | WhatsApp message by contact name | `CallByName.java` | 95 | Yes | Built, not phone tested 🟢 |
| 70 | Fixes after phone test round 1 | `Apps.java`, `Ears.java` | - | Yes | Built, not phone tested 🟢 |
| 71 | Dual voice fix | `voiceengine.py` | - | No | Built, not phone tested 🟢 |
| 72 | Voice notes and recall | `notes.py` | - | No | Built, not phone tested 🟢 |
| 73 | Misheard-word matching, pause for payment apps, screen wake | `PaymentGuard.java` | - | Yes | Built, not phone tested 🟢 |
| 74 | Settings redesign | `index.html` | - | No | Built, not phone tested 🟢 |
| 75 | Daily life | `remind.py`, `brief.py` | - | No | Built, not phone tested 🟢 |
| 76 | Routine at a fixed time | `tasks.py` | - | No | Built, not phone tested 🟢 |
| 77 | Smart follow-up | `remind.py` | - | No | Built, not phone tested 🟢 |
| 78 | Privacy timeline and missed-reminders summary | `Privacy.java` | - | Yes | Built, not phone tested 🟢 |
| 79 | Deep phone doctor | `phone.py`, `PhoneInfo.java` | - | Yes | Built, not phone tested 🟢 |
| 80 | Phone problems in briefing, weekly summary, weekday routines | `brief.py`, `tasks.py` | - | No | Built, not phone tested 🟢 |
| 81 | No separate record in the old notes | - | - | No | Unknown |
| 82 | Snooze, night summary, Hindi routine words, storage trend, payment apps list, backup of | `PaymentGuard.java`, `phone.py` | 250 | Yes | Built, not phone tested 🟢 |
| 83 | Shopping lists, habit tracker, explain screen, battery guardian, day report | `lists.py`, `habits.py` | 297 | No | Built, not phone tested 🟢 |
| 84 | Expense logger, clipboard buttons, reply ideas | `spend.py`, `replyideas.py` | 162 | No | Built, not phone tested 🟢 |
| 85 | Home card next best move | `lens.py`*, `app.py`, `index.html` | about 80 | No | Built, not phone tested 🟢 |
| 86 | Now / Next / Later | `lens.py`, `index.html` | about 43 | No | Built, not phone tested 🟢 |
| 87 | Honest Mission view | `progress.py`, `app.py`, `index.html` | 39 | No | Built, not phone tested 🟢 |
| 88 | Memory Atlas | `memory.py`, `app.py`, `index.html` | 30 | No | Built, not phone tested 🟢 |
| 89 | Search everywhere | `search.py`*, `app.py`, `index.html` | 39 | No | Built, not phone tested 🟢 |
| 90 | Source label | `web.py`, `app.py` | 14 | No | Built, not phone tested 🟢 |
| 91 | Red Team | `redteam.py`, `app.py`, `index.html` | ~60 | No | Built, not phone tested 🟢 |
| 92 | Debate Jarvis | `debate.py`, `app.py`, `index.html` | ~80 | No | Built, not phone tested 🟢 |
| 93 | Decision Debt | `decisions.py`, `brief.py`, `backup.py`, `app.py` | ~90 | No | Built, not phone tested 🟢 |
| 94 | Unfinished business | `decisions.py`, `app.py` | ~50 | No | Built, not phone tested 🟢 |
| 95 | Last talked | `touch.py`, `brief.py`, `backup.py`, `app.py` | ~90 | No | Built, not phone tested 🟢 |
| 96 | Mood check-in | `mood.py`, `brief.py`, `backup.py`, `app.py` | ~80 | No | Built, not phone tested 🟢 |
| 97 | Time Capsule | `capsule.py`, `backup.py`, `app.py`, `index.html` | ~85 | No | Built, not phone tested 🟢 |
| 98 | Conditional capsule | `capsule.py`, `touch.py`, `app.py` | ~70 | No | Built, not phone tested 🟢 |
| 99 | Habit Contract | `habits.py`, `app.py` | ~80 | No | Built, not phone tested 🟢 |
| 100 | Timed modes | `modes.py`, `index.html` | ~70 | No | Built, not phone tested 🟢 |
| 101 | Body Double | `modes.py`, `index.html` | ~60 | No | Built, not phone tested 🟢 |
| 102 | Cool-down | `actions.py`, `index.html` | ~60 | No | Built, not phone tested 🟢 |
| 103 | Dream journal | `dreams.py`, `backup.py`, `app.py`, `index.html` | ~90 | No | Built, not phone tested 🟢 |
| 104 | Signs log | `signs.py`, `backup.py`, `app.py` | ~40 | No | Built, not phone tested 🟢 |
| 105 | One honest question | `redteam.py`, `brief.py`, `app.py`, `memory.py`, `backup.py` | 52 + 2 + 4 + 8 + 1 = 67 | No | Built, not phone tested 🟢 |
| 106 | Topic drift | `drift.py*`, `app.py` | 68 + 4 = 72 | No | Built, not phone tested 🟢 |
| 107 | Context Ghost | `ghost.py*`, `app.py`, `index.html` | 76 + 8 + 3 = 87 | No | Built, not phone tested 🟢 |
| 108 | Recovery card | `brief.py`, `app.py`, `index.html` | 20 + 8 + 12 = 40 | No | Built, not phone tested 🟢 |
| 109 | Life Timeline | `events.py*`, `app.py`, `index.html` | 63 + 5 + 24 = 92 | No | Built, not phone tested 🟢 |
| 110 | Money picture | `money.py*`, `brief.py`, `backup.py`, `memory.py`, `app.py` | 100 + 5 + 2 + 1 + 4 = 112 | No | Built, not phone tested 🟢 |
| 111 | What-if | `money.py` | 30 | No | Built, not phone tested 🟢 |
| 112 | Note after a call | `CallNote.java*`, `MainActivity.java`, manifest, `Privacy.java` | about 95 | Yes | Built, not phone tested 🟢 |
| 113 | Reminders by place | `placenote.py*`, `PlaceWatch.java*`, `MainActivity.java`, manifest | about 430 (shared base for | Yes | Built, not phone tested 🟢 |
| 114 | Bluetooth triggers | `placenote.py`, `PlaceWatch.java`, `MainActivity.java`, manifest | about 75 | Yes | Built, not phone tested 🟢 |
| 115 | Anti-Doomscroll | `UsageWatch.java*`, `MainActivity.java`, manifest, `Privacy.java` | about 215 (shared base for | Yes | Built, not phone tested 🟢 |
| 116 | App habit map | `UsageWatch.java`, `MainActivity.java`, `index.html` | about 40 | Yes | Built, not phone tested 🟢 |
| 117 | What's new answers | `whatsnew.py`*, `app.py` | 81 | No | Built, not phone tested 🟢 |
| 118 | Assist mode: guest session core | `guest.py`*, `app.py`, `index.html` | 56 + 18 + 13 = 87 | No | Built, not phone tested 🟢 |
| 119 | Assist tools | `assist.py`, `see.py`, `app.py`, `index.html` | 43 + 12 + 24 + 8 = 87 | No | Built, not phone tested 🟢 |
| 120 | Lens rail | `lens.py`, `app.py`, `index.html` | about 33 | No | Built, not phone tested 🟢 |
| 121 | Glass skin 1 of 2 | `index.html` | about 90 (CSS 65, JavaScript | No | Built, not phone tested 🟢 |
| 132 | Glass skin 2 of 2 | `index.html` | about 70 (CSS 54, JavaScript | No | Built, not phone tested 🟢 |
| 133 | New app logo | 5 logo pictures (mipmap folders) | 0 | No | Built, not phone tested 🟢 |
| 122 | Bottom bar | `index.html` | 20 added, 4 changed | No | Built, not phone tested 🟢 |
| 123 | Mic keeps going | `Ears.java`, `ScreenService.java`, `index.html` | 17 + 22 + 4 = 43 | Yes | Built, not phone tested 🟢 |
| 124 | One default voice | `voiceengine.py`, `index.html` | 3 + 4 = 7 | No | Built, not phone tested 🟢 |
| 125 | Call by name, dictation tolerant | `actions.py` | 2 | No | Built, not phone tested 🟢 |
| 126 | Better context and word match | `app.py` | - | No | Built, not phone tested 🟢 |
| 127 | Click by number | `ScreenService.java` 42, `actions.py` 14, `index.html` 1 | 58 | Yes | Built, not phone tested 🟢 |
| 128 | Keep going words | `actions.py` 5, `index.html` 2 | 7 | No | Built, not phone tested 🟢 |
| 129 | Look and tap | ScreenService.java, MainActivity.java, see.py, actions.py, app.py, index.html | 253 | Yes | Built, not phone tested 🟢 |
| 130 | Voice fixes from the 17 Nov screenshots | `actions.py`, `MainActivity.java`, `index.html` | ~60 | Yes | Built, not phone tested 🟢 |
| 131 | Port busy fix | `run.sh`, `app.py` | 9 + 6 = 15 | No | Built, not phone tested 🟢 |
| 134 | Conversation pauses, not ends: after 4 silent rounds or when you leave the app it pauses and continues when you return or tap the mic or Jarvis; speech error 2 gets more tries and then a retry every few seconds; its own sentence is ignored. | `index.html`, `MainActivity.java`, `Ears.java` | 49 | Yes | Built, not phone tested 🟢 |
| 135 | Wake word to Conversation: tap the `Jarvis heard you` notification and Conversation starts on Home (needs Parts 39 and 40 phone tested) | `MainActivity.java`, `ListenService.java`, `index.html` | 11 | Yes | Built, not phone tested 🟢 |
| 136 | Table A runner: `table a next` shows the next test row with PASS / FAIL / Skip buttons (typing works too: `table a pass 12`, `table a fail 12 note`, `table a skip 12`, `table a note ...`, `table a show 12`, `table a status`, `table a fails`). Answers are kept in the phone's database with date and note, so a new zip never erases them; they feed the Verified count (Part 87 card and `mission`). Skipped rows come back after the fresh ones | `phonetest.py`, `progress.py`, `app.py`, `index.html` | 133 | No | Built, not phone tested 🟢 |
| 137 | Quiet mode exceptions: `quiet mode 2 hours except namaz, Ammi` (also `quiet mode 45 minutes`). Quiet as before (no voice, short replies), but a SPOKEN alert whose text has an exception word (or its Hindi spelling, for namaz, ammi, abbu, mummy, papa, doctor, dawai) is still read aloud. Up to 5 words, one word each. Speech only: nothing is run | `modes.py`, `index.html` | 36 | No | Built, not phone tested 🟢 |
| 138 | Chat never lost, no fake done: every new pairing joins the oldest device, so chat and data survive a re-pair (old devices merged once); a short AI answer that claims a phone action is replaced by "I did nothing"; old `(phone action)` lines are not sent to the AI | `app.py`, `test_app.py` | 66 | No | Built, not phone tested 🟢 |
| 139 | Loose commands, round two: home, back and scroll work with filler words and one stray word (`होम स्क्रीन पर जाओ`, `open home screen`); `मैं अम्मी को कॉल कर` and `call ammi at anyhow` call Ammi; `usko open karo` asks which app; volume accepts filler. Click, type, send, pay, delete stay as before | `actions.py`, `test_app.py` | 51 | No | Built, not phone tested 🟢 |
| 140 | One Voice mode: Off / Hey Jarvis / Conversation instead of three switches; Interrupt is automatic (starts only when earphones are connected). Voice sheet is solid and tidy | `index.html` | 24 | No | Built, not phone tested 🟢 |
| 141 | Talk on Home: tap Jarvis on Home and it listens and answers there (reply bubble, `Thinking` and `Speaking` status), no jump to Chat; the chat still keeps the messages | `index.html` | 18 | No | Built, not phone tested 🟢 |
| 142 | Simple screens: Home keeps Next best move, AI tools (9 tiles + `More tools`) and Today's schedule; Honest progress, Insights, Smart shortcuts and Phone and server are under `More`. Settings keeps Voice, Look, Privacy; Your Data, Notifications and Advanced are under `More`. The Assist tab shows all tools, the Memory tab opens Your Data | `index.html` | 16 | No | Built, not phone tested 🟢 |
| 143 | What Jarvis learned: counts of whom you call and which app you open, per hour (names only, never words or screen); card in Settings > More > Your Data with Keep and Delete; one offer on Home for this hour (`Shall I?` Yes / Not now); words `seekha dikhao`, `seekhna band karo`, `seekhna chalu karo`, `seekha bhool jao`; a line needs 3 times on 3 days; unkept lines vanish after 30 days; `delete everything` also erases it | `learn.py`, `app.py`, `backup.py`, `test_app.py`, `index.html` | 158 | No | Built, not phone tested 🟢 |
| 144 | Know people by voice: Vosk speaker model (about 13 MB); Jarvis asks aloud and saves only after a yes; greets and remembers the last talk | `*SpeakerId.java`, `*voices.py`, `MainActivity.java`, `app.py`, `index.html` | ~250 | Yes | Planned |
| 145 | Samjha probe: `samjha: <sentence>` shows the language, the understood text, the phone command it would make (or `not a phone command`) and whether it would wait for your Yes. Runs nothing, saves nothing, never asks the AI; a password, OTP, PIN or card is not repeated | `actions.py`, `app.py` | 42 | No | Built, not phone tested 🟢 |
| 146 | Unknown sentences list: a short command-looking sentence the grammar missed is kept (the sentence only, in the app only). Say a clear command right after it and Jarvis pairs them; one tap on Teach (Settings > Your Data) makes it mean that. Words: `unknown dikhao`, `unknown teach N`, `unknown hatao N`, `unknown band karo`/`chalu karo`, `unknown saaf karo`. Calls, messages, clicks, typing, alarms are never taught | `*unknown.py`, `app.py`, `backup.py`, `memory.py`, `index.html`, `test_app.py` | 139 + 20 + 5 + 3 + 15 | No | Built, not phone tested 🟢 |
| 147 | Real tick: a tick or cross after a phone action comes only from the phone's own result (done, failed). Waiting, unsure, refused by a switch: no sign. The AI never writes one at the start of a short answer | `index.html`, `app.py`, `test_app.py` | 12 + 11 + 3 | No | Built, not phone tested 🟢 |
| 148 | More Jarvis mishearings: जरवेस, जरवेश, जर्वेस, जरविस, हिसारिस्ट, jar vis, jarvice and more count as the wake word (page, ListenService, WakeEngine) | `ListenService.java`, `WakeEngine.java`, `index.html` | 6 | Yes | Built, not phone tested 🟢 |
| 149 | Screenshot sentences as tests: torch, call Ammi, scroll, back, home, last update. The 5 that failed before are fixed by Part 139 and now PASS | `test_app.py` | 13 | No | Built, not phone tested 🟢 |
| 150 | No more fingerprint: the app lock (Part 36) is OFF for good. Jarvis never asks for a fingerprint, face or PIN. An old ON saved by an older APK is cleared at start. The App lock card is gone from Settings > Privacy | `AppLock.java`, `index.html` | 55 + 7 removed | Yes | Built, not phone tested 🟢 |
| 151 | Home hologram: a light disc and beam under the orb, three tilted rings turning around it, scan lines, a small float and flicker. Faster when listening, red when stopped. Dark phones only. OFF: Settings > Look > `No hologram`, or say `no hologram` (`hologram on` brings it back) | `index.html` | 39 added + 3 changed | No | Built, not phone tested 🟢 |
| 152 | Zip number already used by an earlier update (the phone says: skipped, same zip already done). No code of its own | - | - | No | Built, phone tested 🟢 |
| 153 | (1) Jarvis searches the internet by itself for live questions (price, news, score, weather); coin prices come from CoinGecko; `net par search karke batana` searches the question before; Settings switch. (2) `hisab` inside a normal sentence no longer opens the ledger. (3) Theme: Auto / Dark / Light / Neon (old), warm calm colours, Settings > Appearance, or say `dark theme` / `light theme`. (4) Settings in sections with icon cards, new Voice & Listening card. (5) Talk opens at the newest message. (6) Keep listening in background: foreground mic service with a Stop notification (`KeepAlive`), Conversation and Hey Jarvis continue after Home or screen off. (7) Faster mic restart (0.12 s) and a Wait-after-I-stop-talking setting (1.5 / 2.5 / 4 s) | `web.py`, `app.py`, `ledger.py`, `test_app.py`, `index.html`, `KeepAlive.java`*, `MainActivity.java`, `Ears.java`, `AndroidManifest.xml` | about 330 added | Yes | Built, not phone tested 🟢 |
| 154 | Reading scroll: `padhte hue scroll karo` / `scroll karte raho` scrolls ONE screenful (about 85% of the page, the last line you read stays on top), waits 1.5 to 2.5 s so you can read, then the next. Stops on `scroll ruko` or `ruko`, at the end of the page, when you leave the app, after 20 screens or 2 minutes. Only scrolls, never taps. The normal single `neeche scroll karo` and its swipe fallback are now also one screenful, with a soft finger end (Android 8+) so the page does not fly further. Not done: nothing special for Shorts | `ScreenService.java`, `MainActivity.java`, `actions.py`, `index.html`, `test_app.py`, `README.md` | about 150 + 5 changed | Yes | Built, not phone tested 🟢 |
| 155 | Auto-learn: every 8th normal chat (in the background, after the answer) the AI is asked for at most 3 lasting facts or likes that Hussain stated himself. Small facts are saved by themselves and sent to the AI as context; health, religion, politics and family matters are only OFFERED (Yes / No, the Part 54 buttons); money, banks, passwords, OTPs, cards, IDs and numbers are never picked up. A fact must rest on his own words. Say `kya samjha` (list), `galat hai #N` (forget for good), `auto seekhna band karo` / `chalu karo`, `auto seekha bhool jao` (erase all); the old `seekhna band karo` stops it too | `autolearn.py` (new), `app.py`, `memory.py`, `backup.py`, `test_app.py`, `README.md` | 177 + about 30 changed | No | Built, not phone tested 🟢 |
| 156 | The `What Jarvis learned` card (Settings > Your Data) also lists the facts picked up from your talk (Part 155), each with `Wrong, delete`, and a `Last 24 hours` line with the new ones. Delete forgets the fact for good (the words go, only a short fingerprint stays so it is not picked up again) | `autolearn.py`, `app.py`, `index.html`, `test_app.py`, `README.md` | about 25 + 20 page | No | Built, not phone tested 🟢 |
| 157 | Jarvis asks at the right moment, never acts alone (`nudge.py`, new): after 8 pm `today I picked up N new things, show?` (runs `kya samjha`); after 7 pm a habit with a streak of 2 or more that is not marked today `ho gaya ho to log kar dun?` (Yes sends `aaj gym gaya`, exactly as typed). One offer at a time, at most 2 answered per day, never before 7 am or after 11 pm. Buttons: Yes, Not now, Never (that kind is gone for good). Words: `sujhav band karo` / `sujhav chalu karo`; `seekhna band karo` also stops them. Added to the Part 143 offer box | `nudge.py` (new), `autolearn.py`, `app.py`, `memory.py`, `backup.py`, `index.html`, `test_app.py`, `README.md` | 89 + about 20 changed | No | Built, not phone tested 🟢 |
| 158 | Context: messages older than the last 20 are folded into ONE short summary (max 700 characters, numbers hidden, made in the background every 10 older messages) that the AI reads with the last 20, so `woh wala` / `usko` still work. `clear history` and `delete everything` delete it | `chatsum.py` (new), `app.py`, `memory.py`, `backup.py`, `test_app.py`, `README.md` | 80 + about 30 changed | No | Built, not phone tested 🟢 |
| 159 | Thinking sound: a soft `hmm` (made by the phone's sound engine, no file) when a spoken answer takes more than 0.8 s. Settings > Voice & Listening > `Thinking sound` (ON), not in quiet mode | `index.html` | about 12 + 3 changed | No | Built, not phone tested 🟢 |
| 160 | Fast interrupt (earphones): the page is told the moment your VOICE starts (mic level, about 0.1 to 0.3 s, not 10 ms) and Jarvis pauses at once; if it was his own voice or no real words follow in 1.8 s he goes on. The interrupt mic now starts together with his voice. The next message also carries what Jarvis was saying and how much you heard (`cutoff.py`), so he knows the topic. Not done: loudspeaker interrupt | `Ears.java`, `index.html`, `app.py`, `cutoff.py` (new), `test_app.py`, `README.md` | about 35 + 3 changed (Java 25, page 14, backend 30) | Yes | Built, not phone tested 🟢 |
| 161 | Hear the whole sentence: if you pause in the middle and go on within `Wait after I stop talking` (Settings > Voice & Listening), the parts are joined and sent as ONE sentence. Before, the first part was answered alone (half caught) | `Ears.java`, `index.html` | about 34 + 6 changed | Yes | Built, not phone tested 🟢 |
| 162 | Mic in one go: (a) no restart beep: the notification and system sounds are muted for about 1 s around each start of the speech service and given back at once (music that is playing is never touched; Settings switch `Mute the listening beep`, ON); (b) Conversation and Hey Jarvis are remembered and come back by themselves when the app opens (Settings switch `Remember Conversation / Hey Jarvis`, ON); only YOUR stop clears it: Stop button, voice card Off, `bas`, or the notification Stop; (c) a mic error never ends the mic: Hey Jarvis, Conversation and the background test try again after 3, 6, 12, 30, 60 s (only a missing permission stops it) | `Ears.java`, `ListenService.java`, `MainActivity.java`, `index.html`, `README.md` | about 55 Java + 25 page | Yes | Built, not phone tested 🟢 |
| 163 | YouTube Shorts / Reels: `agla video`, `pichla video` (also `next short`, `next reel`) do ONE quick swipe through the middle of the screen to the next or the previous video. Only a swipe, never a tap; Phone control must be ON. A sentence with any other word (a title, `send`) is not taken | `actions.py`, `ScreenService.java`, `index.html`, `README.md` | about 24 + 11 Java + 1 page | Yes | Built, not phone tested 🟢 |
| 164 | Interrupt on the loudspeaker (experimental): Settings > Voice & Listening switch, OFF by default. With no earphones the mic listens while Jarvis speaks, but the mic LEVEL is not used (his own voice would trigger it): only your WORDS count, and words that are mostly his own sentence are ignored (stricter than with earphones). So it is slower (about 1 s) and can fail. Android does not give an app echo cancel for the speech service | `Ears.java`, `MainActivity.java`, `index.html`, `README.md` | about 4 Java + 4 page | Yes | Built, not phone tested 🟢 |
| 165 | Learn from `galat samjha`: say `nahi, woh nahi` (or `galat samjha`, `wrong one`) after a sentence Jarvis got wrong, then say the right command. Jarvis does it and asks `Remember this? "X" means "Y"` with Yes / No; Yes = taught (same as `unknown teach N`, so all normal checks still run). Only safe commands can be taught (not calls, clicks, typing, alarms, risky steps); needs `unknown chalu` ON; the pairing lasts 5 minutes and is kept in RAM | `unknown.py`, `app.py`, `index.html`, `README.md` | about 45 backend + 10 page | No | Built, not phone tested 🟢 |
| 166 | Battery guard: below 15% and not charging the background `Hey Jarvis` mic stops, a notification says so once and Settings shows `Battery guard: Paused`; it starts again at 20% or on the charger (checked every 30 to 60 s while the test runs). The mic you open yourself in the app is not touched | `ListenService.java`, `index.html`, `README.md` | about 50 Java + 1 page | Yes | Built, not phone tested 🟢 |
| 167 | Header and voice screen made clear: new logo, short header (only `Online`; tap it for the update note), search button (this chat, or `Search everywhere` = notes, memory, people, lists), the mic line shows only when the mic is on, the speaker button dims when voice is off, Voice mode is 3 cards (Off / Hey Jarvis / Conversation) with one line each. `update kiya?` / `kya update hua` is now answered from the zips on this phone (Part 117) instead of the AI | `index.html`, `whatsnew.py`, `README.md` | about 27 page + 10 changed, 8 + 6 backend | No | Built, not phone tested 🟢 |
| 168 | Attachments: the paperclip in the chat takes ONE file: an image, a text or code file (.py .java .html .json .md and more, up to 400 KB), a PDF or a Word file (up to about 1 MB). It waits in a chip until you send; then Jarvis answers about it (with no question: a summary). Follow-up questions work for 30 minutes (the file text is held in RAM only, never saved). Long number runs (phone, card, Aadhaar) are hidden before the text goes to the AI. A scanned PDF has no text: send a photo of the page. PDF reading is simple; `pip install pypdf` in Termux makes it better. Off in a guest session | `attach.py` (new), `app.py`, `see.py`, `index.html`, `README.md` | about 117 new + 25 backend, page 18 + 4 changed | No | Built, not phone tested 🟢 |
| 169 | Normal-AI mode: for code, audits, long explanations, plans, pasted code or a file, Jarvis writes ONE full answer (own prompt, up to 3000 tokens, 120 s) with simple markdown and code blocks that have a `Copy` button, plus `Copy answer` on long replies. Phone commands, short chat and voice stay 1 to 3 sentences. A long answer is not read aloud (Jarvis says it is on screen). Old long answers are cut when sent back to the AI, so the memory does not fill. Messages up to 12000 characters. Settings > Voice & Listening > `Full answers` turns it off | `deep.py` (new), `app.py`, `index.html`, `README.md` | about 40 new + 11 backend, page 15 + 6 changed | No | Built, not phone tested 🟢 |
| 170 | Works without internet: a quick check (2 servers, cached 20 s; a working AI call in the last 2 minutes counts as online). With no internet the AI path gives ONE clear line at once (`No internet right now ... Phone commands, notes, lists, reminders and habits still work.`, in Hindi too) instead of a 60 s wait and an error, the internet lookup is skipped, and the header shows `● No internet`. Phone commands, notes, lists, reminders and habits never use the internet, so they are unchanged. Hussain dropped the idea of an own AI model on the phone (21 Nov) | `app.py`, `index.html`, `README.md` | about 39 backend + 2 page | No | Built, not phone tested 🟢 |

## 3. WHAT HUSSAIN DOES NOW

1. GitHub > Actions > **Build APK** > Run. Red? Send a screenshot of the error. Java (Parts 112 to 116, 129, 133 and others) was never compiled before.
2. Install the APK. Then Accessibility > `Jarvis screen reader` OFF and ON once (Part 129 needs the screenshot permission; Android 11 or newer).
3. **Retest the voice problems first.** The 17 Nov screenshots show old versions (headers say Part 89 to 122). Parts 125, 126 and 130 already target them (call by name, context, torch words). Try the same sentences again. Send screenshots only of what still fails.
4. Try Table A (section 7). Write PASS or FAIL for each row.
5. Then name the next Part from the plan (section 4).

**Done 19 Nov: 146, 147, 150, 151, 138, 149, 148, 139, 134, 140, 141, 142, 143, 135, 136, 137, 145 (built, not phone tested; 148, 134 and 135 are Java, so the APK must be built). Next in the order below: Part 144.**

**Done 19 Nov (later): 154 to 161 are all built, not phone tested. 154, 160 and 161 are Java, so build the APK. Next: phone-test them (Table A rows 78 to 88) and send what is wrong.**

**Done 21 Nov: 167, 168 and 169 are built (page and backend only, no Java, no new APK), not phone tested. Planned and ready, in this order: 170 (works without internet), then 162 + 166 (mic in one go, battery guard), then 163 + 165, then 164, and 144 last. Dropped by Hussain: the own AI model on the phone, and idea 4 (car / Bluetooth mode). New ideas, not numbered yet: share a screenshot or text from any app to Jarvis (about 60 lines, APK), chat history list (about 100), speak the reply only when you spoke (about 30), export a chat in one tap (about 40).**

**Done 21 Nov (later): 163, 164, 166 and 170 are built, not phone tested (no tests were run, only the page syntax and the `import app` check). 163, 164 and 166 are Java, so build the APK. Still planned: 162 (mic in one go: no beep, mode remembered), 165 (learn from `galat samjha`), 144 (voice to person, last). New ideas, not numbered: share a screenshot or text from any app to Jarvis, chat history list, speak the reply only when you spoke, export a chat in one tap, a Stop button that ends his speech. Phone-test rows: Table A 89 to 102.**

**Done 21 Nov (last): 162 and 165 are built, not phone tested (no tests, only page syntax and the `import app` check). 162 is Java, so build the APK. Still planned: 144 (voice to person, risky, last). New ideas, not numbered: share a screenshot or text from any app to Jarvis, chat history list, speak the reply only when you spoke, export a chat in one tap, a Stop button that ends his speech. Phone-test rows: Table A 89 to 107.**

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
- An own AI model on the phone (21 Nov, Hussain dropped it): a 1 to 2 GB model is too weak for code and long answers. Jarvis keeps using the free AI keys; Part 170 makes the rest work without internet.
- Car / Bluetooth mode (Hussain dropped it, 21 Nov).

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
| 65 | Settings > Voice settings: look at the sheet. Pick `Conversation` in Voice mode, talk to Jarvis, then press Home and open another app for 20 seconds, then come back | One Voice mode choice (Off / Hey Jarvis / Conversation), no Hey Jarvis, Conversation or Interrupt buttons. The sheet is solid. Leaving the app shows `Conversation paused`; coming back continues listening by itself | Yes (Part 134) | not tested |
| 66 | In Conversation mode stay silent for 4 rounds, then tap the mic. Also turn Wi-Fi and data off for 10 seconds while it listens, then turn them on | After 4 silent rounds it says it paused (it does not turn off) and one tap continues. With no internet it waits and tries again by itself; Jarvis's own sentence is not answered | Yes (Part 134) | not tested |
| 67 | On Home tap Jarvis (the orb) and say `what is the time`. Then say it again with `Conversation` on | The page stays on Home, the bubble shows `You: ...` and the answer, status shows Listening, Thinking, Speaking. Chat has the same messages | No (Part 141) | not tested |
| 68 | Open Home. Look at the sections, then open `More`. Then tap the Assist tab and the Memory tab. In Settings look at the list | Home shows Next best move, AI tools (9 tiles and a `More tools` button) and Today's schedule; `More` holds Honest progress, Insights, Smart shortcuts, Phone and server. Assist shows all tools. Settings shows Voice, Look, Privacy and `More`; Memory opens Your Data inside More | No (Part 142) | not tested |
| 69 | Say `call Ammi` (or open YouTube) around the same hour on 3 different days. Next day at that hour open Home. Then Settings > More > Your Data > What Jarvis learned | Home shows `Sir, around this time you usually call Ammi. Shall I?` with Yes and Not now (Yes runs the call command, Not now hides it for today). The card lists the line with Keep and Delete. `seekhna band karo` stops it; `seekha bhool jao` erases it | No (Part 143) | not tested |
| 70 | Turn Hey Jarvis background listening on, lock the phone, say `Jarvis`, then tap the `Jarvis heard you` notification | Jarvis opens on Home and Conversation starts (mic opens by itself, then listens again after each answer) | Yes (Part 135) | not tested |
| 71 | Type `table a next`. Tap PASS (or FAIL) under the row. Then type `table a status`, `table a fails`, `mission` | The next unanswered row shows with Try, Expect and APK, plus PASS / FAIL / Skip buttons. After a tap it says `test N: PASS saved`, shows the count and the next row. `status` shows PASS, FAIL, skipped and not done; `fails` lists failed rows with notes; `mission` Verified goes up by the PASS you tapped. After a new zip the answers are still there | No (Part 136) | not tested |
| 72 | Say `quiet mode 2 hours except namaz, Ammi`. Set a reminder 2 minutes ahead that says `namaz`, and another that says `chai`. Wait for both with the page open | The top bar says `quiet mode until HH:MM, except namaz, ammi`. The namaz reminder is read aloud; the chai reminder is text only. Normal replies stay silent. `normal mode` ends it | No (Part 137) | not tested |
| 73 | Type `samjha: open youtube`, then `samjha: message bhejo`, `samjha: kal 9 baje chai yaad dilana`, `samjha: होम स्क्रीन पर जाओ` | Each answer shows Language, Understood as, and the phone command (or `not a phone command`); `message bhejo` says it waits for your Yes. Nothing opens, nothing is sent or saved, and the end line says `Nothing was run` | No (Part 145) | not tested |
| 74 | Install the new APK. Open Jarvis, close it, wait 6 minutes, open it again. Look in Settings > Privacy | No fingerprint, face or PIN prompt at any time. The `App lock` row is not in Privacy any more | Yes (Part 150) | not tested |
| 75 | On Home (dark phone) look at the orb. Then Settings > Look > tick `No hologram`. Then say `hologram on`. Tap the orb and talk | The orb floats over a light disc with a beam and 3 turning rings. Tick `No hologram`: the rings, beam and disc vanish and the orb is as before. `hologram on` brings them back. While listening the rings turn faster; when Jarvis is stopped the hologram turns red. Phone setting `Remove animations` makes it still | No (Part 151) | not tested |
| 76 | Say a sentence Jarvis cannot parse, like `torch jala de bhai`. Then say `torch chalu karo`. Open Settings > Your Data > Sentences I did not understand. Tap Teach. Say the first sentence again | The sentence is listed with the clear command next to it. After Teach, the first sentence turns the torch on. `unknown band karo`: nothing new is kept and taught lines pause. Delete removes one line | No (Part 146) | not tested |
| 77 | Say `torch chalu karo`, `volume badhao`, then `home jao`. Then turn Phone control OFF and say `torch chalu karo` | A ✔ appears only after the phone really did it. A ✖ appears only when the phone says it failed. With Phone control OFF, or when it says `waiting`, there is no ✔ or ✖ | No (Part 147) | not tested |
| 78 | Open YouTube (home list). Say `neeche scroll karo` three times | Each time the list moves about one screen: the last video you saw is still near the top and new ones show below. It does not jump far | Yes (Part 154) | not tested |
| 79 | In YouTube say `padhte hue scroll karo`. Wait. Then say `scroll ruko` | It scrolls one screen, waits about 2 seconds, scrolls again. `scroll ruko` stops it at once. Without a stop it ends by itself at the end of the page, after 20 screens or 2 minutes. Jarvis says how many screens moved (open Jarvis to see) | Yes (Part 154) | not tested |
| 80 | Turn Conversation ON. Ask a question that needs the internet, like `bitcoin ka price kya hai`. Settings > Voice & Listening > Thinking sound ON | A soft low `hmm` plays if the answer takes more than a moment, then Jarvis answers. Thinking sound OFF: no `hmm`. Quiet mode: no `hmm` | No (Part 159) | not tested |
| 81 | Conversation ON. Say a sentence with a pause in the middle, like `Mumbai ki... (1 second) ...top news batao` | Jarvis answers the WHOLE sentence once, not the first half. Settings > Wait after I stop talking: Fast joins only short pauses, Patient joins longer ones | Yes (Part 161) | not tested |
| 82 | Earphones ON, Conversation ON. Ask something long (`Mumbai ke baare me lamba batao`). While Jarvis speaks, start talking: `nahi, Pune ka batao` | Jarvis goes quiet almost at once when you start (about a quarter second). Your whole sentence is answered, and the answer knows what he was saying before. Cough or clap: he pauses, then goes on after about 2 seconds | Yes (Part 160) | not tested |
| 83 | Talk about Bitcoin and your cousin for 10 messages, e.g. `mujhe bitcoin chart pasand hai`, `mera cousin Arman cricket khelta hai` (the AI needs a real key, not mock). After about 8 chats say `kya samjha` | A short list like `#1 Hussain follows Bitcoin charts`. Nothing about money, banks, passwords or numbers. `galat hai #1` removes it for good. `auto seekhna band karo` stops picking up | No (Part 155) | not tested |
| 84 | Say `meri dawai ka time subah 8 hai` in a normal chat, keep chatting 8 times | Jarvis may ask once `save this?` with Yes / No. Nothing health-related is saved before you tap Yes | No (Part 155) | not tested |
| 85 | Chat 30 messages about a topic (a trip, a person). Then ask `woh wala plan phir se batao` or `usko kya bola tha` | Jarvis knows what `woh` / `usko` means even for things said more than 20 messages ago. `clear history` then forgets the summary too | No (Part 158) | not tested |
| 86 | Settings > Your Data > What Jarvis learned. After a few chats (Part 155) | Under the call/app counts there is a list of picked-up facts, a `Last 24 hours` line, and `Wrong, delete` on each. Delete removes it; `kya samjha` no longer lists it | No (Part 156) | not tested |
| 87 | Make a habit (`habit banao gym`), mark it two days in a row, skip today, and open Jarvis after 7 pm | The offer box shows `aaj gym abhi tak mark nahi hua (streak 2 din). Ho gaya ho to log kar dun?` with Yes, Not now, Never. Yes logs it. Not now: not again today. Never: this habit is not offered again | No (Part 157) | not tested |
| 88 | Say `sujhav band karo`, then open Jarvis in the evening | No offers at all. `sujhav chalu karo` brings them back | No (Part 157) | not tested |
| 89 | Open Jarvis. Look at the top bar and the line under it | Top bar: new round logo, the word JARVIS, and only `● Online` (no long update text). Tap `● Online`: a small `Last update: ...` line opens or closes. The grey mic line is NOT there while the mic is off | No (Part 167) | not tested |
| 90 | Tap the speaker button. Look at the `Voice mode` part | Three cards: Off, Hey Jarvis, Conversation, each with one line that says what it does. The active card has a coloured border. Tap one: it switches (same as before). Voice off in the panel: the speaker button in the top bar looks dim | No (Part 167) | not tested |
| 91 | Chat a bit. Tap the magnifier in the top bar, type a word you said earlier | A list of messages from this chat with the time. Tap one: the chat jumps to it and it flashes. `Search everywhere` sends `sab jagah dhundo <word>` and Jarvis answers from notes, memory, people, lists, reminders | No (Part 167) | not tested |
| 92 | Say or type `update kiya?`, then `kya update hua`, then `last update` | Each time Jarvis names the last zip, the time, the Part and its files (not `I cannot update myself`). `phone update hua?` still goes to the AI | No (Part 167) | not tested |
| 93 | Tap the paperclip, pick a .py or .txt file, leave the question empty, send | A bubble `📎 name` and a full summary of the file. Then ask `line 20 me kya galat hai` or `isme bug dhoondo`: Jarvis answers about that file | No (Part 168) | not tested |
| 94 | Paperclip > a PDF with normal text, ask `is PDF ka summary do`. Then a scanned PDF or photo-PDF | Text PDF: a summary. Scanned PDF: one line saying there is no readable text and to send a photo of the page. A Word .docx works like the PDF | No (Part 168) | not tested |
| 95 | Paperclip > a photo of a bill or a screenshot of some code, ask `isme kya likha hai` | The text is read out in a full answer (code in a code block). Camera button still gives the short answer | No (Part 168) | not tested |
| 96 | Type `python me ek calculator ka code likho`, then `is code ka audit karo` | A full answer with a code block and a `Copy` button (it copies only the code). Long answers have `Copy answer`. Jarvis does NOT read it aloud, he says it is on screen. `kal ka weather` is still short | No (Part 169) | not tested |
| 97 | Settings > Voice & Listening > `Full answers for code and long questions` OFF, then ask for code again | Back to 1 to 3 short sentences. ON again: full answers | No (Part 169) | not tested |
| 98 | Phone control ON. Open YouTube Shorts. Say `agla video`, then `pichla video` | One quick swipe each: the next Short, then the one before. Jarvis says `Next video, sir.` / `Previous video, sir.` Nothing is tapped. Also try `next reel` | Yes (Part 163) | not tested |
| 99 | Switch Wi-Fi and mobile data OFF. Ask `tell me a joke`, then say `torch chalu karo` | The joke gets ONE clear line at once (no long wait): `No internet right now ... Phone commands, notes, lists, reminders and habits still work.` The header shows `● No internet`. The torch works. Switch data back ON: the header says `● Online` again within about 20 s | No (Part 170) | not tested |
| 100 | Turn on the background `Hey Jarvis` test (Settings). Let the battery fall below 15% without a charger (or ask a friend with a low phone to try) | A notification says the background mic is paused. Settings shows `Battery guard: Paused`. Plug in the charger (or reach 20%): it says it is listening again and the test goes on | Yes (Part 166) | not tested |
| 101 | No earphones. Settings > Voice & Listening > `Interrupt on the loudspeaker (experimental)` ON, Interrupt button ON, Conversation ON. Ask something long. While Jarvis speaks, say clearly `nahi, Pune ka batao` | Jarvis stops after about 1 second and answers what you said. Also watch the other way: he must NOT stop by himself while you are quiet. Write what happened | Yes (Part 164) | not tested |
| 102 | Same, but the loudspeaker switch OFF (default), no earphones | Jarvis does not listen while he speaks (like before). With earphones nothing changed: the fast interrupt of Part 160 still works | Yes (Part 164) | not tested |
| 103 | Conversation ON. Wait through a few silent rounds. Listen for the beep | No (or a much quieter) beep each time the mic opens. Settings > Voice & Listening > `Mute the listening beep` OFF: the beep is back. If music plays it keeps playing | Yes (Part 162) | not tested |
| 104 | Turn Conversation ON (or Hey Jarvis ON). Close the app fully (swipe it away), open it again | After about 2 seconds it is ON again by itself with one line `... as you left it`. Tap Stop, close, open: it stays OFF | Yes (Part 162) | not tested |
| 105 | Hey Jarvis ON. Turn mobile data and Wi-Fi OFF for a minute, then ON | The mic does not switch itself off. It tries again after 3, 6, 12, 30, 60 s and works again when the internet is back | Yes (Part 162) | not tested |
| 106 | Say `YouTube kholna` (or any wording Jarvis does not know). Then say `nahi, woh nahi`, then `open youtube` | Jarvis says sorry, opens YouTube, and asks `Remember this? "youtube kholna" means "open youtube"` with Yes / No. Tap Yes: `Okay sir, taught.` Next time that first wording works | No (Part 165) | not tested |
| 107 | Say `unknown dikhao` | The taught sentence is in the list with `(taught)`. `unknown hatao N` removes it | No (Part 165) | not tested |

## 8. RULES FOR EVERY CLAUDE

1. Each Part is under 350 lines. New files only when really needed. After each Part update this README: its row in section 2 (real lines and status) and its Table A rows.
2. Talk to Hussain in simple Roman Hinglish or simple English. Roman script only, NEVER Devanagari, even when he dictates in Hindi. Short plain words, like WhatsApp. He dictates by voice, so spelling mistakes are normal. Show files and lines in a table.
3. Output is ONE zip (see section 0 zip rules) with this Part's files plus every earlier file whose push the app header has not yet shown as "pushed". Never the whole repo.
4. Before a Part say its number, files, lines and WITH or WITHOUT tests. After it say the real lines and offer the next 4 or 5 Parts in a table (Part, files, lines) so he can pick or join them. He may pick 2 or 3 at once.
5. Tests: Python logic is run. Java cannot be compiled by Claude: write "Not run". Never write "tested" for something that was not tested.
6. Ask for as few Termux commands as possible. When he names the next Parts, build at once.
7. Never save passwords, OTPs, PINs or CVVs. Never put keys or tokens in chat, code or Git.
8. His OWL1 trading repo is separate. Never touch it.
9. App lock stays OFF unless he turns it on himself.
10. Read less: sections 0 and 3, your Part's row, its files. Use `grep -n`. Say in one line which files you read.
11. Keep this README short and simple: one Parts table, one line per Part, no pasted chat text. Old detail goes to `docs/`.
12. After a Part, if it was only checked by syntax, its status is `Built, not phone tested`.
13. How Hussain wants things (31 Oct and 21 Nov): ONE zip with only the changed files (all the newest files together), not the whole repo and not files his repo already has. The zip must download with one tap on the file card; if a download fails, fix it, do not send the same file again.
14. No tests every time, to save his limit: syntax check and the `import app` check only; no test file unless he asks. Say `not tested` in the answer.
15. Ask for as few Termux commands as possible, never repeat commands that already ran, and ask for ONE file back at most.
16. Every finished Part shows a green circle in its status cell (section 2). The circle goes at the END of the cell, because `progress.py` reads the status words at the start.
17. Replies in short casual chat words, like WhatsApp. He dictates by voice and writes Hindi: spelling mistakes are normal, read the meaning.

## 9. KNOWN LIMITS

- The phone recognizes ONE language at a time. Choose it in Settings > Voice > `Speak:`. Sarvam speaks only Hindi and English; other languages use Edge voices.
- Android does not let an app open itself from the background, switch Wi-Fi, Bluetooth or location, or delete alarms. Jarvis opens the right page or shows a notification.
- While another app is open Jarvis cannot hear you unless the background listener (Parts 39, 40) runs and you tap its notification.
- Interrupt works best with earphones; a Bluetooth speaker may echo. Stopping Jarvis within 10 ms is not possible: the phone's speech service needs 0.1 to 0.3 s to notice a voice (Part 160 targets that).
- Part 157: the offers come only from habits and from what was picked up (Part 155) and from the call/app counts (Part 143). It does not read your screen, your messages or the news. A habit offer cannot know whether you really did it: it only asks.
- Parts 155 and 158 call the AI in the background (one extra short AI call every 8 chats, and one every 10 older messages). With no real AI key (mock) they do nothing. The AI can still mishear or guess: that is why a fact must rest on your own words and every fact can be deleted.
- Part 154: the scroll length is about one screen, not pixel exact; some apps move a little more or less. Not tested in YouTube Shorts. Part 161: while Jarvis waits for the rest of your sentence the phone's speech service may beep once more.
- Contacts in non-Latin, non-Hindi scripts are not found by `call` (Part 64). Unknown Urdu app names are not matched.
- Place and Bluetooth reminders use the mobile or Wi-Fi position (50 to 200 m) and can be 2 to 10 minutes late.
- Termux may be killed by Android: Settings > Apps > Termux > Battery > No restriction, keep its notification, install Termux:Boot.
- Screenshots (Part 129) work only on Android 11 or newer, never on a screen with a password box or in a payment app, and the AI can point wrong, so you see the spot first.
- The pairing code is in Termux (`PAIRING CODE: ...`, valid 10 minutes). Pairing stays after updates because one fixed signing key is used; uninstalling the app makes a new pairing.
- Part 167: the search button looks only at the messages on screen (this chat) and, with `Search everywhere`, at notes, memory, people, lists and reminders by the same WORDS. The new logo is in the page only: the phone launcher icon and the web icons are the old ones. `update kiya?` can only say what this phone received and pushed (the zips in `~/.jarvis_done`), not what is on GitHub.
- Part 170: the internet check only asks whether two public servers answer on the network; on a network that blocks both while the AI still works, Jarvis may say `No internet` until one AI call succeeds. Part 166: the guard checks about once a minute, so the mic may run a little past 15%. Part 163: one swipe is the same size in every app; if a Short app needs a longer swipe, say so. Part 164: loudspeaker interrupt is experimental and may stop Jarvis by mistake or not at all; earphones work best.
- Part 162: the beep mute is a try: some phones play the beep on a stream Android does not let an app mute (or Do Not Disturb blocks it). If the app dies in the one second of muting, the notification sound stays muted until you press volume up. The restored mode starts the mic by itself when the app opens (switch it off in Settings). Part 165: a taught sentence has to match exactly (same words); `unknown saaf karo` erases them all.
- Parts 168 and 169: the file text and your question go to your AI provider like any message (long digit runs are hidden first). Free AI keys have small limits: only the first 14000 characters of a file are read for the first answer and 9000 for follow-ups, and Jarvis says so. The simple PDF reader fails on some PDFs (special fonts); `pip install pypdf` helps, and a scanned PDF needs a photo of the page. The AI can still write wrong code: Jarvis cannot run it. Full answers are not read aloud.
