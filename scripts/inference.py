import os
import torch
import torchaudio
import torchaudio.transforms as T
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.unet_model import UNet


# -----------------------------
# CONFIG
# -----------------------------
NOISY_FILE = "data/noisy/noisy_18_53ecb7.wav"  # change to your file
OUTPUT_FILE = "data/cleaned/example_cleaned.wav"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TARGET_SR = 16000
TARGET_LEN = int(19.7 * TARGET_SR)  # same as training
N_FFT = 512
HOP_LENGTH = 256

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def load_resample_mono(path):
    wave, sr = torchaudio.load(path)
    if wave.shape[0] > 1:
        wave = torch.mean(wave, dim=0, keepdim=True)
    if sr != TARGET_SR:
        wave = T.Resample(sr, TARGET_SR)(wave)
    return wave

def pad_or_truncate(wave, target_len=TARGET_LEN):
    if wave.shape[1] < target_len:
        pad = torch.zeros((1, target_len - wave.shape[1]))
        wave = torch.cat([wave, pad], dim=1)
    else:
        wave = wave[:, :target_len]
    return wave

# -----------------------------
# LOAD MODEL
# -----------------------------
model = UNet().to(DEVICE)
model.load_state_dict(torch.load("models/unet_battlefield.pth", map_location=DEVICE))
model.eval()

# -----------------------------
# PREPROCESS AUDIO
# -----------------------------
wave = load_resample_mono(NOISY_FILE)
wave = pad_or_truncate(wave)

spec = torch.stft(wave, n_fft=N_FFT, hop_length=HOP_LENGTH, return_complex=True).abs()
spec = spec.unsqueeze(0).to(DEVICE)  # [1, 1, freq, time]

# -----------------------------
# PREDICT MASK
# -----------------------------
with torch.no_grad():
    mask = model(spec)
    cleaned_spec = spec * mask

# -----------------------------
# INVERSE STFT
# -----------------------------
# We’ll just use magnitude + original phase for simplicity
phase = torch.angle(torch.stft(wave, n_fft=N_FFT, hop_length=HOP_LENGTH, return_complex=True))
complex_spec = cleaned_spec.squeeze(0) * torch.exp(1j * phase)
cleaned_wave = torch.istft(complex_spec, n_fft=N_FFT, hop_length=HOP_LENGTH, length=TARGET_LEN)

# -----------------------------
# SAVE OUTPUT
# -----------------------------
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
torchaudio.save(OUTPUT_FILE, cleaned_wave.cpu(), TARGET_SR)
print(f"✅ Cleaned audio saved to: {OUTPUT_FILE}")
