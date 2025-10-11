import os
import numpy as np
import librosa
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, TimeDistributed, Dense, Masking
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences

# -----------------------------
# Paths
# -----------------------------
CLEAN_DIR = "data/clean_processed/"
NOISY_DIR = "data/noisy_processed/"
MAPPING_CSV = "data/noisy/mapping.csv"
MODEL_PATH = "models/rnn_denoiser.h5"

# -----------------------------
# Hyperparameters
# -----------------------------
N_MELS = 257
TARGET_SR = 16000
EPOCHS = 50
BATCH_SIZE = 8

# -----------------------------
# Load CSV mapping
# -----------------------------
mapping = pd.read_csv(MAPPING_CSV)
clean_files = mapping["clean_file"].tolist()
noisy_files = mapping["noisy_file"].tolist()

# -----------------------------
# Convert WAV to Mel
# -----------------------------
def wav_to_mel(path):
    y, _ = librosa.load(path, sr=TARGET_SR)
    mel = librosa.feature.melspectrogram(y=y, sr=TARGET_SR, n_mels=N_MELS)
    mel_db = librosa.power_to_db(mel)
    return mel_db.T  # shape: (time, n_mels)

clean_specs = [wav_to_mel(os.path.join(CLEAN_DIR, f)) for f in clean_files]
noisy_specs = [wav_to_mel(os.path.join(NOISY_DIR, f)) for f in noisy_files]

# -----------------------------
# Pad sequences
# -----------------------------
max_len = max([s.shape[0] for s in clean_specs + noisy_specs])
clean_specs = pad_sequences(clean_specs, maxlen=max_len, dtype="float32", padding="post")
noisy_specs = pad_sequences(noisy_specs, maxlen=max_len, dtype="float32", padding="post")

# -----------------------------
# Model
# -----------------------------
model = Sequential([
    Masking(mask_value=0., input_shape=(max_len, N_MELS)),
    GRU(128, return_sequences=True),
    GRU(128, return_sequences=True),
    TimeDistributed(Dense(N_MELS, activation="linear"))
])

model.compile(optimizer=Adam(0.001), loss="mse")
model.summary()

# -----------------------------
# Train (IMPORTANT: noisy → clean)
# -----------------------------
model.fit(noisy_specs, clean_specs, epochs=EPOCHS, batch_size=BATCH_SIZE)

# -----------------------------
# Save
# -----------------------------
os.makedirs("models", exist_ok=True)
model.save(MODEL_PATH)
print(f"✅ Model saved to {MODEL_PATH}")
