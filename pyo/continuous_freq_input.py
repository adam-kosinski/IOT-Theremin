# suppress wx gui warning before importing pyo
import os
os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time
import numpy as np

# distance sensor can run at a period of 60ms
SENSOR_SAMPLE_PERIOD_MS = 0.060


# class to record a signal and fade in / fade out at the ends to prevent clicking
class FadedRecording:
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
        


# create and boot the server
s = Server().boot()
# drop the gain by 20 dB.
# s.amp = 0.1
# start the audio server, and wait a bit so we don't get weird blips as starting-up artifacts
s.start()
time.sleep(0.1)

# Creates a sine wave player.
# The out() method starts the processing
# and sends the signal to the output.
freq = SigTo(value=440, time=SENSOR_SAMPLE_PERIOD_MS, init=440)
a = Sine(freq).out()

fader = Fader(fadein=0.5, fadeout=0.5)
rec_target = Mix(a, mul=fader)

for i in range(100):
    f = float(880 + 300 * np.sin(i / 5))
    freq.setValue(f)
    time.sleep(SENSOR_SAMPLE_PERIOD_MS)

    # record at arbitrary point
    if i == 10:
        rec = FadedRecording(a, "./recording.wav")
    if i == 70:
        rec.stop_recording()
        print("stopped recording")

s.stop()