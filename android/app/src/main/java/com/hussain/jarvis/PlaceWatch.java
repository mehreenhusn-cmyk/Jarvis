package com.hussain.jarvis;

import android.Manifest;
import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.content.pm.ServiceInfo;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Build;
import android.os.IBinder;
import android.os.Looper;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Set;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Parts 113 + 114: reminders by place and by Bluetooth.
 * The Jarvis page hands this class a copy of your saved places and reminders (placeSet). The phone position is compared HERE and thrown away:
 * it is never saved and never sent to the server or the AI. The service runs only while the switch is on and at least one reminder exists.
 * Battery: a position check every 2 minutes (and only after you moved 50 m) near a saved place, every 10 minutes when you are more than 3 km from all of them.
 * Needs: location permission (While using the app is enough, the service is a foreground service of type location) and, for Bluetooth, Nearby devices.
 */
public class PlaceWatch extends Service implements LocationListener {
    static final String PREF = "pw", CH = "jarvis_place";
    static final long NEAR = 2 * 60000L, FAR = 10 * 60000L, COOL = 30 * 60000L;
    static volatile boolean up;
    LocationManager lm;
    BroadcastReceiver bt;
    long every;
    final HashMap<Integer, Boolean> inside = new HashMap<>();   // place id -> inside the radius? (missing = not known yet)
    final HashMap<Integer, Long> lastFire = new HashMap<>();    // reminder id -> time shown (30 minute pause between two shows)

    // ---------- called from MainActivity ----------

    /** The page gives the newest copy. Returns {"ok":true,"running":..,"need":""} where need is "location" or "bluetooth" if Android must still be asked. */
    static String set(Activity a, String json) {
        try { new JSONObject(json); } catch (Exception e) { return "{\"ok\":false}"; }
        a.getSharedPreferences(PREF, 0).edit().putString("data", json).apply();
        return resume(a, true);
    }

    static JSONObject data(Context c) {
        try { return new JSONObject(c.getSharedPreferences(PREF, 0).getString("data", "{}")); } catch (Exception e) { return new JSONObject(); }
    }

    static boolean has(Context c, String kind) {
        JSONObject o = data(c);
        if (o.optInt("on", 1) != 1) return false;
        JSONArray w = o.optJSONArray("w");
        for (int i = 0; w != null && i < w.length(); i++) if (kind.equals(w.optJSONObject(i).optString("kind"))) return true;
        return false;
    }

    /** Start or stop the service to match the saved copy. Also called from onResume (ask = false), so a killed service comes back when you open Jarvis. */
    static String resume(Context c, boolean ask) {
        boolean place = has(c, "place"), blue = has(c, "bt");
        String need = "";
        if (place && c.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) need = "location";
        else if (blue && Build.VERSION.SDK_INT >= 31 && c.checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) need = "bluetooth";
        if (ask && !need.isEmpty() && c instanceof Activity) {  // Android is asked only when YOU just made a reminder, not at every app start
            final Activity a = (Activity) c;
            final boolean loc = need.equals("location");
            final String perm = loc ? Manifest.permission.ACCESS_FINE_LOCATION : Manifest.permission.BLUETOOTH_CONNECT;
            a.runOnUiThread(() -> a.requestPermissions(new String[]{perm}, loc ? 6 : 7));
        }
        boolean run = (place || blue) && need.isEmpty() && !Privacy.stopped;
        try {
            Intent i = new Intent(c, PlaceWatch.class);
            if (run) { if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(i); else c.startService(i); }
            else c.stopService(i);
        } catch (Exception e) { run = false; }  // Android refused (for example the app is not in front): the next onResume tries again
        return "{\"ok\":true,\"running\":" + run + ",\"need\":\"" + need + "\"}";
    }

