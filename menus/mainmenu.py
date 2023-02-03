""" Main menu class for Noise Shaper
"""

# Import GUI packages
import tkinter as tk
from tkinter import messagebox

class MainMenu(tk.Menu):
    """ Main Menu
    """
    # Find parent window and tell it to 
    # generate a callback sequence
    def _event(self, sequence):
        def callback(*_):
            root = self.master.winfo_toplevel()
            root.event_generate(sequence)
        return callback


    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        #############
        # File menu #
        #############
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label="Import Audio...",
            command=self._event('<<FileImport>>')
        )
        file_menu.add_command(
            label="Export Noise...",
            command=self._event('<<FileExport>>')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quit",
            command=self._event('<<FileQuit>>')
        )
        self.add_cascade(label='File', menu=file_menu)


        ############## 
        # Tools menu #
        ##############
        tools_menu = tk.Menu(self, tearoff=False)
        tools_menu.add_command(
            label='Create Noise',
            command=self._event('<<ToolsShapeNoise>>')
        )
        # Add Tools menu to the menubar
        self.add_cascade(label="Tools", menu=tools_menu)


        #############
        # Help menu #
        #############
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(
            label='About',
            command=self.show_about
        )
        help_menu.add_command(
            label='Help',
            command=self._event('<<HelpHelp>>')
        )
        # Add help menu to the menubar
        self.add_cascade(label="Help", menu=help_menu)


    ##################
    # Menu Functions #
    ##################
    # HELP menu
    def show_about(self):
        """ Show the about dialog """
        about_message = 'Noise Shaper'
        about_detail = (
            'Written by: Travis M. Moore\n'
            'Special thanks to: Daniel Smieja\n'
            'Version 4.0.0\n'
            'Created: Jun 17, 2022\n'
            'Last edited: Feb 03, 2023'
        )
        messagebox.showinfo(
            title='About',
            message=about_message,
            detail=about_detail
        )
