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
    int fails;           // soft errors in a row (speech service disconnected); reset when you actually speak
    boolean retrying;    // true when again() calls start(), so the counter is not reset by our own retry
    volatile boolean wake, on, barge;  // barge (Part 61): listening WHILE Jarvis speaks, partial words go to the page so it can stop talking

    Ears(Activity a, WebView w) { act = a; web = w; }

    /** Main thread only. wakeMode: keep listening again and again, and the page looks for "Hey Jarvis". */
    void start(String l, boolean wakeMode) { start(l, wakeMode, false); }

    void start(String l, boolean wakeMode, boolean bargeMode) {
        stop();
        if (!retrying) fails = 0;
        retrying = false;
        if (Privacy.stopped) { js("onHeardErr", "Jarvis is stopped. Tap Turn mic on first"); return; }
        if (!SpeechRecognizer.isRecognitionAvailable(act)) { js("onHeardErr", "this phone has no speech service"); return; }
        if (ListenService.up) ListenService.halt(act);  // Part 39: only one listener at a time; opening the mic here ends the background test
        lang = l; wake = wakeMode; on = true; barge = bargeMode;
        sr = SpeechRecognizer.createSpeechRecognizer(act);
        sr.setRecognitionListener(this);
        sr.startListening(listenIntent());
        Privacy.used(wake ? "wake" : "mic");
    }

    private Intent listenIntent() {
        boolean bargeMode = barge;
        return (new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang).putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1).putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, bargeMode)
            .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, wake ? 1500L : 4500L)  // Part 36: when you talk, Jarvis waits about 4 to 5 seconds of quiet before answering, like a person
            .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, wake ? 1500L : 4000L));  // (some phone speech services ignore these two numbers)
    }

    void stop() {
        on = false; barge = false;
        ui.removeCallbacksAndMessages(null);
        if (sr != null) { sr.destroy(); sr = null; }
    }

    void js(String fn, String text) {
        web.evaluateJavascript("window." + fn + "&&" + fn + "(" + JSONObject.quote(text) + "," + wake + ")", null);
    }

    /** Listen again. The same recognizer is reused (cancel, then listen) because creating and destroying it every second makes some phone speech services disconnect (error 11). */
    void again(long ms) {
        ui.postDelayed(() -> {
            if (!on) return;
            if (sr == null) { retrying = true; start(lang, wake, barge); return; }
            try { sr.cancel(); sr.startListening(listenIntent()); Privacy.used(wake ? "wake" : "mic"); }
            catch (Exception x) { try { sr.destroy(); } catch (Exception y) { /* gone already */ } sr = null; retrying = true; start(lang, wake, barge); }
        }, ms);
    }

    @Override public void onResults(Bundle b) {
        ArrayList<String> r = b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        boolean w = wake;
        if (!w) on = false;
        js("onHeard", r == null || r.isEmpty() ? "" : r.get(0));
        if (w) again(400);
    }

    @Override public void onError(int e) {
        if (!on) return;
        boolean quiet = e == SpeechRecognizer.ERROR_NO_MATCH || e == SpeechRecognizer.ERROR_SPEECH_TIMEOUT || e == SpeechRecognizer.ERROR_RECOGNIZER_BUSY;
        if (wake && quiet) { again(e == SpeechRecognizer.ERROR_RECOGNIZER_BUSY ? 1500 : 300); return; }
        boolean net = e == SpeechRecognizer.ERROR_NETWORK || e == SpeechRecognizer.ERROR_NETWORK_TIMEOUT || e == SpeechRecognizer.ERROR_SERVER;  // Part 123: 1, 2, 4 = no internet for the phone speech service: try again, do not give up
        boolean soft = net || e == 11 || e == 10 || e == SpeechRecognizer.ERROR_CLIENT;  // 11 = speech service disconnected, 10 = too many requests, 5 = client
        if (soft && fails < (net ? 6 : 4)) {  // a fresh recognizer after a short, growing pause; Jarvis shows nothing unless it keeps failing
            fails++;
            if (sr != null) { try { sr.destroy(); } catch (Exception x) { /* gone already */ } sr = null; }
            again(1200L * fails);
            return;
        }
        on = false;
        js("onHeardErr", quiet ? "I did not hear anything" : e == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ? "allow the microphone permission for Jarvis"
            : net ? "the phone speech service has no internet right now (error " + e + "). Check Wi-Fi or mobile data, then tap the mic again"
            : soft ? "the phone speech service keeps disconnecting (error " + e + "). Update 'Speech Recognition & Synthesis' (Google) in Play Store or restart the phone, then tap the mic again"
            : "speech error " + e);
    }

    @Override public void onReadyForSpeech(Bundle p) { }
    @Override public void onBeginningOfSpeech() { fails = 0; }
    @Override public void onRmsChanged(float v) { }
    @Override public void onBufferReceived(byte[] b) { }
    @Override public void onEndOfSpeech() { }
    @Override public void onPartialResults(Bundle b) {
        if (!barge) return;
        ArrayList<String> r = b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        if (r != null && !r.isEmpty() && !r.get(0).trim().isEmpty()) js("onPartial", r.get(0));
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
