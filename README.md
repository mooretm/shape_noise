# **Noise Shaper**

- Written by: **Travis M. Moore**
- Latest version: **Version 5.0.0**
- Originally created: **February 28, 2023**
- Last edited: **April 11, 2023**
<br>
<br>

---

## Description
Application that creates calibration files for custom stimuli. Noise Shaper filters a white Gaussian noise to the shape of the power spectral density of a given signal. Can handle single- and multi-channel audio. Only compatible with .wav files. 
<br>
<br>

---

## Getting Started

### Dependencies

- Windows 10 or greater (not compatible with Mac OS)

### Installing

- This is a compiled app; the executable file is stored on Starfile at: \\starfile\Public\Temp\MooreT\Custom Software
- Simply copy the executable file and paste to a location on the local machine
- Double click to start the app

### First Use
- Navigate to **File-->Import Audio...** to import a custom audio stimulus. 
- Navigate to **Tools-->Create Calibration File** to generate a new calibration file.
<br>
<br>

---

## Audio File Information
### Imported File
Details regarding the imported audio will appear in the "Imported File" section. This allows verification of file name, data type, sampling rate, and number of channels.

### Exported File
Details regarding the exported calibration file will appear in the "Exported File" section. This allows verification of file name, data type, sampling rate, and number of channels.

---

## Power Spectral Density Comparison plot
The power spectral density of the imported audio and the newly created calibration file will be displayed in the plot area for each channel of the imported audio. You should visually inspect these plots as they appear to ensure the spectra match (i.e., overlap). 

---

## Creating a Calibration File
- Navigate to **File-->Import Audio...** to import a custom audio .wav file. 
- Select the type of noise to use for the calibration file by choosing either "Correlated" or "Uncorrelated" from the **Tools** menu. 
    - Choose "correlated" if the input audio is correlated across channels (e.g., Ambisonics files), or if you need to create several single-channel files using the same noise. 
    - Choose "uncorrelated" if your input audio is uncorrelated (most likely).
- Navigate to **Tools-->Create Calibration File** to generate a new calibration file.
- Upon completion, you will be asked if you want to export/save the newly created file.
<br>
<br>

---

## Compiling from Source
```
pyinstaller --noconfirm --onefile --windowed --add-data "C:/Users/MooTra/Code/Python/shape_noise/assets/README;README/"  "C:/Users/MooTra/Code/Python/shape_noise/controller.py"
```
<br>
<br>

---

## Contact
Please use the contact information below to submit bug reports, feature requests and any other feedback. Thank you for using Noise Shaper!

- Travis M. Moore: travis_moore@starkey.com
