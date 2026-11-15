package com.hussain.jarvis;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Scanner;
import org.json.JSONArray;
import org.json.JSONObject;

/** Part 18: runs in the background and shows a phone notification when a Jarvis reminder is due. */
public class NotifyService extends Service {
    static final String BG = "jarvis_bg", ALERT = "jarvis_alert";
    volatile boolean run;
    static volatile boolean up;  // Part 29: the dashboard shows if the reminder service is really running

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public int onStartCommand(Intent i, int flags, int id) {
        up = true;
        Privacy.init(this);
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(BG, "Jarvis is running", NotificationManager.IMPORTANCE_MIN));
        nm.createNotificationChannel(new NotificationChannel(ALERT, "Reminders", NotificationManager.IMPORTANCE_HIGH));
        Notification n = new Notification.Builder(this, BG).setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle("Jarvis is running").setContentText("Watching for your reminders").build();
        if (Build.VERSION.SDK_INT >= 29) startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
        else startForeground(1, n);
        if (!run) { run = true; new Thread(this::loop).start(); }
        return START_STICKY;
    }

    void loop() {
        while (run) {
            try {
                String tok = getSharedPreferences("j", 0).getString("token", "");
                if (!tok.isEmpty()) poll(tok);
            } catch (Exception e) { /* server may be off; try again later */ }
            try { Thread.sleep(30000); } catch (InterruptedException e) { return; }
        }
    }

    void poll(String tok) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(MainActivity.URL + "/due").openConnection();
        c.setRequestMethod("POST"); c.setDoOutput(true); c.setConnectTimeout(5000); c.setReadTimeout(8000);
        c.setRequestProperty("Content-Type", "application/json");
        c.setRequestProperty("Authorization", "Bearer " + tok);
        String now = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US).format(new Date());
        try (OutputStream o = c.getOutputStream()) { o.write(("{\"now\":\"" + now + "\"}").getBytes("UTF-8")); }
        if (c.getResponseCode() != 200) return;
        String body = new Scanner(c.getInputStream(), "UTF-8").useDelimiter("\\A").next();
        JSONArray a = new JSONObject(body).optJSONArray("due");
        for (int k = 0; a != null && k < a.length(); k++) notify(a.getJSONObject(k).optString("text"));
    }

    void notify(String text) {
        Privacy.used("notify");
        PendingIntent pi = PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(this, ALERT).setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle("Jarvis reminder").setContentText(text).setAutoCancel(true).setContentIntent(pi).build();
        getSystemService(NotificationManager.class).notify((int) System.currentTimeMillis(), n);
    }

    @Override public void onDestroy() { run = false; up = false; super.onDestroy(); }
}
