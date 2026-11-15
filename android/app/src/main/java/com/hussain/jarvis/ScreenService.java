package com.hussain.jarvis;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.os.Build;
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
}
