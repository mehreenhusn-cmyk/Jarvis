package com.hussain.jarvis;

import android.app.Activity;
import android.app.KeyguardManager;
import android.content.Context;
import android.content.Intent;

/** Part 36: lock the Jarvis app with Android's own screen lock prompt (fingerprint, face, PIN, pattern). Jarvis never keeps its own PIN. */
final class AppLock {
    static final int ASK = 9, TURN_OFF = 10;
    static final long GRACE = 60_000;  // leaving the app for less than a minute does not ask again
    private static boolean on;
    private static long okUntil;  // the app is open until this time
    private static boolean loaded;

    private AppLock() {}

    static void init(Context c) {
        if (loaded) return;
        loaded = true;
        on = c.getSharedPreferences("j", 0).getBoolean("applock", false);
    }

    /** True if the phone has a screen lock. Without one Android cannot ask for anything. */
    static boolean available(Context c) {
        KeyguardManager k = c.getSystemService(KeyguardManager.class);
        return k != null && k.isDeviceSecure();
    }

    static boolean enabled() { return on; }

    /** True while the lock is on and the app was not opened in the last minute. The bridge and the page both obey this. */
    static boolean locked() { return on && System.currentTimeMillis() > okUntil; }

    static void opened() { okUntil = System.currentTimeMillis() + GRACE; }

    static void left() { if (on && System.currentTimeMillis() < okUntil) okUntil = System.currentTimeMillis() + GRACE; }

    static void set(Context c, boolean v) {
        on = v;
        c.getSharedPreferences("j", 0).edit().putBoolean("applock", v).apply();
        if (v) opened();
    }

    /** Opens Android's own prompt. Returns false if the phone has no screen lock. */
    static boolean ask(Activity a, int code, String why) {
        KeyguardManager k = a.getSystemService(KeyguardManager.class);
        Intent i = k == null ? null : k.createConfirmDeviceCredentialIntent("Jarvis", why);
        if (i == null) return false;
        try { a.startActivityForResult(i, code); return true; } catch (Exception e) { return false; }
    }

    static String state(Context c) {
        return "{\"on\":" + on + ",\"available\":" + available(c) + ",\"locked\":" + locked() + "}";
    }
}
