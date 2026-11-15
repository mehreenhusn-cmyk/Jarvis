package com.hussain.jarvis;

import android.content.Context;
import android.content.Intent;
import android.media.AudioManager;
import android.net.Uri;
import android.provider.AlarmClock;
import android.view.KeyEvent;
import java.net.URLEncoder;
import java.util.Calendar;
import org.json.JSONObject;

/** Part 66 (alarm, timer) and Part 60 (search inside an app). Alarm and timer use Android's own Clock app through AlarmClock intents.
 *  Search opens a web address that THIS file builds from its own fixed list: the page and the server only send an app key and the words, never a link. */
final class QuickSet {
    private QuickSet() {}

    static JSONObject r(boolean ok, String err) {
        JSONObject o = new JSONObject();
        try { o.put("ok", ok); if (err != null) o.put("err", err); } catch (Exception e) { /* empty answer is still an answer */ }
        return o;
    }

    static JSONObject run(Context c, JSONObject a) {
        String ty = a.optString("type");
        if ("alarm".equals(ty)) return alarm(c, a);
        if ("timer".equals(ty)) return timer(c, a.optInt("seconds"));
        if ("search".equals(ty)) return search(c, a.optString("app"), a.optString("query"));
        if ("media".equals(ty)) return media(c, a.optString("cmd"));
        return r(false, "unknown");
    }

    private static boolean go(Context c, Intent i) {
        try { i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK); c.startActivity(i); return true; } catch (Exception e) { return false; }
    }

    static JSONObject alarm(Context c, JSONObject a) {
        if (a.optBoolean("show")) return go(c, new Intent(AlarmClock.ACTION_SHOW_ALARMS)) ? r(true, null) : r(false, "launch_failed");
        int h = a.optInt("hour", -1), m = a.optInt("minute", -1);
        if (h < 0 || h > 23 || m < 0 || m > 59) return r(false, "bad_time");
        if (a.optBoolean("ambiguous")) {  // "6 baje" with no AM or PM: take whichever of 6 AM / 6 PM comes next on the phone's own clock
            Calendar n = Calendar.getInstance();
            int now = n.get(Calendar.HOUR_OF_DAY) * 60 + n.get(Calendar.MINUTE), h1 = h % 12, h2 = h % 12 + 12;
            int d1 = ((h1 * 60 + m) - now + 1440) % 1440, d2 = ((h2 * 60 + m) - now + 1440) % 1440;
            h = d1 <= d2 ? h1 : h2;
        }
        Intent i = new Intent(AlarmClock.ACTION_SET_ALARM).putExtra(AlarmClock.EXTRA_HOUR, h).putExtra(AlarmClock.EXTRA_MINUTES, m)
                .putExtra(AlarmClock.EXTRA_MESSAGE, "Jarvis").putExtra(AlarmClock.EXTRA_SKIP_UI, true);
        boolean ok = go(c, i);
        if (!ok) {  // some Clock apps refuse the silent form: open it with the time filled in, the person taps Save
            i.removeExtra(AlarmClock.EXTRA_SKIP_UI);
            ok = go(c, i);
        }
        JSONObject o = r(ok, ok ? null : "launch_failed");
        try { o.put("hour", h).put("minute", m); } catch (Exception e) { /* answer without the time */ }
        return o;
    }

    static JSONObject timer(Context c, int sec) {
        if (sec < 1 || sec > 86400) return r(false, "bad_time");
        Intent i = new Intent(AlarmClock.ACTION_SET_TIMER).putExtra(AlarmClock.EXTRA_LENGTH, sec).putExtra(AlarmClock.EXTRA_MESSAGE, "Jarvis").putExtra(AlarmClock.EXTRA_SKIP_UI, true);
        boolean ok = go(c, i);
        if (!ok) { i.removeExtra(AlarmClock.EXTRA_SKIP_UI); ok = go(c, i); }
        return r(ok, ok ? null : "launch_failed");
    }

    /** Part 68: pause, play, next, previous for whatever music or video player is active. Same as the keys on earphones. No permission needed. */
    static JSONObject media(Context c, String cmd) {
        int k;
        switch (cmd) {
            case "pause": k = KeyEvent.KEYCODE_MEDIA_PAUSE; break;
            case "play": k = KeyEvent.KEYCODE_MEDIA_PLAY; break;
            case "next": k = KeyEvent.KEYCODE_MEDIA_NEXT; break;
            case "prev": k = KeyEvent.KEYCODE_MEDIA_PREVIOUS; break;
            default: return r(false, "unknown");
        }
        try {
            AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
            boolean was = am.isMusicActive();  // so Jarvis can say honestly when nothing was playing
            am.dispatchMediaKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN, k));
            am.dispatchMediaKeyEvent(new KeyEvent(KeyEvent.ACTION_UP, k));
            return r(true, null).put("was", was);
        } catch (Exception e) { return r(false, "launch_failed"); }
    }

    static JSONObject search(Context c, String app, String q) {
        q = q == null ? "" : q.trim();
        if (q.isEmpty() || q.length() > 100) return r(false, "bad_query");
        String e;
        try { e = URLEncoder.encode(q, "UTF-8"); } catch (Exception x) { return r(false, "bad_query"); }
        Uri u; String pkg = null;
        switch (app) {
            case "youtube": u = Uri.parse("https://www.youtube.com/results?search_query=" + e); pkg = "com.google.android.youtube"; break;
            case "google": u = Uri.parse("https://www.google.com/search?q=" + e); break;
            case "maps": u = Uri.parse("geo:0,0?q=" + e); pkg = "com.google.android.apps.maps"; break;
            case "play": u = Uri.parse("market://search?q=" + e); pkg = "com.android.vending"; break;
            case "amazon": u = Uri.parse("https://www.amazon.in/s?k=" + e); break;
            case "flipkart": u = Uri.parse("https://www.flipkart.com/search?q=" + e); break;
            case "spotify": u = Uri.parse("https://open.spotify.com/search/" + e.replace("+", "%20")); pkg = "com.spotify.music"; break;
            default: return r(false, "unknown");
        }
        Intent i = new Intent(Intent.ACTION_VIEW, u);
        if (pkg != null) { i.setPackage(pkg); if (go(c, i)) return r(true, null); i.setPackage(null); }  // the app is not installed: the same search in the browser
        if ("maps".equals(app)) i.setData(Uri.parse("https://www.google.com/maps/search/?api=1&query=" + e));
        else if ("play".equals(app)) i.setData(Uri.parse("https://play.google.com/store/search?q=" + e));
        return go(c, i) ? r(true, null) : r(false, "launch_failed");
    }
}
