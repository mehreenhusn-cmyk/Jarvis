package com.hussain.jarvis;

import android.Manifest;
import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.telephony.TelephonyManager;

/**
 * Part 112: note after a call. When a call of 30 seconds or more ends, Jarvis shows ONE notification: "Call ended. Kuch yaad rakhna hai?".
 * You tap it, Jarvis asks, and what you type or say next is saved as a normal note (the existing "note karo" command).
 * It never reads the phone number, the contact or the voice. It only sees "a call started" and "a call ended" (the Android phone-state event).
 * Off until you say "call note on". Needs the Phone permission (READ_PHONE_STATE), asked only then. Stop (Part 28) silences it.
 */
public class CallNote extends BroadcastReceiver {
    static final String PREF = "cn", CH = "jarvis_callnote";
    static final long MIN = 30000L;

    static boolean on(Context c) { return c.getSharedPreferences(PREF, 0).getInt("on", 0) == 1; }

    static boolean allowed(Context c) { return c.checkSelfPermission(Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED; }

    /** From the page: v = 1 on, 0 off, -1 only read. Returns {"ok":true,"on":..,"need":"phone"|""}. Android is asked only when you just switched it on. */
    static String set(Activity a, int v) {
        if (v == 0 || v == 1) a.getSharedPreferences(PREF, 0).edit().putInt("on", v).putLong("start", 0).apply();
        String need = on(a) && !allowed(a) ? "phone" : "";
        if (v == 1 && !need.isEmpty()) a.runOnUiThread(() -> a.requestPermissions(new String[]{Manifest.permission.READ_PHONE_STATE}, 8));
        return "{\"ok\":true,\"on\":" + on(a) + ",\"need\":\"" + need + "\"}";
    }

    @Override public void onReceive(Context c, Intent in) {
        try {
            if (!TelephonyManager.ACTION_PHONE_STATE_CHANGED.equals(in.getAction()) || !on(c) || !allowed(c)) return;
            String st = in.getStringExtra(TelephonyManager.EXTRA_STATE);
            SharedPreferences sp = c.getSharedPreferences(PREF, 0);
            long now = System.currentTimeMillis(), start = sp.getLong("start", 0);
            if (TelephonyManager.EXTRA_STATE_OFFHOOK.equals(st)) {  // a call is talking now (the first OFFHOOK is the start)
                if (start == 0) sp.edit().putLong("start", now).apply();
            } else if (TelephonyManager.EXTRA_STATE_IDLE.equals(st)) {  // the call ended
                sp.edit().putLong("start", 0).apply();
                if (start != 0 && now - start >= MIN) ask(c);  // missed or very short calls are ignored
            }
        } catch (Exception e) { /* nothing to show */ }
    }

    static void ask(Context c) {
        Privacy.init(c);
        if (Privacy.stopped) return;
        Privacy.used("callnote");
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CH, "Jarvis call note", NotificationManager.IMPORTANCE_DEFAULT));
        Intent i = new Intent(c, MainActivity.class).putExtra("callnote", true).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi = PendingIntent.getActivity(c, 112, i, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Notification n = new Notification.Builder(c, CH).setSmallIcon(android.R.drawable.ic_menu_edit)
            .setContentTitle("Call ended").setContentText("Kuch yaad rakhna hai? Tap to add a note.").setAutoCancel(true).setContentIntent(pi).build();
        nm.notify(112, n);
    }
}
