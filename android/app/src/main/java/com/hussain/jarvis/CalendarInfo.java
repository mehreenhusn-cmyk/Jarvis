package com.hussain.jarvis;

import android.content.ContentUris;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.CalendarContract;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Calendar;

/** Part 44: phone calendar events, read only when you ask. Only title, time and place. No notes, no guests. Nothing is saved. */
class CalendarInfo {
    /** spec = "from,days": from = days after today (0 = today), days = how many days (1 to 14). */
    static String events(Context c, String spec) {
        JSONArray a = new JSONArray();
        int from = 0, days = 3;
        try {
            String[] p = spec.split(",");
            from = Math.max(0, Math.min(14, Integer.parseInt(p[0].trim())));
            days = Math.max(1, Math.min(14, Integer.parseInt(p[1].trim())));
        } catch (Exception e) { /* keep the defaults */ }
        Calendar d = Calendar.getInstance();
        d.set(Calendar.HOUR_OF_DAY, 0); d.set(Calendar.MINUTE, 0); d.set(Calendar.SECOND, 0); d.set(Calendar.MILLISECOND, 0);
        d.add(Calendar.DAY_OF_YEAR, from);
        long begin = d.getTimeInMillis();
        d.add(Calendar.DAY_OF_YEAR, days);
        long end = d.getTimeInMillis();
        Uri.Builder u = CalendarContract.Instances.CONTENT_URI.buildUpon();
        ContentUris.appendId(u, begin);
        ContentUris.appendId(u, end);
        try (Cursor q = c.getContentResolver().query(u.build(),
                new String[]{CalendarContract.Instances.TITLE, CalendarContract.Instances.BEGIN, CalendarContract.Instances.END,
                        CalendarContract.Instances.ALL_DAY, CalendarContract.Instances.EVENT_LOCATION},
                null, null, CalendarContract.Instances.BEGIN + " ASC")) {
            while (q != null && q.moveToNext() && a.length() < 20) {
                JSONObject o = new JSONObject();
                o.put("title", q.getString(0)); o.put("begin", q.getLong(1)); o.put("end", q.getLong(2));
                o.put("allDay", q.getInt(3) == 1); o.put("where", q.getString(4));
                a.put(o);
            }
        } catch (Exception e) { /* send what we have */ }
        return a.toString();
    }
}
