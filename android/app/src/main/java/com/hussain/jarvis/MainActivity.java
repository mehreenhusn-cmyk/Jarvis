package com.hussain.jarvis;

import android.Manifest;
import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.content.Intent;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** Part 16: a thin shell. It only shows the Jarvis page served by the Termux server on this phone. */
public class MainActivity extends Activity {
    static final String URL = "http://127.0.0.1:8787";
    WebView web;

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
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setWebViewClient(new WebViewClient() {
            @Override public void onReceivedError(WebView v, int code, String d, String u) {
                v.loadData("<body style='background:#0e1116;color:#e6e9ee;font:18px sans-serif;padding:32px'>"
                    + "<h3>Jarvis server is not running</h3><p>Open Termux and start Jarvis, then pull down to retry.</p>"
                    + "<p><a style='color:#c9a45c' href='" + URL + "'>Try again</a></p></body>", "text/html", "utf-8");
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onGeolocationPermissionsShowPrompt(String o, android.webkit.GeolocationPermissions.Callback cb) { cb.invoke(o, true, false); }
            @Override public void onPermissionRequest(PermissionRequest r) { r.grant(r.getResources()); }
        });
        // Part 18: the page gives us the pairing token, so the background service can check reminders.
        web.addJavascriptInterface(new Object() {
            @JavascriptInterface public String phoneInfo() { return PhoneInfo.json(MainActivity.this); }
            @JavascriptInterface public void saveToken(String t) {
                getSharedPreferences("j", 0).edit().putString("token", t).apply();
                runOnUiThread(() -> startForegroundService(new Intent(MainActivity.this, NotifyService.class)));
            }
        }, "JarvisApp");
        web.loadUrl(URL);
    }

    @Override public void onBackPressed() { if (web.canGoBack()) web.goBack(); else super.onBackPressed(); }
}
