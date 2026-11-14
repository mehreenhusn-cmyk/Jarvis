package com.hussain.jarvis;

import android.content.Context;
import android.database.Cursor;
import android.provider.CallLog;
import android.provider.ContactsContract;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 19: calls and contacts are read only when you ask. Metadata only: no messages, no call audio. */
class ContactsInfo {
    static String calls(Context c, int days) {
        JSONArray a = new JSONArray();
        long since = System.currentTimeMillis() - days * 86400000L;
        try (Cursor q = c.getContentResolver().query(CallLog.Calls.CONTENT_URI,
                new String[]{CallLog.Calls.CACHED_NAME, CallLog.Calls.NUMBER, CallLog.Calls.TYPE, CallLog.Calls.DATE, CallLog.Calls.DURATION},
                CallLog.Calls.DATE + ">?", new String[]{String.valueOf(since)}, CallLog.Calls.DATE + " DESC")) {
            while (q != null && q.moveToNext() && a.length() < 30) {
                JSONObject o = new JSONObject();
                o.put("name", q.getString(0)); o.put("number", q.getString(1));
                o.put("type", q.getInt(2)); o.put("ts", q.getLong(3)); o.put("sec", q.getInt(4));
                a.put(o);
            }
        } catch (Exception e) { /* send what we have */ }
        return a.toString();
    }

    static String find(Context c, String name) {
        JSONArray a = new JSONArray();
        try (Cursor q = c.getContentResolver().query(ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                new String[]{ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER},
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " LIKE ?", new String[]{"%" + name + "%"},
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)) {
            while (q != null && q.moveToNext() && a.length() < 5) {
                JSONObject o = new JSONObject();
                o.put("name", q.getString(0)); o.put("number", q.getString(1));
                a.put(o);
            }
        } catch (Exception e) { /* send what we have */ }
        return a.toString();
    }
}
