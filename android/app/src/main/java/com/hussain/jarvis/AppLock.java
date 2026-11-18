package com.hussain.jarvis;

import android.app.Activity;
import android.app.KeyguardManager;
import android.content.Context;
import android.content.Intent;

/** Part 36 made this; Part 150 switched it OFF for good: Jarvis never asks for a fingerprint, face or PIN any more. The methods stay so the other files compile. */
final class AppLock {
    static final int ASK = 9, TURN_OFF = 10;
    static final long GRACE = 300_000;
    private static boolean on;  // Part 150: always false
    private static long okUntil;
    private static boolean loaded;

    private AppLock() {}

    /** Part 150: also clears an old "ON" saved by an earlier APK, so the prompt never comes back. */
    static void init(Context c) {
        if (loaded) return;
        loaded = true;
        on = false;
        c.getSharedPreferences("j", 0).edit().putBoolean("applock", false).apply();
    }

    static boolean available(Context c) {
        KeyguardManager k = c.getSystemService(KeyguardManager.class);
        return k != null && k.isDeviceSecure();
    }

    static boolean enabled() { return false; }

    static boolean locked() { return false; }

    static void opened() { okUntil = System.currentTimeMillis() + GRACE; }

    static void left() { }

    /** Part 150: ignored. The lock cannot be turned on. */
    static void set(Context c, boolean v) {
        on = false;
        c.getSharedPreferences("j", 0).edit().putBoolean("applock", false).apply();
    }

    static boolean ask(Activity a, int code, String why) {
        KeyguardManager k = a.getSystemService(KeyguardManager.class);
        Intent i = k == null ? null : k.createConfirmDeviceCredentialIntent("Jarvis", why);
        if (i == null) return false;
        try { a.startActivityForResult(i, code); return true; } catch (Exception e) { return false; }
    }

    static String state(Context c) {
        return "{\"on\":false,\"available\":" + available(c) + ",\"locked\":false}";
    }
}
