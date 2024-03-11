""" Code to shape white noise based on the long-term average 
    of a given stimulus. Matches both spectral content and 
    RMS amplitude of the original stimulus. Useful for making 
    calibration noise for custom stimuli. 

    Version 3.0.1
    Written by: Travis M. Moore
    Contributor: Daniel Smieja
    Created: Jun 17, 2022
    Last Edited: Jun 28, 2022
"""

# Import system packages
import os
import sys
from pathlib import Path

# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Import data science packages
import numpy as np
import random
from scipy.io import wavfile
from scipy import signal
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

class Audio:
    """ An object for use with .wav files. Audio objects 
        can import .wav files, handle audio data type 
        conversion, and store information about a .wav 
        file.
    """
    def __init__(self):
        # Initialize attributes
        self.name = None
        self.file_path = None
        self.data_type = None
        self.fs = None
        self.dur = None
        self.t = None
        self.original_audio = None
        self.modified_audio = None

        # Dictionary of data types and ranges
        self.wav_dict = {
            'float32': (-1.0, 1.0),
            'int32': (-2147483648, 2147483647),
            'int16': (-32768, 32767),
            'uint8': (0, 255)
        }


    def do_import_audio(self):
        """ Select file using system file dialog 
            and read it into a dictionary.
        """
        file_name = filedialog.askopenfilename()
        self.file_path = file_name.split(os.sep)
        just_name = file_name.split('/')[-1]
        self.name = str(just_name)

        fs, audio_file = wavfile.read(file_name)
        self.fs = fs
        self.original_audio = audio_file

        audio_dtype = np.dtype(audio_file[0])
        self.data_type = audio_dtype
        print(f"Incoming data type: {audio_dtype}")

        # Immediately convert to float64 for manipulating
        if audio_dtype == 'float64':
            pass
        else:
            # 1. Convert to float64
            audio_file = audio_file.astype(np.float64)
            print(f"Forced audio data type: {type(audio_file[0])}")
            # 2. Divide by original dtype max val
            audio_file = audio_file / self.wav_dict[str(audio_dtype)][1]
            self.modified_audio = audio_file

        self.dur = len(audio_file) / self.fs

        self.t = np.arange(0,self.dur, 1/self.fs)


    def do_convert_to_original_dtype(self):
        # Convert back to original audio data type
        print(self.modified_audio)
        sig = self.modified_audio * self.wav_dict[str(self.data_type)][1]
        if self.data_type != 'float32':
            # Round to return to integer values
            sig = np.round(sig)
        # Convert back to original data type
        sig = sig.astype(self.data_type)
        print(f"Converted data type: {str(type(sig[0]))}")
        self.modified_audio = sig


class MainFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._vars = {
            'In Name': tk.StringVar(value='Name:'),
            'In Data Type': tk.StringVar(value='Data Type:'),
            'In Sampling Rate': tk.StringVar(value='Sampling Rate:'),

