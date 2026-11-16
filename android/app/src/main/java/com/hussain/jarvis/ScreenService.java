package com.hussain.jarvis;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Path;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import java.util.ArrayList;
import java.util.regex.Pattern;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import org.json.JSONObject;

/** Part 23: reads the text on the screen ONLY when you ask. Part 34: also does ONE step when asked (click, scroll, type,
 *  back, home, swipe). Every step is found again on the live screen, checked and verified.
 *  Part 73: the ONE event it does act on is "which app just came to the front" (only the package name, never the screen's
 *  text) - only to notice a payment app and turn this service off, so the bank's accessibility check passes. */
public class ScreenService extends AccessibilityService {
    static ScreenService live;

    @Override protected void onServiceConnected() { live = this; }
    @Override public boolean onUnbind(Intent i) { live = null; return super.onUnbind(i); }

    @Override public void onAccessibilityEvent(AccessibilityEvent e) {
        if (e.getEventType() != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return;  // only "app came to front", never screen content
        String pkg = e.getPackageName() == null ? null : e.getPackageName().toString();
        if (pkg == null || pkg.equals(getPackageName())) return;
        SharedPreferences sp = getSharedPreferences("j", 0);
        if (PaymentGuard.isPaymentApp(sp, pkg)) pauseForPayment(pkg);
    }

    /** Turns this accessibility service off and tells the person how to turn it back on. Android lets an app disable
     *  itself (disableSelf()) but never lets it re-enable itself - only a tap in Settings by the person can do that. */
    private void pauseForPayment(String pkg) {
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            nm.createNotificationChannel(new NotificationChannel("jarvis_payment", "Jarvis paused for payment", NotificationManager.IMPORTANCE_HIGH));
        PendingIntent go = PendingIntent.getActivity(this, 7, new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS),
            PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);
        Notification n = new Notification.Builder(this, "jarvis_payment").setSmallIcon(android.R.drawable.ic_lock_idle_lock)
            .setContentTitle("Jarvis paused for payment").setContentText("Screen-reading is off while " + pkg + " is open. Tap to turn it back on when done.")
            .setContentIntent(go).setAutoCancel(true).build();
        nm.notify(81, n);
        disableSelf();  // after this, onAccessibilityEvent/onServiceConnected will not fire again until the person taps the toggle in Settings
    }

    @Override public void onInterrupt() { }

    /** Text of the app on screen as JSON: {app, text} or {error}. Password fields are only named, never read. Max 3000 characters. */
    static String snapshot() {
        JSONObject o = new JSONObject();
        try {
            AccessibilityNodeInfo root = live == null ? null : live.getRootInActiveWindow();
            if (root == null) o.put("error", "nothing to read");
            else if (String.valueOf(root.getPackageName()).equals(live.getPackageName())) o.put("error", "Jarvis itself was on the screen");
            else {
                StringBuilder sb = new StringBuilder();
                walk(root, sb, 0);
                o.put("app", String.valueOf(root.getPackageName()));
                o.put("text", sb.length() > 3000 ? sb.substring(0, 3000) : sb.toString());
            }
        } catch (Exception e) { /* send what we have */ }
        return o.toString();
    }

    /** Part 32: one line per visible thing, with its kind: button, field, switch, scroll area. A field shows only its label, never what was typed. Password fields are only named. */
    static void walk(AccessibilityNodeInfo n, StringBuilder sb, int depth) {
        if (n == null || depth > 25 || sb.length() > 3000) return;
        if (n.isVisibleToUser()) {
            CharSequence t = n.getText() != null ? n.getText() : n.getContentDescription();
            boolean has = t != null && t.length() > 0;
            if (n.isPassword()) sb.append("field: [password field, hidden]\n");
            else if (n.isEditable()) {
                CharSequence h = Build.VERSION.SDK_INT >= 26 ? n.getHintText() : null;
                if (h == null) h = n.getContentDescription();
                sb.append("field: ").append(h != null && h.length() > 0 ? h : "text box").append('\n');
            } else if (n.isCheckable() && has) sb.append("switch ").append(n.isChecked() ? "on" : "off").append(": ").append(t).append('\n');
            else if (n.isClickable() && has) sb.append("button: ").append(t).append('\n');
            else if (has) sb.append(t).append('\n');
            if (n.isScrollable()) sb.append("scroll area\n");
        }
        for (int i = 0; i < n.getChildCount(); i++) walk(n.getChild(i), sb, depth + 1);
    }

