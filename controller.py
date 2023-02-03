""" Shape white noise based on the long-term average 
    of a given stimulus. Matches both spectral content and 
    RMS amplitude of the original stimulus. Useful for making 
    calibration noise for custom stimuli. 

    Version 4.0.0
    Written by: Travis M. Moore
    Special thanks to: Daniel Smieja
    Created: Jun 17, 2022
    Last Edited: Feb 02, 2023
"""

###########
# Imports #
###########
# Import system packages
from pathlib import Path

# Import audio packages
import soundfile as sf

# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Import data science packages
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

# Import custom modules
# Menus
from menus import mainmenu
# Models
from models import audiomodel
from models import noisemodel
from models import writemodel
# Views
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

        # Create dicts to hold info for each channel of the 
        # input audio file
        self.filtered_noises = {}
        self.noise_pwelch = {}
        self.stim_pwelch = {}

        # Load menus
        menu = mainmenu.MainMenu(self)
        self.config(menu=menu)

        # Load noisemodel
        self.n = noisemodel.NoiseShaper()

        # Load writemodel
        self.w = writemodel.WriteModel()

        # Load main view
        self.main_view = mainview.MainFrame(self, self._vars)
        self.main_view.grid(row=5, column=5)

        # Status label
        self.status_var = tk.StringVar(value="Status: Ready")
        ttk.Label(self, textvariable=self.status_var).grid(
            row=10, column=5, padx=10, pady=(0,10), sticky='w'
        )

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileImport>>': lambda _: self._import(),
            '<<FileExport>>': lambda _: self._export(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsShapeNoise>>': lambda _: self._shape_noise(),

            # Help menu
            '<<HelpHelp>>': lambda _: self._help(),

            # noisemodel
            '<<NoisePlot>>': lambda _: self._plot_spectra(),
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


    #######################
    # File Menu Functions #
    #######################
    def _import(self):
        """ Import audio file using audiomodel. Update _vars
            dict variables with audio data. 
        """
        self._full_path = Path(filedialog.askopenfilename())

        try:
            self.a = audiomodel.Audio(self._full_path)
            self._vars["in_file"].set(f"Name: {self.a.name}")
            self._vars["in_datatype"].set(f"Data Type: {self.a.data_type}")
            self._vars["in_samplingrate"].set(f"Sampling Rate: {self.a.fs} Hz")
            self._vars["in_channels"].set(f"Channels: {len(self.a.channels)}")
        except FileNotFoundError:
            return


    def _export(self):
        """ Write all filtered noises as single .wav file.
        """
        # Convert to df
        df = pd.DataFrame(self.filtered_noises)
        # Create output file name based on input file name
        filename = self.a.name[:-4] + '_cal.wav'
        # Write .wav to current directory
        sf.write(filename, df, self.a.fs)

        # Update labels with exported audio info
        self._vars["out_file"].set(f"Name: {filename}")
        self._vars["out_datatype"].set(f"Data Type: {str(df.dtypes[0])}")
        self._vars["out_samplingrate"].set(f"Sampling Rate: {self.a.fs} Hz")
        self._vars["out_channels"].set(f"Channels: {len(df.columns)}")


    ########################
    # Tools Menu Functions #
    ########################
    def _shape_noise(self):
        """ Create NoiseShaper class to create filtered noise.
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

        for ii in range(0, len(self.a.channels)):
            self.status_var.set(f"Status: Processing channel {ii+1}...")
            self.update_idletasks()

            # Create shaped noise
            self.n._shape_noise(self.a.signal[:, ii], self.a.fs)

            # Fill dicts with iteration values
            self.filtered_noises[ii] = self.n.adj_filtered_noise
            self.noise_pwelch[ii] = (self.n.f_adj_filt_noise, 
                self.n.den_adj_filt_noise)
            self.stim_pwelch[ii] = (self.n.f_stim, self.n.den_stim)

            # Plot spectra
            self._plot_spectra(channel=ii)
            self.update_idletasks()

        self.status_var.set(f"Status: Ready")


    def _plot_spectra(self, channel):
        """ Plot spectrum of original audio and shaped noise 
            for visual inspection.
        """
        # Create figure object
        self.fig = Figure(figsize=(5.5,4), dpi=75)
        self.ax = self.fig.add_subplot(1,1,1)

        # Create stimulus axes
        self.ax.plot(self.stim_pwelch[channel][0],
            20*np.log10(self.stim_pwelch[channel][1]), color="blue", 
            label="stimulus", linewidth=3)

        # Create noise axes
        self.ax.plot(self.noise_pwelch[channel][0],
            20*np.log10(self.noise_pwelch[channel][1]), 
            ls=":", linewidth=3, color="orange", label="Filtered Noise")

        # Set axis labels
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Power Spectral Density")
        self.ax.set_title(f"Power Spectral Density for Channel {channel+1}")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, 
            master=self.main_view.lblfrm_plots)
        self.canvas.get_tk_widget().grid(column=0, row=5)

        self.update()


    #######################
    # Help Menu Functions #
    #######################
    def _help(self):
        messagebox.showinfo(title="Not Ready Yet!",
            message="Help documentation not yet written!" +
                "\nGo find Travis (unless he's cranky...)")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
