import numpy as np
import random
from scipy.io import wavfile
from scipy import signal
from matplotlib import pyplot as plt
import sys
import os

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

#sys.path.append('.\\lib') # Point to custom library file
sys.path.append('C:\\Users\\MooTra\\Documents\\Code\\Python\\my_packages\\tmpy')
import tmsignals as ts # Custom package
import importlib 
importlib.reload(ts) # Reload custom module on every run


def filter_delay(num_taps, fs):
    filt_delay = (num_taps - 1) / (2 * fs)
    return filt_delay


def filter_taps(d1=10**-4, d2=10**-3, Df=1000):
    """ https://dsp.stackexchange.com/questions/31066/how-many-taps-does-an-fir-filter-need
    """
    num_taps = int((2/3)*np.log10(1/(10*d1*d2))*Df)
    if not num_taps % 2:
        num_taps += 1
    return num_taps


# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)


def import_stim_file():
    """ Select file using system file dialog 
        and read it into a dictionary.
    """
    file_name = filedialog.askopenfilename(initialdir=_thisDir)
    fs, stimulus = wavfile.read(file_name)
    return fs, stimulus, file_name


def mk_wgn(fs,dur):
    """ Function to generate white Gaussian noise.
    """
    random.seed(4)
    wgn = [random.gauss(0.0, 1.0) for i in range(fs*dur)]
    wgn = ts.doNormalize(wgn)
    #wgn = ts.setRMS(wgn,lvl)
    return wgn


######################
# Initialize Signals #
######################
# Read in signal from file
fs, stimulus, file_name = import_stim_file()
dur_stim = len(stimulus)/ fs
t_stim = np.arange(0,dur_stim,1/fs)
stimulus = ts.doNormalize(stimulus)

# Make noise
noise = mk_wgn(fs,3)
dur_noise = len(noise) / fs
t_noise = np.arange(0,dur_noise,1/fs)

# P Welch of noise and stimulus tones
f_noise, den_noise = signal.welch(noise, fs, nperseg=2048)
f_stim, den_stim = signal.welch(stimulus, fs, nperseg=2048)

# Plot unprocessed signal data
fig1, axs1 = plt.subplots(nrows=2,ncols=2)
# Normalized stimulus in the time domain
axs1[0,0].plot(t_stim,stimulus)
axs1[0,0].set_title('Stimulus Waveform')
# P Welch stimulus
axs1[0,1].plot(f_stim, np.sqrt(den_stim))
axs1[0,1].set_title('Spectral Density of Stimulus')
# Normalized noise in the time domain
axs1[1,0].plot(t_noise,noise)
axs1[1,0].set_title('Noise Waveform')
# P Welch noise
axs1[1,1].semilogy(f_noise, np.sqrt(den_noise))
axs1[1,1].set_title('Spectral Density of Noise')
plt.show()


#################################################
# Create FIR from spectral density of stimulus  #
#################################################
# Set number of filter taps
num_taps = filter_taps()
print(f"Number of taps: {num_taps}")
offset = num_taps - 1
""" Create even-numbered offset to remove 
    extra points added by convolution
    (directly related to the number of
    taps - 1)
"""
# Find delay introduced by filter
filt_delay = filter_delay(num_taps,fs)
#print(f"Filter delay (s): {filt_delay}")

# Create the filter
fir_filt = signal.firwin2(numtaps=num_taps, freq=f_stim/np.max(f_stim), gain=np.sqrt(den_stim))
# FIR frequency response
w, h = signal.freqz(fir_filt)
w = w * fs / (2*np.pi)
# Apply FIR to noise
filtered_noise = np.convolve(fir_filt, noise)
# Normalize filtered noise
filtered_noise = filtered_noise / np.max(np.abs(filtered_noise))
# Remove the extra values added during convolution
filtered_noise = filtered_noise[:-offset]
# P Welch of filtered noise
f_filt_noise, den_filt_noise = signal.welch(filtered_noise, fs, nperseg=2048)

# Plot filter data
fig2, axs2 = plt.subplots(nrows=2, ncols=3)
# FIR filter shape
axs2[0,0].plot(fir_filt)
axs2[0,0].set_title('FIR filter shape')
# FIR frequency response
axs2[0,1].plot(w, 20 * np.log10(abs(h)))
axs2[0,1].set_xlabel("Frequency (Hz)")
axs2[0,1].set_ylabel("Amplitude (dB)")
axs2[0,1].set_title("FIR frequency response")
# filtered noise
axs2[0,2].plot(t_noise,filtered_noise)
axs2[0,2].set_title('Filtered Noise')
# Original P Welch of stimulus
axs2[1,0].plot(f_stim,den_stim)
axs2[1,0].set_title('Original Spectral Density of Stimulus')
# P Welch of filtered noise
axs2[1,1].plot(f_filt_noise, den_filt_noise)
axs2[1,1].set_title('Spectral Density of Filtered Noise')
# Show Fig2
plt.show()


########################
# Amplitude Correction #
########################
rms_stim = ts.rms(stimulus)
filtered_noise = ts.doGate(sig=filtered_noise,rampdur=0.01,fs=fs)
filtered_noise = ts.doNormalize(filtered_noise)
rms_filt_noise = ts.rms(filtered_noise)
amp_diff =  rms_stim / rms_filt_noise
print(f"RMS of stimulus: {rms_stim}")
print(f"RMS of filtered noise: {rms_filt_noise}")
print(f"RMS diff: {amp_diff}")
adj_filtered_noise = filtered_noise * amp_diff
f_adj_filt_noise, den_adj_filt_noise = signal.welch(adj_filtered_noise, fs, nperseg=2048)
print(f"RMS of adjusted filtered noise: {ts.rms(adj_filtered_noise)}")


#####################
# Visual comparison #
#####################
# Spectral density plots
plt.subplot(2,1,1)
plt.plot(f_stim,20*np.log10(den_stim),color="blue",label="stimulus")
plt.plot(f_adj_filt_noise,20*np.log10(den_adj_filt_noise),ls=":",color="orange",label="Filtered Noise")
plt.title("Spectra after Amplitude Correction")
plt.legend()

# Waveform plots
dur_noise = len(adj_filtered_noise) / fs
t_noise = np.arange(0,dur_noise,1/fs)
plt.subplot(2,1,2)
plt.plot(t_stim,stimulus,color="blue",label="stimulus")
plt.plot(t_noise,adj_filtered_noise,color="orange",ls=":",label="Filtered Noise")
plt.title("Waveforms after Amplitude Correction")
plt.legend()
plt.show()


##########
# Output #
##########
# Write filtered noise to file
file_out = file_name[:-4] + "_calibration.wav"
wavfile.write(file_out, fs, adj_filtered_noise)
