""" Audio class for reading, writing, presenting
    and converting .wav files
"""

###########
# Imports #
###########
#"Chunk (non-data) not understood, skipping it."
# Occurs when scipy reads in files with uninterpretable metadata
#import warnings
#warnings.filterwarnings(action='ignore', category=UserWarning)

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
            self.signal, self.fs = sf.read(self.file_path)
            print("audiomodel: Audio file found")

        # Convert from float64 to float32
        #self.signal = self.signal.astype('float32')

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
                temp[:, chan] = temp[:, chan] - np.mean(temp[:, chan]) # remove DC offset
                temp[:, chan] = temp[:, chan] / np.max(np.abs(temp[:, chan])) # normalize
                temp[:, chan] = temp[:, chan] / self.num_channels # account for num channels
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


    @staticmethod
    def db2mag(db):
        """ 
            Convert decibels to magnitude. Takes a single
            value or a list of values.
        """
        # Must use this form to handle negative db values!
        try:
            mag = [10**(x/20) for x in db]
            return mag
        except:
            mag = 10**(db/20)
            return mag


    @staticmethod
    def mag2db(mag):
        """ 
            Convert magnitude to decibels. Takes a single
            value or a list of values.
        """
        try:
            db = [20 * np.log10(x) for x in mag]
            return db
        except:
            db = 20 * np.log10(mag)
            return db


    def rms(self, sig):
        """ 
            Calculate the root mean square of a signal. 
            
            NOTE: np.square will return invalid, negative 
                results if the number excedes the bit 
                depth. In these cases, convert to int64
                EXAMPLE: sig = np.array(sig,dtype=int)

            Written by: Travis M. Moore
            Last edited: Feb. 3, 2020
        """
        theRMS = np.sqrt(np.mean(np.square(sig)))
        return theRMS


    def setRMS(self, sig, amp, eq='n'):
        """
            Set RMS level of a 1-channel or 2-channel signal.
        
            SIG: a 1-channel or 2-channel signal
            AMP: the desired amplitude to be applied to 
                each channel. Note this will be the RMS 
                per channel, not the total of both channels.
            EQ: takes 'y' or 'n'. Whether or not to equalize 
                the levels in a 2-channel signal. For example, 
                a signal with an ILD would lose the ILD with 
                EQ='y', so the default in 'n'.

            EXAMPLE: 
            Create a 2 channel signal
            [t, tone1] = mkTone(200,0.1,30,48000)
            [t, tone2] = mkTone(100,0.1,0,48000)
            combo = np.array([tone1, tone2])
            adjusted = setRMS(combo,-15)

            Written by: Travis M. Moore
            Created: Jan. 10, 2022
            Last edited: May 17, 2022
        """
        if len(sig.shape) == 1:
            rmsdb = self.mag2db(self.rms(sig))
            refdb = amp
            diffdb = np.abs(rmsdb - refdb)
            if rmsdb > refdb:
                sigAdj = sig / self.db2mag(diffdb)
            elif rmsdb < refdb:
                sigAdj = sig * self.db2mag(diffdb)
            # Edit 5/17/22
            # Added handling for when rmsdb == refdb
            elif rmsdb == refdb:
                sigAdj = sig
            return sigAdj
            
        elif len(sig.shape) == 2:
            rmsdbLeft = self.mag2db(self.rms(sig[0]))
            rmsdbRight = self.mag2db(self.rms(sig[1]))

            ILD = np.abs(rmsdbLeft - rmsdbRight) # get lvl diff

            # Determine lvl advantage
            if rmsdbLeft > rmsdbRight:
                lvlAdv = 'left'
                #print("Adv: %s" % lvlAdv)
            elif rmsdbRight > rmsdbLeft:
                lvlAdv = 'right'
                #print("Adv: %s" % lvlAdv)
            elif rmsdbLeft == rmsdbRight:
                lvlAdv = None

            #refdb = amp - 3 # apply half amp to each channel
            refdb = amp
            diffdbLeft = np.abs(rmsdbLeft - refdb)
            diffdbRight = np.abs(rmsdbRight - refdb)

            # Adjust left channel
            if rmsdbLeft > refdb:
                sigAdjLeft = sig[0] / self.db2mag(diffdbLeft)
            elif rmsdbLeft < refdb:
                sigAdjLeft = sig[0] * self.db2mag(diffdbLeft)
            # Adjust right channel
            if rmsdbRight > refdb:
                sigAdjRight = sig[1] / self.db2mag(diffdbRight)
            elif rmsdbRight < refdb:
                sigAdjRight = sig[1] * self.db2mag(diffdbRight)

            # If there is a lvl difference to maintain across channels
            if eq == 'n':
                if lvlAdv == 'left':
                    sigAdjLeft = sigAdjLeft * self.db2mag(ILD/2)
                    sigAdjRight = sigAdjRight / self.db2mag(ILD/2)
                elif lvlAdv == 'right':
                    sigAdjLeft = sigAdjLeft / self.db2mag(ILD/2)
                    sigAdjRight = sigAdjRight * self.db2mag(ILD/2)

            sigBothAdj = np.array([sigAdjLeft, sigAdjRight])
            return sigBothAdj
