import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter

# ----------------------------
# FILTER HELPERS
# ----------------------------
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype='band')
    return b, a

def apply_bandpass(y, fs):
    # Emphasize 300 Hz – 4 kHz range (where voice intelligibility lives)
    b, a = butter_bandpass(300.0, 4000.0, fs, order=4)
    return lfilter(b, a, y)

def apply_de_harsh(y):
    # Simple high-frequency damping for hiss/static
    smooth = np.convolve(y, np.ones(5)/5, mode='same')
    y = 0.8 * y + 0.2 * smooth
    return y

def compress_dynamic_range(y, threshold=0.6, ratio=4.0):
    # Gentle compression to make quiet sounds audible, reduce peaks
    compressed = np.copy(y)
    mask = np.abs(y) > threshold
    compressed[mask] = np.sign(y[mask]) * (
        threshold + (np.abs(y[mask]) - threshold) / ratio
    )
    return compressed

def fade_edges(y, sr):
    fade_len = int(0.02 * sr)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    y[:fade_len] *= fade_in
    y[-fade_len:] *= fade_out
    return y

# ----------------------------
# MAIN POST-PROCESSING PIPELINE
# ----------------------------
def post_process(y, sr=16000):
    y = apply_bandpass(y, sr)       # remove rumble & hiss
    y = apply_de_harsh(y)           # soften metallic edges
    y = compress_dynamic_range(y)   # more consistent volume
    y = librosa.util.normalize(y)   # loudness normalization
    y = fade_edges(y, sr)           # smooth start/end
    return y

# ----------------------------
# TEST STANDALONE (optional)
# ----------------------------
if __name__ == "__main__":
    inp = "data/cleaned/example_cleaned.wav"
    out = "data/cleaned/example_final.wav"
    y, sr = librosa.load(inp, sr=16000)
    processed = post_process(y, sr)
    sf.write(out, processed, sr)
    print(f"✅ Post-processed audio saved at {out}")
