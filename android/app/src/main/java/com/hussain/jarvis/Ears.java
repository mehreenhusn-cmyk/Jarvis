package com.hussain.jarvis;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.media.AudioDeviceInfo;
import android.media.AudioManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.webkit.WebView;
import java.util.ArrayList;
import org.json.JSONObject;

/** Part 25: the phone's own speech recognizer (the WebView has none). It listens only after you tap the mic or turn on Hey Jarvis. */
class Ears implements RecognitionListener {
    final Activity act;
    final WebView web;
    final Handler ui = new Handler(Looper.getMainLooper());
    SpeechRecognizer sr;
    String lang = "en-IN";
    int boff;            // Part 162: Hey Jarvis never gives up: the pause after an error grows 3, 6, 12, 30, 60 s (back to 0 when a voice or a result comes)
    int fails;           // soft errors in a row (speech service disconnected); reset when you actually speak
    boolean retrying;    // true when again() calls start(), so the counter is not reset by our own retry
    static volatile long quiet = 2500L;  // Part 153: how long Jarvis waits in silence before he answers (Settings > Voice & Listening)
    final StringBuilder held = new StringBuilder();  // Part 161: the parts of ONE sentence heard so far (you paused in the middle)
    volatile boolean speaking;  // Part 161: true while you talk again inside the waiting time
    final Runnable flushJob = this::flush;
    static volatile boolean always;    // Part 188: the page's "Always listening" switch is on
    static volatile int wakeSens = 2;  // Part 191: 1 low, 2 normal, 3 high: how fast "Hey Jarvis" is taken from half-heard words (noisy room, fan)
    private volatile long beat = System.currentTimeMillis();  // Part 188: when the speech service last did anything
    private String lastPartial = "";   // Part 191: the half-heard words that already contain "Jarvis"
    final Runnable partialJob = this::partialFire;
    final Runnable dog = this::watch;
    /** Part 189: words that cannot end a sentence. If the heard text ends with one, or with a comma, Jarvis waits longer before answering. */
    private static final java.util.Set<String> OPEN = new java.util.HashSet<>(java.util.Arrays.asList(
        "जो", "कि", "और", "तो", "क्योंकि", "मतलब", "लेकिन", "पर", "या", "की", "का", "के", "को", "में", "से", "फिर", "जैसे", "अगर", "जब", "तब", "हम", "मैं", "मेरा", "मेरी", "मेरे",
        "jo", "ki", "aur", "to", "kyunki", "lekin", "ya", "ka", "ke", "ko", "mein", "se", "phir", "jaise", "agar", "jab", "tab", "hum", "main",
        "and", "or", "the", "a", "of", "that", "because", "but", "if", "so", "with", "for", "in", "on", "my"));
    static boolean endsOpen(String s) {
        String t = s == null ? "" : s.trim().toLowerCase();
        if (t.isEmpty()) return false;
        if (t.endsWith(",") || t.endsWith("...")) return true;
        String[] w = t.split("\\s+");
        String last = w[w.length - 1].replaceAll("[^\\p{L}\\p{M}]", "");
        return OPEN.contains(last);
    }
    private float floor = 99f;  // Part 160: the quiet level of the room (slowly follows the mic level)
    private int hot;             // Part 160: how many level readings in a row were clearly louder than the room
    private long lastVoice;      // Part 160: when the page was last told "a voice started"
    static volatile boolean loud;  // Part 164: interrupt on the loudspeaker (set by the page): the mic LEVEL is not used then, because Jarvis's own voice would trigger it; only words count
    private WakeEngine.Dictate dict;  // Part 196: offline Hindi listening, used when the phone speech service has no internet or breaks
    volatile boolean wake, on, barge;  // barge (Part 61): listening WHILE Jarvis speaks, partial words go to the page so it can stop talking

    Ears(Activity a, WebView w) { act = a; web = w; }

    // ---- Part 162: no restart beep. The phone speech service beeps each time it starts; the notification and system sounds are muted for about 1 s around the start and given back (music that is playing is never touched). Some phones ignore it. ----
    private static final android.os.Handler HUSH = new android.os.Handler(Looper.getMainLooper());
    private static final ArrayList<Integer> MUTED = new ArrayList<>();
    private static Context hushCtx;
    private static final Runnable GIVE_BACK = () -> unhush();

