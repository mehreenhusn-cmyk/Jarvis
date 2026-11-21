"""Part 200b: fine-tune a Piper Hindi voice on your own voice set (the zip from Jarvis Settings > Voice > Export). Run this in Google Colab, NOT on the phone.

HOW (about 5 clicks):
 1. colab.research.google.com > New notebook > Runtime > Change runtime type > T4 GPU.
 2. Left side Files icon > upload `jarvis_voiceset_<name>.zip` and this file (train_voice.py) into /content.
 3. In a cell run:   !python train_voice.py
 4. If Colab disconnects, upload the zip + this file again and run again: it continues from the last saved checkpoint while /content is alive.
 5. At the end it downloads `jarvis_voice.zip` (jarvis_voice.onnx + jarvis_voice.onnx.json + test.wav). Listen to test.wav, then give the zip to Part 200c.
Only the Piper training code and the open Hindi starting model are downloaded. Your audio stays in your Colab. Not run by Claude: untested on a real GPU.
"""
import glob, os, re, shutil, subprocess, sys, zipfile

BASE_VOICE = "priyamvada"  # starting model: priyamvada, pratham or rohan (open Hindi Piper voices). Pick the one closest to the Sarvam voice
EXTRA_EPOCHS = 500         # how many epochs to train on top of the starting model (more = closer to your voice, slower)
BATCH = 16                 # lower to 8 if Colab says CUDA out of memory
MIN_MINUTES = 20           # below this the copy will sound bad; the script only warns
W = "/content/jv"          # work folder
ONLY_DEVANAGARI = False    # True = drop sentences with no Hindi letters (Roman-only text may be read badly by the Hindi phonemizer)


def sh(cmd, check=True, **kw):
    print("\n$", cmd, flush=True)
    r = subprocess.run(cmd, shell=True, **kw)
    if check and r.returncode:
        sys.exit("FAILED (%d): %s" % (r.returncode, cmd))
    return r


def setup():
    if not os.path.isdir(W + "/piper1-gpl"):
        os.makedirs(W, exist_ok=True)
        sh("apt-get -qq install -y espeak-ng ffmpeg > /dev/null")
        sh("git clone -q https://github.com/OHF-Voice/piper1-gpl.git " + W + "/piper1-gpl")
        sh("cd %s/piper1-gpl && pip install -q -e '.[train]' onnxscript huggingface_hub" % W)
        sh("cd %s/piper1-gpl && chmod +x build_monotonic_align.sh && ./build_monotonic_align.sh && python3 setup.py build_ext --inplace" % W)
    # new PyTorch needs dynamo=False in the ONNX export (the new exporter fails on this model); add it once
    p = W + "/piper1-gpl/src/piper/train/export_onnx.py"
    s = open(p, encoding="utf-8").read()
    if "dynamo=False" not in s:
        n = re.sub(r"(opset_version\s*=\s*[A-Za-z_0-9]+,)", r"\1 dynamo=False,", s, count=1)
        if n != s:
            open(p, "w", encoding="utf-8").write(n)
        else:
            print("NOTE: could not patch export_onnx.py; if the export fails, see piper1-gpl issues about dynamo=False")


def data():
    zs = glob.glob("/content/jarvis_voiceset_*.zip")
    if not zs:
        sys.exit("Upload jarvis_voiceset_<name>.zip into /content first (Files icon on the left).")
    raw, aud = W + "/raw", W + "/audio"
    shutil.rmtree(raw, ignore_errors=True)
    shutil.rmtree(aud, ignore_errors=True)
    os.makedirs(aud)
    zipfile.ZipFile(zs[0]).extractall(raw)
    rows, secs = [], 0.0
    for line in open(raw + "/metadata.csv", encoding="utf-8"):
        i, _, t = line.rstrip("\n").partition("|")
        src = "%s/wavs/%s.wav" % (raw, i)
        if not t or not os.path.exists(src):
            continue
        if ONLY_DEVANAGARI and not re.search("[\u0900-\u097F]", t):
            continue
        # Piper wants 22050 Hz, mono, 16 bit
        r = sh("ffmpeg -y -loglevel error -i %s -ar 22050 -ac 1 -sample_fmt s16 %s/%s.wav" % (src, aud, i), check=False)
        if r.returncode == 0:
            rows.append("%s.wav|%s\n" % (i, t))
    open(W + "/metadata.csv", "w", encoding="utf-8").writelines(rows)
    import wave
    for f in glob.glob(aud + "/*.wav"):
        with wave.open(f) as w:
            secs += w.getnframes() / float(w.getframerate())
    print("\nSentences: %d, audio: %.1f minutes" % (len(rows), secs / 60))
    if not rows:
        sys.exit("No usable sentences in the zip.")
    if secs / 60 < MIN_MINUTES:
        print("WARNING: less than %d minutes. It will run, but the voice will be weak. Collect more in Jarvis and export again." % MIN_MINUTES)


