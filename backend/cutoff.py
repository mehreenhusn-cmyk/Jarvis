"""Part 160: when Hussain cuts Jarvis off by talking, the next message also carries what Jarvis was saying (and how much he had heard),
so the AI knows the topic. It goes only into the AI's instructions for that one answer. It is never saved and never shown."""
import re

import screen


def _clean(x):
    t = re.sub(r"\s+", " ", str(x or "")).strip()[:400]
    return screen.redact(t)[0] if t else ""  # numbers like OTPs or cards are hidden here too, as everywhere


def context(x):
    """Extra AI instructions for ONE answer, or an empty string if nothing sensible came with the message."""
    if not isinstance(x, dict):
        return ""
    said, heard = _clean(x.get("said")), _clean(x.get("heard"))
    if len(said) < 3:
        return ""
    s = f'\n\nHussain just interrupted you by speaking while you were talking. You were saying: "{said}".'
    if heard and heard != said:
        s += f' He had heard only up to: "{heard}".'
    s += " His new words may continue, correct or change that topic. Use the earlier messages and your own sentence to understand what he means. Do not repeat what he already heard."
    return s
