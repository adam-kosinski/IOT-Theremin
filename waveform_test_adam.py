# suppress wx gui warning before importing pyo
import os
os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time
import waveforms

# create and boot the server
s = Server(duplex=0, buffersize=1024).boot()

s.amp = 0.5
# start the audio server, and wait a bit so we don't get weird blips as starting-up artifacts
s.start()
time.sleep(0.1)

freq = SigTo(value=440, init=440, time=0.500)
vol = SigTo(value=1, init=0, time=0.100)
a = waveforms.waveform_dict["harmonic rainbow"](freq, vol)
a.out()

for f in [440.0, 554.365, 659.255, 880.0]:
    print(f"freq {f}")
    freq.setValue(f)
    time.sleep(3)

vol.setValue(0)
time.sleep(1)

s.stop()
