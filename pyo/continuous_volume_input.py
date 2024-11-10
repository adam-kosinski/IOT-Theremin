# suppress wx gui warning before importing pyo
import os
os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time
import numpy as np


# distance sensor can run at a period of 60ms
SENSOR_SAMPLE_PERIOD_MS = 0.060


# create and boot the server
s = Server(duplex=0, buffersize=1024).boot()
s.amp = 0.5
# start the audio server, and wait a bit so we don't get weird blips as starting-up artifacts
s.start()
time.sleep(0.1)



# Creates a sine wave player.
# The out() method starts the processing
# and sends the signal to the output.
# Use SigTo so volume changes happen on a linear ramp
volume = SigTo(value=1, time=SENSOR_SAMPLE_PERIOD_MS, init=1)
a = Sine(880, mul=volume).out()

for i in range(100):
    new_volume = float(0.5 + 0.5 * np.sin(i / 5))
    print(new_volume)
    volume.setValue(new_volume)
    time.sleep(SENSOR_SAMPLE_PERIOD_MS)


s.stop()