package com.hussain.jarvis;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.ServiceInfo;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import java.util.ArrayList;
import java.util.regex.Pattern;
import org.json.JSONObject;

/** Part 39: a TEST of "Hey Jarvis" with the app closed. Started only by your finger tap, always shows a notification with Stop,
 *  stops by itself after 8 hours. It only COUNTS how often it heard the word "Jarvis" (and if the screen was off). It never keeps
 *  what you said, never sends anything to the page or the server, and never does any phone action. */
public class ListenService extends Service implements RecognitionListener {
    static final String CH = "jarvis_listen", STOP = "com.hussain.jarvis.STOP_LISTEN";
    static final long MAX = 8L * 3600_000L;  // battery safety: the test ends by itself after 8 hours
    static final Pattern WAKE = Pattern.compile("jar ?vish|jar ?vis|jervis|jarvas|jarvice|jarves|jarwis|जार्विस|जारविस|जार्विश|जरवेस|जरवेश|जर्वेस|जर्विस|जरविस|जार्वेस|जारवेस|जरवीस|जार्विज|हिसारिस्ट", Pattern.CASE_INSENSITIVE);
    static volatile boolean up;
    final Handler ui = new Handler(Looper.getMainLooper());
    SpeechRecognizer sr;
    final WakeEngine eng = new WakeEngine();  // Part 40: offline engine (used only if the model is downloaded and you switched it on)
    boolean vosk;
    SharedPreferences sp;
    long began;
    int bad;
    boolean lowBatt;  // Part 166: true while the listening is paused because the battery is low
    String why = "stopped by you";

