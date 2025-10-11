import os
import numpy as np
import librosa
import soundfile as sf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# -----------------------------
# Paths
# -----------------------------
MODEL_PATH = "models/rnn_denoiser.h5"
NOISY_INPUT = "data/noisy/noisy_0.wav"
OUTPUT_PATH = "data/denoised.wav"

# -----------------------------
# Parameters
# -----------------------------
N_MELS = 257
TARGET_SR = 16000

print("Loading trained model...")
model = load_model(MODEL_PATH, compile=False)

# -----------------------------
# Load and convert input
# -----------------------------
y, sr = librosa.load(NOISY_INPUT, sr=TARGET_SR)
mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS)
mel_db = librosa.power_to_db(mel, ref=np.max)
mel_db = mel_db.T  # shape: (time, n_mels)

mel_db_padded = pad_sequences([mel_db], padding='post', dtype='float32', value=0.0)

# -----------------------------
# Predict
# -----------------------------
denoised_mel = model.predict(mel_db_padded)
denoised_mel = np.squeeze(denoised_mel, axis=0)  # (time, n_mels)

# -----------------------------
# Convert back to audio
# -----------------------------
denoised_power = librosa.db_to_power(denoised_mel.T)
y_denoised = librosa.feature.inverse.mel_to_audio(denoised_power, sr=TARGET_SR, n_iter=64)

sf.write(OUTPUT_PATH, y_denoised, TARGET_SR)
print(f"✅ Denoised audio saved to {OUTPUT_PATH}")
