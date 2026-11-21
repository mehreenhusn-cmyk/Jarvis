package com.hussain.jarvis;

import android.content.Context;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.json.JSONArray;
import org.json.JSONObject;
import org.vosk.Model;
import org.vosk.Recognizer;
import org.vosk.SpeakerModel;

/** Part 144: "who is speaking". Records a few seconds ONLY when the page asks (you said the words), turns the voice into 128 numbers with the
 *  Vosk speaker model (about 13 MB, downloaded only after your tap) and hands just those numbers to the page. No recording is kept, no words are kept.
 *  The numbers are saved by the server only after the person said yes. Needs the small Vosk model of Part 40 too (it recognizes the speech around the voice). */
final class SpeakerId {
    static final String MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip", NAME = "vosk-model-spk-0.4";
    interface Cb { void done(String json); }
    static volatile boolean downloading, busy;
    static volatile int pct;
    static volatile String err = "";

    static File dir(Context c) { return new File(c.getFilesDir(), "spk/" + NAME); }  // its own folder: the Part 40 download wipes the folder "vosk"
    static boolean modelReady(Context c) { return new File(dir(c), "ok").exists(); }
    static boolean ready(Context c) { return modelReady(c) && WakeEngine.ready(c); }

    static String info(Context c) {
        JSONObject o = new JSONObject();
        try { o.put("ready", ready(c)).put("spk", modelReady(c)).put("en", WakeEngine.ready(c)).put("downloading", downloading).put("pct", pct).put("err", err); } catch (Exception e) { /* send what we have */ }
        return o.toString();
    }

    static void remove(Context c) { WakeEngine.wipe(new File(c.getFilesDir(), "spk")); }

    /** Starts the download on its own thread. Called only after a finger tap (checked in MainActivity). */
    static void download(Context c) {
        if (downloading || modelReady(c)) return;
        downloading = true; pct = 0; err = "";
        final Context app = c.getApplicationContext();
        new Thread(() -> {
            File base = new File(app.getFilesDir(), "spk");
            try {
                WakeEngine.wipe(base); base.mkdirs();
                HttpURLConnection h = (HttpURLConnection) new URL(MODEL_URL).openConnection();
                h.setConnectTimeout(15000); h.setReadTimeout(30000);
                if (h.getResponseCode() != 200) throw new IOException("download server said " + h.getResponseCode());
                long total = h.getContentLengthLong(), out = 0;
                WakeEngine.Count cnt = new WakeEngine.Count(h.getInputStream());
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
                            while ((n = z.read(buf)) > 0) { o.write(buf, 0, n); out += n; if (out > 100_000_000L) throw new IOException("download too big"); }
                        }
                        if (total > 0) pct = (int) Math.min(99, 100 * cnt.n / total);
                    }
                }
                String[] k = dir(app).list();
                if (k == null || k.length < 3) throw new IOException("model files are missing after the download");
                new File(dir(app), "ok").createNewFile();
                pct = 100;
            } catch (Exception e) {
                err = "download failed: " + e.getMessage();
                WakeEngine.wipe(base);
            } finally { downloading = false; }
        }, "spk-download").start();
    }

    /** Listens for sec seconds (3 to 8) and answers once with {"ok":true,"vec":[...128 numbers],"frames":N} or {"ok":false,"err":"..."}. */
    static boolean capture(Context c, int sec, Cb cb) {
        if (busy || !ready(c)) return false;
        busy = true;
        final Context app = c.getApplicationContext();
        final int ms = Math.max(3, Math.min(8, sec)) * 1000;
        new Thread(() -> {
            String res;
            AudioRecord ar = null; Model m = null; SpeakerModel sm = null; Recognizer r = null;
            try {
                Thread.sleep(700);  // the other microphone user (Ears or the background listener) needs a moment to let go
                m = new Model(WakeEngine.dir(app).getAbsolutePath());
                sm = new SpeakerModel(dir(app).getAbsolutePath());
                r = new Recognizer(m, 16000f, sm);
                int min = AudioRecord.getMinBufferSize(16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
                ar = new AudioRecord(MediaRecorder.AudioSource.MIC, 16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, Math.max(min, 4096) * 2);
                if (ar.getState() != AudioRecord.STATE_INITIALIZED) throw new IllegalStateException("microphone is busy or not allowed");
                ar.startRecording();
                short[] b = new short[2048];
                long end = System.currentTimeMillis() + ms;
                java.util.ArrayList<Double> lv = new java.util.ArrayList<>();  // Part 192: loudness of each short piece, to tell a noisy room (fan) from a quiet one
                while (System.currentTimeMillis() < end && !Privacy.stopped) {
                    int n = ar.read(b, 0, b.length);
                    if (n < 0) throw new IllegalStateException("microphone read error " + n);
                    if (n > 0) {
                        r.acceptWaveForm(b, n);
                        long sq = 0;
                        for (int i = 0; i < n; i++) sq += (long) b[i] * b[i];
                        lv.add(Math.sqrt(sq / (double) n));
                    }
                }
                if (Privacy.stopped) throw new IllegalStateException("Jarvis is stopped");
                JSONObject o = new JSONObject(r.getFinalResult());
                JSONArray v = o.optJSONArray("spk");
                int fr = o.optInt("spk_frames", 0);
                double snr = 0;  // Part 192: loud pieces divided by quiet pieces. Near 1 = the room is as loud as you (fan, traffic); 3 or more = a quiet room
                if (lv.size() >= 10) {
                    java.util.Collections.sort(lv);
                    int k = Math.max(1, lv.size() / 5);
                    double lo = 0, hi = 0;
                    for (int i = 0; i < k; i++) { lo += lv.get(i); hi += lv.get(lv.size() - 1 - i); }
                    snr = (hi / k) / Math.max(1.0, lo / k);
                }
                if (v == null || fr < 100) res = new JSONObject().put("ok", false).put("err", "too little speech heard, try again closer to the phone").toString();
                else res = new JSONObject().put("ok", true).put("vec", v).put("frames", fr).put("snr", Math.round(snr * 10) / 10.0).toString();
            } catch (Throwable e) {
                try { res = new JSONObject().put("ok", false).put("err", "voice check: " + e.getMessage()).toString(); } catch (Exception x) { res = "{\"ok\":false}"; }
            } finally {
                try { if (ar != null) { ar.stop(); ar.release(); } } catch (Exception e) { /* already closed */ }
                try { if (r != null) r.close(); } catch (Throwable e) { /* ignore */ }
                try { if (sm != null) sm.close(); } catch (Throwable e) { /* ignore */ }
                try { if (m != null) m.close(); } catch (Throwable e) { /* ignore */ }
                busy = false;
            }
            cb.done(res);
        }, "spk-capture").start();
        return true;
    }
}
