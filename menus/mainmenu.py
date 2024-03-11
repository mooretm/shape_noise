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
    

    def _bind_accelerators(self):
        self.bind_all('<Control-q>', self._event('<<FileQuit>>'))


    def __init__(self, parent, settings, **kwargs):
        super().__init__(parent, **kwargs)

        # Instantiate
        self._settings = settings

        #############
        # File menu #
        #############
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label="Import Audio...",
            command=self._event('<<FileImport>>')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Export Cal File...",
            command=self._event('<<FileExport>>')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Quit",
            command=self._event('<<FileQuit>>'),
            accelerator='Crtl+Q'
        )
        self.add_cascade(label='File', menu=file_menu)


        ############## 
        # Tools menu #
        ##############
        tools_menu = tk.Menu(self, tearoff=False)
        tools_menu.add_command(
            label='Create Cal File',
            command=self._event('<<ToolsShapeNoise>>')
        )
        tools_menu.add_separator()
        tools_menu.add_radiobutton(
            label='Correlated',
            #value='correlated',
            value=True,
            variable=self._settings['noise_type']
        )
        tools_menu.add_radiobutton(
            label='Uncorrelated',
            #value='uncorrelated',
            value=False,
            variable=self._settings['noise_type']
        )
        # Add Tools menu to the menubar
        self.add_cascade(label="Tools", menu=tools_menu)


        #############
        # Help menu #
        #############
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(
            label='About...',
            command=self.show_about
        )
        help_menu.add_command(
            label='Help...',
            command=self._event('<<HelpHelp>>')
        )
        # Add help menu to the menubar
        self.add_cascade(label="Help", menu=help_menu)


        ######################
        # Bind shortcut keys #
        ######################
        self._bind_accelerators()


    ##################
    # Menu Functions #
    ##################
    # HELP menu
    def show_about(self):
        """ Show the about dialog """
        about_message = self._settings['name']
        about_detail = (
            'Written by: Travis M. Moore\n' +
            'Special thanks to: Daniel Smieja\n' +
            'Version {}\n'.format(self._settings['version']) +
            'Created: Jun 17, 2022\n' +
            'Last edited: {}'.format(self._settings['last_edited'])
        )
        messagebox.showinfo(
            title='About',
            message=about_message,
            detail=about_detail
        )
