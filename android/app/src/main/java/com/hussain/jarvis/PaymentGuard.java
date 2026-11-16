package com.hussain.jarvis;

import android.content.SharedPreferences;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Pattern;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 73: while a payment/banking app is on screen, Jarvis's own accessibility service turns itself off, so the bank's
 *  "turn off accessibility services" check passes. Android does not allow an app to turn its OWN accessibility back on,
 *  only the person can, in Settings - so this is one-way by design, and ScreenService posts a one-tap notification for that. */
final class PaymentGuard {
    /** Common UPI/banking app packages. You can add more from Settings > Privacy & Security > Payment apps (Part 82); this list is only a starting point. */
    private static final Set<String> DEFAULT = new HashSet<>(Arrays.asList(
        "com.google.android.apps.nbu.paisa.user", "com.phonepe.app", "net.one97.paytm", "in.org.npci.upiapp",
        "com.myairtelapp", "com.csam.icici.bank.imobile", "com.sbi.lotusintouch", "com.snapwork.hdfc",
        "com.axis.mobile", "com.freecharge.android", "com.whatsapp" /* WhatsApp Pay rides on WhatsApp */));

    private static final Pattern PKG = Pattern.compile("^[a-zA-Z][a-zA-Z0-9_]*(\\.[a-zA-Z][a-zA-Z0-9_]*)+$");
    static final int MAX_EXTRA = 20;

    private PaymentGuard() {}

    /** Part 82: the apps YOU added (sorted). The built-in list is never changed. */
    static TreeSet<String> extra(SharedPreferences sp) {
        TreeSet<String> s = new TreeSet<>();
        String e = sp.getString("pay_extra_pkgs", "");
        if (e != null) for (String p : e.split(",")) if (!p.trim().isEmpty()) s.add(p.trim());
        return s;
    }

    private static void saveExtra(SharedPreferences sp, TreeSet<String> s) {
        StringBuilder b = new StringBuilder();
        for (String p : s) b.append(b.length() > 0 ? "," : "").append(p);
        sp.edit().putString("pay_extra_pkgs", b.toString()).apply();
    }

    /** Adds one package name. False if it is not a valid package name or the list of 20 is full. Adding only makes Jarvis pause for MORE apps, so it is always safe. */
    static boolean add(SharedPreferences sp, String pkg) {
        if (pkg == null || pkg.length() > 150 || !PKG.matcher(pkg).matches()) return false;
        if (DEFAULT.contains(pkg)) return true;
        TreeSet<String> s = extra(sp);
        if (!s.contains(pkg) && s.size() >= MAX_EXTRA) return false;
        s.add(pkg);
        saveExtra(sp, s);
        return true;
    }

    /** Removes an app YOU added. Built-in apps cannot be removed. */
    static boolean remove(SharedPreferences sp, String pkg) {
        TreeSet<String> s = extra(sp);
        boolean had = s.remove(pkg);
        if (had) saveExtra(sp, s);
        return had;
    }

    /** For the Settings card: {"def":[built-in packages],"extra":[your packages]}. */
    static String json(SharedPreferences sp) {
        try {
            return new JSONObject().put("def", new JSONArray(new TreeSet<>(DEFAULT))).put("extra", new JSONArray(extra(sp))).toString();
        } catch (Exception e) { return "{}"; }
    }

    static Set<String> packages(SharedPreferences sp) {
        String extra = sp.getString("pay_extra_pkgs", "");
        if (extra == null || extra.trim().isEmpty()) return DEFAULT;
        Set<String> all = new HashSet<>(DEFAULT);
        for (String p : extra.split(",")) if (!p.trim().isEmpty()) all.add(p.trim());
        return all;
    }

    static boolean isPaymentApp(SharedPreferences sp, String pkg) {
        return pkg != null && packages(sp).contains(pkg);
    }
}
