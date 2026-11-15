package com.hussain.jarvis;

import android.app.NotificationManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Looper;
import org.json.JSONObject;

/** Part 28: one place that knows if Jarvis is stopped. Stop is kept in Java and saved, so the page, a voice command or a restart cannot switch listening back on. */
final class Privacy {
    static final Handler UI = new Handler(Looper.getMainLooper());
    static volatile boolean stopped;
    static volatile Runnable screenJob;  // the 6 second wait before the screen is read
    private static SharedPreferences sp;

    static void init(Context c) {
        sp = c.getSharedPreferences("j", 0);
        stopped = sp.getBoolean("stopped", false);
    }

    private static void save() { if (sp != null) sp.edit().putBoolean("stopped", stopped).apply(); }

    /** What is really active right now, from Java (not from what the page thinks). */
    static JSONObject state(MainActivity a) {
        JSONObject o = new JSONObject();
        try {
            Ears e = a.ears;
            boolean on = e != null && e.on;
            o.put("stopped", stopped).put("mic", on && !e.wake).put("wake", on && e.wake)
                .put("screen", screenJob != null).put("camera", a.picker != null);
        } catch (Exception x) { /* send what we have */ }
        return o;
    }

    /** Called from the bridge thread. Returns what WAS active; the switching off runs on the main thread. */
    static String stopAll(MainActivity a) {
        JSONObject was = state(a);
        stopped = true;
        save();
        a.runOnUiThread(() -> {
            if (a.ears != null) a.ears.stop();
            if (screenJob != null) { UI.removeCallbacks(screenJob); screenJob = null; }
            MainActivity.pending = null;
            a.getSystemService(NotificationManager.class).cancel(77);
            if (a.picker != null) { a.picker.onReceiveValue(null); a.picker = null; }
        });
        return was.toString();
    }

    /** Only a real finger tap on the screen in the last 3 seconds can switch Jarvis on again. */
    static boolean restart() {
        if (System.currentTimeMillis() - MainActivity.touch > 3000) return false;
        stopped = false;
        save();
        return true;
    }
}
