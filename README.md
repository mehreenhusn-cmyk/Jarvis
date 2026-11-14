# JARVIS - Hussain ka personal AI dost (phone par, Termux + Chrome)

> **Naye Claude / AI ke liye (pehle ye padho):** Hussain tumhe sirf is repo ka link bhejta hai, kyunki uske 2-3 Claude
> accounts hain aur limit khatam hoti rehti hai. Is README mein poora plan hai: kya bana rahe, kyun, kaise, rules,
> abhi kahan pahunche, aur agla kaam. Isse padh ke seedha agla part shuru karo. Original chat dobara mat maango.
> Repo: https://github.com/mehreenhusn-cmyk/Jarvis

## 1. Kya bana rahe hain
Ek **personal AI assistant** (Iron Man ke Jarvis jaisa dost), ordinary chatbot nahi. Hindi, English aur Hinglish samajhta hai,
bolkar baat karta hai, aur dheere-dheere phone ke kaam (yaad dilana, memory, contacts, finance ledger) karna seekhega.
Final goal: ek hi app mein sab, phone par hi chale, PC ki zaroorat nahi.

## 2. Kyun
Hussain beginner hai, Termux par kaam karta hai, aur chahta hai ki sab **copy-paste** se ho (nano/.env jaisa mushkil kaam nahi).
Isliye: simple, chhota code, phone par hi chalne wala, aur jo chale wahi "chal raha hai" bola jaye.

## 3. Kaise bana rahe hain (architecture, simple)
```
Chrome / home-screen icon  --->  Python server (Termux, 127.0.0.1:8787)  --->  AI provider (Groq/OpenRouter/...)
   web/index.html                  backend/app.py (+ tts.py)                    SQLite: backend/jarvis.db
```
- **Backend:** Python stdlib server (FastAPI nahi: Termux par pydantic-core compile hoke atakta hai). Koi pip install nahi
  (sirf Part 7 ki awaaz ke liye `pip install edge-tts`, optional).
- **Frontend:** ek hi `web/index.html` (Flutter nahi: build nahi karna padta). Asli APK baad mein, GitHub cloud build se, agar zaroorat padi.
- **AI:** 5 providers (groq, openrouter, mistral, deepseek, nvidia), sab OpenAI-style API. `ask()` pehla chalne wala use karta hai, fail ho to agla.
- **Keys:** app mein ⚙ > key paste > company khud pehchanta hai > asli test > green ✅. `backend/keys.json` (gitignored, encrypted nahi).
- **Pairing:** Termux mein 6-digit code (10 min, ek baar) > phone ko token milta hai, DB mein sirf hash.
- **OpenJarvis** (github.com/open-jarvis/OpenJarvis) ka poora install nahi kiya (Rust extension, bhaari dependencies). Sirf idea liye:
  bearer-token auth, memory (`memory/`), scheduler (`scheduler/`), speech options. Koi file copy nahi hui (copy ho to NOTICE mein credit).

**Awaaz ka target (Hussain ne video bhej ke bataya):** Iron Man ki Hindi dub jaisi gehri, bharosemand, shaant mardana awaaz
(video: "Ironman hindi voice by Rajesh Khattar"). Free edge-tts mein kisi ek actor ki exact awaaz nahi milti; hum Madhur (Hindi male)
+ Gehra slider (pitch kam) + thodi dheemi speed se kareeb jaate hain. Kisi asli actor ki awaaz clone karna (voice cloning) alag, bhaari aur
consent/legal ka mamla hai, abhi nahi. Agar Hussain "aur gehra" kahe to Gehra slider/default (`index.html` mein `pt`) kam karo.

## 4. RULES (zaroori)
1. **Har part mein 350 se kam lines (code).** Naye files tabhi jab sach mein zaroorat ho. Part ke baad README update karo.
2. Hussain ko **Roman Hinglish** mein simple samjhao (Devanagari nahi). Files aur lines **table** mein batao. Wo dictation se likhta hai, galat spelling normal hai.
3. Output: **ek hi zip** `Jarvis_partN.zip`, usme sirf **badli hui/nayi files** (poora repo nahi). Hussain bas zip download karta hai (Downloads mein).
   `run.sh` (neeche Section 5) 5 sec mein khud: zip kholta hai, GitHub push karta hai, server restart karta hai, aur page khud refresh hota hai.
   Hussain ko Termux mein kuch likhna nahi padna chahiye. `sync.sh` aur `run.sh` ko zip se badalna risky hai (chalte script ko badalna): zaroorat ho to Hussain ko ek baar `bash run.sh` dobara chalane ko bolo.
