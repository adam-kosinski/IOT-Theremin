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
FREQ_AT_20_CM = 880


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
        self.s.setOutputDevice(1)  # so it works even when hdmi is plugged in
        self.s.amp = 0.3
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
            target_volume = min(1, volume_cm / 50)
            self.volume.setValue(target_volume)

            # if this is the first pitch measurement, don't interpolate
            # (so that previous irrelevant pitch information doesn't get mixed in)
            # reads previous out_of_range value
            self.freq.setTime(0 if self.out_of_range else SENSOR_SAMPLE_PERIOD_SEC)
            # set out of range correctly
            self.out_of_range = False
            n_measurements_out_of_range = 0

            # calculate semitone delta from reference frequency (at 20cm), based on distance
            # closer to the sensor should be higher pitched, like real theremins
            semitones_delta = (20 - pitch_cm) / CM_PER_SEMITONE
            if AUTOTUNE:
                semitones_delta = int(semitones_delta)
            # set frequency
            self.freq.setValue(FREQ_AT_20_CM * 2**(semitones_delta / 12))

            amplitude_out = self.s.amp * self.volume.value
            print(f"{self.freq.value:.1f} Hz, amplitude {amplitude_out:.3f}")


def signal_handler(sig, frame):
    theremin.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    theremin = Theremin()

    while True:
        print("yay")
        time.sleep(1)