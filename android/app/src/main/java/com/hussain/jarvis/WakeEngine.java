package com.hussain.jarvis;

import android.content.Context;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FilterInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.json.JSONObject;
import org.vosk.Model;
import org.vosk.Recognizer;

/** Part 40: offline "Jarvis" listener (Vosk small English model, runs on the phone, no Google speech service, no internet while listening).
 *  The model (about 40 MB) is downloaded ONLY after your tap, from the Vosk project (https only). It only looks for the word and drops everything else:
 *  no words are saved, shown or sent anywhere. Mic is used only while ListenService runs (notification with Stop). */
final class WakeEngine {
    static final String MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", NAME = "vosk-model-small-en-us-0.15";
    static final Pattern WAKE = Pattern.compile("jarvis|jar vis|jarvish|jervis|jarvas", Pattern.CASE_INSENSITIVE);
    interface Cb { void heard(); void failed(String why); }
    static volatile boolean downloading;
    static volatile int pct;
    static volatile String err = "";
    private volatile boolean run;

    static File dir(Context c) { return new File(c.getFilesDir(), "vosk/" + NAME); }
    static boolean ready(Context c) { return new File(dir(c), "ok").exists(); }

    static void wipe(File f) {
        File[] k = f.listFiles();
        if (k != null) for (File x : k) wipe(x);
        f.delete();
    }

    static void remove(Context c) { wipe(new File(c.getFilesDir(), "vosk")); c.getSharedPreferences("j", 0).edit().putBoolean("wk_vosk", false).apply(); }

    static String info(Context c) {
        JSONObject o = new JSONObject();
        try { o.put("ready", ready(c)).put("downloading", downloading).put("pct", pct).put("err", err).put("use", c.getSharedPreferences("j", 0).getBoolean("wk_vosk", false)); } catch (Exception e) { /* send what we have */ }
        return o.toString();
    }

    /** Counts the bytes that came from the internet so the page can show a percentage. */
    static final class Count extends FilterInputStream {
        long n;
        Count(InputStream i) { super(i); }
        @Override public int read() throws IOException { int b = super.read(); if (b >= 0) n++; return b; }
        @Override public int read(byte[] b, int o, int l) throws IOException { int r = super.read(b, o, l); if (r > 0) n += r; return r; }
    }

    /** Starts the download on its own thread. Called only after a finger tap (checked in MainActivity). */
    static void download(Context c) {
        if (downloading || ready(c)) return;
        downloading = true; pct = 0; err = "";
        final Context app = c.getApplicationContext();
        new Thread(() -> {
            File base = new File(app.getFilesDir(), "vosk");
            try {
                wipe(base); base.mkdirs();
                HttpURLConnection h = (HttpURLConnection) new URL(MODEL_URL).openConnection();
                h.setConnectTimeout(15000); h.setReadTimeout(30000);
                if (h.getResponseCode() != 200) throw new IOException("download server said " + h.getResponseCode());
                long total = h.getContentLengthLong(), out = 0;
                Count cnt = new Count(h.getInputStream());
                String root = base.getCanonicalPath() + File.separator;
                try (ZipInputStream z = new ZipInputStream(new BufferedInputStream(cnt))) {
                    ZipEntry e; byte[] buf = new byte[16384];
                    while ((e = z.getNextEntry()) != null) {
                        File f = new File(base, e.getName());
                        if (!f.getCanonicalPath().startsWith(root)) throw new IOException("bad path inside the zip");
                        if (e.isDirectory()) { f.mkdirs(); continue; }
                        f.getParentFile().mkdirs();
                        try (FileOutputStream o = new FileOutputStream(f)) {
                            int n;
                            while ((n = z.read(buf)) > 0) { o.write(buf, 0, n); out += n; if (out > 250_000_000L) throw new IOException("download too big"); }
                        }
                        if (total > 0) pct = (int) Math.min(99, 100 * cnt.n / total);
                    }
                }
                File d = dir(app);
                if (!new File(d, "am/final.mdl").exists()) throw new IOException("model files are missing after the download");
                new File(d, "ok").createNewFile();
                pct = 100;
            } catch (Exception e) {
                err = "download failed: " + e.getMessage();
                wipe(base);
            } finally { downloading = false; }
        }, "wake-download").start();
    }

    /** Runs the listener on its own thread until stop(). Only a yes/no ("Jarvis heard") leaves this class. */
    void start(Context c, Cb cb) {
        if (run) return;
        run = true;
        new Thread(() -> loop(c.getApplicationContext(), cb), "wake-engine").start();
    }

    void stop() { run = false; }

    private void loop(Context c, Cb cb) {
        AudioRecord ar = null; Model m = null; Recognizer r = null; String bad = null;
        try {
            m = new Model(dir(c).getAbsolutePath());
            r = new Recognizer(m, 16000f);
            int min = AudioRecord.getMinBufferSize(16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
            ar = new AudioRecord(MediaRecorder.AudioSource.MIC, 16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, Math.max(min, 4096) * 2);
            if (ar.getState() != AudioRecord.STATE_INITIALIZED) throw new IllegalStateException("microphone is busy or not allowed");
            ar.startRecording();
            short[] b = new short[2048];
            long last = 0;
            while (run && !Privacy.stopped) {
                int n = ar.read(b, 0, b.length);
                if (n < 0) throw new IllegalStateException("microphone read error " + n);
                if (n == 0) continue;
                String j = r.acceptWaveForm(b, n) ? r.getResult() : r.getPartialResult();
                if (WAKE.matcher(j).find() && System.currentTimeMillis() - last > 4000) {  // 4 s pause so one "Jarvis" is counted once
                    last = System.currentTimeMillis();
                    r.reset();
                    cb.heard();
                }
            }
        } catch (Throwable e) { bad = "offline engine: " + e.getMessage(); }
        finally {
            run = false;
            try { if (ar != null) { ar.stop(); ar.release(); } } catch (Exception e) { /* already closed */ }
            try { if (r != null) r.close(); } catch (Throwable e) { /* ignore */ }
            try { if (m != null) m.close(); } catch (Throwable e) { /* ignore */ }
        }
        if (bad != null) cb.failed(bad);
    }
}
