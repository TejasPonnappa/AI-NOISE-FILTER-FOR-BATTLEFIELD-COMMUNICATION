# scripts/preprocess_audio.py
import os
import csv
from pydub import AudioSegment
import librosa
import soundfile as sf

# -----------------------------
# Paths
# -----------------------------
CLEAN_DIR = "data/clean/"
NOISY_DIR = "data/noisy/"
PROCESSED_CLEAN_DIR = "data/clean_processed/"
PROCESSED_NOISY_DIR = "data/noisy_processed/"
MAPPING_CSV = os.path.join(NOISY_DIR, "mapping.csv")

os.makedirs(PROCESSED_CLEAN_DIR, exist_ok=True)
os.makedirs(PROCESSED_NOISY_DIR, exist_ok=True)

# -----------------------------
# Parameters
# -----------------------------
TARGET_SR = 16000  # 16 kHz

# -----------------------------
# Normalize audio
# -----------------------------
def normalize_audio(audio_segment):
    return audio_segment.apply_gain(-audio_segment.max_dBFS)

# -----------------------------
# Preprocess single file
# -----------------------------
def preprocess_file(input_path, output_path):
    audio = AudioSegment.from_wav(input_path)
    
    # Normalize
    audio = normalize_audio(audio)
    
    # Export temp wav
    temp_path = output_path + "_temp.wav"
    audio.export(temp_path, format="wav")
    
    # Resample using librosa
    y, _ = librosa.load(temp_path, sr=TARGET_SR)
    sf.write(output_path, y, TARGET_SR)
    
    os.remove(temp_path)  # remove temp file
    return True

# -----------------------------
# Process all files according to mapping
# -----------------------------
with open(MAPPING_CSV, "r") as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        clean_file = row["clean_file"]
        noisy_file = row["noisy_file"]
        
        clean_input_path = os.path.join(CLEAN_DIR, clean_file)
        noisy_input_path = os.path.join(NOISY_DIR, noisy_file)
        
        clean_output_path = os.path.join(PROCESSED_CLEAN_DIR, clean_file)
        noisy_output_path = os.path.join(PROCESSED_NOISY_DIR, noisy_file)
        
        # Preprocess clean and noisy files
        preprocess_file(clean_input_path, clean_output_path)
        preprocess_file(noisy_input_path, noisy_output_path)
        
        print(f"Processed pair: {clean_file} + {noisy_file}")

print("All audio preprocessing complete!")