def base_ckpt():
    from huggingface_hub import HfApi, hf_hub_download
    fs = [f for f in HfApi().list_repo_files("rhasspy/piper-checkpoints", repo_type="dataset")
          if f.startswith("hi/") and f.endswith(".ckpt") and "/%s/" % BASE_VOICE in f]
    if not fs:
        sys.exit("No Hindi starting model named %s found. Change BASE_VOICE at the top." % BASE_VOICE)
    print("Starting model:", fs[0])
    return hf_hub_download("rhasspy/piper-checkpoints", fs[0], repo_type="dataset")


def newest(pattern):
    fs = glob.glob(pattern, recursive=True)
    return max(fs, key=os.path.getmtime) if fs else ""


def train():
    if subprocess.run("nvidia-smi -L", shell=True, capture_output=True).returncode:
        sys.exit("No GPU. Colab: Runtime > Change runtime type > T4 GPU, then run again.")
    out = W + "/train"
    last = newest(out + "/**/checkpoints/*.ckpt")  # continue after a disconnect
    start = last or base_ckpt()
    m = re.search(r"epoch=(\d+)", os.path.basename(start))
    done = int(m.group(1)) if m else 2000  # the starting model already has its own epochs; the counter continues from there
    target = (done + EXTRA_EPOCHS) if not last else max(done + 1, _target_from_marker(done))
    open(W + "/target_epoch", "w").write(str(target))
    sh("cd %s/piper1-gpl && python3 -m piper.train fit --data.voice_name jarvis --data.csv_path %s/metadata.csv "
       "--data.audio_dir %s/audio --model.sample_rate 22050 --data.espeak_voice hi --data.cache_dir %s/cache "
       "--data.config_path %s/config.json --data.batch_size %d --ckpt_path %s "
       "--trainer.max_epochs %d --trainer.default_root_dir %s --trainer.accelerator gpu --trainer.devices 1"
       % (W, W, W, W, W, BATCH, start, target, out))


def _target_from_marker(done):
    try:
        return int(open(W + "/target_epoch").read())  # the goal set on the first run stays the same after a restart
    except (OSError, ValueError):
        return done + EXTRA_EPOCHS


def export():
    ck = newest(W + "/train/**/checkpoints/*.ckpt")
    if not ck:
        sys.exit("No checkpoint was saved, nothing to export.")
    o = W + "/jarvis_voice"
    shutil.rmtree(o, ignore_errors=True)
    os.makedirs(o)
    sh("cd %s/piper1-gpl && python3 -m piper.train.export_onnx --checkpoint %s --output-file %s/jarvis_voice.onnx" % (W, ck, o))
    shutil.copy(W + "/config.json", o + "/jarvis_voice.onnx.json")
    sh("cd %s && echo 'नमस्ते, मैं जार्विस हूँ। आज मैं आपकी क्या मदद करूँ?' | python3 -m piper -m jarvis_voice.onnx -f test.wav" % o, check=False)
    z = shutil.make_archive(W + "/jarvis_voice", "zip", o)
    print("\nDONE:", z)
    try:
        from google.colab import files
        files.download(z)
    except Exception:
        print("Download it from the Files icon on the left.")


if __name__ == "__main__":
    setup()
    data()
    train()
    export()
