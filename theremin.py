# suppress wx gui warning before importing pyo
import os
os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time
import numpy as np
import RPi.GPIO as GPIO
import waveforms
import gpio

SENSOR_SAMPLE_PERIOD_SEC = 0.100
AUTOTUNE = True
MAX_DIST_CM = 80
CM_PER_SEMITONE = 1.5
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
        

gpio.init()

# create and boot the server
# raspberry pi hardware doesn't support duplex
s = Server(duplex=0, buffersize=1024)
s.setOutputDevice(1)  # so it works even when hdmi is plugged in
s.amp = 0.3
s.boot().start()

# interpolating signals to control base frequency and volume
freq = SigTo(value=0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0)
volume = SigTo(value=0.0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0.0)

output = waveforms.sine(freq, volume)
output.out()

try:
    n_measurements_out_of_range = 0
    out_of_range = False
    while True:
        distance_cm = gpio.get_distance_cm()
        print("distance cm:", distance_cm)

        # if out of range, turn off the sound
        if distance_cm > MAX_DIST_CM:
            n_measurements_out_of_range += 1
            if n_measurements_out_of_range >= 3:
                out_of_range = True
                volume.setValue(0)
        else:
            volume.setValue(1)

            # if this is the first pitch measurement, don't interpolate
            # (so that previous irrelevant pitch information doesn't get mixed in)
            freq.setTime(0 if out_of_range else SENSOR_SAMPLE_PERIOD_SEC)

            # calculate semitone delta from reference frequency (at 20cm), based on distance
            # closer to the sensor should be higher pitched, like real theremins
            semitones_delta = (20 - distance_cm) / CM_PER_SEMITONE
            if AUTOTUNE:
                semitones_delta = int(semitones_delta)
            # set frequency
            freq.setValue(FREQ_AT_20_CM * 2**(semitones_delta / 12))

            amplitude_out = s.amp * volume.value
            print(f"{freq.value:.1f} Hz, amplitude {amplitude_out:.3f}")

            out_of_range = False
            n_measurements_out_of_range = 0

        time.sleep(SENSOR_SAMPLE_PERIOD_SEC)

except KeyboardInterrupt:
    print("Keyboard interrupt, cleaning up GPIO and audio server")
    gpio.cleanup()
    s.stop()