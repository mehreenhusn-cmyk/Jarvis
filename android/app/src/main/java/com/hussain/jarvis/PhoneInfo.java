package com.hussain.jarvis;

import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.bluetooth.BluetoothAdapter;
import android.media.AudioDeviceInfo;
import android.media.AudioManager;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.Build;
import android.provider.Settings;
import java.util.ArrayList;
import java.util.List;
import org.json.JSONArray;
import android.os.Environment;
import android.os.PowerManager;
import android.os.StatFs;
import android.os.SystemClock;
import org.json.JSONObject;

/** Part 24: numbers only (memory, storage, battery, heat). Part 65 adds network, Bluetooth audio device names, airplane mode and battery health.
 *  Nothing about your apps, files or messages, and nothing is saved or sent anywhere. */
class PhoneInfo {
    static String json(Context c) {
        JSONObject o = new JSONObject();
        try {
            ActivityManager.MemoryInfo m = new ActivityManager.MemoryInfo();
            ((ActivityManager) c.getSystemService(Context.ACTIVITY_SERVICE)).getMemoryInfo(m);
            o.put("ram_total", m.totalMem); o.put("ram_free", m.availMem); o.put("ram_low", m.lowMemory);
            StatFs s = new StatFs(Environment.getDataDirectory().getPath());
            o.put("disk_total", s.getTotalBytes()); o.put("disk_free", s.getAvailableBytes());
            Intent b = c.registerReceiver(null, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
            if (b != null) {
                o.put("battery", 100 * b.getIntExtra("level", 0) / Math.max(1, b.getIntExtra("scale", 100)));
                o.put("temp_c", b.getIntExtra("temperature", 0) / 10.0);
                o.put("charging", b.getIntExtra("plugged", 0) != 0);
            }
            PowerManager p = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
            o.put("power_save", p.isPowerSaveMode());
            if (Build.VERSION.SDK_INT >= 29) o.put("thermal", p.getCurrentThermalStatus());
            o.put("uptime_h", SystemClock.elapsedRealtime() / 3600000);
            if (b != null) { o.put("health", b.getIntExtra("health", 0)); o.put("plug", b.getIntExtra("plugged", 0)); }  // 2 good, 3 hot, 4 dead, 5 over-voltage, 6 failure, 7 cold. plug: 1 AC, 2 USB, 4 wireless
        } catch (Exception e) { /* send what we have */ }
        net(c, o);
        return o.toString();
    }

    /** Part 65: which network is active, Bluetooth on/off and the NAME of connected audio devices (earbuds, speaker, car). Needs only the normal network-state permission.
     *  Other Bluetooth devices (watch, mouse) are not visible without the Bluetooth permission, so Jarvis only says "audio device". */
    private static void net(Context c, JSONObject o) {
        try {
            ConnectivityManager cm = (ConnectivityManager) c.getSystemService(Context.CONNECTIVITY_SERVICE);
            String kind = "none";
            boolean ok = false;
            Network n = cm.getActiveNetwork();
            NetworkCapabilities nc = n == null ? null : cm.getNetworkCapabilities(n);
            if (nc != null) {
                kind = nc.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ? "wifi" : nc.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ? "mobile" : nc.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) ? "ethernet" : "other";
                ok = nc.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED);  // Android itself tested that the internet really works on this network
            }
            o.put("net", kind); o.put("net_ok", ok);
        } catch (Exception e) { /* no network info: the page says so */ }
        try { o.put("airplane", Settings.Global.getInt(c.getContentResolver(), Settings.Global.AIRPLANE_MODE_ON, 0) != 0); } catch (Exception e) { /* skip */ }
        try {
            BluetoothAdapter ad = BluetoothAdapter.getDefaultAdapter();
            o.put("bt_on", ad != null && ad.isEnabled());
            List<String> names = new ArrayList<>();
            boolean wired = false;
            AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
            for (AudioDeviceInfo d : am.getDevices(AudioManager.GET_DEVICES_OUTPUTS)) {
                int t = d.getType();
                boolean bt = t == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP || t == AudioDeviceInfo.TYPE_BLUETOOTH_SCO || (Build.VERSION.SDK_INT >= 31 && t == AudioDeviceInfo.TYPE_BLE_HEADSET);
                if (bt) { String nm = String.valueOf(d.getProductName()); if (!names.contains(nm)) names.add(nm); }
                if (t == AudioDeviceInfo.TYPE_WIRED_HEADSET || t == AudioDeviceInfo.TYPE_WIRED_HEADPHONES || t == AudioDeviceInfo.TYPE_USB_HEADSET) wired = true;
            }
            o.put("bt_audio", new JSONArray(names)); o.put("wired", wired);
        } catch (Exception e) { /* skip */ }
    }
}
