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
    private static final class App { String label, pkg; }

    private static String norm(String s) { return s.toLowerCase(Locale.ROOT).replaceAll("[^\\p{L}\\p{N}]", ""); }

    /** Part 62: only the consonants, so a name written in another script still finds the app: "zomaito" and "Zomato" both give "zmt". */
    private static String skel(String s) { return s.replaceAll("[aeiouyhw]", "").replaceAll("(.)\\1+", "$1"); }

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
            if (hit.isEmpty() && !exact && q.length() >= 3) {  // Part 62: same consonants
                String sk = skel(q);
                if (sk.length() >= 3) for (App a : all(c)) if (skel(norm(a.label)).equals(sk)) hit.add(a);
            }
            if (hit.isEmpty()) return o.put("ok", false).put("err", "not_found");
            if (hit.size() > 1) {
                JSONArray ask = new JSONArray();
                for (int i = 0; i < Math.min(4, hit.size()); i++) ask.put(hit.get(i).label);
                return o.put("ok", false).put("ask", ask);
            }
            Intent go = c.getPackageManager().getLaunchIntentForPackage(hit.get(0).pkg);
            if (go == null) return o.put("ok", false).put("err", "launch_failed");
            c.startActivity(go.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            return o.put("ok", true).put("app", hit.get(0).label);
        } catch (Exception e) {
            try { return o.put("ok", false).put("err", "launch_failed"); } catch (Exception x) { return o; }
        }
    }
}
