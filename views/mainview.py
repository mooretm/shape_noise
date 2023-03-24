""" Main view for Noise Shaper.
"""

###########
# Imports #
###########
# Import GUI packages
from tkinter import ttk

#import customtkinter as ctk
#ctk.set_appearance_mode('dark')

# Import data science packages
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


#########
# BEGIN #
#########
class MainFrame(ttk.Frame):
    def __init__(self, parent, _vars, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Dict of Tk variables
        self._vars = _vars

        #################
        # Create Frames #
        #################
        options_data = {'padx':10, 'pady':10}
        options_lbls = {'width':35}

        # Main container frame
        #self.frm_main = ctk.CTkFrame(self)
        #self.frm_main = ttk.Frame(self)
        self.frm_main.grid()

        # Data labelframe
        self.lfrm_Data = ttk.LabelFrame(self.frm_main, 
            text="Audio File Information")
        self.lfrm_Data.grid(row=0, column=0, sticky='nsew', **options_data)

        # INput labelrame
        self.lfrm_Input = ttk.LabelFrame(self.lfrm_Data, text="Imported File")
        self.lfrm_Input.grid(row=1, column=0, **options_data)

        # OUTput labelframe
        self.lfrm_Output = ttk.LabelFrame(self.lfrm_Data, text="Exported File")
        self.lfrm_Output.grid(row=1, column=1, **options_data)

        # Plot labelframe
        self.lblfrm_plots = ttk.LabelFrame(self.frm_main, 
            text="Power Spectral Density Comparison Plot")
        self.lblfrm_plots.grid(column=0, row=5, ipadx=5, ipady=5, padx=10, 
            pady=10)


        ##################
        # Create Widgets #
        ##################
        # INput file info labels
        # Name
        ttk.Label(self.lfrm_Input, textvariable=self._vars['in_file'], 
            **options_lbls).grid(row=0, column=0, sticky='w')
        # Data Type
        ttk.Label(self.lfrm_Input, textvariable=self._vars['in_datatype'], 
            **options_lbls).grid(row=1, column=0, sticky='w')
        # Sampling Rate
        ttk.Label(self.lfrm_Input, textvariable=self._vars['in_samplingrate'],
            **options_lbls).grid(row=2, column=0, sticky='w')
        # Channels
        ttk.Label(self.lfrm_Input, textvariable=self._vars['in_channels'],
            **options_lbls).grid(row=3, column=0, sticky='w')

        # OUTput file info labels
        # Name
        ttk.Label(self.lfrm_Output, textvariable=self._vars['out_file'], 
            **options_lbls).grid(row=0, column=0, sticky='w')
        # Data Type
        ttk.Label(self.lfrm_Output, textvariable=self._vars['out_datatype'], 
            **options_lbls).grid(row=1, column=0, sticky='w')
        # Sampling Rate
        ttk.Label(self.lfrm_Output, textvariable=self._vars['out_samplingrate'], 
            **options_lbls).grid(row=2, column=0, sticky='w')
        # Channels
        ttk.Label(self.lfrm_Output, textvariable=self._vars['out_channels'],
            **options_lbls).grid(row=3, column=0, sticky='w')

        # Create plot
        self.fig = Figure(figsize=(5.5,4), dpi=75)
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_ylabel("Power Spectral Density")
        self.ax.set_xlabel("Frequency (Hz)")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.lblfrm_plots)
        self.canvas.get_tk_widget().grid(column=0, row=5, **options_data)
