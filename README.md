# JARVIS - a personal AI assistant that runs on Hussain's phone (Termux + Chrome, then an Android app)

> **For any new Claude or AI (read this first):** Hussain only sends you this repo link. He has 2-3 Claude accounts and the chat limit
> runs out often. This README has everything: what Jarvis is, every Part (done and planned) in ONE table, what is next, the rules.
> Read sections 1 to 9, then start the next Part he names. Do not ask him to resend the old chat. Repo: https://github.com/mehreenhusn-cmyk/Jarvis

**Map of this file.** Sections 1 to 9 are for everyone (plain words, numbered). `R1` to `R7` after them are old reference detail; open them only when needed.

| # | Section | In one line |
|---|---|---|
| 1 | What Jarvis is | What it does, in 5 lines |
| 2 | All Parts in ONE table | Part 1 to 122: what is built, what is planned, files, lines |
| 3 | What Hussain does now | 4 steps |
| 4 | Total plan: files and lines | What the planned Parts add up to |
| 5 | Ideas we will not build | And why |
| 6 | Safety rules for the new Parts | Every new Part must keep these |
| 7 | Phone tests (Table A) | 24 things to try on the phone |
| 8 | Rules for every Claude | How we work |
| 9 | Known limits and fixes | What Jarvis cannot do, honest |
| R1 to R7 | Reference | How it works, setup, cheat sheet, security, old status, build log, master plan |

---

## 1. WHAT JARVIS IS

1. A personal assistant on Hussain's phone. A small Python server runs in Termux; an Android app (a WebView plus some Java) shows chat and Home and controls the phone.
2. Hussain speaks or types in any Indian language or English. Jarvis answers, opens apps, calls, sets alarms, runs steps in a row, reminds, remembers, keeps lists, habits and expenses, and keeps the phone safe.
3. Everything he gets is ONE zip. He downloads it; `run.sh` unzips it, pushes it to GitHub, restarts the server. GitHub Actions builds the APK.
4. Hussain's goal in his words (16 Nov): say any app name in any language and it opens, and the screen shows what is happening or failing. "Call Ammi" just calls. Jarvis knows battery, Bluetooth and what is wrong with the phone. Jarvis stops talking when somebody speaks.
5. Jarvis never sends, pays, deletes or runs anything on its own. Every risky step waits for Hussain's tap.

## 2. ALL PARTS IN ONE TABLE (Part 1 to 122)

**How to use this table.** Parts are plain numbers in one sequence. No letters, no groups. A new idea gets the NEXT number at the bottom (now 123). When a Part is built, change its Status and fill in the real lines. A range like `1 to 5` means the old notes did not split them. `*` = new file. `-` = not recorded in the old notes (see R5, R6, R7).

**Honest count (17 Nov 2026).** Code is written for Parts 1 to 87 and Part 117 (about 7,100 lines; Part 67 was dropped, Part 81 has no record). Phone tested: Parts 1 to 17 only (12 to 14 partly). Table A (section 7): 0 of 24 tried. Java has never been fully compiled: GitHub Build APK runs #17 to #21 were green (Parts 48, 49, 64, 65 compile). Not compiled yet: `QuickSet` (alarm, timer, search, media), the WhatsApp part of `CallByName`, `Ears` interrupt, `PaymentGuard`, the deep phone check, the `Privacy` timeline.

