package com.hussain.jarvis;

import android.app.Activity;
import android.app.AppOpsManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.app.usage.UsageEvents;
import android.app.usage.UsageStatsManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.provider.Settings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Parts 115 + 116: Anti-Doomscroll and the app habit map. Everything stays on the phone.
 * 115: after N minutes in the SAME app (you set N) Jarvis shows ONE calm line. It never blocks, closes or locks anything.
 * 116: counts "after app A you usually open app B" (package names and a number only, no times, no content). You read it with: app map.
 * Needs Usage Access (Android settings, you switch it on yourself). A foreground service checks the front app once a minute while the screen is on.
 * Stop (Part 28) and the switches switch it off. Nothing is sent to the server or the AI.
 */
public class UsageWatch extends Service {
    static final String PREF = "uw", CH = "jarvis_usage";
    static final long TICK = 60000L;
    static volatile boolean up;
    final Handler h = new Handler(Looper.getMainLooper());
    String cur;        // app in front now (null = screen off, home screen or Jarvis itself)
    long since;        // when this stretch in the same app began
    boolean nudged;    // the calm line was already shown for this stretch
    final Runnable tick = new Runnable() { @Override public void run() { check(); h.postDelayed(this, TICK); } };

    // ---------- called from MainActivity ----------

    static SharedPreferencesLike p(Context c) { return new SharedPreferencesLike(c); }

    /** Tiny wrapper so the code below stays short. */
    static class SharedPreferencesLike {
        final android.content.SharedPreferences sp;
        SharedPreferencesLike(Context c) { sp = c.getSharedPreferences(PREF, 0); }
        int on() { return sp.getInt("on", 0); }
        int n() { return sp.getInt("n", 20); }
        int map() { return sp.getInt("map", 0); }
        JSONObject counts() { try { return new JSONObject(sp.getString("counts", "{}")); } catch (Exception e) { return new JSONObject(); } }
    }

