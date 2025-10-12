import streamlit as st
import torch
import torchaudio
import torchaudio.transforms as T
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import os
import sys

# -----------------------------
# Import Model + Postprocess
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from models.unet_model import UNet
from audio_postprocessing import post_process

# -----------------------------
# CONFIG
# -----------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TARGET_SR = 16000
N_FFT = 512
HOP_LENGTH = 256

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎧 Battlefield Audio Denoiser")
st.markdown("Upload a **noisy audio file** and let the AI clean it using a U-Net model + post-processing pipeline.")

uploaded_file = st.file_uploader("Upload a noisy `.wav` file", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav", start_time=0)

    # -----------------------------
    # LOAD MODEL
    # -----------------------------
    model = UNet().to(DEVICE)
    model.load_state_dict(torch.load("models/unet_battlefield.pth", map_location=DEVICE))
    model.eval()

    # -----------------------------
    # LOAD AND PREPROCESS
    # -----------------------------
    wave, sr = torchaudio.load(uploaded_file)
    if wave.shape[0] > 1:
        wave = torch.mean(wave, dim=0, keepdim=True)
    if sr != TARGET_SR:
        wave = T.Resample(sr, TARGET_SR)(wave)

    # show original waveform
    fig, ax = plt.subplots()
    ax.plot(wave.squeeze().numpy())
    ax.set_title("Original Noisy Waveform")
    st.pyplot(fig)

    # -----------------------------
    # DENOISE
    # -----------------------------
    spec_complex = torch.stft(wave, n_fft=N_FFT, hop_length=HOP_LENGTH, return_complex=True)
    spec_mag = spec_complex.abs().unsqueeze(0).to(DEVICE)  # [1, 1, freq, time]

    with torch.no_grad():
        mask = model(spec_mag)
        cleaned_spec = spec_mag * mask

    phase = torch.angle(spec_complex)
    complex_spec = cleaned_spec.squeeze(0) * torch.exp(1j * phase)
    cleaned_wave = torch.istft(complex_spec, n_fft=N_FFT, hop_length=HOP_LENGTH)

    # -----------------------------
    # POST-PROCESSING
    # -----------------------------
    cleaned_wave_np = cleaned_wave.squeeze().cpu().numpy()
    processed_wave = post_process(cleaned_wave_np, TARGET_SR)

    # show post-processed waveform
    fig2, ax2 = plt.subplots()
    ax2.plot(processed_wave)
    ax2.set_title("Post-Processed Clean Waveform")
    st.pyplot(fig2)

    # -----------------------------
    # SAVE + PLAY OUTPUT
    # -----------------------------
    output_path = "data/cleaned/final_output.wav"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, processed_wave, TARGET_SR)

    st.audio(output_path, format="audio/wav")
    st.success("✅ Denoising complete!")
    st.download_button(
        label="⬇️ Download Cleaned Audio",
        data=open(output_path, "rb").read(),
        file_name="cleaned_output.wav",
        mime="audio/wav"
    )
