package com.hussain.jarvis;

import android.Manifest;
import android.app.NotificationManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import java.util.HashMap;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 28: one place that knows if Jarvis is stopped. Stop is kept in Java and saved, so the page, a voice command or a restart cannot switch listening back on. */
final class Privacy {
    static final Handler UI = new Handler(Looper.getMainLooper());
    static volatile boolean stopped;
    static volatile boolean control;  // Part 30: master switch "Phone control". OFF by default, saved.
    static volatile Runnable screenJob;  // the 6 second wait before the screen is read
    static volatile Runnable actJob;  // Part 34: the short wait before a screen step runs. Stop cancels it.
    private static SharedPreferences sp;
    private static final HashMap<String, Long> LAST = new HashMap<>();

    static void init(Context c) {
        sp = c.getSharedPreferences("j", 0);
        stopped = sp.getBoolean("stopped", false);
        control = sp.getBoolean("control", false);
    }

    private static void save() { if (sp != null) sp.edit().putBoolean("stopped", stopped).putBoolean("control", control).apply(); }

    /** What is really active right now, from Java (not from what the page thinks). */
    static JSONObject state(MainActivity a) {
        JSONObject o = new JSONObject();
        try {
            Ears e = a.ears;
            boolean on = e != null && e.on;
            o.put("stopped", stopped).put("control", control).put("mic", on && !e.wake).put("wake", on && e.wake)
                .put("screen", screenJob != null).put("camera", a.picker != null).put("bg", ListenService.up).put("task", TaskRunner.running);
        } catch (Exception x) { /* send what we have */ }
        return o;
    }

    /** Called from the bridge thread. Returns what WAS active; the switching off runs on the main thread. */
    static String stopAll(MainActivity a) {
        JSONObject was = state(a);
        event(a, "stop");
        stopped = true;
        control = false;  // Stop also switches phone control OFF; it must be turned on again by a finger tap
        save();
        a.runOnUiThread(() -> {
            if (a.ears != null) a.ears.stop();
            ListenService.halt(a);  // Part 39: the background listening test also ends
            TaskRunner.abort(a);  // Part 42: a running task ends at once
            MainActivity.pendingTask = null;
            a.getSystemService(NotificationManager.class).cancel(79);
            if (screenJob != null) { UI.removeCallbacks(screenJob); screenJob = null; }
            if (actJob != null) { UI.removeCallbacks(actJob); actJob = null; }
            MainActivity.pending = null;
            MainActivity.pendingAct = null;
            a.getSystemService(NotificationManager.class).cancel(78);
            a.getSystemService(NotificationManager.class).cancel(77);
            if (a.picker != null) { a.picker.onReceiveValue(null); a.picker = null; }
        });
        return was.toString();
    }

    /** Part 29: remember that a feature was used (name and time only, never content). Logged at most once a minute per feature. */
    static synchronized void used(String id) {
        if (sp == null) return;
        long now = System.currentTimeMillis();
        Long prev = LAST.get(id);
        if (prev == null) prev = sp.getLong("last_" + id, 0);
        if (now - prev < 60000) return;
        LAST.put(id, now);
        String[] old = (sp.getString("plog", "") + id + "|" + now + "\n").split("\n");
        StringBuilder sb = new StringBuilder();
        for (int i = Math.max(0, old.length - 200); i < old.length; i++) sb.append(old[i]).append('\n');  // Part 78: last 200 uses (was 30), for the timeline
        sp.edit().putLong("last_" + id, now).putString("plog", sb.toString()).apply();
    }

    /** Part 78: rare events for the timeline (stop, phone control on/off, paused for payment app). Name and time only, never content, not throttled. */
    static synchronized void event(Context c, String id) {
        if (sp == null) sp = c.getSharedPreferences("j", 0);
        String[] old = (sp.getString("plog", "") + id + "|" + System.currentTimeMillis() + "\n").split("\n");
        StringBuilder sb = new StringBuilder();
        for (int i = Math.max(0, old.length - 200); i < old.length; i++) sb.append(old[i]).append('\n');
        sp.edit().putString("plog", sb.toString()).apply();
    }

    private static int has(Context c, String perm) { return c.checkSelfPermission(perm) == PackageManager.PERMISSION_GRANTED ? 1 : 0; }

    /** Part 29: for the dashboard. perm: 1 allowed, 0 not allowed, -1 none needed. run: is it active this second. last: when it was last used. */
    static String dashboard(MainActivity a) {
        JSONObject o = new JSONObject();
        try {
            JSONObject s = state(a), p = new JSONObject(), r = new JSONObject(), l = new JSONObject();
            int mic = has(a, Manifest.permission.RECORD_AUDIO);
            p.put("mic", mic).put("wake", mic).put("bg", mic).put("camera", -1).put("screen", ScreenService.live != null ? 1 : 0)
                .put("location", has(a, Manifest.permission.ACCESS_FINE_LOCATION)).put("contacts", has(a, Manifest.permission.READ_CONTACTS))
                .put("calls", has(a, Manifest.permission.READ_CALL_LOG)).put("calendar", has(a, Manifest.permission.READ_CALENDAR)).put("apps", -1)
                .put("place", has(a, Manifest.permission.ACCESS_FINE_LOCATION)).put("usage", UsageWatch.allowed(a) ? 1 : 0).put("callnote", CallNote.allowed(a) ? 1 : 0)
                .put("notify", a.getSystemService(NotificationManager.class).areNotificationsEnabled() ? 1 : 0)
                .put("battery", a.getSystemService(PowerManager.class).isIgnoringBatteryOptimizations(a.getPackageName()) ? 1 : 0);
            r.put("mic", s.getBoolean("mic")).put("wake", s.getBoolean("wake")).put("camera", s.getBoolean("camera"))
                .put("screen", s.getBoolean("screen")).put("notify", NotifyService.up).put("bg", s.getBoolean("bg")).put("place", PlaceWatch.up).put("usage", UsageWatch.up).put("callnote", CallNote.on(a));
            for (String id : new String[]{"mic", "wake", "bg", "camera", "screen", "location", "contacts", "calls", "calendar", "notify", "place", "usage", "callnote", "apps"}) l.put(id, sp == null ? 0 : sp.getLong("last_" + id, 0));
            JSONArray log = new JSONArray();
            for (String line : (sp == null ? "" : sp.getString("plog", "")).split("\n")) {
                String[] x = line.split("\\|");
                if (x.length == 2) log.put(new JSONArray().put(x[0]).put(Long.parseLong(x[1])));
            }
            o.put("stopped", stopped).put("control", control).put("perm", p).put("run", r).put("last", l).put("log", log);
        } catch (Exception e) { /* send what we have */ }
        return o.toString();
    }

    /** Part 30: OFF always works. ON only after a real finger tap in the last 3 seconds, and never while Jarvis is stopped. */
    static String setControl(boolean on) {
        if (on && (stopped || System.currentTimeMillis() - MainActivity.touch > 3000)) return "{\"ok\":false,\"control\":" + control + "}";
        if (control != on && sp != null) event(null, on ? "ctl_on" : "ctl_off");
        control = on;
        save();
        return "{\"ok\":true,\"control\":" + control + "}";
    }

    /** Only a real finger tap on the screen in the last 3 seconds can switch Jarvis on again. */
    static boolean restart() {
        if (System.currentTimeMillis() - MainActivity.touch > 3000) return false;
        stopped = false;
        save();
        return true;
    }
}
