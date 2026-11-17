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
import android.content.SharedPreferences;
import android.os.Handler;
import android.view.MotionEvent;
import android.os.Looper;
import android.provider.Settings;
import org.json.JSONArray;
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
            @JavascriptInterface public String calendar(String spec) {  // Part 44: events only when you ask, nothing saved
                if (AppLock.locked()) return "{\"locked\":true}";
                if (!allowed(Manifest.permission.READ_CALENDAR, 4)) return "{\"perm\":false}";
                Privacy.used("calendar");
                return CalendarInfo.events(MainActivity.this, spec);
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
            // Part 61: listen WHILE Jarvis speaks (interrupt). Same checks as listen(); the page asks only with earphones connected.
            @JavascriptInterface public void listenBarge(String lang) {
                if (AppLock.locked() || Privacy.stopped || !allowed(Manifest.permission.RECORD_AUDIO, 1)) return;
                runOnUiThread(() -> { if (ears == null) ears = new Ears(MainActivity.this, web); ears.start(lang, true, true); });
            }
            @JavascriptInterface public boolean headset() { return Ears.headset(MainActivity.this); }
            // Part 39: background listening TEST. Starts only after a real finger tap, never while locked or stopped. Counts only, keeps no words.
            @JavascriptInterface public String bgListen(boolean on) {
                if (AppLock.locked()) return "{\"ok\":false,\"err\":\"locked\"}";
                if (!on) { runOnUiThread(() -> ListenService.halt(MainActivity.this)); return "{\"ok\":true}"; }
                if (Privacy.stopped) return "{\"ok\":false,\"err\":\"stopped\"}";
                if (System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                if (!allowed(Manifest.permission.RECORD_AUDIO, 1)) return "{\"ok\":false,\"err\":\"perm\"}";
                if (!getSystemService(NotificationManager.class).areNotificationsEnabled()) return "{\"ok\":false,\"err\":\"notif\"}";
                if (!android.speech.SpeechRecognizer.isRecognitionAvailable(MainActivity.this)) return "{\"ok\":false,\"err\":\"nospeech\"}";
                runOnUiThread(() -> {
                    if (ears != null) ears.stop();  // one listener at a time
                    try { startForegroundService(new Intent(MainActivity.this, ListenService.class)); } catch (Exception e) { /* Android refused; info() shows the reason */ }
                });
                return "{\"ok\":true}";
            }
            // Part 42: a task (up to 6 steps) runs here in Java; the result is handed to the page when you come back. Cancel always works.
            @JavascriptInterface public String runTask(String json) { return TaskRunner.start(MainActivity.this, json); }
            @JavascriptInterface public String cancelTask() { TaskRunner.cancel = true; return "{\"ok\":true}"; }
            @JavascriptInterface public String bgInfo() { if (AppLock.locked()) return "{\"locked\":true}"; return ListenService.info(MainActivity.this); }
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
                    if (java.util.Arrays.asList("click", "click_nth", "scroll", "swipe", "type", "back", "home", "current_app", "lock").contains(ty)) {  // Part 34: one step on the screen
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
                    if (java.util.Arrays.asList("alarm", "timer", "search", "media").contains(ty)) {  // Part 66 and Part 60: alarm, timer, search inside an app (fixed addresses built in QuickSet)
                        JSONObject r = QuickSet.run(MainActivity.this, a);
                        if (r.optBoolean("ok")) Privacy.used("apps");
                        try { r.put("type", ty); } catch (Exception e) { /* send what we have */ }
                        return r.toString();
                    }
                    if ("call".equals(ty)) {  // Part 64: call by name. Contacts permission first (only to look the name up), then CallByName asks for the call permission itself.
                        if (a.optString("number").isEmpty() && !allowed(Manifest.permission.READ_CONTACTS, 3)) return "{\"ok\":false,\"err\":\"perm\",\"perm\":true,\"what\":\"contacts\"}";
                        JSONObject r = CallByName.run(MainActivity.this, a);
                        if (r.optBoolean("ok")) Privacy.used("contacts");
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
            // Part 48: Share to Jarvis (in), handoff summary (out), two fixed help links. Nothing is sent anywhere by Jarvis: Android's own share sheet or browser opens and Hussain picks.
            @JavascriptInterface public String takeShare() {
                if (AppLock.locked() || sharedText == null) return "";
                String t = sharedText; sharedText = null;
                return JSONObject.quote(t);
            }
            @JavascriptInterface public String shareOut(String t) {
                if (AppLock.locked() || t == null || t.length() > 8000 || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false}";
                runOnUiThread(() -> { try { Intent s = new Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, t); startActivity(Intent.createChooser(s, "Share handoff summary")); } catch (Exception e) {} });
                return "{\"ok\":true}";
            }
            @JavascriptInterface public String openLink(String k) {
                String u = "findhub".equals(k) ? "https://www.google.com/android/find" : "sanchar".equals(k) ? "https://sancharsaathi.gov.in" : null;
                if (AppLock.locked() || u == null || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false}";
                runOnUiThread(() -> { try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(u))); } catch (Exception e) {} });
                return "{\"ok\":true}";
            }
            // Part 40: offline wake word model (download only after your tap) and the switch that makes the background listener use it
            @JavascriptInterface public String wakeInfo() { if (AppLock.locked()) return "{\"locked\":true}"; return WakeEngine.info(MainActivity.this); }
            @JavascriptInterface public String wakeDownload() {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                WakeEngine.download(MainActivity.this);
                return "{\"ok\":true}";
            }
            @JavascriptInterface public String wakeUse(boolean on) {
                if (AppLock.locked() || (on && !WakeEngine.ready(MainActivity.this))) return "{\"ok\":false}";
                getSharedPreferences("j", 0).edit().putBoolean("wk_vosk", on).apply();
                return "{\"ok\":true}";
            }
            @JavascriptInterface public String wakeDelete() {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false}";
                runOnUiThread(() -> ListenService.halt(MainActivity.this));
                WakeEngine.remove(MainActivity.this);
                return "{\"ok\":true}";
            }
            // Part 49a: clipboard, read only when you tap the button (Android also allows it only while Jarvis is on screen)
            @JavascriptInterface public String clipboard() {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "";
                try {
                    android.content.ClipboardManager cm = getSystemService(android.content.ClipboardManager.class);
                    android.content.ClipData d = cm == null ? null : cm.getPrimaryClip();
                    CharSequence t = d == null || d.getItemCount() == 0 ? null : d.getItemAt(0).coerceToText(MainActivity.this);
                    if (t == null || t.toString().trim().isEmpty()) return "";
                    String x = t.toString();
                    return JSONObject.quote(x.length() > 4000 ? x.substring(0, 4000) : x);
                } catch (Exception e) { return ""; }
            }
            // Part 49b: notification summary. Off by default; the tap rule (3 s) applies to every change; reading needs a tap too.
            @JavascriptInterface public String nsInfo() {
                if (AppLock.locked()) return "{\"locked\":true}";
                try {
                    SharedPreferences p = getSharedPreferences("j", 0);
                    String en = android.provider.Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");
                    return new JSONObject().put("access", en != null && en.contains(getPackageName())).put("on", p.getBoolean("ns_on", false)).put("up", NotifySummary.up)
                        .put("count", NotifySummary.count()).put("apps", new JSONArray(p.getStringSet("ns_apps", new java.util.HashSet<String>()))).toString();
                } catch (Exception e) { return "{}"; }
            }
            @JavascriptInterface public String nsAccess() {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                runOnUiThread(() -> { try { startActivity(new Intent(android.provider.Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); } catch (Exception e) {} });
                return "{\"ok\":true}";
            }
            @JavascriptInterface public String nsSet(boolean on) {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                getSharedPreferences("j", 0).edit().putBoolean("ns_on", on).apply();
                if (!on) NotifySummary.clear();
                return "{\"ok\":true}";
            }
            // Part 82: payment app list. Adding or removing needs a real finger tap (same 3 s rule as the other Settings changes).
            @JavascriptInterface public String payInfo() { if (AppLock.locked()) return "{\"locked\":true}"; return PaymentGuard.json(getSharedPreferences("j", 0)); }
            @JavascriptInterface public String payAdd(String pkg) {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                if (pkg == null || pkg.equals(getPackageName())) return "{\"ok\":false,\"err\":\"bad\"}";
                boolean ok = PaymentGuard.add(getSharedPreferences("j", 0), pkg.trim());
                if (ok) Privacy.event(MainActivity.this, "pay_edit");
                return "{\"ok\":" + ok + "}";
            }
            @JavascriptInterface public String payRemove(String pkg) {
                if (AppLock.locked() || pkg == null || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                boolean ok = PaymentGuard.remove(getSharedPreferences("j", 0), pkg.trim());
                if (ok) Privacy.event(MainActivity.this, "pay_edit");
                return "{\"ok\":" + ok + "}";
            }
            @JavascriptInterface public String nsAppList() { if (AppLock.locked()) return "[]"; return Apps.list(MainActivity.this).toString(); }
            @JavascriptInterface public String nsChoose(String json) {
                if (AppLock.locked() || json == null || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false,\"err\":\"tap\"}";
                try {
                    JSONArray a = new JSONArray(json);
                    SharedPreferences p = getSharedPreferences("j", 0);
                    SharedPreferences.Editor ed = p.edit();
                    java.util.HashSet<String> set = new java.util.HashSet<>();
                    for (int i = 0; i < Math.min(15, a.length()); i++) {
                        JSONObject o = a.getJSONObject(i);
                        String pk = o.optString("p");
                        if (pk.isEmpty() || pk.equals(getPackageName())) continue;
                        set.add(pk);
                        ed.putString("ns_l_" + pk, o.optString("l", pk));
                    }
                    ed.putStringSet("ns_apps", set).apply();
                    NotifySummary.keepOnly(set, getSharedPreferences("j", 0));
                    return "{\"ok\":true}";
                } catch (Exception e) { return "{\"ok\":false}"; }
            }
            @JavascriptInterface public String nsRead() {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "";
                return NotifySummary.json();
            }
            @JavascriptInterface public String nsClear() {
                if (AppLock.locked() || System.currentTimeMillis() - touch > 3000) return "{\"ok\":false}";
                NotifySummary.clear();
                return "{\"ok\":true}";
            }
            @JavascriptInterface public String placeSet(String json) { if (AppLock.locked()) return "{\"locked\":true}"; return PlaceWatch.set(MainActivity.this, json); }  // Part 113: places and reminders; the position never leaves PlaceWatch
            @JavascriptInterface public String btPaired() { if (AppLock.locked()) return "{\"locked\":true}"; return PlaceWatch.paired(MainActivity.this); }  // Part 114: paired Bluetooth names only
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
        takeShare(getIntent());
        if (TaskRunner.CANCEL.equals(getIntent().getAction())) TaskRunner.cancel = true;
        web.loadUrl(URL);
    }

    @Override protected void onNewIntent(Intent i) {
        super.onNewIntent(i);
        setIntent(i);
        wantListen = LISTEN.equals(i.getAction());  // handled in onResume, after the app lock
        takeShare(i);
        if (TaskRunner.CANCEL.equals(i.getAction())) TaskRunner.cancel = true;  // Part 42: the Cancel button of the task notification
    }

    static String sharedText;  // Part 48: text another app shared to Jarvis; the page takes it with takeShare() after the app lock

    void takeShare(Intent i) {
        if (i == null || !Intent.ACTION_SEND.equals(i.getAction())) return;
        String t = i.getStringExtra(Intent.EXTRA_TEXT);
        if (t != null && t.trim().length() > 0) sharedText = t.length() > 4000 ? t.substring(0, 4000) : t;
    }

    static String pending;  // screen text waiting to be handed to the page
    static String pendingTask;  // Part 42: result of the last task, waiting to be shown in the chat
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

    static MainActivity cur;  // Part 40: the offline listener opens the mic through this when Jarvis is on screen
    static volatile boolean visible;  // Part 39: the background test counts how often "Jarvis" was heard with the app NOT on screen
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
        visible = false;
        if (cur == this) cur = null;
        AppLock.left();  // Android does not let apps listen from the background, so Hey Jarvis pauses here
        if (ears != null && ears.on) { ears.stop(); ears.js("onHeardErr", "Hey Jarvis paused because the app went to the background"); }
    }

    @Override public void onRequestPermissionsResult(int code, String[] perms, int[] res) {
        super.onRequestPermissionsResult(code, perms, res);
        if ((code == 6 || code == 7) && res.length > 0 && res[0] == PackageManager.PERMISSION_GRANTED) PlaceWatch.resume(this, false);  // Parts 113, 114: start the watch as soon as Android says yes
    }

    @Override protected void onResume() {
        super.onResume();
        visible = true;
        cur = this;
        PlaceWatch.resume(this, false);  // Parts 113, 114: brings the watch back after a restart (does nothing when no reminder exists)
        gate();
        if (AppLock.locked()) return;  // nothing is handed to the page while it is locked
        if (wantListen) {  // Part 38: tile or shortcut. Same as tapping the mic: the page checks Stop itself.
            wantListen = false;
            web.postDelayed(() -> web.evaluateJavascript("window.go&&go('chat');document.getElementById('mic')&&document.getElementById('mic').click()", null), 900);
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
        deliverTask();
    }

    /** Part 40: same as tapping the mic (the page checks Stop itself). Opening the mic ends the background listener, one listener at a time. */
    void wakeTalk() {
        if (AppLock.locked() || Privacy.stopped || web == null) return;
        web.evaluateJavascript("window.go&&go('chat');document.getElementById('mic')&&document.getElementById('mic').click()", null);
    }

    /** Part 42: hands the finished task to the page (called when Jarvis is on screen again). */
    void deliverTask() {
        if (pendingTask == null || web == null) return;
        String p = pendingTask; pendingTask = null;
        getSystemService(NotificationManager.class).cancel(81);
        web.evaluateJavascript("window.onTaskDone&&onTaskDone(" + JSONObject.quote(p) + ")", null);
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
