"""Excitement and hype scoring from transcript cues: gamers shout "oh my god", "let's go",
"bhaago", "arre yaar", "pulis", "goli", "dhamaka"... Works on word-timed transcripts."""
import re
import numpy as np

# (regex, weight). Roman + Devanagari. Panic / hype / action / chase / disbelief / pain.
_LEX = [
    (r"oh my (god|gosh)|omg|oh shit|holy (shit|crap|fuck|hell)?|no way|what the (fuck|f|hell)|wtf|oh no+|nooo+|oh fuck|oh god", 3),
    (r"let'?s go+|lets go+|insane|crazy|bruh|yooo+|yoo+|ayo|bro+\b|dude|sheesh|goat|clip (it|that)", 2),
    (r"run|run run|go go|get out|watch out|behind you|help|police|cops?|chase|chasing|wanted|swat|shoot|shot|shooting|gun|kill|killed|dead|die|dying|dies", 2),
    (r"headshot|clutch|pog\w*|ace|godlike|rampage|killstreak|unreal|aimbot|one tap|quickscope|no scope", 3),
    (r"boom|explo\w*|blast|blow|crash\w*|fire|burn\w*|bomb|grenade|rocket|jump|flip\w*|fall\w*|drop\w*|ahh+|aaa+h*|scream\w*", 2),
    (r"are+ yaar|arre+|are bhai|oye+|abe+|bhaag\w*|bhago|bachao|pulis|police wale|maar\w*|mar\w*|gaya|goli\w*|dhamaka|uff+|oh teri|kya baat|zabardast|pagal|mast|jhakaas|hat\s*teri|kya mara|mar diya|bhai kya|are baap re|op bhai|op clutch|kya shot", 2),
    (r"अरे+|भागो|भाग|बचाओ|पुलिस|मार|मर गया|गोली|धमाका|ब्लास्ट|पागल|उफ़|ओए|यार", 2),
]
_RX = [(re.compile(p, re.I), w) for p, w in _LEX]

# Short interjections: weak alone (1 point), strong when repeated or combined
_WEAK = {'oh', 'ooh', 'whoa', 'woah', 'wow', 'yo', 'holy', 'damn', 'dang', 'ugh', 'aah', 'ahh', 'ah', 'bro', 'brother', 'nah', 'what', 'no', 'wait', 'stop', 'yes', 'yeah',
         'arre', 'are', 'abe', 'oye', 'uff', 'अरे', 'ओए', 'उफ़', 'वाह', 'नहीं'}
_PUNCT = re.compile(r"[!?]{1,}")


def word_weight(text: str) -> float:
    t = str(text or "").strip().lower()
    if not t:
        return 0.0
    w = 0.0
    for rx, wt in _RX:
        if rx.fullmatch(t) or (len(t) > 3 and rx.search(t) and rx.search(t).group(0) == t):
            w = max(w, wt)
    if w == 0 and t.strip(',.!?') in _WEAK:
        w = 0.7
    if t.endswith('!'):
        w += 1.0
    return w


def _phrase_weight(words: list, i: int) -> float:
    """Two/three-word phrases such as 'oh my god' or 'oh shit' are matched on the joined text."""
    best = 0.0
    for n in (3, 2):
        if i + n <= len(words):
            joined = ' '.join((w.get('text') or w.get('w') or '').strip(',.!?').lower() for w in words[i:i + n])
            for rx, wt in _RX:
                m = rx.search(joined)
                if m and len(m.group(0)) >= len(joined) - 1:
                    best = max(best, wt)
    return best


def seconds_signal(words: list, duration: float) -> np.ndarray:
    """Per-second excitement 0..1 over the whole video (smoothed 5 s)."""
    n = max(1, int(np.ceil(duration)))
    sig = np.zeros(n)
    for i, w in enumerate(words):
        t_val = w.get('text') or w.get('w') or ''
        wt = max(word_weight(t_val), _phrase_weight(words, i))
        if wt:
            s = min(n - 1, int(w.get('start', w.get('s', 0))))
            sig[s] += wt
    sig = np.minimum(sig, 6)
    k = np.ones(5) / 5
    sm = np.convolve(sig, k, 'same')
    peak = max(float(np.percentile(sm[sm > 0], 95)) if (sm > 0).any() else 1.0, 1.0)
    return np.clip(sm / peak, 0, 1)


def window_score(words: list, duration: float) -> float:
    """0..1: how exclamation-dense a candidate clip is."""
    if not words or duration <= 0:
        return 0.0
    total = 0.0
    for i, w in enumerate(words):
        t_val = w.get('text') or w.get('w') or ''
        total += max(word_weight(t_val), _phrase_weight(words, i))
    density = total / max(duration / 8.0, 1.0)
    return float(min(1.0, density / 4.0))


def match_hype(text: str) -> tuple[bool, str]:
    """Check if the text contains gaming shout / hype expressions. Returns (matched, matched_phrase)."""
    t = str(text or "").strip().lower()
    if not t:
        return False, ""
    for rx, _ in _RX:
        m = rx.search(t)
        if m:
            return True, m.group(0)
    return False, ""

