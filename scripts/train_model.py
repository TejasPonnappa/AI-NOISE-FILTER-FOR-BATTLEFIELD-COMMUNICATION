import os
import sys
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import torchaudio
import torchaudio.transforms as T

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.unet_model import UNet

# -----------------------------
# CONFIG
# -----------------------------
NOISY_DIR = "data/noisy"
CLEAN_DIR = "data/clean"
CSV_FILE = "data/noisy/mapping.csv"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TARGET_SR = 16000
BATCH_SIZE = 4
EPOCHS = 20
LEARNING_RATE = 1e-3

# Manual max length in samples (19.7s)
TARGET_LEN = int(19.7 * TARGET_SR)

# -----------------------------
# DATASET
# -----------------------------
class BattlefieldDataset(Dataset):
    def __init__(self, csv_file, noisy_dir, clean_dir, max_len_samples=TARGET_LEN, target_sr=TARGET_SR):
        self.df = pd.read_csv(csv_file)
        self.noisy_dir = noisy_dir
        self.clean_dir = clean_dir
        self.max_len = max_len_samples
        self.target_sr = target_sr

    def load_resample_mono(self, path):
        wave, sr = torchaudio.load(path)
        # Convert to mono
        if wave.shape[0] > 1:
            wave = torch.mean(wave, dim=0, keepdim=True)
        # Resample
        if sr != self.target_sr:
            wave = T.Resample(sr, self.target_sr)(wave)
        return wave

    def pad_or_truncate(self, wave):
        if wave.shape[1] < self.max_len:
            pad = torch.zeros((1, self.max_len - wave.shape[1]))
            wave = torch.cat([wave, pad], dim=1)
        else:
            wave = wave[:, :self.max_len]
        return wave

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        noisy_path = os.path.join(self.noisy_dir, self.df.iloc[idx]['noisy_file'])
        clean_path = os.path.join(self.clean_dir, self.df.iloc[idx]['clean_file'])

        noisy_wave = self.load_resample_mono(noisy_path)
        clean_wave = self.load_resample_mono(clean_path)

        noisy_wave = self.pad_or_truncate(noisy_wave)
        clean_wave = self.pad_or_truncate(clean_wave)

        # STFT
        n_fft = 512
        hop_length = 256
        noisy_spec = torch.stft(noisy_wave, n_fft=n_fft, hop_length=hop_length, return_complex=True).abs()
        clean_spec = torch.stft(clean_wave, n_fft=n_fft, hop_length=hop_length, return_complex=True).abs()

        # Ensure shape [channel=1, freq, time]
        noisy_spec = noisy_spec.unsqueeze(0) if noisy_spec.ndim == 2 else noisy_spec
        clean_spec = clean_spec.unsqueeze(0) if clean_spec.ndim == 2 else clean_spec

        return noisy_spec, clean_spec

# -----------------------------
# LOAD DATA
# -----------------------------
dataset = BattlefieldDataset(CSV_FILE, NOISY_DIR, CLEAN_DIR)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# -----------------------------
# MODEL
# -----------------------------
model = UNet().to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
criterion = torch.nn.MSELoss()

# -----------------------------
# TRAIN LOOP
# -----------------------------
for epoch in range(EPOCHS):
    running_loss = 0.0
    for noisy_mag, clean_mag in dataloader:
        noisy_mag = noisy_mag.to(DEVICE)  # [B, 1, F, T]
        clean_mag = clean_mag.to(DEVICE)

        optimizer.zero_grad()
        mask = model(noisy_mag)
        output = noisy_mag * mask
        loss = criterion(output, clean_mag)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(dataloader)
    print(f"Epoch {epoch+1}/{EPOCHS} | Avg Loss: {avg_loss:.6f}")

# -----------------------------
# SAVE MODEL
# -----------------------------
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), "models/unet_battlefield.pth")
print("✅ Model training complete and saved at models/unet_battlefield.pth")
