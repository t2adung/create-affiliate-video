"""Original, royalty-free music loop and sound effects synthesized in code (licence: original work, this repo)."""
import wave
from pathlib import Path
import numpy as np

SR = 44100


def _save(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())


def _t(d):
    return np.arange(int(SR * d)) / SR


def _tone(f, d, decay=6, amp=.25):
    t = _t(d)
    return amp * np.exp(-t * decay) * (np.sin(2*np.pi*f*t) + .3*np.sin(4*np.pi*f*t) + .1*np.sin(6*np.pi*f*t))


def music(seconds=32, bpm=112, seed=3):
    x = np.zeros(int(SR * seconds)); rng = np.random.default_rng(seed); beat = 60 / bpm
    chords = [[261.63, 329.63, 392.0], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63]]

    def add(sig, at):
        i = int(at * SR); x[i:i + len(sig)] += sig[:max(0, len(x) - i)]
    k = 0
    while k * beat / 2 < seconds:
        c = chords[int(k * beat / 2 // (4 * beat)) % 4]
        add(_tone(c[k % 3] * 2, .5, 7, .18), k * beat / 2)
        if k % 2 == 0:
            if (k // 2) % 4 == 0: add(_tone(c[0] / 2, 1.4, 2.5, .3), k * beat / 2)
            t = _t(.18); add(.5 * np.sin(2*np.pi*(110 - 60*t/.18)*t) * np.exp(-t*25), k * beat / 2)
        else:
            add(rng.normal(0, 1, int(SR*.04)) * np.exp(-_t(.04)*80) * .05, k * beat / 2)
        k += 1
    x = x / np.max(np.abs(x)) * .8; x[-SR:] *= np.linspace(1, 0, SR)
    return x


def write_assets(dest):
    dest = Path(dest); dest.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(7)
    _save(dest / "music.wav", music())
    x = _t(.45); sweep = np.sin(2*np.pi*np.cumsum(np.linspace(300, 3000, len(x)))/SR)
    _save(dest / "whoosh.wav", rng.normal(0, 1, len(x)) * np.sin(np.pi*x/.45)**2 * .3 * (.5 + .5*sweep))
    x = _t(.12); _save(dest / "pop.wav", np.sin(2*np.pi*np.cumsum(np.linspace(900, 250, len(x)))/SR) * np.exp(-x*30) * .7)
    _save(dest / "ding.wav", (_tone(1318.5, .9) + _tone(1975.5, .9) * .5) * .9)
    sp = np.zeros(int(SR*.8))
    for j in range(8):
        f = rng.uniform(2500, 4500); s = np.sin(2*np.pi*f*_t(.12)) * np.exp(-_t(.12)*40) * .25
        i = int(j*.08*SR); sp[i:i+len(s)] += s[:len(sp)-i]
    _save(dest / "sparkle.wav", sp)
    return dest
