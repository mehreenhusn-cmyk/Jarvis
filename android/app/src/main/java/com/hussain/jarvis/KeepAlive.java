package com.hussain.jarvis;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;

/** Part 153: keeps the microphone of Conversation / Hey Jarvis mode working when you press Home or lock the screen.
 *  Android only lets an app listen in the background while a foreground service of type "microphone" is running, so this one
 *  shows a notification with a Stop button the whole time. It does no listening itself (Ears does) and keeps nothing.
 *  It is started only from the page after your own switch (Settings > Voice & Listening > Keep listening in background),
 *  ends when the voice mode ends, and stops by itself after 8 hours. */
public class KeepAlive extends Service {
    static final String CH = "jarvis_keep", STOP = "com.hussain.jarvis.STOP_KEEP";
    static final long MAX = 8L * 3600_000L;
    static volatile boolean on;
    PowerManager.WakeLock wl;

    static void start(Context c) {
        try { c.startForegroundService(new Intent(c, KeepAlive.class)); } catch (Exception e) { on = false; }
    }

    static void halt(Context c) {
        on = false;
        c.stopService(new Intent(c, KeepAlive.class));
    }

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public int onStartCommand(Intent i, int flags, int id) {
        if (i != null && STOP.equals(i.getAction())) {
            on = false;
            final Ears e = MainActivity.liveEars;
            if (e != null) {
                new Handler(Looper.getMainLooper()).post(() -> {
                    e.stop();
                    e.web.evaluateJavascript("window.bgStopped&&bgStopped()", null);
                });
            }
            stopSelf();
            return START_NOT_STICKY;
        }
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CH, "Jarvis background listening", NotificationManager.IMPORTANCE_LOW));
        try {
            Notification n = note();
            if (Build.VERSION.SDK_INT >= 30) startForeground(81, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
            else startForeground(81, n);
        } catch (Exception e) {
            on = false;
            stopSelf();
            return START_NOT_STICKY;
        }
        try {
            if (wl == null) {
                wl = getSystemService(PowerManager.class).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "Jarvis:keep");
                wl.acquire(MAX);  // the CPU stays awake so the mic keeps working with the screen off
            }
        } catch (Exception e) { /* some phones refuse; the service still runs */ }
        on = true;
        return START_NOT_STICKY;
    }

    Notification note() {
        PendingIntent open = PendingIntent.getActivity(this, 11, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        PendingIntent stop = PendingIntent.getService(this, 12, new Intent(this, KeepAlive.class).setAction(STOP), PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, CH).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis is listening")
            .setContentText("Voice mode keeps the mic on in the background. Tap Stop to end.").setOngoing(true).setContentIntent(open)
            .addAction(android.R.drawable.ic_media_pause, "Stop", stop).build();
    }

    @Override public void onDestroy() {
        on = false;
        try { if (wl != null && wl.isHeld()) wl.release(); } catch (Exception e) { /* already released */ }
        super.onDestroy();
    }
}
