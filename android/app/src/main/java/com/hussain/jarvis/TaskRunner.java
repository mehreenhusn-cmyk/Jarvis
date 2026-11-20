package com.hussain.jarvis;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.provider.Settings;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.Arrays;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 42: runs a Part 41 task (up to 6 steps) one step at a time, here in Java, because Jarvis is in the background while the other app is on screen.
 *  Before EVERY step it checks Stop, the Phone control switch, the app lock and Cancel. After every step it checks the step really did something,
 *  and it stops at the first step that failed. It never confirms anything for you: a step that needs your Yes simply fails here, and nothing is typed. */
final class TaskRunner {
    private TaskRunner() {}

    static final String CANCEL = "com.hussain.jarvis.TASK_CANCEL", CH = "jarvis_task";
    static final List<String> OK = Arrays.asList("open_app", "back", "home", "scroll", "click", "torch", "volume", "settings", "current_app", "lock", "wait");  // Part 187: wait = pause
    static final List<String> SCREEN = Arrays.asList("back", "home", "scroll", "click", "current_app", "lock");
    static volatile boolean running, cancel;
    private static int id;
    private static JSONArray res = new JSONArray();

    static JSONObject r(boolean ok, String err) { return ScreenService.r(ok, err); }

    /** From the bridge thread. {ok:true} = started; {ok:false, err} = nothing was done. */
    static String start(MainActivity a, String json) {
        try {
            if (AppLock.locked()) return r(false, "locked").toString();
            if (Privacy.stopped) return r(false, "stopped").toString();
            if (!Privacy.control) return r(false, "off").toString();
            if (running) return r(false, "busy").toString();
            JSONObject t = new JSONObject(json);
            JSONArray steps = t.getJSONArray("steps");
            boolean screen = false;
            if (steps.length() < 1 || steps.length() > 6) return r(false, "bad_plan").toString();
            for (int i = 0; i < steps.length(); i++) {
                String ty = steps.getJSONObject(i).optString("type");
                if (!OK.contains(ty) || ("lock".equals(ty) && i < steps.length() - 1)) return r(false, "bad_plan").toString();
                screen |= SCREEN.contains(ty);
            }
            if (screen && ScreenService.live == null) {
                a.runOnUiThread(() -> a.startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
                return r(false, "perm").toString();
            }
            running = true;
            cancel = false;
            id = t.optInt("id");
            res = new JSONArray();
            Privacy.used("apps");
            a.runOnUiThread(() -> {
                note(a, "Jarvis is running your task", "Tap Cancel to stop it.", true);
                if (!"open_app".equals(steps.optJSONObject(0).optString("type"))) a.moveTaskToBack(true);  // the other app must be on the screen; opening an app does that by itself
                Privacy.UI.postDelayed(() -> next(a, steps, 0), 1200);
            });
            return r(true, null).toString();
        } catch (Exception e) { return r(false, "bad_plan").toString(); }
    }

    static boolean alive() { return running && !cancel && !Privacy.stopped && Privacy.control && !AppLock.locked(); }

    /** Stop everything: the task ends at once and nothing is handed to the page. */
    static void abort(MainActivity a) {
        running = false;
        cancel = true;
        a.getSystemService(NotificationManager.class).cancel(80);
        a.getSystemService(NotificationManager.class).cancel(81);
    }

    static void next(MainActivity a, JSONArray steps, int i) {
        if (!running) return;  // aborted by Stop everything
        if (!alive()) { finish(a); return; }
        if (i >= steps.length()) { finish(a); return; }
        JSONObject st = steps.optJSONObject(i);
        String ty = st == null ? "" : st.optString("type");
        ScreenService.Done done = x -> {
            if (!running) return;
            boolean changed = !x.has("changed") || x.optBoolean("changed");
            if (x.optBoolean("ok") && !changed) { x = r(false, "no_change"); }  // it said OK but nothing on the screen moved: that is not success
            res.put(x);
            if (!x.optBoolean("ok")) { finish(a); return; }
            Privacy.UI.postDelayed(() -> next(a, steps, i + 1), "open_app".equals(ty) ? 600 : 1000);
        };
        try {
            if ("wait".equals(ty)) {  // Part 187: a pause of 1 to 30 seconds; Stop and Cancel are checked again by next() when it ends
                int sec = Math.max(1, Math.min(30, st.optInt("sec", 1)));
                Privacy.UI.postDelayed(() -> done.got(r(true, null)), sec * 1000L);
                return;
            }
            if (SCREEN.contains(ty)) { ScreenService.act(st, false, done); return; }  // false = no step here is ever "confirmed"; a risky button fails with need_yes
            if ("open_app".equals(ty)) {
                JSONObject o = Apps.open(a, st.optString("name"), false);
                if (!o.optBoolean("ok")) { done.got(r(false, o.has("ask") ? "many_app" : "app_missing")); return; }
                Privacy.UI.postDelayed(() -> {  // check the app really came to the front (not Jarvis itself)
                    ScreenService s = ScreenService.live;
                    AccessibilityNodeInfo root = s == null ? null : s.getRootInActiveWindow();
                    boolean front = root == null || !String.valueOf(root.getPackageName()).equals(a.getPackageName());
                    done.got(front ? o : r(false, "not_opened"));
                }, 1800);
                return;
            }
            done.got(PhoneSettings.run(a, st));  // settings page, flashlight, volume: Android answers at once
        } catch (Exception e) { done.got(r(false, "unknown")); }
    }

    static void finish(MainActivity a) {
        boolean wasCancelled = cancel || Privacy.stopped;
        running = false;
        try {
            JSONObject o = new JSONObject().put("id", id).put("cancelled", wasCancelled).put("results", res);
            MainActivity.pendingTask = o.toString();
        } catch (Exception e) { return; }
        NotificationManager nm = a.getSystemService(NotificationManager.class);
        nm.cancel(80);
        note(a, wasCancelled ? "Jarvis stopped your task" : "Jarvis finished your task", "Tap to see the result", false);
        a.runOnUiThread(() -> { if (MainActivity.visible && !AppLock.locked()) a.deliverTask(); });
    }

    /** One notification while the task runs (with Cancel) and one when it ends. Texts never contain what is on your screen. */
    static void note(MainActivity a, String title, String text, boolean ongoing) {
        NotificationManager nm = a.getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CH, "Jarvis tasks", NotificationManager.IMPORTANCE_LOW));
        PendingIntent open = PendingIntent.getActivity(a, 4, new Intent(a, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = new Notification.Builder(a, CH).setSmallIcon(android.R.drawable.ic_popup_reminder).setContentTitle(title).setContentText(text)
            .setOngoing(ongoing).setAutoCancel(!ongoing).setContentIntent(open);
        if (ongoing) b.addAction(android.R.drawable.ic_menu_close_clear_cancel, "Cancel",
            PendingIntent.getActivity(a, 5, new Intent(a, MainActivity.class).setAction(CANCEL), PendingIntent.FLAG_IMMUTABLE));
        nm.notify(ongoing ? 80 : 81, b.build());
    }
}
