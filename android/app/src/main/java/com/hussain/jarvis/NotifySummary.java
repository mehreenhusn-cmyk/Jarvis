package com.hussain.jarvis;

import android.app.Notification;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Set;
import java.util.regex.Pattern;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 49b: notification summary. Off by default. Sees only the apps Hussain chose. Keeps app name, title and 200 characters
 *  in phone memory only (never on disk, never sent) for 24 hours. Anything that looks like an OTP, code, password, PIN or card number is dropped. */
public class NotifySummary extends NotificationListenerService {
    static final int MAX = 50;
    static final long KEEP = 24L * 3600 * 1000;
    static final ArrayList<String[]> ITEMS = new ArrayList<>();  // {app, title, text, time}
    static volatile boolean up;
    static final Pattern SENS = Pattern.compile("(?i)otp|one.?time|passw|passcode|\\bpin\\b|cvv|verif|\\bcode\\b|पासवर्ड|ओटीपी|पिन|(?:\\d[ -]?){13,19}");

    @Override public void onListenerConnected() { up = true; }
    @Override public void onListenerDisconnected() { up = false; }

    @Override public void onNotificationPosted(StatusBarNotification sbn) {
        try {
            SharedPreferences p = getSharedPreferences("j", 0);
            if (!p.getBoolean("ns_on", false)) return;
            String pkg = sbn.getPackageName();
            Set<String> apps = p.getStringSet("ns_apps", Collections.<String>emptySet());
            if (pkg.equals(getPackageName()) || !apps.contains(pkg)) return;
            Notification n = sbn.getNotification();
            if (!sbn.isClearable() || (n.flags & (Notification.FLAG_GROUP_SUMMARY | Notification.FLAG_ONGOING_EVENT)) != 0) return;
            Bundle e = n.extras;
            CharSequence t = e.getCharSequence(Notification.EXTRA_TITLE), x = e.getCharSequence(Notification.EXTRA_TEXT);
            String title = t == null ? "" : t.toString().trim(), text = x == null ? "" : x.toString().trim();
            if (title.isEmpty() && text.isEmpty()) return;
            if (SENS.matcher(title + " " + text).find()) return;
            add(p.getString("ns_l_" + pkg, pkg), cut(title, 60), cut(text, 200));
        } catch (Exception ex) { /* one bad notification must never stop the others */ }
    }

    static String cut(String s, int n) { return s.length() > n ? s.substring(0, n) : s; }

    static synchronized void add(String app, String title, String text) {
        prune();
        if (!ITEMS.isEmpty()) { String[] l = ITEMS.get(ITEMS.size() - 1); if (l[0].equals(app) && l[1].equals(title) && l[2].equals(text)) return; }
        ITEMS.add(new String[]{app, title, text, String.valueOf(System.currentTimeMillis())});
        while (ITEMS.size() > MAX) ITEMS.remove(0);
    }

    private static void prune() {
        long old = System.currentTimeMillis() - KEEP;
        for (int i = ITEMS.size() - 1; i >= 0; i--) if (Long.parseLong(ITEMS.get(i)[3]) < old) ITEMS.remove(i);
    }

    static synchronized int count() { prune(); return ITEMS.size(); }
    static synchronized void clear() { ITEMS.clear(); }

    /** Drops items of apps that are no longer chosen. */
    static synchronized void keepOnly(Set<String> apps, SharedPreferences p) {
        for (int i = ITEMS.size() - 1; i >= 0; i--) {
            boolean ok = false;
            for (String a : apps) if (ITEMS.get(i)[0].equals(p.getString("ns_l_" + a, a))) ok = true;
            if (!ok) ITEMS.remove(i);
        }
    }

    static synchronized String json() {
        prune();
        JSONArray a = new JSONArray();
        try {
            for (String[] s : ITEMS) a.put(new JSONObject().put("app", s[0]).put("title", s[1]).put("text", s[2]).put("t", Long.parseLong(s[3])));
        } catch (Exception e) { /* empty list */ }
        return a.toString();
    }
}