    static synchronized void hush(Context c, boolean allowMusic) {
        try {
            if (!c.getSharedPreferences("j", 0).getBoolean("hush", true)) return;
            hushCtx = c.getApplicationContext();
            AudioManager am = (AudioManager) hushCtx.getSystemService(Context.AUDIO_SERVICE);
            ArrayList<Integer> st = new ArrayList<>();  // never the ring stream: on many phones that would touch the ringer mode
            st.add(AudioManager.STREAM_NOTIFICATION);
            st.add(AudioManager.STREAM_SYSTEM);
            if (allowMusic && !am.isMusicActive()) st.add(AudioManager.STREAM_MUSIC);  // the beep is on this stream on some phones; only when nothing plays
            for (int s : st) {
                if (MUTED.contains(s) || am.isStreamMute(s)) continue;
                am.adjustStreamVolume(s, AudioManager.ADJUST_MUTE, 0);
                MUTED.add(s);
            }
            HUSH.removeCallbacks(GIVE_BACK);
            HUSH.postDelayed(GIVE_BACK, 1100);
        } catch (Exception e) { /* Do Not Disturb or the phone refuses: the beep stays, nothing else happens */ }
    }

    /** Gives every sound back. Called after 1 s, and whenever listening stops, so nothing stays muted. */
    static synchronized void unhush() {
        HUSH.removeCallbacks(GIVE_BACK);
        if (hushCtx == null) { MUTED.clear(); return; }
        try {
            AudioManager am = (AudioManager) hushCtx.getSystemService(Context.AUDIO_SERVICE);
            for (int s : MUTED) am.adjustStreamVolume(s, AudioManager.ADJUST_UNMUTE, 0);
        } catch (Exception e) { /* nothing more to do */ }
        MUTED.clear();
    }

    /** Main thread only. wakeMode: keep listening again and again, and the page looks for "Hey Jarvis". */
    void start(String l, boolean wakeMode) { start(l, wakeMode, false); }

    void start(String l, boolean wakeMode, boolean bargeMode) {
        stop();
        if (!retrying) fails = 0;
        retrying = false;
        if (Privacy.stopped) { js("onHeardErr", "Jarvis is stopped. Tap Turn mic on first"); return; }
        if (!SpeechRecognizer.isRecognitionAvailable(act)) {
            lang = l; wake = wakeMode; barge = bargeMode;
            if (offlineGo()) return;  // Part 196
            js("onHeardErr", "this phone has no speech service"); return;
        }
        if (ListenService.up) ListenService.halt(act);  // Part 39: only one listener at a time; opening the mic here ends the background test
        lang = l; wake = wakeMode; on = true; barge = bargeMode;
        sr = SpeechRecognizer.createSpeechRecognizer(act);
        sr.setRecognitionListener(this);
        hush(act, !barge);  // Part 162
        sr.startListening(listenIntent());
        Privacy.used(wake ? "wake" : "mic");
        beat = System.currentTimeMillis();
        arm();  // Part 188
    }

    /** Part 188: a watchdog for Always listening. If the speech service says nothing at all for 30 seconds (it sometimes hangs without any error), a fresh recognizer is started. */
    void arm() {
        ui.removeCallbacks(dog);
        if (always && on) ui.postDelayed(dog, 15000L);
    }

    private void watch() {
        if (!on || !always) return;
        if (System.currentTimeMillis() - beat > 30000L) {
            beat = System.currentTimeMillis();
            retrying = true;
            start(lang, wake, barge);  // start() arms the watchdog again
            return;
        }
        ui.postDelayed(dog, 15000L);
    }

    /** Part 191: in Hey Jarvis mode the half-heard words are watched too. In a noisy room the speech service may never decide that you finished, so the final text never comes. When the half-heard words already hold "Jarvis" and stay the same for a moment, they are sent as if they were final. */
    private long partialWait() { return wakeSens >= 3 ? 1200L : 1900L; }

    private void partialFire() {
        if (!on || !wake || barge || lastPartial.isEmpty()) return;
        String t = lastPartial;
        lastPartial = "";
        try { if (sr != null) sr.cancel(); } catch (Exception x) { /* gone already */ }
        js("onHeard", t);
        again(400);
    }

