"""Jarvis system card (Part 50): numbers only. RAM, storage, and how much THIS Jarvis server uses. Nothing is saved, nothing leaves the phone.
Every number is optional: if Android blocks a file, that key is simply missing and the page shows "not available"."""
import os, re, shutil, time

_T0 = (time.time(), sum(os.times()[:2]))  # server start, for the first CPU reading
_last = [_T0]


def _num(path, key):
    try:
        for ln in open(path):
            if ln.startswith(key):
                return int(re.search(r"\d+", ln).group())
    except Exception:
        pass
    return None


def stats():
    """Dict of numbers. Never raises."""
    o = {}
    t, f = _num("/proc/meminfo", "MemTotal"), _num("/proc/meminfo", "MemAvailable")
    if t and f is not None:
        o["ram_total"], o["ram_free"] = t * 1024, f * 1024
    rss = _num("/proc/self/status", "VmRSS")
    if rss:
        o["srv_ram"] = rss * 1024
    th = _num("/proc/self/status", "Threads")
    if th:
        o["srv_threads"] = th
    try:  # CPU of this server only, in percent of one core, since the last reading
        now, cpu = time.time(), sum(os.times()[:2])
        t0, c0 = _last[0]
        if now - t0 >= 1:
            o["srv_cpu"] = round(max(0.0, 100.0 * (cpu - c0) / (now - t0)), 1)
            _last[0] = (now, cpu)
        else:
            o["srv_cpu"] = None
    except Exception:
        pass
    try:
        d = shutil.disk_usage(os.path.expanduser("~"))
        o["disk_total"], o["disk_free"] = d.total, d.free
    except Exception:
        pass
    try:
        o["load"] = [float(x) for x in open("/proc/loadavg").read().split()[:3]]
    except Exception:
        pass
    return o
