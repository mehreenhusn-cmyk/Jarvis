# JARVIS - personal AI dost (Android + Termux)

**Naye Claude / AI ke liye:** is README ko poora padho. Ye project ka status aur agle kaam ka plan hai.
Hussain tumhe sirf is repo ka link bhejega; yahin se samajh ke agla part banao.
Repo: https://github.com/mehreenhusn-cmyk/Jarvis

## Rules (zaroori)
- Hussain beginner hai. Roman Hinglish mein samjhao, Devanagari nahi.
- **Har part mein 350 se kam lines.** Naye files tabhi jab sach mein zaroorat ho.
- Test kiye bina "chal raha hai" mat bolo. Result real dikhao, jhooth nahi.
- Secrets (API keys) kabhi chat, code ya Git mein nahi. Sirf `backend/.env` mein (gitignored).
- Hussain ka OWL1 trading repo bilkul alag hai. Usse kabhi mat chhuo.
- Har part ke baad is README ka "Status" update karo.

## Keys kaise daalein (nano/.env ki zaroorat nahi)
Chat page > ⚙ > key copy karke paste karo (ya "Clipboard se paste") > green ✅ aaye to save. Keys `backend/keys.json` mein
rehti hain (gitignored, sirf owner ke liye, **encrypted nahi**; phone ka private storage hai). Keys browser ko wapas nahi bheji jaati.
`.env` ab optional hai (sirf PROVIDER order ya MODEL_* badalna ho to).

## Setup (phone, Termux)
```
pkg install git python unzip
termux-setup-storage
cd ~/Jarvis && cp backend/.env.example backend/.env   # phir .env mein apni key daalo
python backend/app.py                                  # server start, pairing code dikhega
python backend/test_app.py                             # self-test (key nahi chahiye)
```
Server chalu rehte hi Chrome mein kholo: **http://127.0.0.1:8787** (chat page). Pehli baar Termux mein
dikha 6-digit PAIRING CODE wahan daalo. Bina API key ke test: `.env` mein `PROVIDER=mock` (sirf echo karta hai).
Server tabhi tak chalta hai jab tak Termux khula hai (`termux-wake-lock` se phone sone par bhi chalta rehta hai).

## Auto-push (download -> GitHub)
Claude jo `Jarvis_part*.zip` deta hai, usse phone ke Downloads mein save karo. Phir:
```
bash sync.sh once     # ek baar: zip kholta hai, commit karta hai, GitHub push karta hai
bash sync.sh watch    # chalu chhod do: har 10 sec mein naya Jarvis*.zip khud push karega
```
Pehli baar GitHub login: `git config --global credential.helper store`, phir push par username
aur **token** Termux mein hi daalo. Kisi chat mein token mat bhejo. `sync.sh` zip se update nahi
hota (jaan-boojh ke); wo sirf pehle zip mein tha.

## Status (15 Nov 2026) - Part 1: backend, Part 2: browser chat page, Part 3: voice + multi-provider + home-screen icon, Part 4: keys app ke andar paste
| Cheez | Haal |
|---|---|
| Chat API (`/chat`, `/history`) | Mock provider ke saath tested: PASS |
| Pairing (6-digit code, token) | Tested: PASS (galat code, dobara use, 5 galat par lock) |
| SQLite (baat-cheet yaad) | Tested: restart ke baad bhi bachta hai |
| Offline status (`/status`) | Tested: server band hone par connect fail dikhta hai |
| Asli AI provider (Groq etc.) | **Abhi test nahi hua, key baaki hai** (sandbox mein internet nahi). Hussain ke phone par pehla test baaki |
| Chat page `web/index.html` (pair, chat, history, offline status) | **Phone par tested (OnePlus Nord 3): pairing, page, message bhejna, error dikhana sab chala.** Bina key ke ye error aata hai: `GROQ_API_KEY not found` (ye sahi hai) |
| **Keys app mein paste (⚙ Settings)**: key paste karo, company khud pehchanta hai (gsk_=Groq, sk-or-=OpenRouter, nvapi-=Nvidia, sk-+32hex=DeepSeek, mstrl_/32 akshar=Mistral), asli test karta hai, green ✅ ya red ❌ | Pehchan, save, delete, "key wapas nahi aati", file permission 600: tested (mock key se). **Asli providers se test Hussain ke phone par baaki** |
| Voice test (phone, 15 Nov): mic chala, Hindi bola to Chrome ne Devanagari mein likha ("हेलो"). Bug mila: voice dropdown mein pehli awaaz Assamese aa rahi thi (Android `as_IN` jaisa underscore wala code deta hai). Fix: en-IN pehle. Chat box mein key paste ho jaye to ab wo chat mein nahi jaati, seedha key-check mein jaati hai | Fix tested sirf syntax tak; **phone par dekhna baaki** |
| Multi-provider fallback (`PROVIDER=groq,openrouter,...`) | Tested mock se (pehla fail -> agla). Asli keys se **abhi test baaki** |
| `python backend/check_keys.py` (har key ka OK/FAIL, key print nahi hoti) | Bina key ke tested; asli keys par Hussain chalayega |
| Voice: mic button (Chrome SpeechRecognition), bolkar jawab (TTS), voice picker, stop button, "Mic CHALU/band" status | JS syntax OK; **phone par test baaki**. Hindi bolne par Chrome Devanagari likhta hai, Jarvis jawab Roman mein deta hai |
| Home-screen icon (manifest + icons) | Files serve hoti hain (tested); Chrome menu > "Add to Home screen"/"Install app" **phone par test baaki** |
| Flutter / asli APK | Abhi shuru nahi |

