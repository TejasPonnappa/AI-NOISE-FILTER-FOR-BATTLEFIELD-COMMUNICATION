# scripts/mix_audio.py
from pydub import AudioSegment
import os
import csv

# -----------------------------
# Paths
# -----------------------------
CLEAN_DIR = "data/clean/"
NOISE_DIR = "data/noise/"
OUTPUT_DIR = "data/noisy/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_FILE = os.path.join(OUTPUT_DIR, "mapping.csv")  # stores clean ↔ noisy mapping

# -----------------------------
# Parameters
# -----------------------------
SNR_ADJUST_DB = 10  # reduce noise volume by 10 dB

# -----------------------------
# Get sorted file lists
# -----------------------------
clean_files = sorted([f for f in os.listdir(CLEAN_DIR) if f.endswith(".wav")])
noise_files = sorted([f for f in os.listdir(NOISE_DIR) if f.endswith(".wav")])

count = 0

# Prepare CSV
with open(CSV_FILE, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["noisy_file", "clean_file", "noise_file"])  # header

    # -----------------------------
    # Mix each clean with all noise
    # -----------------------------
    for cf in clean_files:
        clean_audio = AudioSegment.from_wav(os.path.join(CLEAN_DIR, cf))
        
        for nf in noise_files:
            noise_audio = AudioSegment.from_wav(os.path.join(NOISE_DIR, nf))
            
            # Repeat noise if shorter than clean
            if len(noise_audio) < len(clean_audio):
                repeats = (len(clean_audio) // len(noise_audio)) + 1
                noise_audio = noise_audio * repeats
            # Trim noise to match clean length
            noise_audio = noise_audio[:len(clean_audio)]
            
            # Reduce noise volume
            noise_audio = noise_audio - SNR_ADJUST_DB
            
            # Overlay clean + noise
            mixed_audio = clean_audio.overlay(noise_audio)
            
            # Export mixed audio
            out_file = os.path.join(OUTPUT_DIR, f"noisy_{count}.wav")
            mixed_audio.export(out_file, format="wav")
            
            # Save mapping
            writer.writerow([f"noisy_{count}.wav", cf, nf])
            
            print(f"Saved: {out_file}")
            count += 1

print(f"All mixed audio generated! Total files: {count}")
print(f"CSV mapping saved at: {CSV_FILE}")
