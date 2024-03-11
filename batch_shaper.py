""" Batch script for creating calibration noise WAV files. 

    Author: Travis M. Moore
    Last edited: 03/11/2024    
"""

###########
# Imports #
###########
# Science
import numpy as np
# System
import os
from pathlib import Path
# Audio
import soundfile as sf
# Custom
from models import noisemodel


#################
# Organize Data #
#################
# Import WAV file paths
_path = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\stimuli'
files = Path(_path).glob('*.wav')
files = list(files)


#############
# Functions #
#############
def multichannel_shaping(audio, fs, correlated, filename):
    """ Apply noise shaping code to file with any number of channels. """
    # Get number of channels
    try:
        num_channels = audio.shape[1]
    except IndexError:
        num_channels = 1

    # Instantiate NoiseShaper
    ns = noisemodel.NoiseShaper()

    # Apply noise shaper to each channel
    cal_noises = []
    for ii in range(0, num_channels):
        msg = f"Status: Processing channel {ii+1} of {num_channels}"
        print("")
        print('*' * len(msg))
        print(msg)
        print('*' * len(msg))
        print(f"batch_shaper: Processing {filename}")
        # Create shaped noise
        if num_channels > 1:
            cal_noise = ns.shape_noise(
                audio=audio[:, ii],
                fs=fs,
                correlated=correlated,
            )
        elif num_channels == 1:
            cal_noise = ns.shape_noise(
                audio=audio,
                fs=fs,
                correlated=correlated,
            )

        cal_noises.append(cal_noise)

    # Convert list into numpy array and transpose
    cal_noise_array = np.array(cal_noises).T
    print(f"\nbatch_shaper: Final array shape: {cal_noise_array.shape}")

    return cal_noise_array


##############
# Controller #
##############
# Create calibration noises
for file in files:
    # Read in audio
    sig, fs = sf.read(file)

    # Create calibration noise for each channel
    cal_noise = multichannel_shaping(
        audio=sig, 
        fs=fs, 
        correlated=True,
        filename=os.path.basename(file)
    )
    
    # Get filename minus extension and append "_cal"
    filename = os.path.basename(file)[:-4] + '_cal.wav'

    # Write WAV to current directory
    sf.write(filename, cal_noise, fs)
