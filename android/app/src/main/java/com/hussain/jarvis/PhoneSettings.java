package com.hussain.jarvis;

import android.content.Context;
import android.content.Intent;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.media.AudioManager;
import android.net.Uri;
import android.provider.Settings;
import org.json.JSONObject;

/** Part 37: settings help. It opens fixed Android settings pages, switches the flashlight, changes the music volume.
 *  It never flips Wi-Fi, Bluetooth or location by itself: Android does not allow that, so Jarvis opens the right page and says so. */
final class PhoneSettings {
    private PhoneSettings() {}

    static JSONObject r(boolean ok, String err) {
        JSONObject o = new JSONObject();
        try { o.put("ok", ok); if (err != null) o.put("err", err); } catch (Exception e) { /* empty answer is still an answer */ }
        return o;
    }

    static JSONObject run(Context c, JSONObject a) {
        String ty = a.optString("type");
        if ("settings".equals(ty)) return page(c, a.optString("page"));
        if ("torch".equals(ty)) return torch(c, a.optBoolean("on"));
        if ("volume".equals(ty)) return volume(c, a.optString("dir"));
        return r(false, "unknown");
    }

    /** Only these pages can be opened. The name comes from the server's fixed list and is checked again here. */
    static JSONObject page(Context c, String w) {
        Intent i;
        switch (w) {
            case "wifi": i = new Intent(Settings.ACTION_WIFI_SETTINGS); break;
            case "bluetooth": i = new Intent(Settings.ACTION_BLUETOOTH_SETTINGS); break;
            case "location": i = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS); break;
            case "sound": i = new Intent(Settings.ACTION_SOUND_SETTINGS); break;
            case "display": i = new Intent(Settings.ACTION_DISPLAY_SETTINGS); break;  // brightness lives here (decision D1: no "modify system settings" permission)
            case "battery": i = new Intent(Settings.ACTION_BATTERY_SAVER_SETTINGS); break;
            case "network": i = new Intent(Settings.ACTION_WIRELESS_SETTINGS); break;
            case "accessibility": i = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS); break;
            case "permissions": i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + c.getPackageName())); break;
            case "notifications": i = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE, c.getPackageName()); break;
            default: return r(false, "unknown");
        }
        try { c.startActivity(i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); return r(true, null).put("page", w); }
        catch (Exception e) { return r(false, "no_page"); }  // this phone has no such page
    }

    static JSONObject torch(Context c, boolean on) {
        try {
            CameraManager cm = c.getSystemService(CameraManager.class);
            for (String id : cm.getCameraIdList()) {
                CameraCharacteristics ch = cm.getCameraCharacteristics(id);
                Boolean flash = ch.get(CameraCharacteristics.FLASH_INFO_AVAILABLE);
                Integer face = ch.get(CameraCharacteristics.LENS_FACING);
                if (Boolean.TRUE.equals(flash) && face != null && face == CameraCharacteristics.LENS_FACING_BACK) {
                    cm.setTorchMode(id, on);  // needs no permission. Another app using the camera can make this fail.
                    return r(true, null).put("on", on);
                }
            }
        } catch (Exception e) { return r(false, "torch_busy"); }
        return r(false, "no_torch");
    }

    /** Music volume only (calls and ringtone are left alone). The answer says what really happened, read back from Android. */
    static JSONObject volume(Context c, String dir) {
        try {
            AudioManager am = c.getSystemService(AudioManager.class);
            int before = am.getStreamVolume(AudioManager.STREAM_MUSIC), max = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC);
            am.adjustStreamVolume(AudioManager.STREAM_MUSIC, "up".equals(dir) ? AudioManager.ADJUST_RAISE : AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI);
            int after = am.getStreamVolume(AudioManager.STREAM_MUSIC);
            return r(true, null).put("vol", after).put("max", max).put("changed", after != before);
        } catch (Exception e) { return r(false, "unknown"); }
    }
}