    private Intent listenIntent() {
        boolean bargeMode = barge;
        return (new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang).putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1).putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, bargeMode || (wake && wakeSens >= 2))
            .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, wake ? 1500L : quiet)  // Part 36: when you talk, Jarvis waits about 4 to 5 seconds of quiet before answering, like a person
            .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, wake ? 1500L : Math.max(1000L, quiet - 500L)));  // (some phone speech services ignore these two numbers)
    }

    /** Part 196: Hindi with no internet. Only for a normal mic tap (never Hey Jarvis or interrupt), only when the switch is on, the Hindi model is downloaded and "Speak" is Hindi. */
    private boolean offlineGo() {
        if (wake || barge || Privacy.stopped || !lang.toLowerCase().startsWith("hi")) return false;
        if (!act.getSharedPreferences("j", 0).getBoolean("off_hi", false) || !WakeEngine.hiReady(act)) return false;
        stop();
        if (ListenService.up) ListenService.halt(act);
        on = true;
        Privacy.used("mic");
        dict = new WakeEngine.Dictate();
        dict.start(act, 25, (t, err) -> ui.post(() -> {
            if (!on) return;  // stopped by you while it listened
            on = false;
            if (err != null) js("onHeardErr", err);
            else if (t.isEmpty()) js("onHeard", "");
            else js("onHeard", t);
        }));
        return true;
    }

    void stop() {
        on = false; barge = false; speaking = false; held.setLength(0); lastPartial = "";
        ui.removeCallbacksAndMessages(null);
        if (sr != null) { sr.destroy(); sr = null; }
        if (dict != null) { dict.stop(); dict = null; }  // Part 196
        unhush();  // Part 162
    }

    void js(String fn, String text) {
        web.evaluateJavascript("window." + fn + "&&" + fn + "(" + JSONObject.quote(text) + "," + wake + ")", null);
    }

    /** Listen again. The same recognizer is reused (cancel, then listen) because creating and destroying it every second makes some phone speech services disconnect (error 11). */
    void again(long ms) {
        ui.postDelayed(() -> {
            if (!on) return;
            if (sr == null) { retrying = true; start(lang, wake, barge); return; }
            try { sr.cancel(); hush(act, !barge); sr.startListening(listenIntent()); Privacy.used(wake ? "wake" : "mic"); beat = System.currentTimeMillis(); }
            catch (Exception x) { try { sr.destroy(); } catch (Exception y) { /* gone already */ } sr = null; retrying = true; start(lang, wake, barge); }
        }, ms);
    }

    /** Part 161: send everything heard so far as ONE sentence. */
    void flush() {
        ui.removeCallbacks(flushJob);
        String t = held.toString().trim();
        held.setLength(0);
        speaking = false;
        on = false;
        if (sr != null) { try { sr.cancel(); } catch (Exception x) { /* gone already */ } }
        js("onHeard", t);
    }

    @Override public void onResults(Bundle b) {
        boff = 0;
        beat = System.currentTimeMillis();
        ui.removeCallbacks(partialJob);
        lastPartial = "";
        ArrayList<String> r = b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        String t = r == null || r.isEmpty() ? "" : r.get(0).trim();
        if (wake) { js("onHeard", t); again(400); return; }
        speaking = false;
        if (t.isEmpty() && held.length() == 0) { on = false; js("onHeard", ""); return; }
        if (!t.isEmpty()) { if (held.length() > 0) held.append(' '); held.append(t); }
        long extra = Math.max(0L, quiet - 1300L);  // Part 161: the speech service already waited about 1.3 s of silence by itself; we wait the rest, and join what you say next
        if (endsOpen(held.toString())) extra += 3000L;  // Part 189: the sentence ends in a joining word (hum jo, aur, ki, to...): wait 3 more seconds for the rest
        if (extra < 150L) { flush(); return; }
        ui.removeCallbacks(flushJob);
        ui.postDelayed(flushJob, extra);
        again(150);
    }

    @Override public void onError(int e) {
        beat = System.currentTimeMillis();
        ui.removeCallbacks(partialJob);
        lastPartial = "";
        if (!on) return;
        boolean quiet = e == SpeechRecognizer.ERROR_NO_MATCH || e == SpeechRecognizer.ERROR_SPEECH_TIMEOUT || e == SpeechRecognizer.ERROR_RECOGNIZER_BUSY;
        if (held.length() > 0 && !wake) {  // Part 161: an error inside the waiting time must never lose the sentence you already said
            if (quiet && !speaking) { again(250); return; }
            flush();
            return;
        }
        if (wake && quiet) { again(e == SpeechRecognizer.ERROR_RECOGNIZER_BUSY ? 1500 : 300); return; }
        boolean net = e == SpeechRecognizer.ERROR_NETWORK || e == SpeechRecognizer.ERROR_NETWORK_TIMEOUT || e == SpeechRecognizer.ERROR_SERVER;  // Part 123: 1, 2, 4 = no internet for the phone speech service: try again, do not give up
        boolean soft = net || e == 11 || e == 10 || e == SpeechRecognizer.ERROR_CLIENT;  // 11 = speech service disconnected, 10 = too many requests, 5 = client
        if (net && offlineGo()) return;  // Part 196: no internet for the speech service: Hindi is heard on the phone itself, if you turned that on
        if (soft && fails < (net ? 8 : 4)) {  // Part 134: error 2 (no internet for the speech service) gets 8 tries, the pause grows up to 6 seconds  // a fresh recognizer after a short, growing pause; Jarvis shows nothing unless it keeps failing
            fails++;
            if (sr != null) { try { sr.destroy(); } catch (Exception x) { /* gone already */ } sr = null; }
            again(Math.min(1200L * fails, 6000L));
            return;
        }
        if (wake && e != SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) {  // Part 162: Hey Jarvis does not die on an error: a fresh recognizer after 3, 6, 12, 30, 60 s
            if (sr != null) { try { sr.destroy(); } catch (Exception x) { /* gone already */ } sr = null; }
            long[] gap = {3000L, 6000L, 12000L, 30000L, 60000L};
            again(gap[Math.min(boff++, 4)]);
            return;
        }
        if (!quiet && e != SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS && offlineGo()) return;  // Part 196: the speech service keeps failing
        on = false;
        js("onHeardErr", quiet ? "I did not hear anything" : e == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ? "allow the microphone permission for Jarvis"
            : net ? "the phone speech service has no internet right now (error " + e + "). Check Wi-Fi or mobile data, then tap the mic again"
            : soft ? "the phone speech service keeps disconnecting (error " + e + "). Update 'Speech Recognition & Synthesis' (Google) in Play Store or restart the phone, then tap the mic again"
            : "speech error " + e);
    }

    @Override public void onReadyForSpeech(Bundle p) { beat = System.currentTimeMillis(); }
    @Override public void onBeginningOfSpeech() {
        fails = 0; boff = 0; beat = System.currentTimeMillis();
        if (barge && !loud) voice();  // Part 160 (Part 164: not on the loudspeaker): the speech service's own start-of-speech also counts (a little slower than the level)
        if (held.length() > 0) { speaking = true; ui.removeCallbacks(flushJob); ui.postDelayed(flushJob, 12000L); }  // Part 161: you are talking again: keep the first part, add the next (12 s safety)
    }
    /** Part 160: while Jarvis speaks (interrupt mode) the page is told the moment your voice starts, from the mic LEVEL (about 0.1 to 0.2 s), before any word is known. The words follow later from the speech service. */
    @Override public void onRmsChanged(float v) {
        if (!barge || loud) { floor = 99f; hot = 0; return; }
        floor = Math.min(v, floor + 0.05f);
        hot = (v > floor + 3.5f && v > 2.5f) ? hot + 1 : 0;
        if (hot >= 2) voice();
    }

    private void voice() {
        long now = System.currentTimeMillis();
        if (now - lastVoice < 1500L) return;
        lastVoice = now;
        js("onVoice", "");
    }
    @Override public void onBufferReceived(byte[] b) { }
    @Override public void onEndOfSpeech() { }
    @Override public void onPartialResults(Bundle b) {
        ArrayList<String> r = b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        String p = r == null || r.isEmpty() ? "" : r.get(0).trim();
        if (p.isEmpty()) return;
        beat = System.currentTimeMillis();
        if (barge) { js("onPartial", p); return; }
        if (wake && wakeSens >= 2 && ListenService.WAKE.matcher(p).find()) {  // Part 191
            lastPartial = p;
            ui.removeCallbacks(partialJob);
            ui.postDelayed(partialJob, partialWait());
        }
    }

    /** Part 61: true when earphones are connected (wired, USB or Bluetooth). Interrupt works only then, because the mic would hear Jarvis' own voice from the speaker. */
    static boolean headset(Context c) {
        try {
            AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
            for (AudioDeviceInfo d : am.getDevices(AudioManager.GET_DEVICES_OUTPUTS)) {
                int t = d.getType();
                if (t == AudioDeviceInfo.TYPE_WIRED_HEADSET || t == AudioDeviceInfo.TYPE_WIRED_HEADPHONES || t == AudioDeviceInfo.TYPE_USB_HEADSET
                        || t == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP || t == AudioDeviceInfo.TYPE_BLUETOOTH_SCO) return true;
            }
        } catch (Exception x) { /* no answer means no earphones */ }
        return false;
    }
    @Override public void onEvent(int t, Bundle b) { }
}
