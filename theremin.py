# suppress wx gui warning before importing pyo
import os
os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time
import numpy as np
import RPi.GPIO as GPIO
import waveforms
import gpio
import signal
from threading import Timer

SENSOR_SAMPLE_PERIOD_SEC = 0.100
AUTOTUNE = True
MAX_DIST_CM = 80
CM_PER_SEMITONE = 1.5
CM_PER_DB = 0.4
FREQ_AT_20_CM = 440


# class to record a signal and fade in / fade out at the ends to prevent clicking
class Recording:
    fade_time = 0.1
    
    def __init__(self, signal, filename):
        self.fader = Fader(fadein=self.fade_time, fadeout=self.fade_time)
        faded_signal = Mix(signal, mul=self.fader)
        self.rec = Record(faded_signal, filename)
        self.fader.play()
    
    def stop_recording(self):
        self.fader.stop()
        # after fade out (plus some buffer time), stop the recording
        Clean_objects(self.fade_time + 0.5, self.rec).start()


class Theremin():
    n_measurements_out_of_range = 0
    out_of_range = False
    timer = None

    def __init__(self):
        gpio.init()

        # create and boot the audio server
        self.s = Server(duplex=0, buffersize=1024)
        self.s.setOutputDevice(1)
        self.s.amp = 0.6
        self.s.boot().start()

        # interpolating signals to control base frequency and volume
        self.freq = SigTo(value=0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0)
        self.volume = SigTo(value=0.0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0.0)
        self.audio_signal = waveforms.sine(self.freq, self.volume)
        self.audio_signal.out()

        self.main_loop()
    
    def cleanup(self):
        print("\nCleaning up theremin GPIO and audio server")
        if self.timer:
            self.timer.cancel()
        gpio.cleanup()
        self.s.stop()
    
    def main_loop(self):
        self.sensor_update()
        self.timer = Timer(SENSOR_SAMPLE_PERIOD_SEC, self.main_loop)
        self.timer.start()
    
    def sensor_update(self):
        pitch_cm, volume_cm = gpio.get_distances(MAX_DIST_CM)
        print(f"pitch {pitch_cm:.1f} cm, volume {volume_cm:.1f} cm")

        # if out of range, turn off the sound
        if pitch_cm > MAX_DIST_CM or volume_cm > MAX_DIST_CM:
            self.n_measurements_out_of_range += 1
            if self.n_measurements_out_of_range >= 3:
                self.out_of_range = True
                self.volume.setValue(0)
        else:

            # if this is the first pitch measurement, don't interpolate
            # (so that previous irrelevant pitch information doesn't get mixed in)
            # reads previous out_of_range value
            self.freq.setTime(0 if self.out_of_range else SENSOR_SAMPLE_PERIOD_SEC)
            # set out of range correctly
            self.out_of_range = False
            n_measurements_out_of_range = 0

            # FREQUENCY ------------------------------------

            # calculate semitone delta from reference frequency (at 20cm), based on distance
            # closer to the sensor should be higher pitched, like real theremins
            semitones_delta = (20 - pitch_cm) / CM_PER_SEMITONE
            if AUTOTUNE:
                semitones_delta = int(semitones_delta)
            # set frequency
            self.freq.setValue(FREQ_AT_20_CM * 2**(semitones_delta / 12))

            # AMPLITUDE -------------------------------------

            zero_volume_cm = 6

            if volume_cm < zero_volume_cm:
                target_amplitude = 0
            else:
                quiet_db = -40
                db_delta = max(0, volume_cm - zero_volume_cm) / CM_PER_DB
                db = quiet_db + db_delta
                target_amplitude = min(1, 10**(db/20))
            
            self.volume.setValue(target_amplitude)

            amplitude_out = self.s.amp * self.volume.value
            print(f"{self.freq.value:.1f} Hz, amplitude {amplitude_out:.3f}")
    
    def set_waveform(self, waveform_name):
        if self.audio_signal:
            self.audio_signal.stop()

        if waveform_name == "sine":
            self.audio_signal = waveforms.sine(self.freq, self.volume)
        elif waveform_name == "supersaw":
            self.audio_signal = waveforms.supersaw(self.freq, self.volume)
        else:
            self.audio_signal = waveforms.standard(self.freq, self.volume)

        self.audio_signal.out()
        
    def start_recording(self, filename):
        if not filename.endswith(".wav"):
            print("Must specify a .wav file")
            return
        self.recording = Recording(self.audio_signal, filename)
    
    def stop_recording(self):
        self.recording.stop()



def signal_handler(sig, frame):
    theremin.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    theremin = Theremin()

    # theremin.start_recording("test_recording.wav")

    i = 0
    while True:
        i += 1
        print(i)

        if i % 5 == 0:
            if i % 2 == 0:
                theremin.set_waveform("standard")
            else:
                theremin.set_waveform("supersaw")

        # if i > 15:
        #     theremin.stop_recording()
        time.sleep(1)