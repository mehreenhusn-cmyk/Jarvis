package com.hussain.jarvis;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import org.json.JSONObject;

/** Part 23: reads the text on the screen ONLY when you ask. It ignores every event and never reads in the background. */
public class ScreenService extends AccessibilityService {
    static ScreenService live;

    @Override protected void onServiceConnected() { live = this; }
    @Override public boolean onUnbind(Intent i) { live = null; return super.onUnbind(i); }
    @Override public void onAccessibilityEvent(AccessibilityEvent e) { /* ignored on purpose */ }
    @Override public void onInterrupt() { }

    /** Text of the app on screen as JSON: {app, text} or {error}. Password fields are skipped. Max 3000 characters. */
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

    static void walk(AccessibilityNodeInfo n, StringBuilder sb, int depth) {
        if (n == null || depth > 25 || sb.length() > 3000) return;
        if (!n.isPassword() && n.isVisibleToUser()) {
            CharSequence t = n.getText() != null ? n.getText() : n.getContentDescription();
            if (t != null && t.length() > 0) sb.append(t).append('\n');
        }
        for (int i = 0; i < n.getChildCount(); i++) walk(n.getChild(i), sb, depth + 1);
    }
}
