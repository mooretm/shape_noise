""" Shape white noise based on the long-term average 
    of a given stimulus. Matches both spectral content and 
    RMS amplitude of the original stimulus. Useful for making 
    calibration noise for custom stimuli. 

    Version 4.0.0
    Written by: Travis M. Moore
    Contributor: Daniel Smieja
    Created: Jun 17, 2022
    Last Edited: Feb 02, 2023
"""

###########
# Imports #
###########
# Import system packages
from pathlib import Path
import time

# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Import data science packages
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

# Import custom modules
from menus import mainmenu
from models import audiomodel
from models import noisemodel
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

        # Status label
        self.status_var = tk.StringVar(value="Status: Ready")
        ttk.Label(self, textvariable=self.status_var).grid(
            row=10, column=5, padx=10, pady=(0,10), sticky='w'
        )

        # Create callback dictionary
        event_callbacks = {
            # File menu
            '<<FileImport>>': lambda _: self._import(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsShapeNoise>>': lambda _: self._shape_noise(),

            # Help menu
            '<<HelpHelp>>': lambda _: self._help(),
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

        self.status_var.set("Status: Working...")
        self.update_idletasks()

        # Create shaped noise
        self.n = noisemodel.NoiseShaper(self.a)
        self.n._shape_noise()

        self.status_var.set("Status: Ready")
        self.update_idletasks()

        # Plot spectra
        self._plot_spectra()


    def _plot_spectra(self):
        """ Plot spectrum of original audio and shaped noise 
            for visual inspection.
        """
        for ii in range(0,len(self.a.channels)):
            self.status_var.set(f"Status: Plotting...")
            self.update_idletasks()

            # Create figure object
            self.fig = Figure(figsize=(5.5,4), dpi=75)
            self.ax = self.fig.add_subplot(1,1,1)

            # Create axes
            self.ax.plot(self.n.stim_pwelch[ii][0],
                20*np.log10(self.n.stim_pwelch[ii][1]), color="blue", 
                label="stimulus", linewidth=3)
            self.ax.plot(self.n.noise_pwelch[ii][0],
                20*np.log10(self.n.noise_pwelch[ii][1]), 
                ls=":", linewidth=3, color="orange", label="Filtered Noise")
            #self.ax.set_title("Spectra after Amplitude Correction")
            self.ax.set_xlabel("Frequency (Hz)")
            self.ax.set_ylabel("Amplitude")
            self.ax.set_title(f"Frequency Spectra: Channel {ii+1}")
            self.ax.legend()

            self.canvas = FigureCanvasTkAgg(self.fig, 
                master=self.main_view.lblfrm_plots)
            #self.canvas.draw()

            #toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
            #toolbar.update()

            self.canvas.get_tk_widget().grid(column=0, row=5)
            self.update_idletasks()

            time.sleep(1)

        self.status_var.set("Status: Ready")


    #######################
    # Help Menu Functions #
    #######################
    def _help(self):
        messagebox.showinfo(title="Not Ready Yet!",
            message="Help documentation not yet written!")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