    // ---- Part 34: safe screen actions ----
    interface Done { void got(JSONObject r); }
    static final Pattern DANGER = Pattern.compile("\\b(send|submit|pay|buy|purchase|order|delete|remove|uninstall|install|log ?out|sign ?out|transfer|confirm)\\b|भेज|पेमेंट|भुगतान|खरीद|ऑर्डर|डिलीट|हटा|इंस्टॉल|लॉग|कन्फर्म", Pattern.CASE_INSENSITIVE);
    static final Pattern SECRET = Pattern.compile("password|passcode|\\botp\\b|\\bpin\\b|cvv|cvc|card number|पासवर्ड|ओटीपी|पिन", Pattern.CASE_INSENSITIVE);

    static JSONObject r(boolean ok, String err) {
        JSONObject o = new JSONObject();
        try { o.put("ok", ok); if (err != null) o.put("err", err); } catch (Exception e) { /* tiny object, cannot fail */ }
        return o;
    }

    static String norm(CharSequence c) { return c == null ? "" : c.toString().toLowerCase().replaceAll("[^\\p{L}\\p{N}\\p{M}]", ""); }

    static String label(AccessibilityNodeInfo n) {
        CharSequence t = n.getText() != null ? n.getText() : n.getContentDescription();
        return t == null ? "" : t.toString();
    }

    static void collect(AccessibilityNodeInfo n, int d, ArrayList<AccessibilityNodeInfo> out, String kind) {
        if (n == null || d > 25 || out.size() > 12) return;
        if (n.isVisibleToUser() && !n.isPassword()) {
            if ("scroll".equals(kind) && n.isScrollable()) out.add(n);
            if ("edit".equals(kind) && n.isEditable()) out.add(n);
            if ("label".equals(kind) && label(n).length() > 0) out.add(n);
        }
        for (int i = 0; i < n.getChildCount(); i++) collect(n.getChild(i), d + 1, out, kind);
    }

    /** Hash of what is on screen. Used only to check that a step changed something. Never stored or sent. */
    static int sig(AccessibilityNodeInfo root) {
        StringBuilder sb = new StringBuilder();
        walk(root, sb, 0);
        return sb.toString().hashCode();
    }

