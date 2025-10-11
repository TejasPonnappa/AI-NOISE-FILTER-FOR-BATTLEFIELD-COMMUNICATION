import os
from pydub import AudioSegment
import librosa
import soundfile as sf

# -----------------------------
# Paths
# -----------------------------
clean_dir = "data/clean/"
noisy_dir = "data/noisy/"
processed_clean_dir = "data/clean_processed/"
processed_noisy_dir = "data/noisy_processed/"

os.makedirs(processed_clean_dir, exist_ok=True)
os.makedirs(processed_noisy_dir, exist_ok=True)

MIN_LENGTH = 2000  # 1 second in ms
TARGET_SR = 16000  # 16 kHz

# -----------------------------
# Function to normalize audio
# -----------------------------
def normalize_audio(audio_segment):
    return audio_segment.apply_gain(-audio_segment.max_dBFS)

# -----------------------------
# Process a folder
# -----------------------------
def process_folder(input_dir, output_dir):
    files = [f for f in os.listdir(input_dir) if f.endswith(".wav")]
    for f in files:
        file_path = os.path.join(input_dir, f)
        audio = AudioSegment.from_wav(file_path)

        if len(audio) < MIN_LENGTH:
            print(f"Skipping {f} (too short)")
            continue

        # Normalize
        audio = normalize_audio(audio)

        # Export to temp WAV for resampling
        temp_path = os.path.join(output_dir, "temp.wav")
        audio.export(temp_path, format="wav")

        # Resample to 16 kHz using librosa
        y, _ = librosa.load(temp_path, sr=TARGET_SR)
        out_path = os.path.join(output_dir, f)
        sf.write(out_path, y, TARGET_SR)
        print(f"Processed: {f}")

# -----------------------------
# Run preprocessing
# -----------------------------
print("Processing clean audio...")
process_folder(clean_dir, processed_clean_dir)

print("Processing noisy audio...")
process_folder(noisy_dir, processed_noisy_dir)

print("All audio preprocessing complete!")
