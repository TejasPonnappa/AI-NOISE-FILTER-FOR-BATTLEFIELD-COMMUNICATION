import os
import shutil

clean_dir = "data/clean_processed/"
noisy_dir = "data/noisy_processed/"
paired_clean_dir = "data/clean_for_training/"

os.makedirs(paired_clean_dir, exist_ok=True)

clean_files = sorted([f for f in os.listdir(clean_dir) if f.endswith(".wav")])
noisy_files = sorted([f for f in os.listdir(noisy_dir) if f.endswith(".wav")])

num_clean = len(clean_files)
num_noisy = len(noisy_files)

print(f"Found {num_clean} clean and {num_noisy} noisy files")

# Repeat clean files to match noisy count
for i, noisy_file in enumerate(noisy_files):
    clean_file = clean_files[i % num_clean]  # cycle through clean files
    src_path = os.path.join(clean_dir, clean_file)
    dest_path = os.path.join(paired_clean_dir, f"clean_{i}.wav")
    shutil.copy(src_path, dest_path)

print(f"✅ Created {len(os.listdir(paired_clean_dir))} clean copies to match noisy set!")
