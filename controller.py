""" Shape white noise based on the long-term average 
    of a given stimulus. Matches both spectral content and 
    RMS amplitude of the original stimulus. Useful for making 
    calibration noise for custom stimuli. 

    Version 4.0.0
    Written by: Travis M. Moore
    Contributor: Daniel Smieja
    Created: Jun 17, 2022
    Last Edited: Feb 01, 2023
"""

###########
# Imports #
###########
# Import system packages
import os
from pathlib import Path

# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Import data science packages
import numpy as np
import random
from scipy import signal

# Import custom modules
from menus import mainmenu
from models import audiomodel
from views import mainview


#########
# BEGIN #
#########
class Application(tk.Tk):
    """Application root window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Setup main window
        self.withdraw() # Hide window during setup
        self.resizable(False, False)
        self.title("Noise Shaper")

        # Create variable dictionary
        self._vars = {
            'in_file': tk.StringVar(value='Name:'),
            'in_datatype': tk.StringVar(value='Data Type:'),
            'in_samplingrate': tk.StringVar(value='Sampling Rate:'),
            'in_channels': tk.StringVar(value='Channels:'),

            'out_file': tk.StringVar(value='Name:'),
            'out_datatype': tk.StringVar(value='Data Type:'),
            'out_samplingrate': tk.StringVar(value='Sampling Rate:'),
            'out_channels': tk.StringVar(value='Channels:')
        }

        # Load menus
        menu = mainmenu.MainMenu(self)
        self.config(menu=menu)

        # Load main view
        self.main_view = mainview.MainFrame(self, self._vars)
        self.main_view.grid(row=5, column=5)

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileImport>>': lambda _: self._import(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsShapeNoise>>': lambda _: self._shape_noise()
        }

        # Bind callbacks to sequences
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        # Center main window
        self.center_window()


    #####################
    # General Functions #
    #####################
    def center_window(self):
        """ Center the root window 
        """
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        self.deiconify()

    
    def _quit(self):
        """ Exit the application.
        """
        self.destroy()


    #####################
    # General Functions #
    #####################
    def _import(self):
        """ Import audio file using audiomodel. Update _vars
            dict variables with audio data. 
        """
        self._full_path = Path(filedialog.askopenfilename())
        self.a = audiomodel.Audio(self._full_path)
        self._vars["in_file"].set(f"Name: {self.a.name}")
        self._vars["in_datatype"].set(f"Data Type: {self.a.data_type}")
        self._vars["in_samplingrate"].set(f"Sampling Rate: {self.a.fs} Hz")
        self._vars["in_channels"].set(f"Channels: {len(self.a.channels)}")


    ########################
    # Tools Menu Functions #
    ########################
    def _shape_noise(self):
        """ Function to create the filtered white noise.
        """
        # First check that an audio file was loaded
        try:
            self.a.name
        except:
            messagebox.showerror(
                title="File Not Found!",
                message="Please import an audio file first!"
            )
            return

        # Create noise
        noise = self.mk_wgn(self.a.fs,30)
        dur_noise = len(noise) / self.a.fs
        t_noise = np.arange(0,dur_noise,1/self.a.fs)

        # P Welch of noise and stimulus tones
        f_noise, den_noise = signal.welch(noise, self.a.fs, nperseg=2048)
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




if __name__ == "__main__":
    app = Application()
    app.mainloop()