    /** Runs ONE step on the live screen. The caller has already checked Stop and the master switch. sure = Hussain confirmed with a real finger tap. */
    static void act(JSONObject a, boolean sure, Done cb) {
        ScreenService s = live;
        String t = a.optString("type");
        if (s == null) { cb.got(r(false, "perm")); return; }
        if ("back".equals(t) || "home".equals(t)) {
            cb.got(r(s.performGlobalAction("back".equals(t) ? GLOBAL_ACTION_BACK : GLOBAL_ACTION_HOME), "refused"));
            return;
        }
        if ("lock".equals(t)) {  // Part 35: Android's own lock action (Android 9+). It can only lock, never unlock. We check the real lock state afterwards.
            if (Build.VERSION.SDK_INT < 28) { cb.got(r(false, "old_android")); return; }
            if (!s.performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN)) { cb.got(r(false, "refused")); return; }
            new Handler(Looper.getMainLooper()).postDelayed(() -> {
                android.app.KeyguardManager k = (android.app.KeyguardManager) s.getSystemService(android.content.Context.KEYGUARD_SERVICE);
                JSONObject o = r(true, null);
                try { o.put("locked", k != null && k.isKeyguardLocked()); } catch (Exception e) { /* send what we have */ }
                cb.got(o);
            }, 1200);
            return;
        }
        AccessibilityNodeInfo root = s.getRootInActiveWindow();
        if (root == null || String.valueOf(root.getPackageName()).equals(s.getPackageName())) { cb.got(r(false, "no_app")); return; }
        if ("current_app".equals(t)) {
            JSONObject o = r(true, null);
            try {
                String pkg = String.valueOf(root.getPackageName()), nm = pkg;
                try { nm = String.valueOf(s.getPackageManager().getApplicationLabel(s.getPackageManager().getApplicationInfo(pkg, 0))); } catch (Exception e) { /* keep the package name */ }
                o.put("app", nm);
            } catch (Exception e) { /* send what we have */ }
            cb.got(o);
            return;
        }
        if ("swipe".equals(t)) {
            if (Build.VERSION.SDK_INT < 24 || !sure) { cb.got(r(false, "need_yes")); return; }
            android.util.DisplayMetrics m = s.getResources().getDisplayMetrics();
            boolean down = !"up".equals(a.optString("dir"));
            Path p = new Path();
            p.moveTo(m.widthPixels / 2f, m.heightPixels * (down ? 0.7f : 0.3f));
            p.lineTo(m.widthPixels / 2f, m.heightPixels * (down ? 0.3f : 0.7f));
            boolean sent = s.dispatchGesture(new GestureDescription.Builder().addStroke(new GestureDescription.StrokeDescription(p, 0, 350)).build(), null, null);
            cb.got(r(sent, "refused"));
            return;
        }
        int before = sig(root);
        boolean did = false;
        if ("scroll".equals(t)) {
            ArrayList<AccessibilityNodeInfo> sc = new ArrayList<>();
            collect(root, 0, sc, "scroll");
            if (sc.isEmpty()) { cb.got(r(false, "no_scroll")); return; }
            did = sc.get(0).performAction("up".equals(a.optString("dir")) ? AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD : AccessibilityNodeInfo.ACTION_SCROLL_FORWARD);
        } else if ("click".equals(t)) {
            String q = norm(a.optString("name"));
            if (q.length() == 0) { cb.got(r(false, "not_found")); return; }
            if (DANGER.matcher(a.optString("name")).find() && !sure) { cb.got(r(false, "need_yes")); return; }
            ArrayList<AccessibilityNodeInfo> all = new ArrayList<>(), exact = new ArrayList<>(), hit = new ArrayList<>();
            collect(root, 0, all, "label");
            for (AccessibilityNodeInfo n : all) if (norm(label(n)).equals(q)) exact.add(n);
            for (AccessibilityNodeInfo n : exact.isEmpty() ? all : exact) {
                if (!exact.isEmpty() || norm(label(n)).contains(q)) {
                    AccessibilityNodeInfo c = n;
                    while (c != null && !c.isClickable()) c = c.getParent();
                    if (c != null && !hit.contains(c)) hit.add(c);
                }
            }
            if (hit.isEmpty()) { cb.got(r(false, "not_found")); return; }
            if (hit.size() > 1) { cb.got(r(false, "many")); return; }
            if (DANGER.matcher(label(hit.get(0))).find() && !sure) { cb.got(r(false, "need_yes")); return; }  // the real button text is checked too, not only what was said
            did = hit.get(0).performAction(AccessibilityNodeInfo.ACTION_CLICK);
        } else if ("type".equals(t)) {
            String txt = a.optString("text");
            String digits = txt.replaceAll("[\\s-]", "");
            if (txt.length() == 0 || txt.length() > 200 || SECRET.matcher(txt).find() || (digits.matches("\\d+") && (digits.length() <= 8 || (digits.length() >= 13 && digits.length() <= 19)))) { cb.got(r(false, "secret_text")); return; }
            AccessibilityNodeInfo f = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
            if (f != null && f.isPassword()) { cb.got(r(false, "secret_field")); return; }
            if (f == null || !f.isEditable()) {
                ArrayList<AccessibilityNodeInfo> ed = new ArrayList<>();
                collect(root, 0, ed, "edit");
                if (ed.isEmpty()) { cb.got(r(false, "no_field")); return; }
                f = ed.get(0);
            }
            String hint = (Build.VERSION.SDK_INT >= 26 && f.getHintText() != null ? f.getHintText() : "") + " " + (f.getContentDescription() == null ? "" : f.getContentDescription());
            if (SECRET.matcher(hint).find()) { cb.got(r(false, "secret_field")); return; }
            Bundle b = new Bundle();
            b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, txt);
            did = f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
        } else { cb.got(r(false, "unknown")); return; }
        if (!did) { cb.got(r(false, "refused")); return; }
        // verify: look again after a moment. If nothing on the screen changed we say so and never claim success.
        final int was = before;
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            AccessibilityNodeInfo now = live == null ? null : live.getRootInActiveWindow();
            JSONObject o = r(true, null);
            try { o.put("changed", now != null && sig(now) != was); } catch (Exception e) { /* send what we have */ }
            cb.got(o);
        }, 900);
    }
}
