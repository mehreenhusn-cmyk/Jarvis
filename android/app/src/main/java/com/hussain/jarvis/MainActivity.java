package com.hussain.jarvis;

import android.Manifest;
import android.app.Activity;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.os.Handler;
import android.view.MotionEvent;
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
    static final String LISTEN = "com.hussain.jarvis.LISTEN";  // Part 38: sent by the Quick Settings tile and the icon shortcut
    boolean wantListen;
    WebView web;
    Ears ears;
    ValueCallback<Uri[]> picker;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        Privacy.init(this);
        AppLock.init(this);
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
            // Part 27: location only for the Jarvis page, and only if Android location permission is given (asked here, when first needed).
            @Override public void onGeolocationPermissionsShowPrompt(String o, android.webkit.GeolocationPermissions.Callback cb) {
                boolean has = checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
                if (trusted(o) && !has) requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, 4);
                if (trusted(o) && has) Privacy.used("location");
                cb.invoke(o, trusted(o) && has, false);
            }
            @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (Privacy.stopped) { cb.onReceiveValue(null); return true; }
                Privacy.used("camera");
                if (picker != null) picker.onReceiveValue(null);
                picker = cb;
                try { startActivityForResult(p.createIntent(), 7); } catch (Exception e) { picker = null; return false; }
                return true;
            }
            // Part 27: the page may use only the microphone, only from the Jarvis address, only if Android already allowed it. Camera is never given.
            @Override public void onPermissionRequest(PermissionRequest r) {
                boolean audio = false;
                for (String x : r.getResources()) audio |= PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(x);
                if (audio && !Privacy.stopped && trusted(String.valueOf(r.getOrigin())) && checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED)
                    r.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                else r.deny();
            }
        });
        // Part 18: the page gives us the pairing token, so the background service can check reminders.
        web.addJavascriptInterface(new Object() {
            boolean allowed(String perm, int code) {
                if (checkSelfPermission(perm) == PackageManager.PERMISSION_GRANTED) return true;
                runOnUiThread(() -> requestPermissions(new String[]{perm}, code));
                return false;
            }
            @JavascriptInterface public String calls(int days) {
                if (AppLock.locked()) return "{\"locked\":true}";
                if (!allowed(Manifest.permission.READ_CALL_LOG, 2)) return "{\"perm\":false}";
                Privacy.used("calls");
                return ContactsInfo.calls(MainActivity.this, days);
            }
            @JavascriptInterface public String contact(String name) {
                if (AppLock.locked()) return "{\"locked\":true}";
                if (!allowed(Manifest.permission.READ_CONTACTS, 3)) return "{\"perm\":false}";
                Privacy.used("contacts");
                return ContactsInfo.find(MainActivity.this, name);
            }
            @JavascriptInterface public void listen(String lang, boolean wake) {
                if (AppLock.locked()) return;
                if (Privacy.stopped) { web.post(() -> web.evaluateJavascript("window.onHeardErr&&onHeardErr('Jarvis is stopped. Tap Turn mic on first',false)", null)); return; }
                if (!allowed(Manifest.permission.RECORD_AUDIO, 1)) { web.post(() -> web.evaluateJavascript("window.onHeardErr&&onHeardErr('allow the microphone, then tap the mic again',false)", null)); return; }
                runOnUiThread(() -> { if (ears == null) ears = new Ears(MainActivity.this, web); ears.start(lang, wake); });
            }
            @JavascriptInterface public void stopListen() {
                runOnUiThread(() -> { if (ears != null) ears.stop(); });
            }
            @JavascriptInterface public String dashboard() { return Privacy.dashboard(MainActivity.this); }
            // Part 29: opens one fixed Android settings page (nothing else can be opened from the page)
            @JavascriptInterface public void openSettings(String w) {
                Intent i;
                if ("acc".equals(w)) i = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
                else if ("battery".equals(w)) i = new Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS);
                else if ("notif".equals(w) && Build.VERSION.SDK_INT >= 26) i = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE, getPackageName());
                else i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getPackageName()));
                final Intent go = i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                runOnUiThread(() -> { try { startActivity(go); } catch (Exception e) { /* this phone has no such page */ } });
            }
            @JavascriptInterface public String privacy() { return Privacy.state(MainActivity.this).toString(); }
            @JavascriptInterface public String stopAll() { return Privacy.stopAll(MainActivity.this); }
            @JavascriptInterface public String restart() { return "{\"ok\":" + Privacy.restart() + "}"; }
            @JavascriptInterface public String screen() {
                if (AppLock.locked()) return "{\"locked\":true}";
                if (Privacy.stopped) return "{\"stopped\":true}";
                if (ScreenService.live == null) {
                    runOnUiThread(() -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
                    return "{\"perm\":false}";
                }
                runOnUiThread(() -> moveTaskToBack(true));
                Privacy.screenJob = () -> { Privacy.screenJob = null; screenDone(); };
                Privacy.UI.postDelayed(Privacy.screenJob, 6000);
                return "{\"wait\":6}";
            }
            // Part 30/31: the ONE door for phone actions. Java checks Stop and the master switch itself, so the page cannot skip them.
            @JavascriptInterface public String act(String json) {
                if (AppLock.locked()) return "{\"ok\":false,\"err\":\"locked\"}";
                try {
                    JSONObject a = new JSONObject(json);
                    if (Privacy.stopped) return "{\"ok\":false,\"err\":\"stopped\"}";
                    if (!Privacy.control) return "{\"ok\":false,\"err\":\"off\"}";
                    String ty = a.optString("type");
                    if (java.util.Arrays.asList("click", "scroll", "swipe", "type", "back", "home", "current_app", "lock").contains(ty)) {  // Part 34: one step on the screen
                        if (ScreenService.live == null) { runOnUiThread(() -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))); return "{\"ok\":false,\"err\":\"perm\"}"; }
                        // a risky step runs only if the page says Hussain tapped Yes AND a real finger tap happened in the last 3 seconds
                        final boolean sure = a.optBoolean("confirmed") && System.currentTimeMillis() - touch < 3000;
                        runOnUiThread(() -> moveTaskToBack(true));  // the other app must be on the screen, not Jarvis
                        if (Privacy.actJob != null) Privacy.UI.removeCallbacks(Privacy.actJob);
                        Privacy.actJob = () -> {
                            Privacy.actJob = null;
                            if (Privacy.stopped || !Privacy.control) return;  // checked again at the moment of the step
                            ScreenService.act(a, sure, r -> actDone(ty, r));
                        };
                        Privacy.UI.postDelayed(Privacy.actJob, 1200);
                        return "{\"wait\":1}";
                    }
                    if (java.util.Arrays.asList("settings", "torch", "volume").contains(ty)) {  // Part 37: fixed settings pages, flashlight, music volume. Answer comes back at once, read from Android.
                        JSONObject r = PhoneSettings.run(MainActivity.this, a);
                        if (r.optBoolean("ok")) Privacy.used("apps");
                        try { r.put("type", ty); } catch (Exception e) { /* send what we have */ }
                        return r.toString();
                    }
                    if ("open_app".equals(a.optString("type"))) {
                        JSONObject r = Apps.open(MainActivity.this, a.optString("name"), a.optBoolean("exact"));
                        if (r.optBoolean("ok")) Privacy.used("apps");
                        return r.toString();
                    }
                } catch (Exception e) { /* fall through */ }
                return "{\"ok\":false,\"err\":\"unknown\"}";
            }
            // Part 36: turning the lock ON needs a phone screen lock; turning it OFF needs the Android prompt first
            @JavascriptInterface public String lockState() { return AppLock.state(MainActivity.this); }
            @JavascriptInterface public String appLock(boolean on) {
                if (AppLock.locked()) return "{\"ok\":false,\"err\":\"locked\"}";
                if (on) {
                    if (!AppLock.available(MainActivity.this)) return "{\"ok\":false,\"err\":\"nolock\"}";
                    AppLock.set(MainActivity.this, true);
                    return "{\"ok\":true}";
                }
                runOnUiThread(() -> { if (!AppLock.ask(MainActivity.this, AppLock.TURN_OFF, "Confirm to turn off the Jarvis app lock")) AppLock.set(MainActivity.this, false); });
                return "{\"ok\":true,\"wait\":true}";
            }
            @JavascriptInterface public String setControl(boolean on) { return Privacy.setControl(on); }
            @JavascriptInterface public String phoneInfo() { if (AppLock.locked()) return "{\"locked\":true}"; return PhoneInfo.json(MainActivity.this); }
            @JavascriptInterface public void saveToken(String t) {
                getSharedPreferences("j", 0).edit().putString("token", t).apply();
                // Part 27: ask for notifications once, now that reminders are used (Android 13+)
                if (Build.VERSION.SDK_INT >= 33 && !getSharedPreferences("j", 0).getBoolean("askedN", false) && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                    getSharedPreferences("j", 0).edit().putBoolean("askedN", true).apply();
                    runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 5));
                }
                runOnUiThread(() -> startForegroundService(new Intent(MainActivity.this, NotifyService.class)));
            }
        }, "JarvisApp");
        wantListen = LISTEN.equals(getIntent().getAction());
        web.loadUrl(URL);
    }

    @Override protected void onNewIntent(Intent i) {
        super.onNewIntent(i);
        setIntent(i);
        wantListen = LISTEN.equals(i.getAction());  // handled in onResume, after the app lock
    }

    static String pending;  // screen text waiting to be handed to the page
    static String pendingAct;  // Part 34: result of the last screen step, waiting to be shown in the chat
    static volatile long touch;  // time of the last finger tap (Part 28: needed to switch Jarvis on again)

    @Override public boolean dispatchTouchEvent(MotionEvent e) {
        if (e.getAction() == MotionEvent.ACTION_UP) touch = System.currentTimeMillis();
        return super.dispatchTouchEvent(e);
    }

    /** Part 27: true only for the Jarvis page itself. */
    static boolean trusted(String origin) { return origin != null && origin.replaceAll("/+$", "").equals(URL); }

    void screenDone() {
        if (Privacy.stopped) return;
        Privacy.used("screen");
        pending = ScreenService.snapshot();
        try { startActivity(new Intent(this, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK)); }
        catch (Exception e) { /* the notification below still works */ }
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(NotifyService.ALERT, "Reminders", NotificationManager.IMPORTANCE_HIGH));
        nm.notify(77, new Notification.Builder(this, NotifyService.ALERT).setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle("Jarvis read your screen").setContentText("Tap to see the answer").setAutoCancel(true)
            .setContentIntent(PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE)).build());
    }

    /** Part 34: the step is done. The other app stays on screen so you can see it; the result waits in the chat and a notification brings you back. */
    void actDone(String type, JSONObject r) {
        if (Privacy.stopped) return;
        Privacy.used("apps");
        try { r.put("type", type); } catch (Exception e) { /* send what we have */ }
        pendingAct = r.toString();
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(NotifyService.ALERT, "Reminders", NotificationManager.IMPORTANCE_HIGH));
        nm.notify(78, new Notification.Builder(this, NotifyService.ALERT).setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle("Jarvis did the step").setContentText("Tap to see the result").setAutoCancel(true)
            .setContentIntent(PendingIntent.getActivity(this, 0, new Intent(this, MainActivity.class), PendingIntent.FLAG_IMMUTABLE)).build());
    }

    boolean asking, closing;

    /** Part 36: while the lock is on, the page stays hidden until Android's own prompt says yes. */
    void gate() {
        if (web == null || closing) return;
        if (!AppLock.locked()) { web.setVisibility(android.view.View.VISIBLE); AppLock.opened(); return; }
        web.setVisibility(android.view.View.INVISIBLE);
        if (asking) return;
        asking = true;
        if (!AppLock.ask(this, AppLock.ASK, "Unlock Jarvis")) { asking = false; AppLock.set(this, false); gate(); }
    }

    @Override protected void onPause() {
        super.onPause();
        AppLock.left();  // Android does not let apps listen from the background, so Hey Jarvis pauses here
        if (ears != null && ears.on) { ears.stop(); ears.js("onHeardErr", "Hey Jarvis paused because the app went to the background"); }
    }

    @Override protected void onResume() {
        super.onResume();
        gate();
        if (AppLock.locked()) return;  // nothing is handed to the page while it is locked
        if (wantListen) {  // Part 38: tile or shortcut. Same as tapping the mic: the page checks Stop itself.
            wantListen = false;
            web.postDelayed(() -> web.evaluateJavascript("document.getElementById('mic')&&document.getElementById('mic').click()", null), 900);
        }
        if (pendingAct != null && web != null) {
            String q = pendingAct; pendingAct = null;
            getSystemService(NotificationManager.class).cancel(78);
            web.evaluateJavascript("window.onActDone&&onActDone(" + JSONObject.quote(q) + ")", null);
        }
        if (pending != null && web != null) {
            String p = pending; pending = null;
            getSystemService(NotificationManager.class).cancel(77);
            web.evaluateJavascript("window.onScreen&&onScreen(" + JSONObject.quote(p) + ")", null);
        }
    }

    @Override protected void onActivityResult(int req, int res, Intent data) {
        if (req == AppLock.ASK) {
            asking = false;
            if (res == RESULT_OK) { AppLock.opened(); gate(); }
            else { closing = true; finish(); }  // cancelled or failed: the app closes, nothing is shown
        } else if (req == AppLock.TURN_OFF) {
            if (res == RESULT_OK) AppLock.set(this, false);
            web.evaluateJavascript("window.onLock&&onLock()", null);
        } else if (req == 7 && picker != null) { picker.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data)); picker = null; }
        else super.onActivityResult(req, res, data);
    }

    @Override public void onBackPressed() { if (web.canGoBack()) web.goBack(); else super.onBackPressed(); }
}
