package com.hussain.jarvis;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 31: finds an app on THIS phone by its name and opens ONE. Only names that really exist can be opened. Nothing is saved or sent anywhere. */
final class Apps {
    private static final class App { String label, pkg, act; }

    private static String norm(String s) { return s.toLowerCase(Locale.ROOT).replaceAll("[^\\p{L}\\p{N}]", ""); }

    private static int dist(String a, String b) {
        int[] p = new int[b.length() + 1], q = new int[b.length() + 1];
        for (int j = 0; j <= b.length(); j++) p[j] = j;
        for (int i = 1; i <= a.length(); i++) {
            q[0] = i;
            for (int j = 1; j <= b.length(); j++) q[j] = Math.min(Math.min(q[j - 1], p[j]) + 1, p[j - 1] + (a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1));
            int[] t = p; p = q; q = t;
        }
        return p[b.length()];
    }

    /** Every app that has a launcher icon (needs only the <queries> line in the manifest, no extra permission). */
    private static List<App> all(Context c) {
        PackageManager pm = c.getPackageManager();
        List<App> out = new ArrayList<>();
        for (ResolveInfo r : pm.queryIntentActivities(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)) {
            if (r.activityInfo.packageName.equals(c.getPackageName())) continue;
            App a = new App();
            a.pkg = r.activityInfo.packageName;
            a.act = r.activityInfo.name;  // the exact launcher screen, so we do not depend on getLaunchIntentForPackage
            a.label = String.valueOf(r.loadLabel(pm));
            out.add(a);
        }
        return out;
    }

    /** Part 49b: [{l:name,p:package}] of every app with a launcher icon, A to Z. Names only. */
    static JSONArray list(Context c) {
        List<App> l = all(c);
        java.util.Collections.sort(l, (x, y) -> x.label.compareToIgnoreCase(y.label));
        JSONArray a = new JSONArray();
        try { for (App x : l) a.put(new JSONObject().put("l", x.label).put("p", x.pkg)); } catch (Exception e) { /* empty */ }
        return a;
    }

    /** Part 202: opens the camera app already on the front side. Android has no fixed rule for this: the extras below are the ones camera apps know; an app that ignores them opens on the back (then the flip button). */
    static JSONObject openFront(Context c) {
        JSONObject o = new JSONObject();
        try {
            Intent go = new Intent(android.provider.MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA)
                .putExtra("android.intent.extras.CAMERA_FACING", 1)
                .putExtra("android.intent.extras.LENS_FACING_FRONT", 1)
                .putExtra("android.intent.extra.USE_FRONT_CAMERA", true)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(go);
            return o.put("ok", true).put("app", "Camera (front)").put("front", true);
        } catch (Exception e) {  // no camera app answers this: open Camera by name like Part 186
            return open(c, "Camera", false);
        }
    }

    /** Result: {ok,app} opened | {ask:[names]} two or more fit, the page shows buttons | {err:not_found|launch_failed}. exact=true when Hussain tapped a name from our own list. */
    static JSONObject open(Context c, String name, boolean exact) {
        JSONObject o = new JSONObject();
        try {
            String q = norm(name == null ? "" : name);
            List<App> hit = new ArrayList<>();
            if (q.length() >= 2) {
                for (App a : all(c)) if (norm(a.label).equals(q)) hit.add(a);
                if (hit.isEmpty() && !exact) {  // starts with, or (4+ letters) contains: "whatsapp" finds "WhatsApp Business"
                    for (App a : all(c)) { String n = norm(a.label); if (n.startsWith(q) || (q.length() >= 4 && n.contains(q))) hit.add(a); }
                }
                if (hit.isEmpty() && !exact) {  // small spelling mistakes: "watsapp", "cromme"
                    int best = q.length() >= 7 ? 2 : q.length() >= 4 ? 1 : 0, found = best + 1;
                    for (App a : all(c)) { int d = dist(norm(a.label), q); if (d <= best && d < found) { found = d; hit.clear(); } if (d == found && d <= best) hit.add(a); }
                }
            }
            if (hit.isEmpty()) return o.put("ok", false).put("err", "not_found");
            if (hit.size() > 1) {
                JSONArray ask = new JSONArray();
                for (int i = 0; i < Math.min(4, hit.size()); i++) ask.put(hit.get(i).label);
                return o.put("ok", false).put("ask", ask);
            }
            App h = hit.get(0);
            Intent go = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER).setClassName(h.pkg, h.act).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED);
            try {
                c.startActivity(go);
            } catch (Exception first) {  // second try: Android's own launch intent for the package
                Intent alt = c.getPackageManager().getLaunchIntentForPackage(h.pkg);
                if (alt == null) return o.put("ok", false).put("err", "launch_failed").put("why", first.getClass().getSimpleName() + ": " + first.getMessage());
                try { c.startActivity(alt.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); }
                catch (Exception second) { return o.put("ok", false).put("err", "launch_failed").put("why", second.getClass().getSimpleName() + ": " + second.getMessage()); }
            }
            return o.put("ok", true).put("app", h.label);
        } catch (Exception e) {
            try { return o.put("ok", false).put("err", "launch_failed").put("why", e.getClass().getSimpleName() + ": " + e.getMessage()); } catch (Exception x) { return o; }
        }
    }
}
