package com.hussain.jarvis;

import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.webkit.WebView;
import java.util.Locale;

/** Part 193: the phone's OWN voice (Android text-to-speech). It is the last voice in the backup order:
 *  saved Sarvam audio, Sarvam, Edge (only if you allow it), then this one. The page asks for it only when the online voices failed.
 *  Nothing is kept: the sentence is spoken and forgotten. When it is done (or cannot speak) the page is told through window.onPhoneSpoken(true or false),
 *  so Conversation and Always listening go on listening. Everything here runs on the main thread. */
final class PhoneVoice implements TextToSpeech.OnInitListener {
    private final Context app;
    private final WebView web;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private TextToSpeech tts;
    private boolean ready, failed;
    private String waitText;      // the sentence that arrived while the engine was still starting
    private float waitPitch = 1f, waitRate = 1f;
    private String cur = "";      // id of the sentence that is spoken now; an old one that was stopped is ignored
    private int n;

    PhoneVoice(Context c, WebView w) { app = c.getApplicationContext(); web = w; }

    void speak(String text, float pitch, float rate) {
        stop();
        if (text == null || text.trim().isEmpty()) { done(true); return; }
        if (failed) { done(false); return; }
        waitText = text;
        waitPitch = Math.max(0.5f, Math.min(1.5f, pitch));
        waitRate = Math.max(0.6f, Math.min(1.4f, rate));
        if (tts == null) { tts = new TextToSpeech(app, this); return; }  // onInit speaks the waiting sentence
        if (ready) go();
    }

    @Override public void onInit(int status) {
        ui.post(() -> {
            if (status != TextToSpeech.SUCCESS) { failed = true; ready = false; waitText = null; done(false); return; }
            ready = true;
            tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
                @Override public void onStart(String id) { }
                @Override public void onDone(String id) { ui.post(() -> finished(id, true)); }
                @Override public void onError(String id) { ui.post(() -> finished(id, false)); }
                @Override public void onError(String id, int code) { ui.post(() -> finished(id, false)); }
            });
            go();
        });
    }

    private void go() {
        if (tts == null || !ready || waitText == null) return;
        String t = waitText;
        waitText = null;
        boolean deva = false;
        for (int i = 0; i < t.length(); i++) { char ch = t.charAt(i); if (ch >= '\u0900' && ch <= '\u097F') { deva = true; break; } }
        Locale loc = deva ? new Locale("hi", "IN") : new Locale("en", "IN");
        int r = tts.setLanguage(loc);
        if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) {
            if (deva) { done(false); return; }  // no Hindi voice installed: reading Hindi letters in an English voice would be nonsense, so the text stays on the screen
            r = tts.setLanguage(Locale.ENGLISH);
            if (r == TextToSpeech.LANG_MISSING_DATA || r == TextToSpeech.LANG_NOT_SUPPORTED) { done(false); return; }
        }
        int max = TextToSpeech.getMaxSpeechInputLength();
        if (t.length() > max) t = t.substring(0, max);
        tts.setPitch(waitPitch);
        tts.setSpeechRate(waitRate);
        cur = "pv" + (++n);
        int ok = tts.speak(t, TextToSpeech.QUEUE_FLUSH, new Bundle(), cur);
        if (ok != TextToSpeech.SUCCESS) { cur = ""; done(false); }
    }

    private void finished(String id, boolean ok) {
        if (id == null || !id.equals(cur)) return;
        cur = "";
        done(ok);
    }

    /** Stops the voice. The page is NOT told (the page itself asked for the stop). */
    void stop() {
        waitText = null;
        cur = "";
        try { if (tts != null && ready) tts.stop(); } catch (Exception e) { /* nothing is speaking */ }
    }

    private void done(boolean ok) {
        web.evaluateJavascript("window.onPhoneSpoken&&onPhoneSpoken(" + ok + ")", null);
    }
}
