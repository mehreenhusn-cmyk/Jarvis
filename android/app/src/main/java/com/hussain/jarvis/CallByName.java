package com.hussain.jarvis;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.provider.ContactsContract;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 64: "Ammi ko call karo". Finds the contact by name in the phone's own contacts and starts the call. Runs only when Hussain asked
 *  (the master switch and Stop are checked in MainActivity). Nothing is saved or sent. A typed number only opens the dialer, it never calls by itself. */
final class CallByName {
    private static String norm(String s) { return s == null ? "" : s.toLowerCase(Locale.ROOT).replaceAll("[^\\p{L}\\p{N}]", ""); }

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

    /** name -> numbers, for every contact that has a phone number. */
    private static Map<String, List<String>> all(Activity a) {
        Map<String, List<String>> m = new LinkedHashMap<>();
        try (Cursor c = a.getContentResolver().query(ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                new String[]{ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER}, null, null,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)) {
            while (c != null && c.moveToNext() && m.size() < 5000) {
                String n = c.getString(0), num = c.getString(1);
                if (n == null || num == null) continue;
                List<String> l = m.get(n);
                if (l == null) { l = new ArrayList<>(); m.put(n, l); }
                String d = num.replaceAll("[^+0-9]", "");
                boolean dup = false;
                for (String x : l) if (x.equals(d)) dup = true;
                if (!dup && d.length() >= 3) l.add(d);
            }
        } catch (Exception e) { /* empty list: not found */ }
        return m;
    }

    /** 2 = sure (same name, starts with it, contains it), 1 = only close (spelling, same consonants), 0 = no. Close matches are never called without Hussain's tap. */
    private static int fits(String label, String q) {
        String n = norm(label);
        if (q.length() < 2 || n.isEmpty()) return 0;
        if (n.equals(q) || n.startsWith(q) || (q.length() >= 3 && n.contains(q))) return 2;
        if (n.length() >= 4 && q.length() - n.length() <= 5 && q.startsWith(n)) return 1;  // "ammaku" (to Amma): a word ending added to the name
        if (q.length() >= 4 && dist(n, q) <= (q.length() >= 7 ? 2 : 1)) return 1;
        return q.length() >= 3 && skel(q).length() >= 2 && skel(n).equals(skel(q)) ? 1 : 0;  // same consonants: "amma" and "ammi"
    }

    /** {ok,name,mode:call|dial} started | {ask:[{label,number}]} several fit | {err:not_found} | {err:perm,perm:true} Call permission was asked. */
    static JSONObject run(Activity a, JSONObject q) {
        JSONObject o = new JSONObject();
        try {
            String number = q.optString("number").replaceAll("[^+0-9]", "");
            boolean exact = q.optBoolean("exact"), raw = q.optBoolean("raw");
            String label = q.optString("name");
            if (number.isEmpty()) {
                String n1 = norm(q.optString("name")), n2 = norm(q.optString("said"));
                List<String[]> hit = new ArrayList<>(), near = new ArrayList<>();  // {name, number}
                for (Map.Entry<String, List<String>> e : all(a).entrySet()) {
                    int f = Math.max(fits(e.getKey(), n1), fits(e.getKey(), n2));
                    if (f > 0) for (String num : e.getValue()) (f == 2 ? hit : near).add(new String[]{e.getKey(), num});
                }
                if (hit.isEmpty()) hit = near;
                if (hit.isEmpty()) return o.put("ok", false).put("err", "not_found");
                if (hit.size() > 1 || (hit == near && !exact)) {  // several fit, or only a close spelling: Hussain taps the right one
                    JSONArray ask = new JSONArray();
                    for (int i = 0; i < Math.min(4, hit.size()); i++) {
                        String num = hit.get(i)[1];
                        ask.put(new JSONObject().put("label", hit.get(i)[0] + " (..." + num.substring(Math.max(0, num.length() - 4)) + ")").put("number", num));
                    }
                    return o.put("ok", false).put("ask", ask);
                }
                number = hit.get(0)[1];
                label = hit.get(0)[0];
            }
            if ("whatsapp".equals(q.optString("via"))) {  // Part 69: only OPENS the chat with the words filled in. WhatsApp's send button is Hussain's own tap.
                String d = number.startsWith("+") ? number.substring(1) : number.startsWith("00") ? number.substring(2) : number;
                if (number.startsWith("0") && !number.startsWith("00")) d = "91" + number.substring(1);  // India: 098... -> 9198...
                else if (d.length() == 10) d = "91" + d;
                String text = q.optString("text");
                Uri u = Uri.parse("https://wa.me/" + d + (text.isEmpty() ? "" : "?text=" + Uri.encode(text)));
                Intent w = new Intent(Intent.ACTION_VIEW, u).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                try { a.startActivity(new Intent(w).setPackage("com.whatsapp")); }
                catch (Exception e1) {
                    try { a.startActivity(new Intent(w).setPackage("com.whatsapp.w4b")); }
                    catch (Exception e2) { a.startActivity(w); }  // no WhatsApp app: the link opens in the browser
                }
                return o.put("ok", true).put("name", label).put("mode", "whatsapp");
            }
            boolean direct = !raw;
            if (direct && a.checkSelfPermission(Manifest.permission.CALL_PHONE) != PackageManager.PERMISSION_GRANTED) {
                a.runOnUiThread(() -> a.requestPermissions(new String[]{Manifest.permission.CALL_PHONE}, 6));
                return o.put("ok", false).put("err", "perm").put("perm", true);
            }
            Uri tel = Uri.fromParts("tel", number, null);
            a.startActivity(new Intent(direct ? Intent.ACTION_CALL : Intent.ACTION_DIAL, tel).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            return o.put("ok", true).put("name", label).put("mode", direct ? "call" : "dial");
        } catch (Exception e) {
            try { return o.put("ok", false).put("err", "launch_failed"); } catch (Exception x) { return o; }
        }
    }
}
