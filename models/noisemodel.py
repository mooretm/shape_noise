""" Class that handles shaping white Gaussian noise. """

###########
# Imports #
###########
# GUI
from tkinter import messagebox

# Data Science
import numpy as np
import random
from scipy import signal

# System
import sys


#########
# BEGIN #
#########
class NoiseShaper:
    """ Create filtered noise based on the power spectral
        density of a given audio signal.
    """
    def shape_noise(self, audio, fs, correlated):
        """ Create white Gaussian noise. Create filter shaped like 
            the spectrum of the provided audio file. Pass the 
            noise through the filter. Adjust RMS amplitude of noise 
            to match RMS amplitude of audio file.

            :returns: a filtered white Gaussian noise
        """
        # Assign public attributes
        self.audio = audio
        self.fs = fs
        self.correlated = correlated

        # Create noise
        self._create_noise()

        # Create filtered noise
        self._create_filter()

        # Return calibration noise
        return self.adj_filtered_noise


    def _create_noise(self):
        """ Create and prepare Gaussian noise. """
        print("noisemodel: Creating white noise")
        # Create noise
        self.noise = self.mk_wgn(self.fs, 30)
        self.dur_noise = len(self.noise) / self.fs
        self.t_noise = np.arange(0, self.dur_noise, 1/self.fs)

        # P Welch of noise and audio file
        self.f_stim, self.den_stim = signal.welch(
            self.audio, self.fs, nperseg=2048)


    def mk_wgn(self, fs, dur):
        """ Function to generate white Gaussian noise. """
        if self.correlated:
            print(f"noisemodel: Using correlated noise")
            random.seed(4)
        else:
            print(f"noisemodel: Using uncorrelated noise")
        
        wgn = [random.gauss(0.0, 1.0) for i in range(fs*dur)]
        wgn = self._doNormalize(wgn)

        return wgn


    ####################
    # Filter Functions #
    ####################
    def _create_filter(self):
        """ Create even-numbered offset to remove 
            extra points added by convolution
            (directly related to the number of
            taps - 1)
        """
        print(f"noisemodel: Creating filter")
        # Set number of filter taps
        num_taps = self._filter_taps() # Must be odd
        offset = num_taps - 1

        # # Find delay introduced by filter
        # filt_delay = self._filter_delay(num_taps, self.fs)
        # print(f"Filter delay (s): {filt_delay}")

        # Create the filter
        fir_filt = signal.firwin2(
            numtaps=num_taps, 
            freq=self.f_stim/np.max(self.f_stim), 
            gain=np.sqrt(self.den_stim))

        # FIR frequency response
        w, h = signal.freqz(fir_filt)
        w = w * self.fs / (2*np.pi)

        # Call function to apply filter
        self._apply_filter(fir_filt, offset)


    def _apply_filter(self, filter, offset):
        """ Convolve noise with filter. """
        print("noisemodel: Applying filter to noise")
        # Apply FIR to noise
        filtered_noise = np.convolve(filter, self.noise)
        # Normalize filtered noise
        filtered_noise = filtered_noise / np.max(np.abs(filtered_noise))
        # Remove the extra values added during convolution from beginning/end
        filtered_noise = filtered_noise[:-offset]
        # P Welch of filtered noise
        f_filt_noise, den_filt_noise = signal.welch(
            filtered_noise, self.fs, nperseg=2048)

        # Equalize RMS
        self._correct_amplitude(filtered_noise)


    def _correct_amplitude(self, filtered_noise):
        """ Set the RMS of the noise to the RMS of the signal. """
        print("noisemodel: Matching amplitudes")
        # Get RMS of audio
        rms_stim = self._rms(self.audio)
        # Apply gating to filtered noise
        filtered_noise = self._doGate(sig=filtered_noise,
            rampdur=0.02,fs=self.fs)
        # Normalize gated filtered noise
        filtered_noise = self._doNormalize(filtered_noise)
        # Get RMS of gated and normalized filtered noise
        rms_filt_noise = self._rms(filtered_noise)
        # Get difference in RMS between signal and noise
        amp_diff =  rms_stim / rms_filt_noise
        print(f"noisemodel: RMS of stimulus: {np.round(rms_stim, 5)}")
        # Apply RMS offset to noise to equate RMS levels
        self.adj_filtered_noise = filtered_noise * amp_diff
        # Find PSD of final noise
        self.f_adj_filt_noise, self.den_adj_filt_noise = signal.welch(
            self.adj_filtered_noise, self.fs, nperseg=2048)
        print(f"noisemodel: RMS of adjusted filtered noise: " +
            f"{np.round(self._rms(self.adj_filtered_noise), 5)}")


    ###################################
    # Noise Shaping Support Functions #
    ###################################
    @staticmethod
    def _filter_delay(num_taps, fs):
        """ Calculate filter delay. """
        filt_delay = (num_taps - 1) / (2 * fs)
        return filt_delay


    @staticmethod
    def _filter_taps(d1=10**-4, d2=10**-3, Df=1000):
        """ Determine number of filter taps. Based on:
            https://dsp.stackexchange.com/questions/31066/how-many-taps-does-an-fir-filter-need
        """
        num_taps = int((2/3)*np.log10(1/(10*d1*d2))*Df)
        if not num_taps % 2:
            num_taps += 1

        return num_taps


    @staticmethod
    def _doNormalize(sig):
        """ Remove DC offset and normalize by max value. """
        # remove DC offset
        sig = sig - np.mean(sig)
        # normalize
        sig = sig / np.max(abs(sig))

        return sig


    @staticmethod
    def _check_for_clipping(adj_filtered_noise):
        """ Check for clipping in the final noise. """
        max_amp = np.max(abs(adj_filtered_noise))
        if max_amp > 1:
            print("noisemodel: Clipping has occurred!\n" +
                  "Calibration file not created!")
            messagebox.showerror(
                title="Clipping!",
                message="There is clipping in the output file!",
                detail="If the original audio file is near the +1/-1 " +
                    "limits, some noise fluctuations will exceed these  " +
                    "boundaries and cause clipping\n" +
                    "Aborting."
            )
            sys.exit()
        else:
            print("No clipping! File OK!")


    @staticmethod
    def _db2mag(db):
        """ Convert decibels to magnitude. Takes a single
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
    def _mag2db(mag):
        """ Convert magnitude to decibels. Takes a single
            value or a list of values.
        """
        try:
            db = [20 * np.log10(x) for x in mag]
            return db
        except:
            db = 20 * np.log10(mag)
            return db


    @staticmethod
    def _doGate(sig, rampdur=0.02, fs=48000):
        """ Apply rising and falling ramps to signal SIG, of 
            duration RAMPDUR. Takes a 1-channel or 2-channel 
            signal. 

                SIG: a 1-channel or 2-channel signal
                RAMPDUR: duration of one side of the gate in 
                    seconds
                FS: sampling rate in samples/second

                Example: 
                [t, tone] = mkTone(100,0.4,0,48000)
                gated = _doGate(tone,0.01,48000)

            Original code: Anonymous
            Adapted by: Travis M. Moore
            Last edited: Jan. 13, 2022          
        """
        gate =  np.cos(np.linspace(np.pi, 2*np.pi, int(fs*rampdur)))
        # Adjust envelope modulator to be within +/-1
        gate = gate + 1 # translate modulator values to the 0/+2 range
        gate = gate/2 # compress values within 0/+1 range
        # Create offset gate by flipping the array
        offsetgate = np.flip(gate)
        # Check number of channels in signal
        if len(sig.shape) == 1:
            # Create "sustain" portion of envelope
            sustain = np.ones(len(sig)-(2*len(gate)))
            envelope = np.concatenate([gate, sustain, offsetgate])
            gated = envelope * sig
        elif len(sig.shape) == 2:
            # Create "sustain" portion of envelope
            sustain = np.ones(len(sig[0])-(2*len(gate)))
            envelope = np.concatenate([gate, sustain, offsetgate])
            gatedLeft = envelope * sig[0]
            gatedRight = envelope * sig[1]
            gated = np.array([gatedLeft, gatedRight])
        return gated


    @staticmethod
    def _rms(sig):
        """ Calculate the root mean square of a signal. 
            
            NOTE: np.square will return invalid, negative 
                results if the number excedes the bit 
                depth. In these cases, convert to int64
                EXAMPLE: sig = np.array(sig,dtype=int)

            Written by: Travis M. Moore
            Last edited: Feb. 3, 2020
        """
        theRMS = np.sqrt(np.mean(np.square(sig)))
        return theRMS


if __name__ == "__main__":
    pass
