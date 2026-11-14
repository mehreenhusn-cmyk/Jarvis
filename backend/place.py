"""Jarvis location (Part 21). The page sends the phone position ONLY when you ask (where am I / near me). Never stored."""
import json, re, urllib.request

ASK = re.compile(r"where am i|my location|near me|nearby|around me|nearest|mere paas|मैं कहाँ हूँ|मेरे पास", re.I)
HERE = re.compile(r"where am i|my location|मैं कहाँ हूँ", re.I)


def parse(loc):
    """Check what the page sent. Returns (lat, lon, accuracy_m) or None."""
    try:
        la, lo = float(loc["lat"]), float(loc["lon"])
        if -90 <= la <= 90 and -180 <= lo <= 180:
            return la, lo, int(float(loc.get("acc", 0)))
    except (TypeError, KeyError, ValueError):
        pass
    return None


def name(la, lo):
    """Place name from OpenStreetMap. Empty text if the internet fails."""
    try:
        req = urllib.request.Request(f"https://nominatim.openstreetmap.org/reverse?format=json&zoom=16&lat={la:.5f}&lon={lo:.5f}",
                                     headers={"User-Agent": "JarvisPersonalAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return str(json.load(r).get("display_name", ""))[:200]
    except Exception:
        return ""


def handle(msg, loc, hindi):
    """Reply to 'where am I'. Other 'near me' questions go to the AI with context() below."""
    if not HERE.search(msg):
        return None
    p = parse(loc)
    if not p:
        return "सर, मुझे आपकी लोकेशन नहीं मिली। लोकेशन की अनुमति दीजिए और फिर पूछिए।" if hindi else \
            "Sir, I could not get your location. Allow location access and ask again."
    n = name(p[0], p[1])
    t = f"{p[0]:.4f}, {p[1]:.4f} (±{p[2]} m)"
    return (f"सर, आप यहाँ हैं: {n or t}" if hindi else f"Sir, you are near: {n or t}") + ("\n" + t if n else "")


def context(msg, loc):
    """For other location questions: give the AI the position and say it has no live map data."""
    if not ASK.search(msg) or HERE.search(msg):
        return ""
    p = parse(loc)
    if not p:
        return "\n\n[The user asked about their surroundings but location was not shared. Say so and ask them to allow location.]"
    return (f"\n\n[PHONE LOCATION, shared only for this message: {name(p[0], p[1]) or 'unknown place'} ({p[0]:.4f}, {p[1]:.4f}). "
            "You have no live map or shop data. Help in general terms and be honest about that.]")
