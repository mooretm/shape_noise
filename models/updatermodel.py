""" Class to check current version number against latest version 
    library on Starfile. If upgrade is available, display
    a message. If upgrade is mandatory, show warning and 
    kill app. 

    Written by: Travis M. Moore
    Created: Apr 11, 2023
    Last Edited: Apr 11, 2023
"""

###########
# Imports #
###########
# Data science
import pandas as pd

# GUI
from tkinter import messagebox


#########
# BEGIN #
#########
class VersionChecker:
    """ Class to check current version number against latest version 
        library on Starfile. If upgrade is available but not mandatory,
        return TRUE and display a message. If upgrade is mandatory, 
        return FALSE, display a message, and kill app. 
    """
    def __init__(self, lib_path, app_name, app_version):
        self.lib_path = lib_path
        self.app_name = app_name
        self.app_version = app_version
        self.current = None

        # Import version library to cross-reference
        try:
            self.import_version_library(self.lib_path)
        except FileNotFoundError:
            print(f"updater: Could not read from version library!")
            messagebox.showwarning(
                title="Cannot Reach Library",
                message="Cannot check for updates!",
                detail="The version library is unreachable. Please check " +
                "that you have access to Starfile and try again."
            )
            # Return True if version library file is unreachable. Defaults 
            # to being able to use the app if it cannot check the server.
            self.current = True
            return

        # Check version number
        self.check_for_updates()


    def import_version_library(self, lib_path):
        """ Load version library
        """
        # Download version library for crossreferencing
        try:
            self.version_library = pd.read_csv(lib_path)
        except FileNotFoundError:
            raise FileNotFoundError
            

    def check_for_updates(self):
        """ Check app version against latest available version from library.
        """
        # Retrieve app record from library 
        bools = self.version_library['name']==self.app_name
        status = self.version_library[bools]

        # Check whether current version matches version library
        try:
            if status.iloc[0]['version'] != self.app_version:
                print('\nupdater: New version available!')
                print(f"updater: You are using version {self.app_version}, but " +
                    f"version {status.iloc[0]['version']} is available.")
                if status.iloc[0]['mandatory'] == 'yes':
                    messagebox.showerror(
                        title="New Version Available",
                        message=f"Mandatory software update required!",
                        detail=f"You must download version " +
                        f"{status.iloc[0]['version']} to continue."
                    )
                    self.current = False
                    return
                elif status.iloc[0]['mandatory'] == 'no':
                    messagebox.showwarning(
                        title="New Version Available",
                        message=f"Software update available!",
                        detail=f"Please download {self.app_name} " + 
                        f"version {status.iloc[0]['version']}."
                    )
                self.current = True
                return
            else:
                print("\nupdater: You are up to date!")
                self.current = True
                return
        except IndexError:
            print("\nupdater: Check for updates failed!")
            print(f"updater: '{self.app_name}' cannot be found in the " +
                  "version library!")
            messagebox.showerror(
                title="Update Check Failed",
                message="Could not check for updates!",
                detail=f"'{self.app_name}' cannot be found in the version library."
            )
            # Return True if app name cannot be found in version library. 
            # Defaults to being able to use the app if updates cannot be checked.
            self.current = True
            return