    static boolean allowed(Context c) {
        try {
            AppOpsManager ops = c.getSystemService(AppOpsManager.class);
            return ops.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, android.os.Process.myUid(), c.getPackageName()) == AppOpsManager.MODE_ALLOWED;
        } catch (Exception e) { return false; }
    }

    /**
     * The page sends {"on":0|1,"n":minutes,"map":0|1} (any key may be missing). Returns {"ok":true,"running":..,"need":"usage"|"","on":..,"n":..,"map":..}.
     * need = "usage" means Android's Usage Access page was opened and you must switch Jarvis on there.
     */
    static String set(Activity a, String json) {
        try {
            JSONObject o = new JSONObject(json);
            android.content.SharedPreferences.Editor e = a.getSharedPreferences(PREF, 0).edit();
            if (o.has("on")) e.putInt("on", o.optInt("on") == 1 ? 1 : 0);
            if (o.has("n")) e.putInt("n", Math.max(5, Math.min(180, o.optInt("n", 20))));
            if (o.has("map")) e.putInt("map", o.optInt("map") == 1 ? 1 : 0);
            if (o.optInt("reset") == 1) e.putString("counts", "{}");
            e.apply();
        } catch (Exception e) { return "{\"ok\":false}"; }
        return resume(a, true);
    }

    /** Start or stop the service to match the switches. Also called from onResume (ask = false), so a killed service comes back when you open Jarvis. */
    static String resume(Context c, boolean ask) {
        SharedPreferencesLike s = p(c);
        boolean want = s.on() == 1 || s.map() == 1;
        String need = "";
        if (want && !allowed(c)) {
            need = "usage";
            if (ask && c instanceof Activity) {  // only after YOU gave the command, never at app start
                try { c.startActivity(new Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); } catch (Exception e) { /* no such page on this phone */ }
            }
        }
        boolean run = want && need.isEmpty() && !Privacy.stopped;
        try {
            Intent i = new Intent(c, UsageWatch.class);
            if (run) { if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(i); else c.startService(i); }
            else c.stopService(i);
        } catch (Exception e) { run = false; }  // Android refused (the app is not in front): the next onResume tries again
        return "{\"ok\":true,\"running\":" + run + ",\"need\":\"" + need + "\",\"on\":" + s.on() + ",\"n\":" + s.n() + ",\"map\":" + s.map() + "}";
    }

    /** Part 116: the top app pairs with real app names, most used first. {"list":[{"from":"YouTube","to":"Instagram","n":7}],"on":..,"n":..,"map":..} */
    static String map(Context c) {
        SharedPreferencesLike s = p(c);
        JSONObject out = new JSONObject();
        try {
            JSONObject k = s.counts();
            ArrayList<String> keys = new ArrayList<>();
            for (Iterator<String> it = k.keys(); it.hasNext(); ) keys.add(it.next());
            Collections.sort(keys, (x, y) -> k.optInt(y) - k.optInt(x));
            JSONArray l = new JSONArray();
            for (String key : keys) {
                if (l.length() >= 8) break;
                String[] ab = key.split(">");
                if (ab.length != 2 || k.optInt(key) < 2) continue;  // one time is not a habit yet
                l.put(new JSONObject().put("from", label(c, ab[0])).put("to", label(c, ab[1])).put("n", k.optInt(key)));
            }
            out.put("list", l).put("on", s.on()).put("n", s.n()).put("map", s.map()).put("allowed", allowed(c));
        } catch (Exception e) { /* send what we have */ }
        return out.toString();
    }

    static String label(Context c, String pkg) {
        try { return c.getPackageManager().getApplicationLabel(c.getPackageManager().getApplicationInfo(pkg, 0)).toString(); } catch (Exception e) { return pkg; }
    }

    // ---------- the service ----------

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public int onStartCommand(Intent in, int flags, int id) {
        up = true;
        Privacy.init(this);
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CH, "Jarvis scroll alert", NotificationManager.IMPORTANCE_MIN));
        nm.createNotificationChannel(new NotificationChannel(NotifyService.ALERT, "Reminders", NotificationManager.IMPORTANCE_HIGH));
        Notification n = new Notification.Builder(this, CH).setSmallIcon(android.R.drawable.ic_menu_recent_history)
            .setContentTitle("Jarvis scroll alert").setContentText("Checks which app is in front, on this phone only. Nothing is saved or sent.").build();
        try {
            if (Build.VERSION.SDK_INT >= 34) startForeground(3, n, 1 << 30);  // FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            else startForeground(3, n);
        } catch (Exception e) { stopSelf(); return START_NOT_STICKY; }
        cur = null; since = 0; nudged = false;
        h.removeCallbacks(tick);
        h.post(tick);
        return START_STICKY;
    }

    /** The app that is in front now, from Android's usage events of the last 10 minutes. Null when none (or when Jarvis or the home screen is in front). */
    String front() {
        try {
            UsageStatsManager us = getSystemService(UsageStatsManager.class);
            long now = System.currentTimeMillis();
            UsageEvents ev = us.queryEvents(now - 10 * 60000L, now);
            UsageEvents.Event e = new UsageEvents.Event();
            String top = null;
            while (ev.hasNextEvent()) {
                ev.getNextEvent(e);
                int t = e.getEventType();
                if (t == UsageEvents.Event.ACTIVITY_RESUMED) top = e.getPackageName();
                else if ((t == UsageEvents.Event.ACTIVITY_PAUSED) && e.getPackageName().equals(top)) top = null;
            }
            if (top == null || top.equals(getPackageName()) || top.equals("com.android.systemui") || isHome(top)) return null;
            return top;
        } catch (Exception e) { return null; }
    }

    boolean isHome(String pkg) {
        try {
            ResolveInfo r = getPackageManager().resolveActivity(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME), PackageManager.MATCH_DEFAULT_ONLY);
            return r != null && r.activityInfo != null && pkg.equals(r.activityInfo.packageName);
        } catch (Exception e) { return false; }
    }

    void check() {
        SharedPreferencesLike s = p(this);
        if (Privacy.stopped || !allowed(this) || (s.on() != 1 && s.map() != 1)) { stopSelf(); return; }
        PowerManager pm = getSystemService(PowerManager.class);
        String now = pm.isInteractive() ? front() : null;
        long t = System.currentTimeMillis();
        if (now == null) { cur = null; since = 0; nudged = false; return; }  // screen off, home screen or Jarvis: the stretch is over
        if (!now.equals(cur)) {
            if (cur != null && s.map() == 1 && t - since >= 20000L) count(cur, now);  // Part 116: "after cur you opened now" (only if you stayed 20 s or more)
            cur = now; since = t; nudged = false;
            return;
        }
        long mins = (t - since) / 60000L;
        if (s.on() == 1 && !nudged && mins >= s.n()) {
            nudged = true;  // one line per stretch, never repeated, nothing is blocked
            Privacy.used("usage");
            String text = "You have been in " + label(this, now) + " for " + (mins < 60 ? mins + " min" : (mins / 60) + " h " + (mins % 60) + " min") + ". A short break may feel good.";
            PendingIntent pi = PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
            Notification n = new Notification.Builder(this, NotifyService.ALERT).setSmallIcon(android.R.drawable.ic_popup_reminder)
                .setContentTitle("Jarvis").setContentText(text).setStyle(new Notification.BigTextStyle().bigText(text)).setAutoCancel(true).setContentIntent(pi).build();
            getSystemService(NotificationManager.class).notify(3003, n);
        }
    }

    /** Add 1 to "from>to". Package names and a number only; keeps the 60 biggest pairs. */
    void count(String from, String to) {
        try {
            android.content.SharedPreferences sp = getSharedPreferences(PREF, 0);
            JSONObject k = new JSONObject(sp.getString("counts", "{}"));
            String key = from + ">" + to;
            k.put(key, k.optInt(key) + 1);
            if (k.length() > 60) {
                String worst = null;
                for (Iterator<String> it = k.keys(); it.hasNext(); ) { String x = it.next(); if (worst == null || k.optInt(x) < k.optInt(worst)) worst = x; }
                if (worst != null && !worst.equals(key)) k.remove(worst);
            }
            sp.edit().putString("counts", k.toString()).apply();
        } catch (Exception e) { /* one count is lost, nothing else */ }
    }

    @Override public void onDestroy() { up = false; h.removeCallbacks(tick); super.onDestroy(); }
}