Providers: groq, openrouter, mistral, deepseek, nvidia. `PROVIDER=` mein comma se order do; pehla fail ho (key nahi / error) to agla chalta hai. Sab OpenAI-style API
hain isliye ek hi chhota adapter (`ask()` in `backend/app.py`) sab chalata hai. Default model names
untested guess hain; galat nikle to `MODEL=` se badlo.

**FastAPI ki jagah Python stdlib server** use hua: Termux par FastAPI ka pydantic-core compile ho kar
atak sakta hai. Stdlib mein koi pip install nahi, aur Flutter ke liye API same rahegi. Zaroorat padi to baad mein badal sakte hain.

## OpenJarvis se kya liya / kya nahi
Zip audit hua (2,468 files). Poora install **nahi** kiya: Rust extension zaroori hai, `datasets`,
`posthog` (analytics) jaise bhaari dependencies hain, Termux par mushkil, aur code bahut bada hai.
| Cheez | Faisla |
|---|---|
| Bearer-token auth ka idea (`server/auth_middleware.py`) | Liya (khud chhota version likha) |
| Memory (`memory/`), scheduler (`scheduler/`) | Phase 2 ke liye idea, abhi nahi |
| Speech options (`speech/`) | Voice part mein dekhenge |
| agents, tools, evals, channels, server (60k+ lines) | Nahi liya |
**Abhi tak OpenJarvis ki koi file is repo mein copy nahi hui.** Sab code naya likha gaya hai.
Apache-2.0: koi file seedhi copy ho to NOTICE mein credit likhna hai (abhi koi copy nahi hui).

## Aage ka plan (ek-ek part, har part < 350 lines, Hussain ke "approve" ke baad)
1. ~~Part 2/3: chat screen, voice, icon~~ browser page se ho gaya (Flutter ki jagah, kyunki Flutter build ke bina turant chalta hai). Flutter app zaroorat par baad mein.
2. **Part 3 (done, test baaki):** push-to-talk, text-to-speech, voice picker (male/female Android ki available voices par depend karta hai), mic stop. Hinglish ke liye en-IN voice behtar padti hai.
3. **Part 4:** Memory (yaad dilao, dekho, sudharo, delete) + simple reminders.
4. Baad mein: app launch/screen samajhna, contacts/call history, finance ledger, location, wake word ("Hey Jarvis" - Android par uncertain, test ke baad).

## Security (ab tak)
Server sirf `127.0.0.1` par sunta hai (phone ke bahar se nahi dikhta). Token ka sirf hash DB mein.
Pairing code 10 min, ek baar. API keys sirf `.env` mein. Call logs/camera/mic features abhi hain hi nahi.

## Dhyan rakho (galtiyan jo ho chuki)
- GitHub se download kiya `Jarvis-main.zip` kabhi Downloads mein mat chhodo: `sync.sh` usse bhi utha leta tha aur repo mein nested `Jarvis-main/` folder ban gaya. Ab sirf `Jarvis_part*.zip` uthana hai (sync.sh mein ek `sed` se badla, README ke upar steps dekho).
- Chrome page ko auto-translate kar deta tha (Hinglish ko English bana deta tha). Ab `notranslate` laga hai.
