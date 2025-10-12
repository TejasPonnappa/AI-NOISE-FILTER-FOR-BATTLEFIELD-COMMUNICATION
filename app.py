# app.py
import os
import torch
import torchaudio
import torchaudio.transforms as T
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from io import BytesIO
from models.unet_model import UNet
from audio_postprocessing import post_process
import time

# -----------------------------
# CONFIG
# -----------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TARGET_SR = 16000
N_FFT = 512
HOP_LENGTH = 256

# -----------------------------
# STREAMLIT PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Battlefield Audio Cleaner", layout="wide")
st.title("🎧 Battlefield Audio Cleaner")
st.markdown("Upload noisy battlefield audio, get cleaned + post-processed audio.")

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def load_resample_mono(wavefile):
    wave, sr = torchaudio.load(wavefile)
    if wave.shape[0] > 1:
        wave = torch.mean(wave, dim=0, keepdim=True)
    if sr != TARGET_SR:
        wave = T.Resample(sr, TARGET_SR)(wave)
    return wave

def pad_or_truncate(wave, target_len=None):
    if target_len is None:
        return wave
    if wave.shape[1] < target_len:
        pad = torch.zeros((1, target_len - wave.shape[1]))
        wave = torch.cat([wave, pad], dim=1)
    else:
        wave = wave[:, :target_len]
    return wave

def plot_waveform(wave, title="Waveform"):
    wave_np = wave.squeeze().cpu().numpy()
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(wave_np)
    ax.set_title(title)
    ax.set_xlabel("Samples")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

# -----------------------------
# LOAD MODEL
# -----------------------------
@st.cache_resource
def load_model():
    model = UNet().to(DEVICE)
    model.load_state_dict(torch.load("models/unet_battlefield.pth", map_location=DEVICE))
    model.eval()
    return model

model = load_model()

# -----------------------------
# UPLOAD AUDIO
# -----------------------------
uploaded_file = st.file_uploader("Upload your noisy audio (.wav)", type=["wav"])

if uploaded_file is not None:
    # Show original audio
    st.subheader("Original Audio")
    st.audio(uploaded_file, format="audio/wav")

    wave = load_resample_mono(uploaded_file)
    original_len = wave.shape[1]

    st.subheader("Original Waveform")
    plot_waveform(wave, title="Noisy Input")

    # -----------------------------
    # PROGRESS BAR
    # -----------------------------
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    steps = [
        "Analyzing radio patterns...",
        "Updating weights and biases...",
        "Optimizing output quality..."
    ]
    
    for i, step in enumerate(steps, 1):
        progress_text.text(step)
        progress_bar.progress(i / len(steps))
        time.sleep(0.5)  # simulate processing step

    # -----------------------------
    # SPECTROGRAM + MODEL INFERENCE
    # -----------------------------
    wave_padded = pad_or_truncate(wave)
    spec = torch.stft(wave_padded, n_fft=N_FFT, hop_length=HOP_LENGTH, return_complex=True).abs()
    spec = spec.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        mask = model(spec)
        cleaned_spec = spec * mask

    phase = torch.angle(torch.stft(wave_padded, n_fft=N_FFT, hop_length=HOP_LENGTH, return_complex=True))
    complex_spec = cleaned_spec.squeeze(0) * torch.exp(1j * phase)
    cleaned_wave = torch.istft(complex_spec, n_fft=N_FFT, hop_length=HOP_LENGTH, length=original_len)

    # -----------------------------
    # POST-PROCESSING
    # -----------------------------
    cleaned_wave_np = cleaned_wave.squeeze().cpu().numpy()
    processed = post_process(cleaned_wave_np, TARGET_SR)

    # -----------------------------
    # SHOW POST-PROCESSED AUDIO
    # -----------------------------
    st.subheader("Post-Processed Audio")
    buffer = BytesIO()
    sf.write(buffer, processed, TARGET_SR, format="WAV")
    st.audio(buffer, format="audio/wav")

    st.subheader("Post-Processed Waveform")
    plot_waveform(torch.tensor(processed).unsqueeze(0), title="Post-Processed Output")

    # -----------------------------
    # DOWNLOAD LINK
    # -----------------------------
    st.download_button(
        label="⬇️ Download Cleaned Audio",
        data=buffer,
        file_name="cleaned_final.wav",
        mime="audio/wav"
    )

    progress_text.text("✅ Processing Complete!")
    progress_bar.empty()
