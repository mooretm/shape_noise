""" Class to handle writing .wav files.

******************* Not currently implemented *******************
"""

###########
# Imports #
###########
# Import GUI packages
from tkinter import filedialog

# Import data science packages
import pandas as pd

# Import system packages
from pathlib import Path

# Import audio packages
import soundfile as sf


#########
# BEGIN #
#########
class WriteModel:
    """ Class to handle writing audio files.
    """

    def _write_audio(self, audio, fs):
        # cols = len(audio.keys())
        # rows = len(list(audio.values())[0])
        # M = np.matlib.zeros(rows, cols)

        df = pd.DataFrame(audio)
        sf.write('test.wav', df, fs)


    def test(self):
        # Ask user to specify save location
        save_path = filedialog.askdirectory()
        # Do nothing if cancelled
        if save_path is None:
            return

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
