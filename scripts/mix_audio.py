from pydub import AudioSegment
import os

# -----------------------------
# Paths
# -----------------------------
clean_dir = "data/clean/"
noise_dir = "data/noise/"
output_dir = "data/noisy/"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# Get file lists
# -----------------------------
clean_files = [f for f in os.listdir(clean_dir) if f.endswith(".wav")]
noise_files = [f for f in os.listdir(noise_dir) if f.endswith(".wav")]

# Minimum clip length in ms (1 second)
MIN_LENGTH = 1500

count = 0
# -----------------------------
# Full combinatorial mixing
# -----------------------------
for cf in clean_files:
    clean_audio = AudioSegment.from_wav(os.path.join(clean_dir, cf))
    
    if len(clean_audio) < MIN_LENGTH:
        print(f"Skipping {cf} (too short)")
        continue
    
    for nf in noise_files:
        noise_audio = AudioSegment.from_wav(os.path.join(noise_dir, nf))
        
        if len(noise_audio) < MIN_LENGTH:
            print(f"Skipping {nf} (too short)")
            continue
        
        # Repeat/pad noise to match clean length
        if len(noise_audio) < len(clean_audio):
            repeats = (len(clean_audio) // len(noise_audio)) + 1
            noise_audio = noise_audio * repeats
        noise_audio = noise_audio[:len(clean_audio)]
        
        # Lower noise volume randomly (simulate SNR)
        snr_adjust = 10  # fixed reduction, or random.randint(5,15)
        noise_audio = noise_audio - snr_adjust
        
        # Overlay
        mixed_audio = clean_audio.overlay(noise_audio)
        
        # Export
        out_file = os.path.join(output_dir, f"noisy_{count}.wav")
        mixed_audio.export(out_file, format="wav")
        print(f"Saved: {out_file}")
        count += 1

print(f"All mixed audio generated! Total files: {count}")
