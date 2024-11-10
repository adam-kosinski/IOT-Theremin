# suppress wx gui warning before importing pyo
# import os
# os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time

# create and boot the server
s = Server().boot()

s,setOutputDevice(0)
# drop the gain by 20 dB.
s.amp = 0.1
# start the audio server, and wait a bit so we don't get weird blips as starting-up artifacts
s.start()
time.sleep(0.1)

# Creates a sine wave player.
# The out() method starts the processing
# and sends the signal to the output.
a = Sine(440).out()

for f in [440.0, 554.365, 659.255, 880.0]:
    print(f"freq {f}")
    a.setFreq(f)
    time.sleep(1)

s.stop()