4. Test: bas syntax check, test file tabhi jab sach mein zaroorat ho (limit bachane ke liye). Jo test nahi hua use "tested" mat likho.
5. Hussain se kam se kam Termux commands maango. Jo pehle chal chuka wo dobara mat batao.
6. Memory mein password/OTP/PIN/CVV kabhi save mat karo (`memory.py` mein rok hai). Secrets (keys, GitHub token) kabhi chat, code ya Git mein nahi. Keys sirf `backend/keys.json`/`.env` (dono gitignored).
7. Hussain ka **OWL1 trading repo bilkul alag** hai. Kabhi mat chhuo.
8. Har part ke baad Hussain ko table mein batao: agle parts ki files + lines, aur **ab tak kul kitni files/lines hui aur kitni baaki** (Section 7). README ka status update karo.
9. Galtiyan jo ho chuki: GitHub se download kiya `Jarvis-main.zip` Downloads mein mat chhodo (sync.sh sirf `Jarvis_part*.zip` uthata hai). Chrome page translate na kare (`notranslate` laga hai).

## 5. Setup aur auto-update (phone, Termux)
Ek baar: `pkg install git python unzip && termux-setup-storage`, `pip install edge-tts` (awaaz ke liye), GitHub login (`git config --global credential.helper store`, push par username + token Termux mein hi).
Phir roz bas: **`cd ~/Jarvis && bash run.sh`** (Termux khula rakho). Ye server chalata hai aur Downloads mein naya `Jarvis_part*.zip` aate hi
update + GitHub push + server restart khud karta hai. Page `/status` ke `boot` number se restart pehchan ke khud reload hota hai; pair dobara nahi karna padta (token DB mein hai).
Chrome: **http://127.0.0.1:8787**, pehli baar 6-digit code, phir ⚙ se key paste. Bina key test: `.env` mein `PROVIDER=mock`.
**Auto-start (Part 11):** ek baar `python backend/app.py` ya `bash run.sh` chalne ke baad Termux kholte hi Jarvis khud chalta hai (copy-paste nahi). Band karna ho: `.env` mein `JARVIS_NO_AUTOSTART=1`.
Purane tareeke: `python backend/app.py` (sirf server), `bash sync.sh once` (sirf zip kholo + push).

