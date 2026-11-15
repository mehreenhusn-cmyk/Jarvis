package com.hussain.jarvis;

import android.app.Activity;
import android.content.Intent;
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
    volatile boolean wake, on;

    Ears(Activity a, WebView w) { act = a; web = w; }

    /** Main thread only. wakeMode: keep listening again and again, and the page looks for "Hey Jarvis". */
    void start(String l, boolean wakeMode) {
        stop();
        if (Privacy.stopped) { js("onHeardErr", "Jarvis is stopped. Tap Turn mic on first"); return; }
        if (!SpeechRecognizer.isRecognitionAvailable(act)) { js("onHeardErr", "this phone has no speech service"); return; }
        if (ListenService.up) ListenService.halt(act);  // Part 39: only one listener at a time; opening the mic here ends the background test
        lang = l; wake = wakeMode; on = true;
        sr = SpeechRecognizer.createSpeechRecognizer(act);
        sr.setRecognitionListener(this);
        sr.startListening(new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang).putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, wake ? 1500L : 4500L)  // Part 36: when you talk, Jarvis waits about 4 to 5 seconds of quiet before answering, like a person
            .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, wake ? 1500L : 4000L));  // (some phone speech services ignore these two numbers)
        Privacy.used(wake ? "wake" : "mic");
    }

    void stop() {
        on = false;
        ui.removeCallbacksAndMessages(null);
        if (sr != null) { sr.destroy(); sr = null; }
    }

    void js(String fn, String text) {
        web.evaluateJavascript("window." + fn + "&&" + fn + "(" + JSONObject.quote(text) + "," + wake + ")", null);
    }

    void again(long ms) { ui.postDelayed(() -> { if (on) start(lang, wake); }, ms); }

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
        on = false;
        js("onHeardErr", quiet ? "I did not hear anything" : e == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ? "allow the microphone permission for Jarvis" : "speech error " + e);
    }

    @Override public void onReadyForSpeech(Bundle p) { }
    @Override public void onBeginningOfSpeech() { }
    @Override public void onRmsChanged(float v) { }
    @Override public void onBufferReceived(byte[] b) { }
    @Override public void onEndOfSpeech() { }
    @Override public void onPartialResults(Bundle b) { }
    @Override public void onEvent(int t, Bundle b) { }
}