    /** Names of the paired Bluetooth devices, so you can pick a word for a Part 114 reminder. */
    static String paired(Activity a) {
        try {
            if (Build.VERSION.SDK_INT >= 31 && a.checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                a.runOnUiThread(() -> a.requestPermissions(new String[]{Manifest.permission.BLUETOOTH_CONNECT}, 7));
                return "{\"need\":\"bluetooth\"}";
            }
            BluetoothAdapter ad = a.getSystemService(BluetoothManager.class).getAdapter();
            JSONArray l = new JSONArray();
            Set<BluetoothDevice> s = ad == null ? null : ad.getBondedDevices();
            if (s != null) for (BluetoothDevice d : s) if (d.getName() != null) l.put(d.getName());
            return new JSONObject().put("list", l).toString();
        } catch (Exception e) { return "{\"list\":[]}"; }
    }

    // ---------- the service ----------

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public int onStartCommand(Intent in, int flags, int id) {
        up = true;
        Privacy.init(this);
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CH, "Jarvis place watch", NotificationManager.IMPORTANCE_MIN));
        nm.createNotificationChannel(new NotificationChannel(NotifyService.ALERT, "Reminders", NotificationManager.IMPORTANCE_HIGH));
        Notification n = new Notification.Builder(this, CH).setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setContentTitle("Jarvis place watch").setContentText("Checking the places you chose. Your position is not saved or sent.").build();
        int t = 0;
        if (Build.VERSION.SDK_INT >= 29) {
            if (has(this, "place")) t |= ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION;
            if (has(this, "bt")) t |= ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE;
        }
        try {
            if (t != 0) startForeground(2, n, t); else startForeground(2, n);
        } catch (Exception e) { stopSelf(); return START_NOT_STICKY; }  // Android says no (permission missing): stay off
        loadState();
        arm();
        return START_STICKY;
    }

    void arm() {
        disarm();
        if (has(this, "place") && checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            lm = getSystemService(LocationManager.class);
            every = NEAR;
            listen();
        }
        if (has(this, "bt") && bt == null && (Build.VERSION.SDK_INT < 31 || checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED)) {
            bt = new BroadcastReceiver() {
                @Override public void onReceive(Context c, Intent in) {
                    try {
                        BluetoothDevice d = in.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                        String nm = d == null ? null : d.getName();
                        if (nm != null) fire(nm, "connect", "bt");
                    } catch (Exception e) { /* no permission or no name: nothing to show */ }
                }
            };
            registerReceiver(bt, new IntentFilter(BluetoothDevice.ACTION_ACL_CONNECTED));
        }
    }

    void listen() {
        try {
            lm.removeUpdates(this);
            String p = lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER) ? LocationManager.NETWORK_PROVIDER : LocationManager.GPS_PROVIDER;
            lm.requestLocationUpdates(p, every, 50f, this, Looper.getMainLooper());
            Location last = lm.getLastKnownLocation(p);
            if (last != null && System.currentTimeMillis() - last.getTime() < 10 * 60000L) onLocationChanged(last);
        } catch (SecurityException | IllegalArgumentException e) { stopSelf(); }
    }

    void disarm() {
        try { if (lm != null) lm.removeUpdates(this); } catch (Exception e) { /* already off */ }
        try { if (bt != null) unregisterReceiver(bt); } catch (Exception e) { /* already off */ }
        bt = null;
    }

    @Override public void onLocationChanged(Location l) {
        if (Privacy.stopped || l.getAccuracy() > 300) return;  // Stop switches this off too; a very fuzzy fix is ignored
        JSONArray ps = data(this).optJSONArray("places");
        double near = 1e9;
        for (int i = 0; ps != null && i < ps.length(); i++) {
            JSONObject p = ps.optJSONObject(i);
            float[] d = new float[1];
            Location.distanceBetween(l.getLatitude(), l.getLongitude(), p.optDouble("lat"), p.optDouble("lon"), d);
            near = Math.min(near, d[0]);
            int id = p.optInt("id"), r = p.optInt("r", 150);
            Boolean was = inside.get(id);
            boolean now = d[0] <= r || (was != null && was && d[0] <= r * 1.3 + 30);  // a wider ring to leave, so a border walk does not flip
            inside.put(id, now);
            if (was != null && was != now) fire(p.optString("name"), now ? "arrive" : "leave", "place");  // the first fix only learns where you are
        }
        saveState();
        long want = near > 3000 ? FAR : NEAR;  // far from every place: look less often (battery)
        if (want != every && lm != null) { every = want; listen(); }
    }

    // ---------- showing a reminder ----------

    static boolean same(String kind, String target, String name) {
        String a = target.trim().toLowerCase(), b = name.trim().toLowerCase();
        return kind.equals("bt") ? b.contains(a) : a.equals(b);
    }

    void fire(String name, String ev, String kind) {
        if (Privacy.stopped) return;
        JSONArray w = data(this).optJSONArray("w");
        long now = System.currentTimeMillis();
        for (int i = 0; w != null && i < w.length(); i++) {
            JSONObject x = w.optJSONObject(i);
            int id = x.optInt("id");
            if (!kind.equals(x.optString("kind")) || !ev.equals(x.optString("ev")) || !same(kind, x.optString("target"), name)) continue;
            Long last = lastFire.get(id);
            if (last != null && now - last < COOL) continue;
            lastFire.put(id, now);
            show(kind.equals("bt") ? "Bluetooth: " + name : name.substring(0, 1).toUpperCase() + name.substring(1), x.optString("text"));
            if (x.optInt("rep") == 0) done(id);
        }
    }

    void show(String title, String text) {
        Privacy.used("place");
        PendingIntent pi = PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(this, NotifyService.ALERT).setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle(title).setContentText(text).setStyle(new Notification.BigTextStyle().bigText(text)).setAutoCancel(true).setContentIntent(pi).build();
        getSystemService(NotificationManager.class).notify((int) System.currentTimeMillis(), n);
    }

    /** A once-only reminder was shown: take it out of the local copy at once and tell the server (if the server is off, the local copy still protects from a second show). */
    void done(int id) {
        try {
            JSONObject o = data(this);
            JSONArray w = o.optJSONArray("w"), k = new JSONArray();
            for (int i = 0; w != null && i < w.length(); i++) if (w.optJSONObject(i).optInt("id") != id) k.put(w.optJSONObject(i));
            getSharedPreferences(PREF, 0).edit().putString("data", o.put("w", k).toString()).apply();
        } catch (Exception e) { /* keep the old copy */ }
        final String tok = getSharedPreferences("j", 0).getString("token", "");
        if (tok.isEmpty()) return;
        new Thread(() -> {
            try {
                HttpURLConnection c = (HttpURLConnection) new URL(MainActivity.URL + "/place/fired").openConnection();
                c.setRequestMethod("POST"); c.setDoOutput(true); c.setConnectTimeout(5000); c.setReadTimeout(8000);
                c.setRequestProperty("Content-Type", "application/json");
                c.setRequestProperty("Authorization", "Bearer " + tok);
                try (OutputStream out = c.getOutputStream()) { out.write(("{\"id\":" + id + "}").getBytes("UTF-8")); }
                c.getResponseCode();
            } catch (Exception e) { /* server may be off; the page sends a fresh copy on the next start */ }
        }).start();
    }

    void loadState() {
        try {
            JSONObject s = new JSONObject(getSharedPreferences(PREF, 0).getString("in", "{}"));
            inside.clear();
            for (java.util.Iterator<String> it = s.keys(); it.hasNext(); ) { String k = it.next(); inside.put(Integer.parseInt(k), s.optBoolean(k)); }
        } catch (Exception e) { inside.clear(); }
    }

    void saveState() {
        try {
            JSONObject s = new JSONObject();
            for (java.util.Map.Entry<Integer, Boolean> e : inside.entrySet()) s.put(String.valueOf(e.getKey()), e.getValue());
            getSharedPreferences(PREF, 0).edit().putString("in", s.toString()).apply();
        } catch (Exception e) { /* only a remembered state is lost */ }
    }

    @Override public void onProviderEnabled(String p) { }
    @Override public void onProviderDisabled(String p) { }
    @Override public void onStatusChanged(String p, int s, android.os.Bundle b) { }

    @Override public void onDestroy() { up = false; disarm(); super.onDestroy(); }
}
