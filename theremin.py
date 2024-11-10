# suppress wx gui warning before importing pyo
import os
os.environ['PYO_GUI_WX'] = '0'

from pyo import *
import time
import numpy as np
import RPi.GPIO as GPIO
import waveforms

TRIG_PIN = 24
ECHO_PIN = 23
SENSOR_SAMPLE_PERIOD_SEC = 0.080
AUTOTUNE = True
MAX_DIST_CM = 80
CM_PER_SEMITONE = 1.5
FREQ_AT_20_CM = 880


def distance_measurement():
    # Send 10us pulse to trigger
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    # Measure pulse duration
    start_time = time.time()
    stop_time = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()

    # Calculate pulse duration (in seconds)
    us_elapsed = 1000000*(stop_time - start_time)
    distance_cm = us_elapsed / 58  # from datasheet

    return distance_cm


# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)


# create and boot the server
s = Server(duplex=0, buffersize=1024).boot()
s.amp = 0.5
# start the audio server, and wait a bit so we don't get weird blips as starting-up artifacts
s.start()
time.sleep(0.1)

# interpolating signals to control base frequency and volume
freq = SigTo(value=FREQ_AT_20_CM, time=SENSOR_SAMPLE_PERIOD_SEC, init=FREQ_AT_20_CM)
volume = SigTo(value=0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0)

output = waveforms.basic(freq, volume)
output.out()

try:
    while True:
        distance_cm = distance_measurement()
        print("distance cm:", distance_cm)

        # if out of range, turn off the sound
        if distance_cm > MAX_DIST_CM:
            volume.setValue(0)
        else:
            volume.setValue(1)

            # calculate semitone delta from reference frequency (at 20cm), based on distance
            # closer to the sensor should be higher pitched, like real theremins
            semitones_delta = (20 - distance_cm) / CM_PER_SEMITONE
            if AUTOTUNE:
                semitones_delta = int(semitones_delta)
            
            freq.setValue(FREQ_AT_20_CM * 2**(semitones_delta / 12))

            # bring volume up to 1 once we get our first measurement
            volume.setValue(1)

        time.sleep(SENSOR_SAMPLE_PERIOD_SEC)

except KeyboardInterrupt:
    print("Keyboard interrupt, cleaning up GPIO and audio server")
    GPIO.cleanup()
    s.stop()