package com.hussain.jarvis;

import android.Manifest;
import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import org.json.JSONObject;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.webkit.ValueCallback;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebResourceRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Part 16: a thin shell. It only shows the Jarvis page served by the Termux server on this phone. */
public class MainActivity extends Activity {
    static final String URL = "http://127.0.0.1:8787";
    WebView web;
    Ears ears;
    ValueCallback<Uri[]> picker;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO, Manifest.permission.POST_NOTIFICATIONS, Manifest.permission.ACCESS_FINE_LOCATION}, 1);
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0e1116"));
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setGeolocationEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setWebViewClient(new WebViewClient() {
            // Part 26: the page can use phone features, so it must never leave the Jarvis server address.
            @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                return !("127.0.0.1".equals(u.getHost()) && u.getPort() == 8787);
            }
            @Override public void onReceivedError(WebView v, int code, String d, String u) {
                v.loadData("<body style='background:#0e1116;color:#e6e9ee;font:18px sans-serif;padding:32px'>"
                    + "<h3>Jarvis server is not running</h3><p>Open Termux and start Jarvis, then pull down to retry.</p>"
                    + "<p><a style='color:#c9a45c' href='" + URL + "'>Try again</a></p></body>", "text/html", "utf-8");
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onGeolocationPermissionsShowPrompt(String o, android.webkit.GeolocationPermissions.Callback cb) { cb.invoke(o, true, false); }
            @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (picker != null) picker.onReceiveValue(null);
                picker = cb;
                try { startActivityForResult(p.createIntent(), 7); } catch (Exception e) { picker = null; return false; }
                return true;
            }
            @Override public void onPermissionRequest(PermissionRequest r) { r.grant(r.getResources()); }
        });
        // Part 18: the page gives us the pairing token, so the background service can check reminders.
        web.addJavascriptInterface(new Object() {
            boolean allowed(String perm, int code) {
                if (checkSelfPermission(perm) == PackageManager.PERMISSION_GRANTED) return true;
                runOnUiThread(() -> requestPermissions(new String[]{perm}, code));
                return false;
            }
            @JavascriptInterface public String calls(int days) {
                return allowed(Manifest.permission.READ_CALL_LOG, 2) ? ContactsInfo.calls(MainActivity.this, days) : "{\"perm\":false}";
            }
            @JavascriptInterface public String contact(String name) {
                return allowed(Manifest.permission.READ_CONTACTS, 3) ? ContactsInfo.find(MainActivity.this, name) : "{\"perm\":false}";
            }
            @JavascriptInterface public void listen(String lang, boolean wake) {
                runOnUiThread(() -> { if (ears == null) ears = new Ears(MainActivity.this, web); ears.start(lang, wake); });
            }
            @JavascriptInterface public void stopListen() {
                runOnUiThread(() -> { if (ears != null) ears.stop(); });
            }
            @JavascriptInterface public String screen() {
                if (ScreenService.live == null) {
                    runOnUiThread(() -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
                    return "{\"perm\":false}";
                }
                runOnUiThread(() -> moveTaskToBack(true));
                new Handler(Looper.getMainLooper()).postDelayed(() -> screenDone(), 6000);
                return "{\"wait\":6}";
            }
            @JavascriptInterface public String phoneInfo() { return PhoneInfo.json(MainActivity.this); }
            @JavascriptInterface public void saveToken(String t) {
                getSharedPreferences("j", 0).edit().putString("token", t).apply();
                runOnUiThread(() -> startForegroundService(new Intent(MainActivity.this, NotifyService.class)));
            }
        }, "JarvisApp");
        web.loadUrl(URL);
    }

    static String pending;  // screen text waiting to be handed to the page

    void screenDone() {
        pending = ScreenService.snapshot();
        try { startActivity(new Intent(this, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK)); }
        catch (Exception e) { /* the notification below still works */ }
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(NotifyService.ALERT, "Reminders", NotificationManager.IMPORTANCE_HIGH));
        nm.notify(77, new Notification.Builder(this, NotifyService.ALERT).setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle("Jarvis read your screen").setContentText("Tap to see the answer").setAutoCancel(true)
            .setContentIntent(PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE)).build());
    }

    @Override protected void onPause() {
        super.onPause();  // Android does not let apps listen from the background, so Hey Jarvis pauses here
        if (ears != null && ears.on) { ears.stop(); ears.js("onHeardErr", "Hey Jarvis paused because the app went to the background"); }
    }

    @Override protected void onResume() {
        super.onResume();
        if (pending != null && web != null) {
            String p = pending; pending = null;
            getSystemService(NotificationManager.class).cancel(77);
            web.evaluateJavascript("window.onScreen&&onScreen(" + JSONObject.quote(p) + ")", null);
        }
    }

    @Override protected void onActivityResult(int req, int res, Intent data) {
        if (req == 7 && picker != null) { picker.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data)); picker = null; }
        else super.onActivityResult(req, res, data);
    }

    @Override public void onBackPressed() { if (web.canGoBack()) web.goBack(); else super.onBackPressed(); }
}