## 6. Status (15 Nov 2026)  🟢 phone par chala  🟡 bana, phone par test baaki  ⚪ shuru nahi
| Part | Cheez | Haal |
|---|---|---|
| 1 | Backend: chat, pairing, token auth, SQLite history | 🟢 |
| 2 | Chrome chat page (pair, chat, history, offline status) | 🟢 |
| 3 | Mic (Hindi/English bolna, Chrome likhta hai), bolkar jawab, stop button | 🟢 mic chala; awaaz robot jaisi lagi |
| 3 | Home-screen icon (Add to Home screen) | 🟡 |
| 4-5 | Keys app mein paste, green tick, 5 providers + fallback | 🟢 OpenRouter ✅ aur chat jawab aaya; baaki providers 🟡 |
| 6 | Awaaz tune: Gehra (pitch) + Speed slider (ab net-awaaz par bhi chalte hain), 🔊 test | 🟡 phone par sunna baaki |
| 7 | Neural awaaz `backend/tts.py` (edge-tts) | 🟡 `pip install edge-tts` Hussain ke phone par ho gaya; sunna baaki |
| 8 | Iron Man Hindi-dub wala Jarvis: default awaaz Madhur, jawab shuddh Hindi (Devanagari), "sir" kehta hai. Hindi awaaz = Hindi style, English awaaz = Hinglish | 🟡 sunna baaki |
| 9 | **Memory** (`backend/memory.py`): chat mein "yaad rakho: ...", "kya yaad hai", "sudhaar 3: ...", "bhool jao 3"; ⚙ mein list + hatao. Jo yaad hai wo AI ko har chat mein diya jaata hai. Password/OTP/PIN kabhi save nahi | 🟡 logic check hua (regex/DB), phone par chat se test baaki |
| 10 | **Reminders** (`backend/remind.py`): "kal subah 10 baje Faisal ko 5000 dene yaad dilana" (tareekh AI se, phone ke time se), "reminders dikhao", "reminder hatao 2". Page khula ho to ⏰ message + awaaz + vibrate. **`run.sh`:** zip download > auto update + push + restart + page auto-refresh | 🟡 logic check hua (nakli AI jawab se), phone par test baaki. Reminder tabhi aata hai jab page khula ho; band app mein notification APK (Part 17) se |
| 11 | **Hisab/ledger** (`backend/ledger.py`): "Faisal ko 5000 dene hain, 15 Nov ko yaad dilana" > entry + due date par subah 9 baje reminder; "hisab dikhao" (total dena/lena), "paid 3", "hisab hatao 3"; ⚙ mein list + "chuka" button. Sirf likhai-padhai, asli payment nahi. **Auto-start** (`backend/autostart.py`): server pehli baar chalne par `~/.bashrc` mein 2 line + `~/.termux/boot/jarvis.sh` bana deta hai, to Termux kholte hi Jarvis chalu (phone restart par bhi, agar Termux:Boot app install ho) | 🟡 logic check hua (nakli AI jawab, nakli HOME), phone par test baaki |
| 8+ | Neeche roadmap | ⚪ |

## 7. Roadmap: kul ~25 parts, har part < 350 lines (andaza, files aur lines)
Ab tak (Part 1-11): **~16 files, ~870 lines** code (app.py 297, index.html 156, ledger 85, remind 70, memory 58, tts 35, autostart 27, run.sh 24...).
| Stage | Part | Kya | Nayi files | Lines |
|---|---|---|---|---|
| A. Browser Jarvis (Termux) | 12 | Privacy: "stop listening" + mic/awaaz status bar | 0 (edit) | ~60 |
| | 13 | Internet search + link/PDF samjhana | 1 | ~120 |
| | 14 | Subah ka briefing (reminders + baaki dues) | 1 | ~80 |
| B. Asli APK | 15 | Flutter/WebView APK shell + GitHub Actions build | ~6 | ~150 |
| | 16 | APK build fixes (1-3 round, error screenshot se) | 0-2 | ~50 |
| | 17 | App band ho tab bhi notification | 2 | ~150 |
| C. Android powers | 18 | Contacts + call history metadata | 2 | ~200 |
| | 19 | People profiles (dost, notes) | 1 | ~150 |
| | 20 | Location (permission ke saath) | 2 | ~120 |
| | 21 | Camera se surroundings samajhna | 2 | ~200 |
| | 22 | Screen/app samajhna (AccessibilityService) | 3 | ~300 |
| | 23 | Phone slow kyun hai (diagnostics) | 2 | ~150 |
| D. Aakhri | 24 | "Hey Jarvis" wake word (Android par uncertain, pehle test) | 2 | ~150 |
| | 25 | Security audit + final polish | 0-1 | ~100 |
| **Baaki (12-25)** | | | **~26 files** | **~1,980 lines** |
| **Final total (andaza)** | | | **~42 files** | **~2,800 lines** |
Part 14 ke baad Jarvis roz kaam ka. Stage B/C Android-only hain, yahi sabse risky (build errors, permissions).

Security vision (lambi): password/OTP/PIN kabhi store nahi; message bhejne/delete/payment se pehle confirmation; mic/camera chhupke nahi;
call log se sirf metadata (baat-cheet ka content nahi); "stop listening" se mic turant band.

## 8. Security (ab tak)
Server sirf `127.0.0.1` par sunta hai. Token ka sirf hash. Pairing 10 min, ek baar, 5 galat par lock. Keys browser ko wapas nahi bheji jaati.
Part 7 mein jo text bola jaata hai wo Microsoft ki awaaz service ko jaata hai (internet par), isliye awaaz band rakho agar baat private ho.