| Part | What it does | Files | Lines | New APK? | Status |
|---|---|---|---|---|---|
| 1 to 5 | Server, pairing code, chat, history, mic in Chrome, keys, 5 AI providers | - | - | No | Built, phone tested |
| 6 to 9 | Neural voices, voice sliders, Hindi style, memory (yaad rakho) | - | - | No | Built, phone tested |
| 10 to 11 | Reminders, money ledger (owe/get), auto-update `run.sh`, auto-start | - | - | No | Built, phone tested |
| 12 to 14 | Privacy bar, web read and search, morning briefing, duplicate-zip protection | - | - | No | Built, partly tested |
| 15 | Professional look (dark and light) | - | - | No | Built, phone tested |
| 16 to 17 | Android app shell, GitHub APK build, build log | - | - | Yes | Built, phone tested |
| 18 | Reminder notifications with the app closed | - | - | Yes | Built, not phone tested |
| 19 | Calls and contacts (not saved) | - | - | Yes | Built, not phone tested |
| 20 | People notes | `people.py` | - | No | Built, not phone tested |
| 21 | Location, only when asked | - | - | Yes | Built, not phone tested |
| 22 | Camera: describe one photo | - | - | Yes | Built, not phone tested |
| 23 | Screen reader (not saved) | `ScreenService.java` | - | Yes | Built, not phone tested |
| 24 | Phone check (`why is my phone slow`) | `phone.py` | - | Yes | Built, not phone tested |
| 25 | Mic inside the app, Hey Jarvis while the app is open | `Ears.java` | - | Yes | Built, not phone tested |
| 26 | Security check, polish, `clear history` | - | - | No | Built, not phone tested |
| 27 | WebView security: permission checks, local-only http | `MainActivity.java` | 36 | Yes | Built, not phone tested |
| 28 | Real Stop that cannot be undone by voice | `Privacy.java` | 94 | Yes | Built, not phone tested |
| 29 | Privacy dashboard in Settings | `Privacy.java`, `index.html` | 109 | Yes | Built, not phone tested |
| 30 | Command layer: `WhatsApp kholo` becomes one safe action | `actions.py` | 120 | No | Built, not phone tested |
| 31 | Open an app by name | `Apps.java` | 128 | Yes | Built, not phone tested |
| 32 | Better screen reading (buttons, fields, switches) | `screen.py` | 63 | Yes | Built, not phone tested |
| 33 | Risk and confirm rules (send, pay, delete need your tap) | `actions.py` | 52 | No | Built, not phone tested |
| 34 | Safe screen actions (press, scroll, type) and `kitna kaam hua` | `ScreenService.java`, `progress.py` | 355 | Yes | Built, not phone tested |
| 35 | Lock the phone by voice | `ScreenService.java` | 22 | Yes | Built, not phone tested |
| 36 | App lock with Android's prompt, fixed signing key, chat times | `AppLock.java`, `clock.py` | 176 | Yes | Built, not phone tested |
| 37 | Settings by voice (Wi-Fi, Bluetooth, torch, volume) | `PhoneSettings.java` | 152 | Yes | Built, not phone tested |
| 38 | Quick Settings tile and shortcut | `JarvisTile.java` | 46 | Yes | Built, not phone tested |
| 39 | Background listening test (8 hour limit) | `ListenService.java` | 216 | Yes | Built, not phone tested |
| 40 | Offline wake word (Vosk) | `WakeEngine.java` | 230 | Yes | Built, not phone tested |
| 41 | Task engine: several steps in one sentence | `tasks.py` | 133 | No | Built, not phone tested |
| 42 | Task runner in the app | `TaskRunner.java` | 181 | Yes | Built, not phone tested |
| 43 | Phone checklist table | README only | 40 | No | Built, not phone tested |
| 44 | Repeat reminders, birthdays, phone calendar | `remind.py`, `CalendarInfo.java` | 130 | Yes | Built, not phone tested |
| 45 | Richer briefing, suggestions, quiet hours | `brief.py` | 140 | No | Built, not phone tested |
| 46 | Routines (saved task sentences) | `tasks.py` | 75 | No | Built, not phone tested |
| 47 | Encrypted backup, restore with preview, delete everything | `backup.py` | 210 | No | Built, not phone tested |
| 48 | Share to Jarvis, handoff summary, lost-phone card, new Home look | `handoff.py`, `index.html` | 215 | Yes | Built, not phone tested |
| 49 | Clipboard button and notification summary (old notes call them 49a and 49b) | `NotifySummary.java`, `index.html` | - | Yes | Built, not phone tested |
| 50 | System card in Settings | `sysinfo.py` | - | No | Built, not phone tested |
| 51 | Two voices engine (Tony and JARVIS) | `voiceengine.py` | 90 | No | Built, not phone tested |
| 52 | Voice personality cards in Settings | `index.html` | 46 | No | Built, not phone tested |
| 53 | Sarvam voice provider and neon chat look (old notes: 53 and 53b) | `voiceengine.py`, `index.html` | - | No | Built, not phone tested |
| 54 | Smart memory: remembers personal facts you state | `memory.py` | 41 | No | Built, not phone tested |
| 55 | Conversation mode | `index.html` | 31 | No | Built, not phone tested |
| 56 | Home tab (orb, today, quick buttons) | `index.html` | 75 | No | Built, not phone tested |
| 57 | Research answers with sources, mood-support rules | `web.py` | - | No | Built, not phone tested |
| 58 | Voice modes: research, quiet, focus, normal | `modes.py` | - | No | Built, not phone tested |
| 59 | Hindi-script spelling of English words, clean message bar | `actions.py`, `index.html` | 70 | No | Built, not phone tested |
| 60 | Search inside an app (YouTube, Maps, Play Store...) | `actions.py`, `QuickSet.java` | 114 | Yes | Built, not phone tested |
| 61 | Smart interrupt: Jarvis stops when you speak (earphones only) | `Ears.java`, `index.html` | 68 | Yes | Built, not phone tested |
| 62 | Open any app in any script | `actions.py`, `lang.py` | 60 | Yes | Built, not phone tested |
| 63 | Any Indian language | `lang.py` | 85 | No | Built, not phone tested |
| 64 | Call by name (`Ammi ko call karo`) | `CallByName.java` | 199 | Yes | Built, not phone tested |
| 65 | Phone health questions in Hindi or English | `phone.py`, `PhoneInfo.java` | 147 | Yes | Built, not phone tested |
| 66 | Alarm and timer by voice | `QuickSet.java` | 150 | Yes | Built, not phone tested |
| 67 | Weather on Home | - | - | No | DROPPED by Hussain |
| 68 | Music control by voice | `QuickSet.java` | 62 | Yes | Built, not phone tested |
| 69 | WhatsApp message by contact name (you tap Send) | `CallByName.java` | 95 | Yes | Built, not phone tested |
| 70 | Fixes after phone test round 1 (app opening, mic error 11, voice message) | `Apps.java`, `Ears.java` | - | Yes | Built, not phone tested |
| 71 | Dual voice fix (Tony for talk, JARVIS for information) | `voiceengine.py` | - | No | Built, not phone tested |
| 72 | Voice notes and recall (`note karo ...`) | `notes.py` | - | No | Built, not phone tested |
| 73 | Misheard-word matching, pause for payment apps, screen wake | `PaymentGuard.java` | - | Yes | Built, not phone tested |
| 74 | Settings redesign (5 collapsible cards) | `index.html` | - | No | Built, not phone tested |
| 75 | Daily life: Home card, birthdays, notes in the briefing | `remind.py`, `brief.py` | - | No | Built, not phone tested |
| 76 | Routine at a fixed time (one-tap Run) | `tasks.py` | - | No | Built, not phone tested |
| 77 | Smart follow-up (`ho gaya?`) | `remind.py` | - | No | Built, not phone tested |
| 78 | Privacy timeline and missed-reminders summary | `Privacy.java` | - | Yes | Built, not phone tested |
| 79 | Deep phone doctor | `phone.py`, `PhoneInfo.java` | - | Yes | Built, not phone tested |
| 80 | Phone problems in briefing, weekly summary, weekday routines | `brief.py`, `tasks.py` | - | No | Built, not phone tested |
| 81 | No separate record in the old notes | - | - | No | Unknown |
| 82 | Snooze, night summary, Hindi routine words, storage trend, payment apps list, backup of routine time | `PaymentGuard.java`, `phone.py` | 250 | Yes | Built, not phone tested |
| 83 | Shopping lists, habit tracker, explain screen, battery guardian, day report | `lists.py`, `habits.py` | 297 | No | Built, not phone tested |
| 84 | Expense logger, clipboard buttons, reply ideas | `spend.py`, `replyideas.py` | 162 | No | Built, not phone tested |
| 85 | Home card **next best move**: Do, Why, Later and the source; fixed rules, no AI | `lens.py`*, `app.py`, `index.html` | about 80 | No | Built, not phone tested |
| 86 | **Now / Next / Later** strip under that card (built together with 85) | `lens.py`, `index.html` | about 43 | No | Built, not phone tested |
| 87 | **Honest Mission view**: three separate counts, Code built, Phone tested, Verified (Table A PASS), read from the status column and Table A. Chat word `mission`; Home card `Honest progress`. Plain count, no percentage | `progress.py`, `app.py`, `index.html` | 39 | No | Built, not phone tested |
| 88 | **Memory Atlas**: memories, people and notes on one page, with delete. Nothing new is saved | `memory.py`, `people.py`, `app.py`, `index.html` | ~110 | No | Planned |
| 89 | **Search everywhere**: `sab jagah dhundo Bombay` looks in notes, memories, people, lists, reminders (and later decisions, capsules, dreams) and says where each hit came from. Matches words, not meaning | `search.py*`, `app.py`, `index.html` | ~70 | No | Planned |
| 90 | **Source label** on research answers: `One report` or `N sources agree`, counted from the real search result | `web.py`, `index.html` | ~45 | No | Planned |
| 91 | **Red Team**: `red team: yeh phone kharidna hai`. The AI gets only your own Jarvis numbers (this month's spending, habits, memories), asks 3 hard questions and gives 2 counter-points. No invented numbers | `redteam.py*`, `app.py`, `index.html` | ~60 | No | Planned |
| 92 | **Debate Jarvis**: `debate ruthless: ...`, `debate spiritual: ...` or `debate opposite: ...`. Jarvis argues that side with a visible badge for 10 minutes, then goes back to normal. Only when you call it | `debate.py*`, `app.py`, `index.html` | ~80 | No | Planned |
| 93 | **Decision Debt**: `sochenge baad mein: phone lena hai` saves it; `pending decisions` lists them; the briefing shows up to 2 older than 3 days; `decision ho gaya 2` closes one | `decisions.py*`, `brief.py`, `backup.py`, `app.py` | ~90 | No | Planned |
| 94 | **Unfinished business**: `adhoora: Faisal se baat` shows in the briefing now and then (at most once in 3 days) until `adhoora khatam 2` | `decisions.py`, `app.py` | ~50 | No | Planned |
| 95 | **Last talked**: only people you pick. `ammi track karo`, then `ammi se baat hui`. The briefing says `Ammi se 7 din se baat nahi hui` (days changeable). No call log, no WhatsApp reading | `touch.py*`, `brief.py`, `backup.py`, `app.py` | ~90 | No | Planned |
| 96 | **Mood check-in**, only when you say it: `mood 3` (1 to 5) or `aaj mood low`; `mood history`. After 4 low days one gentle line in the briefing, only if you switched `mood care on` | `mood.py*`, `brief.py`, `backup.py`, `app.py` | ~80 | No | Planned |
| 97 | **Time Capsule** (text): `6 mahine baad yeh sunana: ...`. On that day a card appears and Jarvis reads it after your tap | `capsule.py*`, `backup.py`, `app.py`, `index.html` | ~85 | No | Planned |
| 98 | **Conditional capsule**: show a capsule only when a phrase you chose is typed to Jarvis, or when 30 days pass without talking to a person from Part 95 | `capsule.py`, `touch.py`, `app.py` | ~70 | No | Planned |
| 99 | **Habit Contract**: `contract gym 7 din penalty 100`. Each day that closes without `aaj gym gaya` adds 100 to a penalty pot shown in `my habits`. The pot is only a number; no real money moves | `habits.py`, `app.py` | ~80 | No | Planned |
| 100 | **Timed modes**: `meeting mode 45 minute`, `namaz mode 20 minute`, `sleep mode`, `focus 45 minute`. No voice, short replies, reminders as text; ends by itself | `modes.py`, `index.html` | ~70 | No | Planned |
| 101 | **Body Double**: `body double 45 minute`. Every 15 minutes a text check-in `abhi bhi kaam par?` with Haan / Nahi; a count at the end. It does not watch the screen and does not block apps | `modes.py`, `index.html` | ~60 | No | Planned |
| 102 | **Cool-down** before a message: say `thanda karo` first, then the WhatsApp command. A 20 second countdown shows your text and a Continue button. Only when you ask for it | `actions.py`, `index.html` | ~60 | No | Planned |
| 103 | **Dream journal**: `sapna: ...` saves your words as they are; `sapne dikhao`; `sapno me Ammi kitni baar` counts a word. An AI explanation only if you ask `sapne ka matlab` (sends only that dream) | `dreams.py*`, `backup.py`, `app.py`, `index.html` | ~90 | No | Planned |
| 104 | **Signs log**: `sign: 11:11 dekha`; `signs dikhao` counts repeats. Only what you type; nothing is detected by itself | `signs.py*`, `backup.py`, `app.py` | ~40 | No | Planned |
| 105 | **One honest question**: `sach sawal on` lets Jarvis ask at most ONE hard question every 14 days. The AI gets only counts from your decisions, unfinished business, habits and mood, and the reply says what was sent. `sach sawal off` stops it | `redteam.py`, `brief.py`, `app.py` | ~60 | No | Planned |
| 106 | **Topic drift**: `drift on`, then `drift dikhao` compares the words you used most last month and this month in your chat history. Word counts, no AI. Says so if there are not 2 months of history yet | `drift.py*`, `app.py` | ~80 | No | Planned |
| 107 | **Context Ghost**: `Chrome kholo research ke liye` keeps the reason for 7 days; opening the same app through Jarvis again asks once `Pehle wali research continue karni hai?`. Jarvis does not watch other app use | `ghost.py*`, `actions.py`, `index.html` | ~70 | No | Planned |
| 108 | **Recovery card** `jab tu door tha`: 3 reminders, 1 phone issue, with Review and Dismiss | `index.html`, `app.py` | ~45 | No | Planned |
| 109 | **Life Timeline**: reminder done, routine run, note saved, expense noted, with filters | `events.py*`, `app.py`, `index.html` | ~145 | No | Planned |
| 110 | **Money picture**: `kamai 40000 mahina`, `bachat 5000`; `paisa picture` shows income, spending (Part 84) and what is left | `money.py*`, `backup.py`, `brief.py`, `app.py` | ~70 | No | Planned |
| 111 | **What-if**: `agar job chhod du`. Plain arithmetic on the numbers from Parts 84 and 110 (months you can manage). It says clearly that it is a simple calculation, not advice | `money.py`, `app.py`, `index.html` | ~60 | No | Planned |
| 112 | **Note after a call** (Java): after a call ends Jarvis asks `kuch yaad rakhna hai?`. Needs the phone-state permission | `CallNote.java*`, `MainActivity.java`, manifest, `index.html` | ~80 | Yes | Planned |
| 113 | **Reminders by place** (Java): `jab ghar pahunchu`. Needs background location; battery and privacy design first | `PlaceWatch.java*`, `MainActivity.java`, manifest, `index.html`, `app.py` | ~120 | Yes | Planned |
| 114 | **Place and Bluetooth triggers** (Java): a note shows when you reach a place or a chosen Bluetooth device connects. Jarvis never changes its tone or guesses a mood | `PlaceWatch.java`, `index.html`, `app.py` | ~90 | Yes | Planned |
| 115 | **Anti-Doomscroll** (Java): one calm line after N minutes in the same app (you set N). Needs Usage Access. Never blocks anything | `UsageWatch.java*`, `MainActivity.java`, manifest, `index.html` | ~110 | Yes | Planned |
| 116 | **App habit map** (Java): `YouTube ke baad usually Instagram`, a count kept on the phone and shown as a note | `UsageWatch.java`, `index.html` | ~40 | Yes | Planned |
| 117 | **What's new answers**: `last update`, `kya kya add hua`, `last 5 updates`. Jarvis answers from the zip names in `~/.jarvis_done` (name, time, files inside the zip) plus that Part's row in this README (files, lines, what it does). Fixes the chat saying `I cannot access GitHub`. It only knows what this phone received and pushed, not other commits on GitHub | `whatsnew.py`*, `app.py` | 81 | No | Built, not phone tested |
| 118 | **Assist mode: guest session core**. `guest session shuru` and `End & erase`. While on: nothing is saved (no memory, people, notes, habits, expenses, mood, chat history), the guest chat lives in RAM only, a badge shows `Guest: temporary / Memory saved: No`. Aadhaar-like 12 digit numbers, phone numbers and card numbers are masked BEFORE the text goes to the AI. The badge says the text still goes to the AI provider | `guest.py`*, `app.py`, `index.html` | ~150 | No | Planned |
| 119 | **Assist tools** (inside a guest session or for you): **Photo or screenshot helper**: send a form, bill, medicine strip or message as a photo or screenshot; Jarvis translates it, explains it in simple words and answers your follow-up questions about it (reuses `see.py`; photo not saved). Plus Translate, Explain simply, Find reliable info (uses the Part 90 source label), Make a plan, Big-text read-aloud for elders. No emergency guide (Hussain, 17 Nov). Medicine and forms: reads what is printed and says `doctor ya pharmacist se confirm karo`. Reply help already exists in Part 84 | `assist.py`*, `see.py`, `app.py`, `index.html` | ~150 | No | Planned |
| 120 | **Lens rail** on Home: chips Project, Phone, Life filter the Next best move card and the strip. World and Sports chips wait until a news source exists | `lens.py`, `index.html` | ~60 | No | Planned |
| 121 | **Glass skin**: the premium glass look (orb, glass cards, gradient buttons) for Home and Assist only, dark only, with a `Reduce effects` switch. CSS from Hussain, about 330 lines. Only after Table A passes | `index.html` | ~380 | No | Planned |
| 122 | **Bottom bar**: tabs appear as their Parts are built (Home, Talk, Assist, Timeline, Memory, Settings). Needs Parts 88, 109 and 118. Only after Table A passes | `index.html` | ~90 | No | Planned |

## 3. WHAT HUSSAIN DOES NOW

1. GitHub > Actions > **Build APK** > Run. If it goes red, send a screenshot of the error. That is fixed before anything else.
2. Install the APK on the phone.
3. Try the 24 rows of Table A (section 7). For each row write PASS or FAIL. For a FAIL send a screenshot.
4. Then say **"ok 88"** (or any Part number from section 2). Claude builds one Part at a time.

Why this order: Parts 18 to 87 and Part 117 are built and none is phone tested. A new feature on top of an untested base only makes bugs harder to find. Parts 112 to 116 (Java) wait longest, because Java is not even compiled yet. This README-only update needs no new APK.

## 4. TOTAL PLAN: FILES AND LINES (Parts 87 to 122)

| What | Parts | Count | Lines (estimate) |
|---|---|---|---|
| Python and page, no new APK | 87 to 111 and 117 to 122 | 31 Parts | 2525 |
| Java, new APK needed | 112 to 116 | 5 Parts | 440 |
| **Everything** | 87 to 122 | **36 Parts** | **2965** (expect about 2800 real lines, because the last two rounds ran about 25 percent over) |

- **New Python files (16):** `assist.py`, `capsule.py`, `debate.py`, `decisions.py`, `dreams.py`, `drift.py`, `events.py`, `ghost.py`, `guest.py`, `money.py`, `mood.py`, `redteam.py`, `search.py`, `signs.py`, `touch.py`, `whatsnew.py`.
- **New Java files (3):** `CallNote.java`, `PlaceWatch.java`, `UsageWatch.java`.
- **Older files that grow:** `MainActivity.java`, `actions.py`, `app.py`, `backup.py`, `brief.py`, `habits.py`, `index.html`, `memory.py`, `modes.py`, `people.py`, `progress.py`, `web.py` and the manifest.
- **Order of work (changed 17 Nov):** 87 with 117, then 88, 89, 90, then 118 and 119 (the guest guard needs the list of every store from Part 88), then 91 to 111, then 120, then 121 and 122 (look only, after Table A passes), Java 112 to 116 last. Older text below: the table order. Python Parts first, Java Parts last. Parts 85, 86, 87 and 117 are built. Part 98 needs Parts 95 and 97. Part 111 needs Parts 84 and 110. Part 114 needs Part 113. Part 116 needs Part 115.
- **Each Part stays under 350 lines** (rule 1). Every Part: no full test suite (Hussain's rule), only a syntax check and a small run; everything else is written as NOT RUN.

## 5. IDEAS WE WILL NOT BUILD (and why)

| Idea | Why not |
|---|---|
| Unlock the phone by voice, or any lock-screen bypass | REFUSED: a spoken secret that opens the phone is the pattern banking trojans use |
| Voice commands with the screen locked or off | REFUSED; Android also does not allow it. The only safe form is the optional test in Settings that wakes the screen |
| Always-on "Hey Jarvis" as the default phone assistant | NOT PLANNED: big and risky. The background listening test is the safe version |
| Saving Aadhaar, card or bank numbers | REFUSED: passwords, OTPs, PINs and card numbers are never saved |
| Group or family status ("who is at home") | REFUSED: needs other people's data and consent. (Part 95 is different: only what Hussain tells Jarvis about his own contact) |
| Recording the screen or "everything I say and do" as a memory | REFUSED: it records other people's chats, voices and OTPs |
| Detecting arguments, mood or anger from chats, typing, voice or heart rate | REFUSED: Jarvis notes a mood only when Hussain says it (Part 96) |
| A personality that appears by itself when you are alone or low | REFUSED: it needs mood detection. Part 92 gives the same thing only when YOU call it, with a visible badge |
| Sending messages to people automatically after the phone is unused for some days | REFUSED: Jarvis never sends on its own, and a wrong trigger would message people by mistake |
| Blocking apps or sites, or watching the screen all the time, for focus | NOT PLANNED: Part 101 is a check-in only |
| Spotting coincidences by reading notifications | NOT PLANNED: Part 104 is a log you type yourself |
| Moving real money as a penalty | REFUSED: the penalty pot (Part 99) is only a number |
| Routines that run with no tap | NOT PLANNED on purpose: the one-tap Run is the safety design |
| Splitting `index.html` into files | NOT NOW: a big rewrite of a page that is not phone tested is the biggest regression risk. The look and the bottom bar are Parts 121 and 122, later, after Table A passes |
| Emergency guide, and medical steps written by the AI | NOT PLANNED (Hussain, 17 Nov): a wrong or misused guide could cause harm. Part 119 only reads and explains what is printed on a form or medicine strip, and says `doctor ya pharmacist se confirm karo` |
| Saying `Private session` without the AI-provider note | REFUSED: in a guest session Jarvis saves nothing, but the text still goes to the AI provider, so the badge says so |
| Remembering a guest's voice, name or questions, or keeping guest items in Help history | REFUSED: End & erase wipes the whole guest chat. Only your own use keeps a label and time, never the text |
| Evidence drawer, trust meter, hologram HUD, weather and stock cards | NOT PLANNED: needs data Jarvis does not have, or is decoration |
| Weather on Home (Part 67), car mode | DROPPED by Hussain |

## 6. SAFETY RULES FOR THE NEW PARTS (every Part must keep these)

1. Only real data from Jarvis's own tables. No fake percentages, no invented numbers, no "confidence" score.
2. Nothing is saved that Hussain did not say or tap. Passwords, OTPs, PINs, CVVs and card numbers are refused in every new feature (same filter as `memory.SECRET`).
3. New personal data (mood, last talked, decisions, capsules, dreams, signs, contract pot, money) stays in the phone's own database, is part of Backup and Restore, is wiped by `delete everything`, and is never sent to the AI. The only exceptions are Parts 91, 103 (only if asked), 105 and 111, which send the few things they need and say so in the reply.
4. Jarvis only suggests. Sending, paying, deleting and running steps still need Hussain's tap.
5. Every new feature has an OFF word (`mood care off`, `sach sawal off`, `drift off`, `track band karo`, `contract band karo`) and a delete word.
6. Heavy emotional features (Parts 92, 94, 96, 103, 105) are opt-in, show a clear badge or label, and are never started by Jarvis on its own.
7. Guest session (Parts 118 and 119): started only by Hussain's tap or words; every save path is skipped while it is on (Part 88 lists them); Aadhaar-like, phone and card numbers are masked before the AI; End & erase also wipes the guest chat in the page.

## 7. PHONE TESTS (TABLE A)

Nothing below is phone tested yet. Build APK first for the Java rows. Write PASS, FAIL or not tested in the last column. Part 87 reads this column for the "Verified" count, so keep the table format. Every new Part adds rows 21 and up when it is built.

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

## 8. RULES FOR EVERY CLAUDE (always follow)
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
12. App lock stays OFF unless Hussain turns it on himself in Settings (16 Nov 2026: he did not want the fingerprint prompt on every open). Never switch it on by default.
13. **How to resume (any new Claude):** (1) Read sections 1 to 9. (2) Take the Part Hussain names; if he names none, ask him for the Build APK and Table A result first (section 3). (3) Say first "with tests" or "without tests" and why. (4) Build it, give the changed files with real line counts, keep ONE cumulative zip. (5) Update this README: the Part row in section 2 (real lines, status), the totals in section 4, the new Table A rows in section 7, the Part row in R7 (11.6) and the real-lines line in R6. (6) Never touch `run.sh` or `sync.sh` through a zip.
14. **Zip name and shape:** `Jarvis_partN.zip` where N is the Part number (underscore, NO letters). A README-only update reuses the last built Part number. Files at the top level with NO `Jarvis-main/` folder. `run.sh` and `sync.sh` pick up only `Jarvis_part*.zip`. A wrongly named zip once left `lang.py` out and the server crashed in a loop.
15. **Keep this README simple:** a normal person must understand sections 1 to 9. One table (section 2) lists every Part with plain numbers only: never letters like 49a, never separate lists with other codes. New detail goes to the R sections, not to the top. Never paste chat text or other AI's answers into this file.
16. **Language:** Hussain may speak or dictate in ANY language or script (Hindi, Marathi, Urdu, English...). Always answer him in Roman script (English letters), in simple Hinglish or simple English. Never Devanagari or any other script in replies.
17. **Plan before, plan after:** BEFORE building a Part say its number, files and lines in a small table (and WITH or WITHOUT tests). AFTER building say the real lines, then the NEXT Part in the same way (number, files, lines). Part numbers are plain numbers from the table in section 2 only.


## 9. KNOWN LIMITS AND FIXES (honest list)
- Speech to text: the phone listens in ONE language at a time. For Tamil, Gujarati and so on, choose that language in "Speak:" (Settings, voice panel). Switching by itself between languages needs the Sarvam key (not built yet).
- Urdu: command words (open, torch, on, off) work; unknown Urdu app names are NOT matched, only known apps such as YouTube.
- Odia: commands work; answers come in English or Hindi text (no Odia voice).
- Sarvam voice speaks only Hindi and English. Other languages use the free Edge voices.
- Send, pay, delete and similar steps always need Hussain's own tap. Passwords, OTPs and PINs are never typed.
- Android does not let any app switch Wi-Fi, Bluetooth or location on or off by itself. Jarvis opens the page.
- Interrupt (61): only with earphones; a Bluetooth speaker counts as earphones and may echo (the echo filter helps, not perfect). The phone speech service may beep and on some phones lowers Jarvis' voice while it listens. Needs a phone test.
- Alarm (66): Android lets no app delete or switch off alarms or stop a timer; Jarvis opens the alarm list instead. Alarm, timer and search are said on their own, never inside a multi-step task.
- Screen off: Android does not let an app open itself from the background. Making Jarvis the default phone assistant is the only full fix; it is big and risky, NOT planned.
- Contacts saved in Tamil or other non-Latin, non-Hindi script are not found by `call` (Part 64).
- Lists (Part 83): with only spaces, every word is one item; use commas for two-word items. Habits (Part 83): `aaj gym gaya` works only after `habit banao gym`, on purpose, so normal sentences are not taken. The streak counts the phone's calendar days. The day report is a button, it never runs by itself.
- Fixes from phone test round 1 (17 Nov 2026): if `Open YouTube` says `Android did not let me open it`, the chat now shows Android's real reason in brackets; send that reason. If `Mic: speech error 11` keeps coming, update Google Speech Services or restart. If `Online voice failed ... NoAudioReceived`, run `pip install -U edge-tts` in Termux, restart `bash run.sh`, and make sure the phone has a Google speech voice installed. An app that is not installed is not found (the list is the phone's real list).
- Termux closing by itself: Android kills it to save battery. Settings > Apps > Termux > Battery > No restriction; keep the Termux notification visible; install Termux:Boot for restarts.


---

# REFERENCE (old detail, open only when needed)

## R1. How it works
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

## R2. Setup (phone, Termux)
Once: `pkg install git python unzip openssl-tool && termux-setup-storage` (openssl-tool is for backups, Part 47), `pip install edge-tts`, GitHub login (`git config --global credential.helper store`).
The GitHub token must also allow **workflow** files (needed from Part 16, or the push is rejected).
Daily: `cd ~/Jarvis && bash run.sh`. Open **http://127.0.0.1:8787** (or the Jarvis app). First time: pairing code, then Settings for the key.
Auto-start (Part 11): Termux starts Jarvis when opened. Turn off with `JARVIS_NO_AUTOSTART=1` in `.env`.
**Pairing screen:** open Termux, find the last line `PAIRING CODE: 123456` and type those 6 numbers (valid 10 minutes). Old or missing? Tap "Show code in Termux". Pairing stays after updates because Part 36 uses one fixed signing key; if an old APK was signed with a random key, uninstall it ONCE, install the new APK and pair one last time.


## R3. Cheat sheet (type or say)
**Languages (Part 62, 63):** say or type the app name in any script: `ઓપન યુટ્યુબ`, `ஓபன் யூடியூப்`, `ఓపెన్ యూట్యూబ్`, `यूट्यूब उघडा`, `open Zomato`. Steps in a row work too (`ઓપન યુટ્યુબ અને ઓપન ક્રોમ`). Choose the same language in "Speak:" for the mic. Ask `battery kitni hai` or `charging status` for a local answer.

**Notes (Part 72):** `note karo ki ...`, `meri notes`, `notes me bijli dhundo`, `delete note 3`.

**Lists, habits, day report (Part 83):** `list me doodh bread add karo`, `list dikhao`, `list se doodh hatao`, `list saaf karo`, `packing list me charger add karo`. `habit banao gym`, `aaj gym gaya`, `my habits`, `habit report`, `gym streak`, `habit hatao gym`. `day report 9 baje`, `day report off`. `explain this screen`.

**Spending (Part 84):** `200 coffee`, `kharcha 50 auto`, `50 rupaye auto mein diye`, `kharcha`, `kharcha hatao`. Clipboard tile: Save as note, Add to list. Notifications tile: Reply ideas.

**Two voices (Part 71):** Settings, Voice personality: Tony (conversation) and JARVIS (information, tasks, reminders, briefings, alerts). With Sarvam each has its own speaker. Listen to both before you decide.

**Music (Part 68):** `gaana pause karo`, `next song`, `agla gaana`, `pichla gaana`, `music band karo`, `resume`. Works on whatever player is active.

**WhatsApp by name (Part 69):** `Ammi ko WhatsApp pe hello bhejo`, `Ammi ko whatsapp karo`, `send hello to Ammi on WhatsApp`. Opens the chat with the text filled in; you press send. Needs Phone control ON and Contacts permission.

**Alarm and timer (Part 66):** say `subah 6 baje alarm laga`, `alarm 18:30`, `raat 1 baje alarm`, `saade 6 baje alarm`, `5 minute ka timer`, `aadha ghanta ka timer`, `alarm band karo` (opens the alarm list). Needs Phone control ON. A bare `6 baje` takes the next 6 AM or 6 PM on the phone's clock.

**Search inside an app (Part 60):** `YouTube par Arijit ke gaane search karo`, `play Kesariya on YouTube`, `Maps par petrol pump search karo`, `Chrome par weather in Mumbai search karo`; also Amazon, Flipkart, Play Store, Spotify. Needs Phone control ON.

**Interrupt (Part 61):** connect earphones, tap `Interrupt: off` next to Conversation so it says on. While Jarvis speaks, just start talking: he stops and answers. Say `ruko` to only stop him.

**Call by name (Part 64):** say `Ammi ko call karo`, `call Ammi`, `अम्मी को कॉल करो` or `Ammi ko phone lagao`. Needs Phone control ON. Android asks once for Contacts and once for Phone calls. A sure match (same name, or the name starts with it) is called at once. Two or more matches, or only a close spelling ("Ammi" and "Amma"), show buttons with the last 4 digits and only YOUR tap places the call. `call 9876543210` only opens the dialer; the green button is your own tap. A call cannot be a step in a multi-step task, say it on its own. Limits: names are matched in Latin or Hindi script (a contact saved in Tamil script is not found); the call permission is asked on the first call, then say it again. Nothing about the contacts is saved or sent.

**Phone health (Part 65):** ask `phone me kya problem hai`, `phone slow hai`, `phone garam kyu hai`, `bluetooth connected hai kya`, `wifi connected hai`, `internet chal raha hai kya`, `storage kitna bacha hai` or `battery health`. Works only in the Jarvis app (Chrome shows memory and storage only). Commands like `bluetooth on karo` are NOT questions: they open the settings page (Part 37). Limits: Bluetooth shows only AUDIO devices (earbuds, speaker, car) because other devices need a dangerous permission that was not added; the Wi-Fi network NAME is not shown for the same reason; Android cannot say how healthy the battery is in percent, only good, hot, dead or failing. Needs only the normal network-state permission. Nothing is saved or sent.
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
| Home > Clipboard | Use the text you just copied (never passwords, OTPs, PINs or card numbers) |
| handoff / summary for Claude | Short summary of the recent chat to copy or share (no passwords, OTPs or private answers) |
| phone kho gaya / lost phone | Lost-phone steps with buttons for Google Find Hub and Sanchar Saathi |
| (any app) Share > Jarvis | Shared text or link opens in Jarvis chat with buttons; nothing is sent until you tap one |

## R4. Security and privacy
- Server listens on 127.0.0.1 only. Only the page from that address may call it (Host and Origin are checked). Pairing code: 10 minutes, one use, locks after 5 wrong tries.
- Token is stored as a hash on the server. Keys are stored in `backend/keys.json` (owner-only file, never in Git, never sent back to the browser).
- Passwords, OTPs and PINs are never saved. Calls, contacts and screen text are never saved. Chat history is saved on the phone only; "clear history" deletes it.
- These go to the internet only when you use them: your question to the AI provider; voice text to Microsoft (online voice); photo to the vision AI; location to OpenStreetMap; screen text to the AI for that one answer.
- Part 27: the page can use only the microphone, only from the Jarvis address, only after Android allowed it. Camera and other requests are denied. Plain http works only for 127.0.0.1. Microphone, location and notification permissions are asked when first used, not at app start.
- Part 28: Stop is stored in Java. While stopped, the app will not listen, read the screen or open the photo picker, even if the page asks. Only a real finger tap on "Turn mic on" can switch Jarvis on again. A photo or camera app that is already open cannot be closed by Jarvis.
- The Android app only opens the Jarvis address, has no file access, and is excluded from cloud backup. Accessibility is used only to read text when you ask.
- Zips: only put zips you trust in Downloads. A zip can replace any file in the repo, including scripts.

## R5. OLD STATUS TABLE (16 Nov 2026): Parts 1 to 39, 41 to 47, 50, 51, 52, 54, 55 and 56 are built
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
| 48 | **App lock fix:** the fingerprint prompt came back on every open because App lock was ON in Settings and asked again after 1 minute. Now it is switched OFF once on update, and if you turn it on again it waits 5 minutes. **Share to Jarvis:** in any app tap Share > Jarvis (text or a link); Jarvis shows it in chat with buttons Summarize, Explain simply, Hindi me batao, Reply draft, Remember. Nothing goes to the AI until you tap a button. **Handoff:** say `handoff` and Jarvis writes a short summary of the last chat lines (passwords, OTPs and private phone answers left out) with Copy and Share buttons, to paste in Claude or ChatGPT. **Lost phone:** say `phone kho gaya`: 5 steps (Google Find Hub, block SIM, Google password and sign-out, bank and UPI, FIR then Sanchar Saathi CEIR block) with buttons that open Find Hub and Sanchar Saathi. Jarvis cannot find, lock or erase the phone itself. **New Home dashboard** (from your two reference pictures): neon blue look, moving sound bars, a ring orb you tap to talk, greeting bubble, AI tools (Summarize, Translate, Write, Explain type the start of a sentence for you; Plan my day = briefing; Handoff), today's schedule, battery ring, reminders and money counts, smart shortcuts, phone and server numbers. The app now opens on Home. Weather, devices and trending news are NOT shown because Jarvis has no real data for them yet | BUILT | NOT YET (Python run here; page rendered and JS syntax checked; Java not compiled) |
| 40 | **Offline wake word.** Settings > Background listening test now has a card "Offline wake word": tap Download model (about 40 MB, Vosk small English model from alphacephei.com over https, only after your tap), then "Use offline engine". The background listener then runs the Vosk engine ON THE PHONE (no Google speech service) and only looks for the word Jarvis (jarvis, jar vis, jarvish, jervis); nothing is saved, shown or sent. On a hit: Jarvis on screen = the mic opens (this ends the background listener, one listener at a time); app closed or screen off = a notification "Jarvis heard you, Tap to talk" (Android does not let an app open itself from the background). Counts still show in the test card. Same safety: finger tap to start, notification with Stop, 8 h limit, Stop everything ends it, never while locked. Delete model frees the space. New file `WakeEngine.java`; `build.gradle` gets two libraries (vosk-android 0.3.47 and jna 5.13.0) and only arm64 and armv7 code; app version 1.2. No checksum is checked for the model download (the Vosk project publishes none we could verify here). Hindi words are not understood; only the English-sounding word Jarvis | BUILT | NOT YET (Java not compiled; library and model download not run; first GitHub build is the compile test and may need one fix) |
| 49a | **Clipboard button** (Home > Smart shortcuts > Clipboard): reads what you copied only when you tap, shows it in chat with the same buttons as Share (Summarize, Explain simply, Hindi me batao, Reply draft, Remember). A password, OTP, PIN or card-number-looking text is refused and never shown. Nothing is read in the background | BUILT | NOT YET (page JS syntax checked; Java not compiled) |
| 50 | System card in Settings: phone RAM, storage, battery, heat, Jarvis server memory and CPU, uptime, internet. Server tests pass; page JS syntax checked only | BUILT | NOT YET |
Total: about 40 files and about 2,650 lines of code. Known limits (not bugs): Hey Jarvis works only while the app is open; mic in Chrome and in the app use different engines; the real actor's voice cannot be copied, only approached with the free voices; Android Files app may show empty ghost entries for zips that Termux already moved to `~/.jarvis_done`.

## R6. BUILD LOG (what each Part did, with real lines)

**Part 82: files and real lines.** `backup.py` 5, `remind.py` 31, `brief.py` 32, `phone.py` 68, `tasks.py` 15, `app.py` 6, `index.html` 31, `PaymentGuard.java` 48, `MainActivity.java` 15, `.gitignore` 1 (about 250 lines of code), README 60. The estimate was about 295. Tests: the full test suite was NOT RUN (Hussain's rule); only a Python syntax check, a JavaScript syntax check, a parse-only check of the Java and a small run of the new Python code were done.

**Part 83: files and real lines.** `lists.py` 93 (new), `habits.py` 122 (new), `tasks.py` 47, `brief.py` 19, `app.py` 10, `backup.py` 3, `index.html` 3 (about 297 lines of code; `screen.py` was not touched, the screen reader already existed). The estimate for these five ideas was about 245. Tests: the full test suite was NOT RUN (Hussain's rule). Done: Python compile of every backend file, a JavaScript syntax check of the page, a small run of each new function (lists, habits, day report time, battery guardian, backup and restore of the new tables, no clash with the older commands and no normal sentence taken by mistake). Not done: any phone test.

**Part 84: files and real lines.** `spend.py` 109 (new), `replyideas.py` 26 (new), `brief.py` 10, `app.py` 7, `index.html` 8, `backup.py` 2 (about 162 lines of code; the estimate for ideas 3, 7 and 8 was about 130; the expense logger got its own file instead of growing `ledger.py`). Tests: the full test suite was NOT RUN (Hussain's rule). Done: Python compile of every backend file, a JavaScript syntax check of the page, a small run of the expense logger (logging, totals, undo, 12 ordinary sentences NOT taken), of the reply-ideas text (a secret in a notification is refused), and of backup and restore of the spending table. Not done: any phone test, and the real AI answer for reply ideas.

**Part 85 and 86:** files and real lines. `lens.py` 109 (new), `app.py` 2, `index.html` 12 (about 123 lines of code; the estimate was 190). Rules in `lens.py`: late or not-yet-told reminders, low battery, late money, a routine in the next hour and today's birthday come first; then habits, then later today and tomorrow. Tests: the full test suite was NOT RUN (Hussain's rule). Done: Python compile, a JavaScript syntax check of the page, and a small run of `lens.py` with sample reminders, a routine, late money, a habit and battery 17 and 12 percent (right card each time, a bad time gives no card). NOT RUN: the page on a phone.

### R6a. Parts 60 to 72 (each Part: files, lines, benefit, status)

| Part | What it does | Files | Est. lines | Real lines | Benefit for Hussain | Status |
|---|---|---|---|---|---|---|
| 62 | Open ANY app on the phone by saying its name, in any script. The name is matched with the phone's real app list (exact, spelling, same consonants). Chat shows "Looking for the app...", then a tick or a cross. | `actions.py`, `lang.py`*, `Apps.java`, `index.html` | ~120 | about 60 | Every installed app opens, and he sees what happened | BUILT, not phone tested, Java not compiled |
| 63 | Any Indian language: Hindi, Marathi, Gujarati, Tamil, Telugu, Kannada, Malayalam, Bengali, Punjabi, Odia, Urdu (commands) and English. Open app, torch, volume, settings pages and multi-step all work. Open-app answers come in the language spoken. Chat answers in that language. Voice for Tamil, Telugu, Gujarati, Kannada, Malayalam, Bengali, Marathi, Urdu. Speak language list in the app. | `lang.py`*, `actions.py`, `tasks.py`, `app.py`, `tts.py`, `index.html` | ~180 | about 85 | Speak in his own language and get work done | BUILT, not phone tested |
| 64 | "Ammi ko call karo" (any language) calls the contact by name. Two matches: asks which. Screen shows "Calling Ammi...". | `CallByName.java`*, `MainActivity.java`, manifest, `actions.py`, `tasks.py`, `index.html` | ~110 | about 199 (`CallByName.java` 105 new, `actions.py` 61, `index.html` 22, `MainActivity` 6, `tasks.py` 3, manifest 2) | No speed dial needed | BUILT, not phone tested, Java not compiled |
| 65 | Phone health in Roman Hindi or English: "phone me kya problem hai", "bluetooth connected hai kya", "internet chal raha hai kya", "storage kitna bacha", "battery health". Says what is wrong and how to fix it (low battery, hot or failing battery, airplane mode, no internet, Wi-Fi without internet, full storage or memory, restart needed). | `PhoneInfo.java`, `phone.py`, `index.html`, manifest | ~100 | about 147 (`phone.py` 96, `PhoneInfo.java` 46, `index.html` 4, manifest 1) | One question tells him what is wrong with the phone | BUILT, not phone tested, Java not compiled |
| 66 | Alarm and timer by voice in Roman Hindi or English: `subah 6 baje alarm laga`, `alarm 18:30`, `saade 6 baje alarm`, `raat 1 baje alarm`, `5 minute ka timer`, `aadha ghanta ka timer`, `alarm band karo` (opens the alarm list: Android lets no app delete alarms). A bare "6 baje" with no AM or PM becomes whichever comes next on the phone's clock. Uses Android's own Clock app. | `QuickSet.java`*, `MainActivity.java`, manifest (SET_ALARM, a normal permission), `actions.py`, `index.html`, `tasks.py` | ~60 | about 150 (`actions.py` about 105, `QuickSet.java` about 40, `index.html` 4, `MainActivity` 6, manifest 1) | Alarm and timer without touching the phone | BUILT, Python tested, Java not compiled, not phone tested |
| 60 | Search inside an app, no typing: `YouTube par Arijit ke gaane search karo`, `play Kesariya on YouTube`, `Maps par petrol pump search karo`, `Chrome par weather in Mumbai search karo`; also Google, Play Store, Amazon, Flipkart, Spotify. Hindi script works too. Java builds the web address from its own fixed list (the page never sends a link); if the app is not installed the same search opens in the browser. `YouTube kholo` alone still just opens the app. | `actions.py`, `QuickSet.java`*, `MainActivity.java`, `index.html`, `tasks.py` | ~110 | about 114 (`actions.py` about 58, `QuickSet.java` about 46, `tasks.py` 3, `index.html` 1, tests 12) | "YouTube par Shah Rukh ke gaane chalao" works | BUILT, Python tested, Java not compiled, not phone tested |
| 61 | Smart interrupt: while Jarvis speaks, the phone mic listens; the moment you start talking Jarvis stops and answers what you said. Button `Interrupt: on/off` next to Conversation (OFF by default). Works only with earphones connected (wired, USB or Bluetooth; checked each time Jarvis speaks), because the mic would hear Jarvis' own voice from the speaker. Words that match Jarvis' own sentence are ignored (echo filter). `ruko` / `stop` only stops him. Stop everything and Privacy mode switch it off. | `index.html`, `Ears.java`, `MainActivity.java` | ~160 | about 68 (`index.html` 33, `Ears.java` 29, `MainActivity` 6) | He can speak in the middle of an answer | BUILT, not phone tested, Java not compiled. Risk: some phones lower or pause Jarvis' voice when the speech service starts |
| 67 | Weather on Home from a free weather service | `app.py`, `index.html` | ~80 | - | - | DROPPED by Hussain (17 Nov 2026): not wanted |
| 68 | Music control by voice: `gaana pause karo`, `next song`, `agla gaana`, `pichla gaana`, `music band karo`, `gaana badlo`, a lone `pause` or `resume`. Sends the same media keys as earphone buttons to whatever player is active (Spotify, YouTube Music, YouTube...). Says honestly if nothing was playing. Volume words go to Part 37; `play Kesariya on YouTube` stays a search (Part 60). | `actions.py`, `QuickSet.java`, `index.html`, `tasks.py` | ~50 | about 62 (`actions.py` 40, `QuickSet.java` 19, `index.html` 3) | Pause or skip a song without touching the phone | BUILT, Python tested, Java not compiled, not phone tested |
| 69 | WhatsApp message by contact name: `Ammi ko WhatsApp pe hello bhejo`, `Ammi ko whatsapp karo`, `send hello to Ammi on WhatsApp`, `Ammi ko whatsapp par bol do ki main late hu`, Hindi script works. Java finds the number in the phone's contacts (same finder as Part 64: sure match opens at once, several or close spelling show buttons). It only OPENS the chat with the text filled in; WhatsApp's send button is YOUR tap, Jarvis never sends. Needs Phone control ON and the Contacts permission. Uses `wa.me` (WhatsApp, then WhatsApp Business, then browser). | `actions.py`, `CallByName.java`, `index.html` | ~90 | about 95 (`actions.py` 56, `CallByName.java` 14, `index.html` 3, tests 6) | Message a person by name, hands free until send | BUILT, Python tested, Java not compiled, not phone tested |
| 71 | Dual voice FIX (from the 17 Nov audit): Conversation now speaks as TONY; information, tasks, reminders, briefings, alerts and any unclear intent speak as JARVIS. Tony is shown again in Settings. Both are there from the first install, auto routing ON, saved in `voice.json` across restarts. On Sarvam each personality has its OWN speaker (Tony: aditya, JARVIS: rahul, changeable), so they really sound different. The badge and Settings say honestly when Edge Hindi uses ONE male voice (Madhur) for both, so only depth and speed differ. A speaker chosen before this Part is kept for JARVIS. | `voiceengine.py`, `app.py` (`/tts`), `index.html` | ~60 | about 55 | Two personalities that match what you asked for | BUILT, Python tested (routing, persistence), not phone tested, nobody has LISTENED to the voices yet |
| 72 | Voice notes and recall: `note karo ki kal bijli ka bill bharna hai`, `note: ...`, `take a note ...`, `नोट करो कि ...`; `meri notes`, `notes me bijli dhundo`, `bijli wala note`, `delete note 3`. Saved only on your own words, kept in a new small `notes` table in the SAME database (no second database), included in backup and restore and wiped by `delete everything`. Never sent to the AI. Passwords, OTPs, PINs, CVVs and card numbers are refused. Max 300 notes of 500 characters. The note text also sits in chat history like any message; `clear history` removes that copy. | `notes.py`*, `app.py`, `backup.py`, `test_app.py` | ~60 | about 75 (`notes.py` 70, `backup.py` 4, `app.py` 3) | Say a thought, find it later | BUILT, Python tested, not phone tested |

`*` = new file. Estimates are rough; real numbers are filled in after each Part.

**Total left: 0 required Parts.** Part 67 (weather) is dropped. The only open work is Build APK, the phone test (section 11.8) and the optional ideas in the list below.

### R6b. Parts 73 to 84: what was built and what was left out on purpose
| Item | Decision |
|---|---|
| Dual voice, Conversation = Tony | BUILT (Part 71) |
| Voice notes and recall | BUILT (Part 72) |
| Fuzzy/misheard command words (alarm, timer, music) | BUILT (Part 73), Python tests pass, phone not tested |
| Pause ScreenService while a payment app is open | BUILT (Part 73): auto OFF only (disableSelf), Android never lets an app turn accessibility back ON by itself, so a notification takes you straight to the Settings toggle. Default package list in `PaymentGuard.java`, editable later from Settings |
| Screen wakes (like the power button) when "Jarvis" is heard with the screen off | BUILT (Part 73): same as pressing power, the lock screen still shows and still needs your own fingerprint/PIN/swipe |
| Phone unlock by voice / bypassing the lock screen | REFUSED, will not be built in any form (always-listening + spoken secret = the exact pattern banking trojans use; a stolen or overheard phrase would open the phone to anyone) |
| Settings page redesign | BUILT (Part 74): all 10 old flat sections grouped into 5 collapsible cards (Voice & Personality, Privacy & Security, Your Data, Notifications, Advanced). 🔊 voice panel is now a bottom sheet with its own ✕ close button instead of a tall inline row. No element id changed, so no backend/JS wiring broke; JS syntax check pass |
| Daily Life Manager: Home card and briefing show today's reminders, ledger, birthdays (next 7 days) and latest notes in one place | BUILT (Part 75): `/today` now also returns `birthdays` and `notes`; one shared helper `remind.birthdays()`; briefing lists birthdays (3 days) and the 2 latest notes (only when you ask, never in the automatic one). Python only, no APK needed, not phone tested |
| Routine at a fixed time | BUILT (Part 76): `routine subah roz 7 baje` (also `routine subah 7:30`, `routine gym shaam 6 baje`, `routine subah time hatao`). Time is the phone's clock, 24-hour; the reply repeats it so a wrong AM/PM can be fixed. No second scheduler: the page's existing 10-second `/due` check also asks `tasks.due_routines`. When the time comes the chat shows a message with a **Run** button (one tap, Jarvis never starts the phone steps by itself); once a day; silent if the page was closed for more than 3 hours. `my routines` shows the time; Home card shows timed routines (tap to run). Python + page only, no APK needed, not phone tested |
| Smart Follow-up | BUILT (Part 77): 3 to 48 hours after a ONE-TIME reminder was told, the chat asks once 'ho gaya?' with buttons Haan / Nahi abhi. Spam rules: one question per day, one per reminder, never for repeating reminders or birthdays, silent from 22:00 to 07:00. Nahi = the same reminder once more after 2 hours (or 09:00 next morning), no further follow-up on it. New column `ask` on `reminders` (nothing deleted). Python + page only, no APK needed, not phone tested |
| Privacy Activity Timeline | BUILT (Part 78): Settings > Privacy now shows a timeline grouped by day (Today / Yesterday / date), a 'Today: Mic 5x, Apps 3x' summary, and 40 latest lines. Java keeps the last 200 uses (was 30). New events logged, name and time only: Stop everything, Phone control ON/OFF, Paused for a payment app (app name NOT saved). Needs a new APK (`Privacy.java`, `ScreenService.java`); Java not compiled, not phone tested |
| Missed-reminders summary (Claude's idea) | BUILT (Part 78): if 3 or more reminders are waiting when the page opens (you were away), they come as ONE chat message and ONE short voice line, not a pile of voices. 1 or 2 reminders speak one by one as before |
| Deep Phone Performance Doctor | BUILT (Part 79): say `phone doctor`, `deep phone check`, `phone performance` or `full phone check`. Normal phone check plus a Deep check block: battery voltage, charge cycles (only Android 14+ if the phone reports it), charge now in mAh, RAM in GB, days since restart, brightness, screen timeout, with advice (long timeout, high brightness, old battery). Anything Android does not give is said as UNAVAILABLE, nothing is made up: CPU load, per-app battery/RAM/storage, heavy-app names (Jarvis does not ask for Usage Access). Needs a new APK (`PhoneInfo.java`); Java not compiled, not phone tested |
| Phone problems in the briefing | BUILT (Part 80): `briefing` (and the automatic morning one) adds a 'Phone:' block with up to 2 real problems (low battery, full storage, heat...) from the same rules as Phone Doctor; nothing is added when the phone is fine. Python + page, no APK |
| Weekly summary | BUILT (Part 80): say `weekly summary` or `is hafte ka summary`: last 7 days in numbers (reminders told, phone tasks/routines completed and failed, notes saved, open ledger entries and late ones, birthdays in the next 7 days). Read from existing tables, nothing new saved |
| Routine on weekdays or weekends | BUILT (Part 80): `routine subah roz 7 baje sirf weekdays` (Mon to Fri) or `... weekend` (Sat, Sun). Without the word it is every day. New column `days` on `routines`. `my routines` shows it |
| Duplicate folder cleanup | BUILT (Part 80): `scripts/sync.sh` now deletes the old stale copy `Jarvis-main/Jarvis-main/` (only if it holds its own `backend` and `README.md`) before each push, so GitHub loses it too and no old zip can bring it back. One-time command for right now: see the chat |
| Backup keeps routine time and days | BUILT (Part 82): `backup.py` now saves and restores the routine time (HH:MM) and days (every day, weekdays, weekend). Old backups still restore (they get no time). A bad time in a file becomes 'no time', never an error. Python only, no APK |
| Reminder snooze | BUILT (Part 82): every reminder in chat has a `⏰ 10 min` button; or say `snooze`, `snooze 20 min`, `10 min baad phir yaad dilao`, `थोड़ी देर बाद फिर याद दिलाओ` (the reminder told in the last 6 hours). The same text comes again, once, and gets no 'ho gaya?' question. New route `/snooze`. Python + page, no APK |
| Day summary at night | BUILT (Part 82): say `aaj ka summary`, `day summary`, `evening summary` or `आज का सारांश`: reminders told, phone tasks and routines done, notes saved, open ledger, tomorrow's reminders and birthdays. Numbers only from existing tables, nothing new saved. Python only, no APK |
| Hindi-script words | BUILT (Part 82): `रूटीन बनाओ`, `रूटीन सुबह रोज़ 7 बजे सिर्फ़ वीकडेज़`, `रूटीन सुबह समय हटाओ`, `रूटीन हटाओ ...`, `... रूटीन चलाओ`, the day words (`सुबह शाम रात दोपहर`) and weekday words. Letters like ज़ and फ़ work typed either way (NFC). Python only, no APK |
| Phone Doctor storage trend | BUILT (Part 82): once a day (when you say `briefing` or a phone check in the app, or the morning briefing runs) Jarvis keeps TWO numbers, free and total storage, in `backend/phone_trend.json` (40 days, not in git). Say `storage trend` or `phone trend`: how much less or more free storage than up to 7 days ago, and if it keeps falling, in about how many days it is full. `phone doctor` shows the change and warns when it would be full in under 30 days. Needs 2 days of numbers. Chrome page numbers are never used (they are Termux's disk). Python only, no APK |
| Payment apps list in Settings | BUILT (Part 82): Settings > Privacy & Security > Payment apps. The built-in apps cannot be removed. You add your own bank or UPI app from the phone's app list (up to 20) and can remove only your own. Add and remove need a real finger tap (same 3 second rule). Only package names are kept. Timeline shows 'Payment app list changed'. Needs a new APK (`PaymentGuard.java`, `MainActivity.java`); Java not compiled here (parse check only), not phone tested |
| Shopping and packing lists by voice | BUILT (Part 83): `list me doodh bread add karo` (spaces or commas between items; use commas for two-word items like `brown bread, doodh`), `list dikhao`, `list se doodh hatao` (or the number), `list saaf karo`. A word before list makes another list: `packing list me charger add karo`. Max 100 items, 40 characters each. Passwords, OTPs, PINs and card numbers are refused. In Backup and Restore. Home tile Shopping list. Python + page, no APK |
| Habit and streak tracker | BUILT (Part 83): first `habit banao gym` (max 10), then `aaj gym gaya`, `medicine le li` or `gym done` marks today once. `my habits` shows streaks, `habit report` the last 7 days, `gym streak` one habit, `habit hatao gym` removes it. Only habits you made are marked, so normal chat is never taken. The briefing lists the habits not done yet and the day summary shows done today. In Backup and Restore. Home tile Habits. Python + page, no APK |
| Explain this screen in one tap | BUILT (Part 83): Home tile Explain screen, or say `explain this screen`, `screen samjhao`, `is screen pe kya hai`, `स्क्रीन समझाओ`. The old flow stays: switch to the app, Jarvis reads it after a few seconds, secrets are hidden first, nothing is saved. Page only, no APK |
| Battery guardian | BUILT (Part 83): in the briefing, battery 16 to 19 percent and not charging gives one calm suggestion (charger, or battery saver and the words `battery settings kholo`). At 15 or less the older Phone Doctor line shows instead. It only suggests, nothing is switched. Python only, no APK |
| Day report at a fixed time | BUILT (Part 83): `day report 9 baje` (a bare 9 means evening, 21:00; say `subah` or `am` for morning), `day report` shows the time, `day report off` stops it. Once a day at that time (up to 3 hours late) the page shows a Show day report button; the summary appears only after your tap and never by itself. Python + page, no APK |
| Quick expense logger | BUILT (Part 84): `200 coffee`, `kharcha 50 auto`, `50 rupaye auto mein diye`, `spent 300 on petrol`. Category from a short word list (food, travel, bills, health, shopping, other). `kharcha` shows today, 7 days, this month and the 7-day split; `kharcha hatao` removes the last entry (or `#number`). The bare form `200 coffee` needs an amount of 10 or more and is not taken for time or counting words (`10 baje`, `5 minute`). Briefing, day summary and weekly summary show the total. Not the owe/get ledger. In Backup and Restore. Home tile Spending. Python + page, no APK |
| Clipboard: Save as note, Add to list | BUILT (Part 84): after Home > Clipboard (or any text shared to Jarvis) two more buttons: Save as note (runs `note karo`) and Add to list (one item, up to 40 characters, runs `list me ... add karo`). Secrets are refused as before. Page only, no APK |
| Reply ideas for a notification | BUILT (Part 84): Home > Notifications > Reply ideas, pick one of the last 5. The AI writes 3 short options, you tap Copy and send it yourself; Jarvis sends nothing. The notification text goes only in its own field, secrets are cleaned first, it is treated as data, and the chat history keeps only a placeholder. Needs the AI to be reachable. Python + page, no APK |
| Smart App Search, Voice interruption | Already built (Parts 60, 61): only phone testing is left |
| Scheduled routines at a time | BUILT (Part 76), see above: one-tap Run button, no auto-run |
| Smart follow-ups, Privacy activity timeline | BUILT (Parts 77 and 78), see the rows above |
| PC companion | NOT built: a security design must be agreed first, phone-first stays |
| Weather on Home | DROPPED by Hussain |

## R7. MASTER PLAN (old section 11; the sub-headings keep their 11.x numbers): real phone control (Parts 27, 28 and 29 are built, not phone tested. The rest is plan only)
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
| 40 DONE | Offline wake-word engine (Hussain said OK on 16 Nov 2026, before the Part 39 phone test) | WakeEngine.java*, ListenService, MainActivity, app/build.gradle, index.html | ~200 (real: about 230) | Without | Reliable hands-free. Bigger app (about 15 MB more) and more battery |
| 41 DONE | Task engine backend: tasks table, 10 states, steps, restart rule | tasks.py*, app.py | ~180 | With | Multi-step jobs are tracked honestly |
| 42 DONE | Task runner in the page: shows steps, runs them through the bridge, verifies each, Cancel button, stops on failure | index.html, MainActivity, ScreenService, Privacy | ~120 | Without | "Chrome kholo aur ..." sequences, cancel any time |
| 43 DONE | Phone checklist table, regression list of old features. No test_app.py (Hussain's no-tests rule, 16 Nov 2026) | README | ~40 | Without | We know what to check on the phone before more features |
| 44 DONE | (old Batch B) Repeat reminders, birthdays, phone calendar | remind.py, people.py, calls.py, app.py, CalendarInfo.java*, MainActivity, Privacy, AndroidManifest, index.html | ~250 (real: about 130) | Python logic run, Java without | Birthdays and repeat jobs are remembered |
| 45 DONE | (old Batch C) Richer briefing, max 3 suggestions a day, quiet hours, each can be switched off | brief.py, app.py, index.html | ~200 (real: about 140) | With | One useful morning summary, not noise |
| 46 DONE | (old Batch D, smaller) Routines = saved task lists. Uses the task engine, no second system | tasks.py, app.py, index.html | ~115 (real: about 75) | With | One command runs a safe set of steps |
| 47 DONE | (old Batch E) Encrypted backup, restore with preview, delete everything | backup.py*, app.py, index.html | ~210 (real: about 210) | With | Memory is safe and can move to a new phone |
| 48 DONE | (old Batch G) Share to Jarvis, handoff summary for Claude or ChatGPT, lost-phone steps card. Also: app lock OFF by default, neon Home dashboard | AndroidManifest, MainActivity, AppLock, handoff.py*, app.py, index.html | ~180 (real: about 215 code lines) | Python run, Java without | Official sharing only, no private sessions |
| 49a DONE | Clipboard button (half of old Part 49, safe) | MainActivity, index.html | ~60 (real: about 45) | Without | Use a copied text without typing |
| 49b DONE | Notification summary. `NotifySummary.java` (NotificationListenerService, needs the Android notification access switch, Android shows a warning). OFF by default. Settings > Notification summary: 1 allow access, 2 choose up to 15 apps, 3 turn on. Keeps app name, title and 200 characters in phone memory only (never on disk, never sent) for 24 h, max 50. Drops anything with OTP, code, password, PIN, verification or a card number, ongoing and group-summary notifications, and Jarvis' own. Home > Smart shortcuts > Notifications shows the list; only the Summarize tap sends it to the AI; Clear list and Turn off wipe it. No server change (reuses chat and the same redaction idea as 49a) | NotifySummary.java*, Apps.java, MainActivity, AndroidManifest, index.html | ~230 | Page JS syntax only; Java NOT compiled | Day summary. Needs special notification access
| 57 DONE | Research answers and mood support. `web.py` `lookup()`: a link or `search: ...` is always read; in Research mode every question (8+ letters) is searched and the first result page is read too. The AI gets the search time and rules: direct answer first, confirmed vs unsure, only dates seen in the text, say so when sources disagree, say "could not find reliable confirmation" when unsure, no guesses on politics, war, health, money. The reply gets a `Sources:` line made from the real search result (not by the AI). `MOOD` text in `app.py`: listen first, ask vent / distract / fix, no diagnosis, no claim to be a doctor, emergency 112 or Tele-MANAS 14416 if he speaks of hurting himself. Nothing about mood is saved | web.py, app.py | ~90 | Python route tests with a mock AI and a fake search; real search NOT run | Honest, sourced answers; kind answers when he is low |
| 58 DONE | Voice modes and status line. `modes.py`: "research mode on", "quiet mode", "focus mode", "normal mode" (also "... off", Hindi words). The page keeps the mode (`localStorage jmode`) and sends it with every chat message. Quiet = no speaking and one short sentence; focus = two short sentences. A status line above the chat (Idle, Listening, Thinking, Jarvis is speaking, Waiting for Hey Jarvis) is worked out from the real state every 0.4 s, plus a mode picker | modes.py*, app.py, index.html | ~120 | Python tests; page JS syntax only, not rendered | One look shows what Jarvis is doing
| 50 DONE | Live system card (like the PC screenshot): RAM used/free, storage, battery and heat, Jarvis server own memory and CPU, uptime, net online. New `/stats` route, refreshed every 5 s only while the card is open. Honest "not available" if Android blocks a number | sysinfo.py*, app.py, index.html | ~110 | With (Python) | Hussain sees what Jarvis and the phone are using |
| 51 DONE | Voice Personality Engine, backend: intent classifier (CONVERSATION, INFORMATION, TASK_CONFIRMATION, REMINDER, BRIEFING, ALERT), policy table, JARVIS fallback, two voice profiles, `/tts` takes `intent` or `profile` | voiceengine.py*, tts.py, app.py | ~170 | With | The right voice is chosen by intent, not by keywords |
| 52 DONE | Voice Personality settings: Tony and JARVIS cards, Auto routing ON, manual override, Test Tony, Test JARVIS, active-voice badge, saved in `voice.json` on the server (survives restart), stop and switch while speaking | index.html, app.py | ~160 | Without (page) plus Python route tests | One clear place to control both voices |
| 53 DONE | Second voice provider = **Sarvam Bulbul v3** (changed from Google on 16 Nov 2026: Indian company, Hindi voices). Settings > Voice personality > Voice maker: Edge (free) or Sarvam, speaker list (shubh, rahul, aditya, ratan, amit, rohan), own key saved in `keys.json` under `sarvam` (never sent back, not in the chat key list). Tested with one short sentence before saving. If Sarvam fails, Edge speaks and the badge says so. **Tony is hidden** (page shows JARVIS only; server keeps the Tony profile, every reply is routed to JARVIS). Sarvam has no depth control, so the Depth slider is hidden when Sarvam is on | tts.py, voiceengine.py, app.py, index.html | ~170 | Python route tests with a fake Sarvam; real Sarvam call NOT run | Needs Hussain's Sarvam key |
| 53b DONE | Chat screen in the neon blue-purple look of Home: gradient own bubbles, Jarvis bubbles with a round J, glowing mic, new input bar. CSS only, no new feature | index.html | ~25 | Page JS syntax only, not rendered | Chat and Home look like one app |
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
| 85 DONE | Home card next best move: Do, Why, Later and the source, fixed rules | lens.py*, app.py, index.html | ~130 | With | One card tells what matters now |
| 86 DONE | Now / Next / Later strip under that card | lens.py, index.html | ~60 | With | The day in three columns |
| 87 DONE | Honest Mission view: three separate counts, Code built, Phone tested, Verified | progress.py, app.py, index.html | 39 | With | Honest count of what is really done |
| 88 | Memory Atlas: memories, people and notes on one page, with delete. Nothing new is saved | memory.py, people.py, app.py, index.html | ~110 | With | Planned, see section 2 |
| 89 | Search everywhere: sab jagah dhundo Bombay looks in notes, memories, people, lists, reminders (and later decis | search.py*, app.py, index.html | ~70 | With | Planned, see section 2 |
| 90 | Source label on research answers: One report or N sources agree, counted from the real search result | web.py, index.html | ~45 | With | Planned, see section 2 |
| 91 | Red Team: red team: yeh phone kharidna hai. The AI gets only your own Jarvis numbers (this month's spending, h | redteam.py*, app.py, index.html | ~60 | With | Planned, see section 2 |
| 92 | Debate Jarvis: debate ruthless: ..., debate spiritual: ... or debate opposite: .... Jarvis argues that side wi | debate.py*, app.py, index.html | ~80 | With | Planned, see section 2 |
| 93 | Decision Debt: sochenge baad mein: phone lena hai saves it; pending decisions lists them; the briefing shows u | decisions.py*, brief.py, backup.py, app.py | ~90 | With | Planned, see section 2 |
| 94 | Unfinished business: adhoora: Faisal se baat shows in the briefing now and then (at most once in 3 days) until | decisions.py, app.py | ~50 | With | Planned, see section 2 |
| 95 | Last talked: only people you pick. ammi track karo, then ammi se baat hui. The briefing says Ammi se 7 din se | touch.py*, brief.py, backup.py, app.py | ~90 | With | Planned, see section 2 |
| 96 | Mood check-in, only when you say it: mood 3 (1 to 5) or aaj mood low; mood history. After 4 low days one gentl | mood.py*, brief.py, backup.py, app.py | ~80 | With | Planned, see section 2 |
| 97 | Time Capsule (text): 6 mahine baad yeh sunana: .... On that day a card appears and Jarvis reads it after your | capsule.py*, backup.py, app.py, index.html | ~85 | With | Planned, see section 2 |
| 98 | Conditional capsule: show a capsule only when a phrase you chose is typed to Jarvis, or when 30 days pass with | capsule.py, touch.py, app.py | ~70 | With | Planned, see section 2 |
| 99 | Habit Contract: contract gym 7 din penalty 100. Each day that closes without aaj gym gaya adds 100 to a penalt | habits.py, app.py | ~80 | With | Planned, see section 2 |
| 100 | Timed modes: meeting mode 45 minute, namaz mode 20 minute, sleep mode, focus 45 minute. No voice, short replie | modes.py, index.html | ~70 | With | Planned, see section 2 |
| 101 | Body Double: body double 45 minute. Every 15 minutes a text check-in abhi bhi kaam par? with Haan / Nahi; a co | modes.py, index.html | ~60 | With | Planned, see section 2 |
| 102 | Cool-down before a message: say thanda karo first, then the WhatsApp command. A 20 second countdown shows your | actions.py, index.html | ~60 | With | Planned, see section 2 |
| 103 | Dream journal: sapna: ... saves your words as they are; sapne dikhao; sapno me Ammi kitni baar counts a word. | dreams.py*, backup.py, app.py, index.html | ~90 | With | Planned, see section 2 |
| 104 | Signs log: sign: 11:11 dekha; signs dikhao counts repeats. Only what you type; nothing is detected by itself | signs.py*, backup.py, app.py | ~40 | With | Planned, see section 2 |
| 105 | One honest question: sach sawal on lets Jarvis ask at most ONE hard question every 14 days. The AI gets only c | redteam.py, brief.py, app.py | ~60 | With | Planned, see section 2 |
| 106 | Topic drift: drift on, then drift dikhao compares the words you used most last month and this month in your ch | drift.py*, app.py | ~80 | With | Planned, see section 2 |
| 107 | Context Ghost: Chrome kholo research ke liye keeps the reason for 7 days; opening the same app through Jarvis | ghost.py*, actions.py, index.html | ~70 | With | Planned, see section 2 |
| 108 | Recovery card jab tu door tha: 3 reminders, 1 phone issue, with Review and Dismiss | index.html, app.py | ~45 | With | Planned, see section 2 |
| 109 | Life Timeline: reminder done, routine run, note saved, expense noted, with filters | events.py*, app.py, index.html | ~145 | With | Planned, see section 2 |
| 110 | Money picture: kamai 40000 mahina, bachat 5000; paisa picture shows income, spending (Part 84) and what is lef | money.py*, backup.py, brief.py, app.py | ~70 | With | Planned, see section 2 |
| 111 | What-if: agar job chhod du. Plain arithmetic on the numbers from Parts 84 and 110 (months you can manage). It | money.py, app.py, index.html | ~60 | With | Planned, see section 2 |
| 112 | Note after a call (Java): after a call ends Jarvis asks kuch yaad rakhna hai?. Needs the phone-state permissio | CallNote.java*, MainActivity.java, manifest, index.html | ~80 | Without | Planned, see section 2 |
| 113 | Reminders by place (Java): jab ghar pahunchu. Needs background location; battery and privacy design first | PlaceWatch.java*, MainActivity.java, manifest, index.html, app.py | ~120 | Without | Planned, see section 2 |
| 114 | Place and Bluetooth triggers (Java): a note shows when you reach a place or a chosen Bluetooth device connects | PlaceWatch.java, index.html, app.py | ~90 | Without | Planned, see section 2 |
| 115 | Anti-Doomscroll (Java): one calm line after N minutes in the same app (you set N). Needs Usage Access. Never b | UsageWatch.java*, MainActivity.java, manifest, index.html | ~110 | Without | Planned, see section 2 |
| 116 | App habit map (Java): YouTube ke baad usually Instagram, a count kept on the phone and shown as a note | UsageWatch.java, index.html | ~40 | Without | Planned, see section 2 |
| 117 DONE | What's new answers: last update, kya kya add hua, from zip names and this README | whatsnew.py*, app.py | 81 | With | Chat can say what was last added and how it helps |
| 118 | Assist mode guest session: nothing saved, End & erase, numbers masked | guest.py*, app.py, index.html | ~150 | With | Help another person without keeping their data |
| 119 | Assist tools: photo/screenshot helper, Translate, Explain simply, Reliable info, Plan, Big text | assist.py*, see.py, app.py, index.html | ~150 | With | Family, elders and students get quick help |
| 120 | Lens rail on Home: Project, Phone, Life chips | lens.py, index.html | ~60 | With | Filter the Home card by topic |
| 121 | Glass skin: premium look for Home and Assist, Reduce effects switch | index.html | ~380 | With | Look only, after Table A |
| 122 | Bottom bar with tabs as Parts are built | index.html | ~90 | With | One tap to Home, Talk, Assist, Timeline, Memory |
Estimates are rough (plus or minus 25 percent). Real numbers go into this table after each Part.


**Build order (next first):** 87, 117, 88, 89, 90, 118, 119, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 120, 121, 122, 112, 113, 114, 115, 116.
First of all comes Build APK and the phone tests of Table A (section 7). Weather is dropped.

### 11.6b Dual voice personality plan (added 15 Nov 2026; Parts 51, 52 and 53 built 16 Nov 2026; Tony hidden, provider changed to Sarvam)
Goal: two default voices that switch by themselves. Default from the first start: Tony and JARVIS with Auto routing ON (Hussain asked for this on 16 Nov 2026); the classic voice is only used if he switches it on in Settings. TONY = conversation (confident, witty, Hinglish). JARVIS = information, tasks, reminders, briefings, alerts (calm, deep, precise). No cloning of Rajesh Khattar or Atul Kapoor. Original or licensed voices only.
**What exists today (read from the repo):** `backend/tts.py` (35 lines) runs `edge_tts` with a fixed list `VOICES` (line 4): en-GB-Ryan, en-IN-Prabhat, hi-IN-Madhur, en-IN-Neerja, hi-IN-Swara. `app.py` route `POST /tts` (line 292) returns mp3. `index.html`: `neural()` (line 147) plays it, `speak()` (156) falls back to the browser voice, `#voice` and `#pre` select a voice and a preset (lines 41 to 42), `stopAll()` (262) stops sound, saved in `localStorage` (`jvoice`). There is no intent routing and no server-side voice settings.
**Two real profiles today? NO.** Edge has only one Hindi male voice (Madhur). Khattar, Rolex and Jarvis studio are Madhur with different pitch and speed. That is one voice in two moods, not two voices. Prabhat is male but Indian-English and reads Hindi badly.
**Rules for Parts 51 to 53:** reuse `tts.py` and `/tts`; no second server, no new database table, no new Android permission; keys only in `keys.json`; JARVIS is the fallback when intent is unclear; the voice that speaks is the voice that is shown; if a provider fails, fall back to Edge, then to the browser voice, and show which one spoke.
**Provider choice:** step 1 (Part 51 and 52) uses Edge only: Tony = Madhur, normal pitch, a little faster; JARVIS = Madhur, lower and slower. Free, but the two will sound related. Step 2 (Part 53, built): Sarvam Bulbul v3 instead of Google (Hussain's choice). Endpoint `POST https://api.sarvam.ai/text-to-speech`, header `api-subscription-key`, reply is JSON with base64 wav in `audios`. Needs internet and his own key; pricing and free credit not checked, look at his Sarvam account. Not yet tested with a real key or for Hinglish.
**Cost and internet:** Edge is free and needs internet. Google is pay as you go (a 200 character reply is about 0.006 USD at list price). Offline fallback is the browser voice, not Tony or JARVIS.

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
| 40 | Settings > Background listening test > Offline wake word: Download model, wait for "ready", Use offline engine; Start test; say Jarvis with the app open, then with the screen off | Model shows ready; with Jarvis open the mic opens by itself; with the screen off a "Jarvis heard you, Tap to talk" notification; the count goes up |
| 49a | Copy some text in Chrome, open Jarvis Home > Clipboard | The text shows in chat with buttons; a copied OTP or password is refused |
| 48 | Install the new APK. Open the app; share a link from Chrome (Share > Jarvis); say `handoff`; say `phone kho gaya` | App opens on Home with NO fingerprint prompt (App lock is OFF); shared text shows with buttons; handoff shows Copy and Share; lost-phone card opens Find Hub and Sanchar Saathi |
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
| 69 | BUILT | ~90 | about 95 | NOT YET. Python phrases tested; Java not compiled |
| 68 | BUILT | ~50 | about 62 | NOT YET. Python phrases tested; Java not compiled |
| 61 | BUILT | ~160 | about 68 (`index.html` 33, `Ears.java` 29, `MainActivity` 6) | NOT YET. JS syntax checked, echo filter run in Node; Java not compiled |
| 60 | BUILT | ~110 | about 114 | NOT YET. Python phrases tested (12 asserts in `test_app.py`); Java not compiled |
| 66 | BUILT | ~60 | about 150 | NOT YET. Python phrases tested; Java not compiled |
| 65 | BUILT | ~100 | about 147 (`phone.py` 96, `PhoneInfo.java` 46, `index.html` 4, manifest 1) | NOT YET. Python: 12 question phrases answered, 11 commands/chat phrases left alone; page JS syntax only. Java not compiled |
| 64 | BUILT | ~110 | about 199 (`CallByName.java` 105 new, `actions.py` 61, `index.html` 22, `MainActivity.java` 6, `tasks.py` 3, manifest 2) | NOT YET. Python phrases checked (21 phrases, 5 scripts); page JS syntax only. Java not compiled |
| 63 | BUILT | ~180 | about 85 (`lang.py` 104 new counted in 62/63 together; `actions.py`, `tasks.py`, `app.py`, `tts.py`, `index.html`) | NOT YET. Python phrases checked in 9 scripts; page JS syntax only |
| 62 | BUILT | ~120 | about 60 (`Apps.java` 7, `actions.py`, `index.html`) | NOT YET. Java not compiled |
| 59 | BUILT | ~60 | about 70 (`actions.py` 14, `tasks.py` 1, `index.html` about 55) | NOT YET. Python phrases checked, page JS syntax only. Not run: phone |
| 52 | BUILT | ~160 | 46 (`index.html` only; the routes were already in Part 51) | NOT YET. Page JS syntax checked only. Not run: phone |
| 47 | BUILT | ~210 | about 210 (`backup.py` 170 new, `index.html` +22, `app.py` +17, README setup line) | NOT YET. Python logic run here with real OpenSSL (lock, wrong passphrase, damage, path trick, merge, wipe); page not run |
| 46 | BUILT | ~115 | about 75 (`tasks.py` +70, `app.py` 1, `index.html` 1) | NOT YET. Python logic run here (save, run, refusals, limit 10, switch OFF); Java runner not compiled |
| 45 | BUILT | ~200 | about 140 (`brief.py` +100, `index.html` +4, `app.py` 1, `.gitignore` 1) | NOT YET. Python logic run here (cap, quiet hours, next day, settings); page not run |
| 44 | BUILT | ~250 | about 130 (`remind.py` +85, `calls.py` +22, `people.py` +14, `CalendarInfo.java` 39 new, `index.html` +3, `MainActivity` +6, `Privacy` +2, `app.py` 2, manifest 1) | NOT YET. Python logic run here (repeat, month end, 29 Feb, duplicate birthday, calendar text); Java not compiled |
| 48 | BUILT | ~180 | about 215 (`handoff.py` 48 new, `MainActivity` 28, `AppLock` 4, manifest 1, `app.py` 3, `index.html` about 130 incl. the new Home look; the Home block replaced the old Part 56 block) | NOT YET. Python handoff logic run here; Home page rendered in a headless browser and JS syntax checked; Java not compiled |
| 40 | BUILT | ~200 | about 230 (`WakeEngine.java` 125 new, `ListenService` 40, `MainActivity` 30, `index.html` 14, `build.gradle` 5) | NOT YET. Java not compiled; Vosk library and model download never run here |
| 49a | BUILT | ~60 | about 45 (`MainActivity` 14, `index.html` 12 plus a shared function change) | NOT YET |
| 56 | BUILT | ~130 | about 75 (`index.html` about 46, `remind.py` 11, `app.py` 4, plus fixes below) | NOT YET. Page syntax checked only |
Fixes in the same zip: (1) the Settings system card used a helper (`el`) that only existed inside another function, so it would have stayed empty; it is global now. (2) Durations over 60 minutes now show as hours and minutes everywhere (page and `clock.py`, for example "1 h 15 min", never "75 minutes").

How the dashboard works (Part 29): open Settings (gear), the first card is "Privacy and permissions". Each row shows three separate things: permission (Allowed or Not allowed, from Android), running now (from Java, not from the page), and last used. A permission being allowed never means a feature is running. Screen reader shows "Accessibility ON" only when the Jarvis accessibility service is really connected. "Reminder service ON" means the background service is really up. The activity log keeps only the feature name and time (max 30 lines, one entry per feature per minute) and never any content. "Open settings" buttons open one fixed Android page each. If the server stops, a red banner appears after about 10 seconds and Jarvis retries every 5 seconds; it clears by itself when the server is back. Chrome shows only the server line, because Android permissions exist only in the app.
