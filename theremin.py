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


def get_distance_cm():
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
# raspberry pi hardware doesn't support duplex
s = Server(duplex=0, buffersize=1024).boot()
s.amp = 0.5

# start the audio server, and wait a bit so we don't get weird blips as starting-up artifacts
s.start()
time.sleep(0.1)

# interpolating signals to control base frequency and volume
freq = SigTo(value=0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0)
volume = SigTo(value=0, time=SENSOR_SAMPLE_PERIOD_SEC, init=0)

output = waveforms.basic(freq, volume)
output.out()

try:
    n_measurements_out_of_range = 0
    out_of_range = False
    while True:
        distance_cm = get_distance_cm()
        print("distance cm:", distance_cm)

        # if out of range, turn off the sound
        if distance_cm > MAX_DIST_CM:
            n_measurements_out_of_range += 1
            if n_measurements_out_of_range >= 3:
                out_of_range = True
                volume.setValue(0)
        else:
            volume.setValue(1)

            # calculate semitone delta from reference frequency (at 20cm), based on distance
            # closer to the sensor should be higher pitched, like real theremins
            semitones_delta = (20 - distance_cm) / CM_PER_SEMITONE
            if AUTOTUNE:
                semitones_delta = int(semitones_delta)
            
            # if this is the first pitch measurement, don't interpolate
            # (so that previous irrelevant pitch information doesn't get mixed in)
            freq.setTime(0 if out_of_range else SENSOR_SAMPLE_PERIOD_SEC)

            freq.setValue(FREQ_AT_20_CM * 2**(semitones_delta / 12))

            out_of_range = False
            n_measurements_out_of_range = 0


        time.sleep(SENSOR_SAMPLE_PERIOD_SEC)

except KeyboardInterrupt:
    print("Keyboard interrupt, cleaning up GPIO and audio server")
    GPIO.cleanup()
    s.stop()