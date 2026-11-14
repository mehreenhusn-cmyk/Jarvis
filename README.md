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

## 4. RULES (zaroori)
1. **Har part mein 350 se kam lines (code).** Naye files tabhi jab sach mein zaroorat ho. Part ke baad README update karo.
2. Hussain ko **Roman Hinglish** mein simple samjhao (Devanagari nahi). Files aur lines **table** mein batao. Wo dictation se likhta hai, galat spelling normal hai.
3. Output: **ek hi zip** `Jarvis_partN.zip`, usme sirf **badli hui/nayi files** (poora repo nahi). Phone ke Downloads mein save, phir `bash sync.sh once` GitHub par push kar deta hai.
4. Test: bas syntax check, test file tabhi jab sach mein zaroorat ho (limit bachane ke liye). Jo test nahi hua use "tested" mat likho.
5. Hussain se kam se kam Termux commands maango. Jo pehle chal chuka wo dobara mat batao.
6. Secrets (keys, GitHub token) kabhi chat, code ya Git mein nahi. Keys sirf `backend/keys.json`/`.env` (dono gitignored).
7. Hussain ka **OWL1 trading repo bilkul alag** hai. Kabhi mat chhuo.
8. Har part ke baad agle 4-5 parts (files + lines) table mein dikhao taaki Hussain chun ya jod sake.
9. Galtiyan jo ho chuki: GitHub se download kiya `Jarvis-main.zip` Downloads mein mat chhodo (sync.sh sirf `Jarvis_part*.zip` uthata hai). Chrome page translate na kare (`notranslate` laga hai).

## 5. Setup (phone, Termux)
```
pkg install git python unzip && termux-setup-storage
cd ~/Jarvis && python backend/app.py        # pairing code dikhega
```
Chrome: **http://127.0.0.1:8787**, code daalo, ⚙ se key paste karo. Server tabhi chalta hai jab Termux khula ho (`termux-wake-lock`).
Bina key test: `.env` mein `PROVIDER=mock`.

## 6. Status (15 Nov 2026)  🟢 phone par chala  🟡 bana, phone par test baaki  ⚪ shuru nahi
| Part | Cheez | Haal |
|---|---|---|
| 1 | Backend: chat, pairing, token auth, SQLite history | 🟢 |
| 2 | Chrome chat page (pair, chat, history, offline status) | 🟢 |
| 3 | Mic (Hindi/English bolna, Chrome likhta hai), bolkar jawab, stop button | 🟢 mic chala; awaaz robot jaisi lagi |
| 3 | Home-screen icon (Add to Home screen) | 🟡 |
| 4-5 | Keys app mein paste, green tick, 5 providers + fallback | 🟢 OpenRouter ✅ aur chat jawab aaya; baaki providers 🟡 |
| 6 | Awaaz tune: gehra (pitch) + speed slider, test button | 🟡 phone par dekhna baaki |
| 7 | Asli Jarvis awaaz (Edge neural: British Ryan, Indian Prabhat, Hindi Madhur...), `backend/tts.py` | 🟡 `pip install edge-tts` chalna chahiye (Termux par pakka nahi); fail ho to phone ki awaaz par lautta hai |
| 8+ | Neeche roadmap | ⚪ |

## 7. Roadmap (har part < 350 lines, Hussain ke "approve" ke baad)
| Part | Kya | Files | Lines (andaza) |
|---|---|---|---|
| 8 | **Memory:** "yaad rakho", dekho, sudharo, delete (kabhi kuch invent nahi) | `backend/memory.py` (naya), `app.py`, `index.html` | ~140 |
| 9 | **Reminders:** "Faisal ko 5000 dene hain 15 Nov ko yaad dilana", page khula ho to notification | `backend/remind.py` (naya), `index.html` | ~110 |
| 10 | **Personality:** Jarvis ka andaaz, Hussain ka naam, chhote jawab, `backend/persona.txt` | `persona.txt`, `app.py` | ~35 |
| 11 | **Finance ledger:** kisko dena/lena, amount, due date, total | `backend/ledger.py`, `index.html` | ~150 |
| 12 | **Auto-start:** Termux:Boot se server khud chalu, wake-lock | `start.sh` | ~20 |
| Baad mein | Asli APK (Flutter + GitHub build), contacts/call history, location, screen padhna, "Hey Jarvis" wake word (Android par uncertain, pehle test) | - | - |

Security vision (lambi): password/OTP/PIN kabhi store nahi; message bhejne/delete/payment se pehle confirmation; mic/camera chhupke nahi;
call log se sirf metadata (baat-cheet ka content nahi); "stop listening" se mic turant band.

## 8. Security (ab tak)
Server sirf `127.0.0.1` par sunta hai. Token ka sirf hash. Pairing 10 min, ek baar, 5 galat par lock. Keys browser ko wapas nahi bheji jaati.
Part 7 mein jo text bola jaata hai wo Microsoft ki awaaz service ko jaata hai (internet par), isliye awaaz band rakho agar baat private ho.
