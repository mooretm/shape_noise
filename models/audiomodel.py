""" Audio class for reading, writing, presenting
    and converting .wav files
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np

# Import system packages
import os

# Import audio packages
import soundfile as sf
import sounddevice as sd


#########
# BEGIN #
#########
class Audio:
    """ Class for use with .wav files.
    """

    def __init__(self, file_path, device_id=None):
        """ Read audio file and generate info.

            Arguments:
            file_path: a Path object from pathlib
            device_id: audio device querried from sounddevice for playback
        """
        print(f"\naudiomodel: Attempting to load audio file...")
        # Parse file path
        self.directory = os.path.split(file_path)[0]
        self.name = os.path.basename(file_path)
        self.file_path = file_path

        # Assign default audio device
        if not device_id:
            self.device_id = sd.default.device
            self.num_outputs = sd.query_devices(sd.default.device[1])['max_output_channels']
        else:
            self.device_id = device_id
            self.num_outputs = sd.query_devices(self.device_id)['max_output_channels']

        # Read audio file
        file_exists = os.access(self.file_path, os.F_OK)
        if not file_exists:
            print("audiomodel: Audio file not found!")
            raise FileNotFoundError
        else:
            try:
                self.signal, self.fs = sf.read(self.file_path)
                print("audiomodel: Audio file found")
            except sf.LibsndfileError:
                print("audiomodel: No file imported!")
                raise FileNotFoundError

        # Get number of channels
        self.num_channels = self.signal.shape[1]
        self.channels = np.array(range(1, self.num_channels+1))
        print(f"audiomodel: Number of channels: {self.num_channels}")

        # Assign audio file attributes
        self.dur = len(self.signal) / self.fs
        self.t = np.arange(0, self.dur, 1/self.fs)
        print(f"audiomodel: Duration: {np.round(self.dur, 2)} seconds " +
            f"({np.round(self.dur/60, 2)} minutes)")

        # Get data type
        self.data_type = self.signal.dtype
        print(f"audiomodel: Data type: {self.data_type}")

        print("audiomodel: Done!")


    def play(self, level=None):
        """ Present working audio
        """
        # Create a temporary signal to be modified
        temp = self.signal.copy()

        # Get presentation level
        if not level:
            for chan in range(0, self.num_channels):
                # remove DC offset
                temp[:, chan] = temp[:, chan] - np.mean(temp[:, chan]) 
                # normalize
                temp[:, chan] = temp[:, chan] / np.max(np.abs(temp[:, chan]))
                # account for num channels
                temp[:, chan] = temp[:, chan] / self.num_channels 
                #print(f"\nMax of signal: {np.max(np.abs(self.signal[:, chan]))}")
                #print(f"Max of temp: {np.max(np.abs(temp[:, chan]))}")
        else:
            self.level = level
            # Apply presentation level
            for chan in range(0, self.num_channels):
                temp[:, chan] = temp[:, chan] * self.level
                #print(f"\nMax of signal: {np.max(np.abs(self.signal[:, chan]))}")
                #print(f"Max of temp: {np.max(np.abs(temp[:, chan]))}")

        # Make modified signal available for testing
        self.sig = temp

        # Present audio
        if self.num_outputs < self.num_channels:
            print(f"\naudiomodel: {self.num_channels}-channel file, but "
                f"only {self.num_outputs} audio device output channels!")
            print("audiomodel: Dropping " +
                f"{self.num_channels - self.num_outputs} audio file channels")
            sd.play(temp[:, 0:self.num_outputs], mapping=self.channels[0:self.num_outputs])
        else:
            sd.play(temp.T, self.fs, mapping=self.channels)
            #sd.wait(self.dur+0.5)


    def stop(self):
        """ Stop audio presentation.
        """
        sd.stop()
