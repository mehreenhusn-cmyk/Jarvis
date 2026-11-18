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
        Privacy.event(this, "pay");  // Part 78: timeline shows "paused for a payment app" (no app name saved)
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
        boolean swiped = false;
        if ("scroll".equals(t)) {
            ArrayList<AccessibilityNodeInfo> sc = new ArrayList<>();
            collect(root, 0, sc, "scroll");
            AccessibilityNodeInfo big = null;
            long best = -1;
            for (AccessibilityNodeInfo n : sc) {  // Part 123: the BIGGEST scroll area, not the first one (the first is often a small row of chips)
                android.graphics.Rect rc = new android.graphics.Rect();
                n.getBoundsInScreen(rc);
                long ar = (long) rc.width() * rc.height();
                if (ar > best) { best = ar; big = n; }
            }
            boolean up = "up".equals(a.optString("dir"));
            if (big != null) did = big.performAction(up ? AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD : AccessibilityNodeInfo.ACTION_SCROLL_FORWARD);
            if (!did && Build.VERSION.SDK_INT >= 24) { did = swipeNow(s, !up); swiped = did; }  // nothing to scroll (YouTube, charts, web pages): one plain swipe, it only moves the page
        } else if ("click_nth".equals(t)) {  // Part 127: the Nth big tappable card or row from the top
            ArrayList<AccessibilityNodeInfo> it = items(root, s.getResources().getDisplayMetrics());
            int k = a.optInt("n", 0);
            if (k < 1 || it.size() < k) { JSONObject o = r(false, "few"); try { o.put("count", it.size()); } catch (Exception e) { /* send what we have */ } cb.got(o); return; }
            AccessibilityNodeInfo pick = it.get(k - 1);
            if (DANGER.matcher(label(pick)).find() && !sure) { cb.got(r(false, "need_yes")); return; }
            did = pick.performAction(AccessibilityNodeInfo.ACTION_CLICK);
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
        final boolean sw = swiped, isScroll = "scroll".equals(t), dn = !"up".equals(a.optString("dir"));
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            AccessibilityNodeInfo now = live == null ? null : live.getRootInActiveWindow();
            boolean ch = now != null && sig(now) != was;
            if (isScroll && !ch && !sw && Build.VERSION.SDK_INT >= 24 && swipeNow(s, dn)) {  // Part 123: the scroll did nothing: swipe once, then check again
                new Handler(Looper.getMainLooper()).postDelayed(() -> {
                    AccessibilityNodeInfo n2 = live == null ? null : live.getRootInActiveWindow();
                    JSONObject o2 = r(true, null);
                    try { o2.put("changed", n2 != null && sig(n2) != was); } catch (Exception e) { /* send what we have */ }
                    cb.got(o2);
                }, 900);
                return;
            }
            JSONObject o = r(true, null);
            try { o.put("changed", ch); } catch (Exception e) { /* send what we have */ }
            cb.got(o);
        }, 900);
    }

    // ---- Part 129: look and tap. ONE screenshot of the open app (Android 11+), kept only in memory and sent only to the vision AI after your request.
    //      A screen with a password box, or a payment app, is never photographed. The tap needs your real finger tap on Yes, in the same app, within 2 minutes. ----
    static volatile String shotPkg;  // the app that was open when the picture was taken
    static volatile long shotAt;
    static volatile int shotW, shotH;  // real screen pixels of that picture (the tap spot is a fraction of these)

    static boolean hasPassword(AccessibilityNodeInfo n, int d) {
        if (n == null || d > 25) return false;
        if (n.isVisibleToUser() && n.isPassword()) return true;
        for (int i = 0; i < n.getChildCount(); i++) if (hasPassword(n.getChild(i), d + 1)) return true;
        return false;
    }

    /** Takes the picture. Result: {ok, w, h, image: data URL} or {ok:false, err}. The caller has already checked Stop, the master switch and the app lock. */
    static void shot(Done cb) {
        final ScreenService s = live;
        if (s == null) { cb.got(r(false, "perm")); return; }
        if (Build.VERSION.SDK_INT < 30) { cb.got(r(false, "old_shot")); return; }
        AccessibilityNodeInfo root = s.getRootInActiveWindow();
        if (root == null || String.valueOf(root.getPackageName()).equals(s.getPackageName())) { cb.got(r(false, "no_app")); return; }
        final String pkg = String.valueOf(root.getPackageName());
        if (PaymentGuard.isPaymentApp(s.getSharedPreferences("j", 0), pkg) || hasPassword(root, 0)) { cb.got(r(false, "secret_screen")); return; }
        s.takeScreenshot(android.view.Display.DEFAULT_DISPLAY, s.getMainExecutor(), new AccessibilityService.TakeScreenshotCallback() {
            @Override public void onSuccess(AccessibilityService.ScreenshotResult res) {
                try {
                    android.hardware.HardwareBuffer hb = res.getHardwareBuffer();
                    android.graphics.Bitmap hw = android.graphics.Bitmap.wrapHardwareBuffer(hb, res.getColorSpace());
                    android.graphics.Bitmap bmp = hw == null ? null : hw.copy(android.graphics.Bitmap.Config.ARGB_8888, false);
                    if (hw != null) hw.recycle();
                    hb.close();
                    if (bmp == null) { cb.got(r(false, "shot_failed")); return; }
                    int w = bmp.getWidth(), h = bmp.getHeight();
                    float k = Math.min(1f, 720f / w);  // a small picture is enough to point at a button, and it is quicker and cheaper
                    android.graphics.Bitmap sm = k < 1f ? android.graphics.Bitmap.createScaledBitmap(bmp, Math.round(w * k), Math.round(h * k), true) : bmp;
                    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
                    sm.compress(android.graphics.Bitmap.CompressFormat.JPEG, 60, bo);
                    if (sm != bmp) sm.recycle();
                    bmp.recycle();
                    String b64 = android.util.Base64.encodeToString(bo.toByteArray(), android.util.Base64.NO_WRAP);
                    if (b64.length() > 1300000) { cb.got(r(false, "shot_failed")); return; }
                    shotPkg = pkg; shotAt = System.currentTimeMillis(); shotW = w; shotH = h;
                    JSONObject o = r(true, null);
                    o.put("w", w); o.put("h", h); o.put("image", "data:image/jpeg;base64," + b64);
                    cb.got(o);
                } catch (Exception e) { cb.got(r(false, "shot_failed")); }
            }
            @Override public void onFailure(int code) { cb.got(r(false, code == 2 ? "perm_shot" : code == 3 ? "too_fast" : "shot_failed")); }
        });
    }

    /** ONE tap at the spot (fx, fy = fractions of the picture). Needs sure (your real finger tap on Yes). Refuses if another app is open now. Never claims success when nothing changed. */
    static void tapAt(JSONObject a, boolean sure, Done cb) {
        ScreenService s = live;
        if (s == null) { cb.got(r(false, "perm")); return; }
        if (!sure) { cb.got(r(false, "need_yes")); return; }
        double fx = a.optDouble("fx", -1), fy = a.optDouble("fy", -1);
        if (Build.VERSION.SDK_INT < 24 || !(fx >= 0 && fx <= 1 && fy >= 0 && fy <= 1) || shotW <= 0 || shotH <= 0) { cb.got(r(false, "unknown")); return; }
        if (SECRET.matcher(a.optString("label")).find()) { cb.got(r(false, "secret_field")); return; }
        AccessibilityNodeInfo root = s.getRootInActiveWindow();
        String want = shotPkg;
        shotPkg = null;  // one picture, one tap
        if (root == null || want == null || !want.equals(String.valueOf(root.getPackageName())) || System.currentTimeMillis() - shotAt > 120000) { cb.got(r(false, "screen_changed")); return; }
        if (hasPassword(root, 0)) { cb.got(r(false, "secret_screen")); return; }
        final int was = sig(root);
        Path p = new Path();
        p.moveTo((float) (fx * shotW), (float) (fy * shotH));
        if (!s.dispatchGesture(new GestureDescription.Builder().addStroke(new GestureDescription.StrokeDescription(p, 0, 60)).build(), null, null)) { cb.got(r(false, "refused")); return; }
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            AccessibilityNodeInfo now = live == null ? null : live.getRootInActiveWindow();
            JSONObject o = r(true, null);
            try { o.put("changed", now != null && sig(now) != was); } catch (Exception e) { /* send what we have */ }
            cb.got(o);
        }, 1000);
    }

    /** Part 127: big tappable cards and rows (not small buttons), outermost only, top to bottom. A drawn chart has none: Android shows no items inside a picture. */
    static ArrayList<AccessibilityNodeInfo> items(AccessibilityNodeInfo root, android.util.DisplayMetrics m) {
        ArrayList<AccessibilityNodeInfo> all = new ArrayList<>(), out = new ArrayList<>();
        gather(root, 0, all, m);
        for (int i = 0; i < all.size(); i++) {
            android.graphics.Rect a = new android.graphics.Rect();
            all.get(i).getBoundsInScreen(a);
            boolean inside = false;
            for (int j = 0; j < all.size() && !inside; j++) {
                if (j == i) continue;
                android.graphics.Rect b = new android.graphics.Rect();
                all.get(j).getBoundsInScreen(b);
                if (b.contains(a) && (!b.equals(a) || j < i)) inside = true;  // another candidate holds this one: count only the outer card
            }
            if (!inside) out.add(all.get(i));
        }
        java.util.Collections.sort(out, (x, y) -> {
            android.graphics.Rect p = new android.graphics.Rect(), q = new android.graphics.Rect();
            x.getBoundsInScreen(p);
            y.getBoundsInScreen(q);
            return p.top != q.top ? Integer.compare(p.top, q.top) : Integer.compare(p.left, q.left);
        });
        return out;
    }

    private static void gather(AccessibilityNodeInfo n, int d, ArrayList<AccessibilityNodeInfo> out, android.util.DisplayMetrics m) {
        if (n == null || d > 25 || out.size() > 60) return;
        if (n.isVisibleToUser() && n.isClickable() && !n.isPassword()) {
            android.graphics.Rect r = new android.graphics.Rect();
            n.getBoundsInScreen(r);
            if (r.width() >= m.widthPixels * 0.35f && r.height() >= m.heightPixels * 0.06f && r.height() < m.heightPixels * 0.9f) out.add(n);
        }
        for (int i = 0; i < n.getChildCount(); i++) gather(n.getChild(i), d + 1, out, m);
    }

    /** Part 123: one plain vertical swipe in the middle of the screen. down = the page moves down (finger goes up). */
    private static boolean swipeNow(ScreenService s, boolean down) {
        android.util.DisplayMetrics m = s.getResources().getDisplayMetrics();
        Path p = new Path();
        p.moveTo(m.widthPixels / 2f, m.heightPixels * (down ? 0.7f : 0.3f));
        p.lineTo(m.widthPixels / 2f, m.heightPixels * (down ? 0.3f : 0.7f));
        return s.dispatchGesture(new GestureDescription.Builder().addStroke(new GestureDescription.StrokeDescription(p, 0, 350)).build(), null, null);
    }
}