            'Out Name': tk.StringVar(value='Name:'),
            'Out Data Type': tk.StringVar(value='Data Type:'),
            'Out Sampling Rate': tk.StringVar(value='Sampling Rate:')
        }

        self.frm_main = ttk.Frame(self)
        self.frm_main.grid()
        
        #lbl_title = ttk.Label(self.frm_main, text="Calibration Noise Shaper")
        #lbl_title.grid(row=0, column=0)

        options_data = {'padx':10, 'pady':10}
        # Buttons
        self.frm_buttons = ttk.LabelFrame(self.frm_main, text="Controls")
        self.frm_buttons.grid(row=1, column=0, **options_data)
        # Import
        btn_import = ttk.Button(self.frm_buttons, text="Import File",
            command=self.master._on_import)
        btn_import.grid(row=0, column=0, padx=(10,0), pady=10)
        #Shape Noise
        btn_filter = ttk.Button(self.frm_buttons, text="Shape Noise", 
            command=self.do_shape_noise)
        btn_filter.grid(row=0, column=1, padx=10)
        # Save
        btn_get_class = ttk.Button(self.frm_buttons, text="Save File",
            command=self.master.do_write_audio)
        btn_get_class.grid(row=0, column=2, padx=(0,10))


        # Data
        options_lbls = {'width':35}
        # Main Data Label Frame
        self.lfrm_Data = ttk.LabelFrame(self.frm_main, text="Audio Data")
        self.lfrm_Data.grid(row=0, column=0, sticky='nsew', **options_data)

        # INput File Frame
        self.lfrm_Input = ttk.LabelFrame(self.lfrm_Data, text="Imported File")
        self.lfrm_Input.grid(row=1, column=0, **options_data)
        # Name
        self.lbl_name = ttk.Label(self.lfrm_Input, textvariable=self._vars['In Name'], **options_lbls)
        self.lbl_name.grid(row=0, column=0, sticky='w')
        # Data Type
        self.lbl_name = ttk.Label(self.lfrm_Input, textvariable=self._vars['In Data Type'], **options_lbls)
        self.lbl_name.grid(row=1, column=0, sticky='w')
        # Sampling Rate
        self.lbl_name = ttk.Label(self.lfrm_Input, textvariable=self._vars['In Sampling Rate'], **options_lbls)
        self.lbl_name.grid(row=2, column=0, sticky='w')

        # OUTput File Frame
        self.lfrm_Output = ttk.LabelFrame(self.lfrm_Data, text="Exported File")
        self.lfrm_Output.grid(row=1, column=1, **options_data)
        # Name
        ttk.Label(self.lfrm_Output, textvariable=self._vars['Out Name'], **options_lbls).grid(row=0, column=0, sticky='w')
        # Data Type
        ttk.Label(self.lfrm_Output, textvariable=self._vars['Out Data Type'], **options_lbls).grid(row=1, column=0, sticky='w')
        # Sampling Rate
        ttk.Label(self.lfrm_Output, textvariable=self._vars['Out Sampling Rate'], **options_lbls).grid(row=2, column=0, sticky='w')


        # Plots
        self.lblfrm_plots = ttk.LabelFrame(self.frm_main, text="Audio Data Plot")
        self.lblfrm_plots.grid(column=0, row=5, ipadx=5, ipady=5, padx=10, pady=10)

        self.fig = Figure(figsize=(5.5,4), dpi=75)
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlabel("Frequency (Hz)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.lblfrm_plots)
        self.canvas.get_tk_widget().grid(column=0, row=5, **options_data)
        #self.canvas.draw()
        #toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        #toolbar.update()

        # Info label
        ttk.Label(self.frm_main, text="Version 3.0.1. Updated: 06-28-2022.").grid(row=100, column=0, sticky='w')
        ttk.Label(self.frm_main, text="Authors: Travis Moore, Daniel Smieja").grid(row=100, column=0, sticky='e')

        
    def do_shape_noise(self):
        # Make noise
        try:
            audio_obj.name
        except:
            messagebox.showwarning(
                title="File Not Found!",
                message="Please import a file first!"
            )
            return
        noise = self.mk_wgn(audio_obj.fs,30)
        dur_noise = len(noise) / audio_obj.fs
        t_noise = np.arange(0,dur_noise,1/audio_obj.fs)

        # P Welch of noise and stimulus tones
        f_noise, den_noise = signal.welch(noise, audio_obj.fs, nperseg=2048)
        f_stim, den_stim = signal.welch(audio_obj.modified_audio, 
            audio_obj.fs, nperseg=2048)

        # Set number of filter taps
        num_taps = self.filter_taps() # Must be odd
        print(f"Number of taps: {num_taps}")
        offset = num_taps - 1
        """ Create even-numbered offset to remove 
            extra points added by convolution
            (directly related to the number of
            taps - 1)
        """
        # Find delay introduced by filter
        filt_delay = self.filter_delay(num_taps, audio_obj.fs)
        print(f"Filter delay (s): {filt_delay}")

        # Create the filter
        fir_filt = signal.firwin2(
            numtaps=num_taps, 
            freq=f_stim/np.max(f_stim), 
            gain=np.sqrt(den_stim))
        # FIR frequency response
        w, h = signal.freqz(fir_filt)
        w = w * audio_obj.fs / (2*np.pi)
        # Apply FIR to noise
        filtered_noise = np.convolve(fir_filt, noise)
        # Normalize filtered noise
        filtered_noise = filtered_noise / np.max(np.abs(filtered_noise))
        # Remove the extra values added during convolution from beginning/end
        filtered_noise = filtered_noise[:-offset]
        #filtered_noise = filtered_noise[int(offset/2):int(-offset/2)]
        # P Welch of filtered noise
        f_filt_noise, den_filt_noise = signal.welch(
            filtered_noise, audio_obj.fs, nperseg=2048)


        ########################
        # Amplitude Correction #
        ########################
        rms_stim = self.rms(audio_obj.modified_audio)
        filtered_noise = self.doGate(sig=filtered_noise,rampdur=0.02,fs=audio_obj.fs)
        filtered_noise = self.doNormalize(filtered_noise)
        rms_filt_noise = self.rms(filtered_noise)
        amp_diff =  rms_stim / rms_filt_noise
        print(f"RMS of stimulus: {rms_stim}")
        print(f"RMS of filtered noise: {rms_filt_noise}")
        print(f"RMS diff: {amp_diff}")
        adj_filtered_noise = filtered_noise * amp_diff
        f_adj_filt_noise, den_adj_filt_noise = signal.welch(
            adj_filtered_noise, audio_obj.fs, nperseg=2048)
        print(f"RMS of adjusted filtered noise: {self.rms(adj_filtered_noise)}")

        # Assign adjusted filtered noise to audio object
        audio_obj.modified_audio = adj_filtered_noise


        ######################
        # Check for Clipping #
        ######################
        clip_flag = False
        max_amp = np.max(abs(adj_filtered_noise))
        if max_amp > 1:
            print("Oh no! Some values are clipping!\nCalibration file not created!")
            clip_flag = True
            messagebox.showerror(
                title="Clipping!",
                message="There is clipping in the output file!\nAborting..."
            )
            sys.exit()
        else:
            print("No clipping! File OK!")


        #####################
        # Visual comparison #
        #####################
        # t_stim = np.arange(0,audio_obj.dur,1/audio_obj.fs)
        # # Spectral density plots
        # plt.subplot(2,1,1)
        # plt.plot(f_stim,20*np.log10(den_stim),color="blue",label="stimulus")
        # plt.plot(f_adj_filt_noise,20*np.log10(den_adj_filt_noise),ls=":",color="orange",label="Filtered Noise")
        # plt.title("Spectra after Amplitude Correction")
        # plt.legend()

        # # Waveform plots
        # dur_noise = len(adj_filtered_noise) / audio_obj.fs
        # t_noise = np.arange(0,dur_noise,1/audio_obj.fs)
        # plt.subplot(2,1,2)
        # plt.plot(t_stim, audio_obj.modified_audio, color="blue",label="stimulus")
        # plt.plot(t_noise,adj_filtered_noise,color="orange",ls=":",label="Filtered Noise")
        # plt.title("Waveforms after Amplitude Correction")
        # plt.legend()
        # plt.show()

        self.fig = Figure(figsize=(5.5,4), dpi=75)
        self.ax = self.fig.add_subplot(1,1,1)


        self.ax.plot(f_stim,20*np.log10(den_stim), color="blue", 
            label="stimulus", linewidth=3)
        self.ax.plot(f_adj_filt_noise,20*np.log10(den_adj_filt_noise), 
            ls=":", linewidth=3, color="orange", label="Filtered Noise")
        #self.ax.set_title("Spectra after Amplitude Correction")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("Frequency Spectra")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.lblfrm_plots)
        #self.canvas.draw()

        #toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        #toolbar.update()

        self.canvas.get_tk_widget().grid(column=0, row=5)


    def get(self):
        data = dict()
        for key, variable in self._vars.items():
            try:
                data[key] = variable.get()
            except tk.TclError:
                message=f'Error with: {key}.'
                raise ValueError(message)
        return data


    #############
    # Functions #
    #############
    def filter_delay(self, num_taps, fs):
        filt_delay = (num_taps - 1) / (2 * fs)
        return filt_delay


    def filter_taps(self, d1=10**-4, d2=10**-3, Df=1000):
        """ Determine number of filter taps. Based on:
            https://dsp.stackexchange.com/questions/31066/how-many-taps-does-an-fir-filter-need
        """
        num_taps = int((2/3)*np.log10(1/(10*d1*d2))*Df)
        if not num_taps % 2:
            num_taps += 1
        return num_taps


    def mk_wgn(self,fs,dur):
        """ Function to generate white Gaussian noise.
        """
        #random.seed(4)
        wgn = [random.gauss(0.0, 1.0) for i in range(fs*dur)]
        wgn = self.doNormalize(wgn)
        return wgn


    def doNormalize(self,sig):
        sig = sig - np.mean(sig) # remove DC offset
        sig = sig / np.max(abs(sig)) # normalize
        return sig


    def doGate(self,sig,rampdur=0.02,fs=48000):
        """
            Apply rising and falling ramps to signal SIG, of 
            duration RAMPDUR. Takes a 1-channel or 2-channel 
            signal. 

                SIG: a 1-channel or 2-channel signal
                RAMPDUR: duration of one side of the gate in 
                    seconds
                FS: sampling rate in samples/second

                Example: 
                [t, tone] = mkTone(100,0.4,0,48000)
                gated = doGate(tone,0.01,48000)

            Original code: Anonymous
            Adapted by: Travis M. Moore
            Last edited: Jan. 13, 2022          
        """
        gate =  np.cos(np.linspace(np.pi, 2*np.pi, int(fs*rampdur)))
        # Adjust envelope modulator to be within +/-1
        gate = gate + 1 # translate modulator values to the 0/+2 range
        gate = gate/2 # compress values within 0/+1 range
        # Create offset gate by flipping the array
        offsetgate = np.flip(gate)
        # Check number of channels in signal
        if len(sig.shape) == 1:
            # Create "sustain" portion of envelope
            sustain = np.ones(len(sig)-(2*len(gate)))
            envelope = np.concatenate([gate, sustain, offsetgate])
            gated = envelope * sig
        elif len(sig.shape) == 2:
            # Create "sustain" portion of envelope
            sustain = np.ones(len(sig[0])-(2*len(gate)))
            envelope = np.concatenate([gate, sustain, offsetgate])
            gatedLeft = envelope * sig[0]
            gatedRight = envelope * sig[1]
            gated = np.array([gatedLeft, gatedRight])
        return gated


    def rms(self,sig):
        """ 
            Calculate the root mean square of a signal. 
            
            NOTE: np.square will return invalid, negative 
                results if the number excedes the bit 
                depth. In these cases, convert to int64
                EXAMPLE: sig = np.array(sig,dtype=int)

            Written by: Travis M. Moore
            Last edited: Feb. 3, 2020
        """
        theRMS = np.sqrt(np.mean(np.square(sig)))
        return theRMS


class Application(tk.Tk):
    """Application root window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Calibration Noise Shaper")
        self.withdraw()

        self.main_frame = MainFrame(self)
        self.main_frame.grid(row=1, padx=10, sticky='ew')

        self._files_processed = 0

        # Center the window
        self.update_idletasks()
        #self.attributes('-topmost',1)
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        #self.resizable(False, False)
        self.deiconify()

    def _on_import(self):
        global audio_obj
        audio_obj = Audio()
        audio_obj.do_import_audio()

        self.main_frame._vars['In Name'].set(f'Name: {audio_obj.name}')
        self.main_frame._vars['In Data Type'].set(f'Data Type: {audio_obj.data_type}')
        self.main_frame._vars['In Sampling Rate'].set(f'Sampling Rate (Hz): {audio_obj.fs}')






        self.main_frame.fig = Figure(figsize=(5.5,4), dpi=75)
        self.main_frame.ax = self.main_frame.fig.add_subplot(1,1,1)

        self.main_frame.ax.plot(audio_obj.t,audio_obj.modified_audio)
        self.main_frame.ax.set_title("Stimulus Time Waveform")
        self.main_frame.ax.set_xlabel("Time (s)")
        self.main_frame.ax.set_ylabel("Amplitude")

        self.main_frame.canvas = FigureCanvasTkAgg(self.main_frame.fig, master=self.main_frame.lblfrm_plots)
        self.main_frame.canvas.draw()

        toolbar = NavigationToolbar2Tk(self.main_frame.canvas, self.main_frame, pack_toolbar=False)
        toolbar.update()

        self.main_frame.canvas.get_tk_widget().grid(column=0, row=5)


    def do_write_audio(self):
        # Ask user to specify save location
        save_path = filedialog.askdirectory()
        # Do nothing if cancelled
        if save_path is None:
            return
        # Convert back to original audio data type
        audio_obj.do_convert_to_original_dtype()
        # Check for existing file
        file_name = audio_obj.name
        file_name = file_name[:-4] + '_cal.wav'
        audio_obj.name = file_name
        file_out = save_path + os.sep + audio_obj.name
        if Path(file_out).exists():
            resp = messagebox.askyesno(
                title="Overwrite File?",
                message=f"A file named {audio_obj.name} already exists!\nDo you want to overwrite the file?"
            )
            if not resp:
                return
        print("Writing audio file...")
        wavfile.write(file_out, audio_obj.fs, audio_obj.modified_audio)
        self.main_frame._vars['Out Name'].set(f'Name: {audio_obj.name}')
        self.main_frame._vars['Out Data Type'].set(f'Data Type: {audio_obj.data_type}')
        self.main_frame._vars['Out Sampling Rate'].set(f'Sampling Rate (Hz): {audio_obj.fs}')
        print("Done!")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
