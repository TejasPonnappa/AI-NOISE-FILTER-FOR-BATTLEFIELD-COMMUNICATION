from pydub import AudioSegment
import os
import csv
import hashlib
import random

# === Paths ===
CLEAN_DIR = "data/clean/"
NOISE_DIR = "data/noise/"
OUTPUT_DIR = "data/noisy/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_FILE = os.path.join(OUTPUT_DIR, "mapping.csv")

# === Parameters ===
TARGET_DBFS = -20            # normalize clean & noise
TARGET_SR = 16000            # model sample rate
SNR_RANGE_DB = (-2, 5)       # noise can be slightly louder (-2) or clean louder (+5)

# === List files ===
clean_files = sorted([f for f in os.listdir(CLEAN_DIR) if f.endswith(".wav")])
noise_files = sorted([f for f in os.listdir(NOISE_DIR) if f.endswith(".wav")])
count = 0

def normalize_audio(audio, target_dbfs):
    change_in_dbfs = target_dbfs - audio.dBFS
    return audio.apply_gain(change_in_dbfs)

with open(CSV_FILE, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["noisy_file", "clean_file", "noise_file", "snr_db"])

    for cf in clean_files:
        clean_audio = AudioSegment.from_wav(os.path.join(CLEAN_DIR, cf))
        clean_audio = clean_audio.set_frame_rate(TARGET_SR)
        clean_audio = normalize_audio(clean_audio, TARGET_DBFS)

        for nf in noise_files:
            noise_audio = AudioSegment.from_wav(os.path.join(NOISE_DIR, nf))
            noise_audio = noise_audio.set_frame_rate(TARGET_SR)
            noise_audio = normalize_audio(noise_audio, TARGET_DBFS)

            # Match length
            if len(noise_audio) < len(clean_audio):
                repeats = (len(clean_audio) // len(noise_audio)) + 1
                noise_audio = noise_audio * repeats
            noise_audio = noise_audio[:len(clean_audio)]

            # Random SNR -2 to +5 dB
            snr_db = random.uniform(*SNR_RANGE_DB)
            noise_audio_adjusted = noise_audio - snr_db  # negative → louder noise, positive → quieter

            # Mix clean + noise
            mixed_audio = clean_audio.overlay(noise_audio_adjusted)

            # Normalize final mix
            mixed_audio = normalize_audio(mixed_audio, TARGET_DBFS)

            # Safe filename
            hash_id = hashlib.md5(f"{cf}_{nf}".encode()).hexdigest()[:6]
            out_file = os.path.join(OUTPUT_DIR, f"noisy_{count}_{hash_id}.wav")

            # Export
            mixed_audio.export(out_file, format="wav")

            # Write CSV
            writer.writerow([os.path.basename(out_file), cf, nf, round(snr_db, 2)])

            print(f"Saved: {out_file} | SNR: {round(snr_db,2)} dB")
            count += 1

print(f"\n✅ All mixed audio generated! Total files: {count}")
print(f"📄 CSV mapping saved at: {CSV_FILE}")
