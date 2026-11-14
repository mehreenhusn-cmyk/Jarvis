package com.hussain.jarvis;

import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.os.Environment;
import android.os.PowerManager;
import android.os.StatFs;
import android.os.SystemClock;
import org.json.JSONObject;

/** Part 24: numbers only (memory, storage, battery, heat). Nothing about your apps, files or messages. */
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
        } catch (Exception e) { /* send what we have */ }
        return o.toString();
    }
}
