package com.hussain.jarvis;

import android.content.SharedPreferences;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/** Part 73: while a payment/banking app is on screen, Jarvis's own accessibility service turns itself off, so the bank's
 *  "turn off accessibility services" check passes. Android does not allow an app to turn its OWN accessibility back on,
 *  only the person can, in Settings - so this is one-way by design, and ScreenService posts a one-tap notification for that. */
final class PaymentGuard {
    /** Common UPI/banking app packages. The person can add more from Settings (Part 74); this list is only a starting point. */
    private static final Set<String> DEFAULT = new HashSet<>(Arrays.asList(
        "com.google.android.apps.nbu.paisa.user", "com.phonepe.app", "net.one97.paytm", "in.org.npci.upiapp",
        "com.myairtelapp", "com.csam.icici.bank.imobile", "com.sbi.lotusintouch", "com.snapwork.hdfc",
        "com.axis.mobile", "com.freecharge.android", "com.whatsapp" /* WhatsApp Pay rides on WhatsApp */));

    private PaymentGuard() {}

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