    static void halt(Context c) { c.stopService(new Intent(c, ListenService.class)); }

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public int onStartCommand(Intent i, int flags, int id) {
        if (i != null && STOP.equals(i.getAction())) { stopSelf(); return START_NOT_STICKY; }
        Privacy.init(this);
        sp = getSharedPreferences("j", 0);
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CH, "Jarvis background listening", NotificationManager.IMPORTANCE_LOW));
        try {  // must be called within seconds of startForegroundService
            Notification n = note("Listening for \"Hey Jarvis\" (test). Tap Stop to end.");
            if (Build.VERSION.SDK_INT >= 30) startForeground(79, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
            else startForeground(79, n);
        } catch (Exception e) {
            sp.edit().putString("bg_err", "Android refused the microphone service").apply();
            stopSelf();
            return START_NOT_STICKY;
        }
        if (up) return START_NOT_STICKY;  // already running
        vosk = sp.getBoolean("wk_vosk", false) && WakeEngine.ready(this);
        if (Privacy.stopped || (!vosk && !SpeechRecognizer.isRecognitionAvailable(this))) {
            sp.edit().putString("bg_err", Privacy.stopped ? "Jarvis is stopped" : "this phone has no speech service").apply();
            stopSelf();
            return START_NOT_STICKY;
        }
        up = true;
        began = System.currentTimeMillis();
        sp.edit().putLong("bg_since", began).putInt("bg_hits", 0).putInt("bg_off", 0).putInt("bg_bg", 0).putLong("bg_last", 0)
            .putString("bg_err", "").putLong("bg_ended", 0).apply();
        Privacy.used("bg");
        sp.edit().putString("bg_eng", vosk ? "offline" : "google").apply();
        sp.edit().putString("bg_batt", "").apply();
        lowBatt = false;
        begin();
        ui.postDelayed(guard, 60000);  // Part 166
        return START_NOT_STICKY;  // not restarted by Android: Stop stays stopped
    }

    /** Starts the listener (the offline engine or the phone's speech service). Also used again when the battery is back. */
    void begin() {
        if (vosk) eng.start(this, new WakeEngine.Cb() {
            public void heard() { ui.post(() -> hit()); }
            public void failed(String m) { ui.post(() -> { why = m; sp.edit().putString("bg_err", m).apply(); stopSelf(); }); }
        });
        else listen();
    }

    // ---- Part 166: battery guard. Below 15% and not charging the background mic stops and says so ONCE. It starts again at 20% or when a charger is plugged in. ----
    final Runnable guard = new Runnable() {
        @Override public void run() {
            if (!up) return;
            battCheck();
            ui.postDelayed(this, lowBatt ? 30000 : 60000);
        }
    };

    /** {percent, 1 if charging}. If Android gives nothing we assume a full battery, so the mic is never stopped by mistake. */
    int[] battery() {
        try {
            Intent b = registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            if (b == null) return new int[]{100, 1};
            int lv = b.getIntExtra(BatteryManager.EXTRA_LEVEL, 100), sc = b.getIntExtra(BatteryManager.EXTRA_SCALE, 100);
            return new int[]{sc > 0 ? lv * 100 / sc : 100, b.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0) != 0 ? 1 : 0};
        } catch (Exception e) { return new int[]{100, 1}; }
    }

    void battCheck() {
        int[] b = battery();
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (!lowBatt && b[0] < 15 && b[1] == 0) {
            lowBatt = true;
            eng.stop();
            if (sr != null) { sr.destroy(); sr = null; }
            sp.edit().putString("bg_batt", "paused").apply();
            nm.notify(79, note("Battery is " + b[0] + "%, so the background mic is paused. It starts again at 20% or on the charger. Tap Stop to end."));
        } else if (lowBatt && (b[0] >= 20 || b[1] == 1)) {
            lowBatt = false;
            sp.edit().putString("bg_batt", "").apply();
            nm.notify(79, note("Battery is back. Listening for \"Hey Jarvis\" again. Tap Stop to end."));
            begin();
        }
    }

    Notification note(String text) {
        PendingIntent open = PendingIntent.getActivity(this, 1, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        PendingIntent stop = PendingIntent.getService(this, 2, new Intent(this, ListenService.class).setAction(STOP), PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, CH).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis is listening (test)")
            .setContentText(text).setOngoing(true).setContentIntent(open).addAction(android.R.drawable.ic_media_pause, "Stop", stop).build();
    }

    void listen() {
        if (!up || lowBatt) return;  // Part 166: nothing starts while the battery guard has paused the mic
        if (Privacy.stopped) { why = "Jarvis was stopped"; stopSelf(); return; }
        if (System.currentTimeMillis() - began > MAX) { why = "8 h limit reached"; stopSelf(); return; }
        try {
            if (sr != null) sr.destroy();
            sr = SpeechRecognizer.createSpeechRecognizer(this);
            sr.setRecognitionListener(this);
            Ears.hush(this, true);  // Part 162: no restart beep
            sr.startListening(new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN").putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
                .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 1500L)
                .putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 1500L));
        } catch (Exception e) { fail("speech start failed"); }
    }

    void again(long ms) { ui.postDelayed(this::listen, ms); }

    /** Turns the screen on for a few seconds, exactly like a power-button press. The lock screen (fingerprint/pattern/PIN)
     *  still shows and still has to be opened by the person - this never skips or touches that. */
    @SuppressWarnings("deprecation")
    private void wakeScreen() {
        try {
            PowerManager pm = getSystemService(PowerManager.class);
            PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP, "Jarvis:heard");
            wl.acquire(4000);
        } catch (Exception e) { /* some phones restrict this; the notification still works either way */ }
    }

    void fail(String m) {
        sp.edit().putString("bg_err", m).apply();
        long[] gap = {3000L, 6000L, 12000L, 30000L, 60000L};  // Part 162: an error never ends the mic (only Stop or the 8 h limit): the pause grows 3, 6, 12, 30, 60 s
        again(gap[Math.min(bad++, 4)]);
    }

    /** One "Jarvis" was heard. Counts it (numbers only). With the offline engine it also acts: on screen it opens the mic; otherwise a notification says "Tap to talk". */
    void hit() {
        boolean off = !getSystemService(PowerManager.class).isInteractive();
        if (off) wakeScreen();  // Part 73: same as pressing the power button - shows the (locked) screen, does NOT unlock it
        long now = System.currentTimeMillis();
        sp.edit().putInt("bg_hits", sp.getInt("bg_hits", 0) + 1).putLong("bg_last", now)
            .putInt("bg_off", sp.getInt("bg_off", 0) + (off ? 1 : 0)).putInt("bg_bg", sp.getInt("bg_bg", 0) + (MainActivity.visible ? 0 : 1)).apply();
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.notify(79, note("Heard \"Jarvis\" " + sp.getInt("bg_hits", 0) + " time(s). Tap Stop to end."));
        if (!vosk || Privacy.stopped) return;
        MainActivity m = MainActivity.cur;
        if (MainActivity.visible && m != null) { m.runOnUiThread(m::wakeTalk); return; }
        nm.createNotificationChannel(new NotificationChannel("jarvis_wake", "Jarvis heard you", NotificationManager.IMPORTANCE_HIGH));
        PendingIntent go = PendingIntent.getActivity(this, 3, new Intent(this, MainActivity.class).setAction(MainActivity.CONVERSE), PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);  // Part 135: Conversation, not one question
        nm.notify(80, new Notification.Builder(this, "jarvis_wake").setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis heard you")
            .setContentText("Tap to start a conversation").setAutoCancel(true).setTimeoutAfter(15000).setContentIntent(go).build());
    }

    @Override public void onResults(Bundle b) {
        bad = 0;
        ArrayList<String> r = b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        if (r != null && !r.isEmpty() && WAKE.matcher(r.get(0)).find()) hit();  // only a yes/no is used; the words are dropped here
        again(400);
    }

    @Override public void onError(int e) {
        if (!up) return;
        if (e == SpeechRecognizer.ERROR_NO_MATCH || e == SpeechRecognizer.ERROR_SPEECH_TIMEOUT) { bad = 0; again(300); return; }
        if (e == SpeechRecognizer.ERROR_RECOGNIZER_BUSY) { again(1500); return; }
        if (e == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) { why = "microphone permission missing"; sp.edit().putString("bg_err", why).apply(); stopSelf(); return; }
        fail("speech error " + e);
    }

    @Override public void onDestroy() {
        up = false;
        if (Privacy.stopped) why = "Jarvis was stopped";
        ui.removeCallbacksAndMessages(null);
        eng.stop();
        if (sr != null) { sr.destroy(); sr = null; }
        Ears.unhush();  // Part 162
        if (sp != null) sp.edit().putLong("bg_since", 0).putLong("bg_ended", System.currentTimeMillis()).putString("bg_why", why).apply();
        stopForeground(true);
        super.onDestroy();
    }

    /** For the page: what the test found. since > 0 and up == false means Android killed the service. Numbers only, no words you said. */
    static String info(Context c) {
        SharedPreferences sp = c.getSharedPreferences("j", 0);
        JSONObject o = new JSONObject();
        try {
            long since = sp.getLong("bg_since", 0);
            o.put("up", up).put("since", since).put("killed", since > 0 && !up).put("hits", sp.getInt("bg_hits", 0)).put("off", sp.getInt("bg_off", 0))
                .put("bg", sp.getInt("bg_bg", 0)).put("last", sp.getLong("bg_last", 0)).put("err", sp.getString("bg_err", "")).put("ended", sp.getLong("bg_ended", 0))
                .put("batt", sp.getString("bg_batt", "")).put("why", sp.getString("bg_why", "")).put("eng", sp.getString("bg_eng", "")).put("phone", Build.MANUFACTURER + " " + Build.MODEL).put("android", Build.VERSION.RELEASE)
                .put("battery_ok", c.getSystemService(PowerManager.class).isIgnoringBatteryOptimizations(c.getPackageName()))
                .put("notif", c.getSystemService(NotificationManager.class).areNotificationsEnabled());
        } catch (Exception e) { /* send what we have */ }
        return o.toString();
    }

    @Override public void onReadyForSpeech(Bundle p) { }
    @Override public void onBeginningOfSpeech() { }
    @Override public void onRmsChanged(float v) { }
    @Override public void onBufferReceived(byte[] b) { }
    @Override public void onEndOfSpeech() { }
    @Override public void onPartialResults(Bundle b) { }
    @Override public void onEvent(int t, Bundle b) { }
}
