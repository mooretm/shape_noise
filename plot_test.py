# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

# Import science packages
import numpy as np
import random
from scipy.io import wavfile
from scipy import signal
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

# Import system packages
import sys
import os


# Begin root window
root = tk.Tk()
root.title("Noise Shaping Tool")
root.withdraw()

frm_options = {'padx':10, 'pady':10}

lblfrm_plots = ttk.LabelFrame(root, text="Signal Plots")
lblfrm_plots.grid(column=0, row=0, **frm_options, ipadx=5, ipady=5)

lblfrm_data = ttk.LabelFrame(root, text="Signal Data")
lblfrm_data.grid(column=0, row=1, **frm_options)

fig = Figure(figsize=(4,2), dpi=100)
t = np.arange(0,3,.01)
ax = fig.add_subplot()
line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
ax.set_xlabel("time [s]")
ax.set_ylabel("f(t)")

canvas = FigureCanvasTkAgg(fig, master=lblfrm_plots)
canvas.draw()

toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.get_tk_widget().grid(column=0, row=0, **frm_options)


root.update_idletasks()
#root.attributes('-topmost',1)
window_width = root.winfo_width()
window_height = root.winfo_height()
# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
#root.resizable(False, False)
root.deiconify()

root.mainloop()
