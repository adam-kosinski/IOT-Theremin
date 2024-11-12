import RPi.GPIO as GPIO
import time

PITCH_TRIG = 24
PITCH_ECHO = 23

VOLUME_ECHO = 17
VOLUME_TRIG = 27


def init():
    # Initialize GPIO pins
    
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(PITCH_TRIG, GPIO.OUT)
    GPIO.setup(PITCH_ECHO, GPIO.IN)

    GPIO.setup(VOLUME_TRIG, GPIO.OUT)
    GPIO.setup(VOLUME_ECHO, GPIO.IN)



def cleanup():
    GPIO.cleanup()


def get_distance_cm():
    trigger = VOLUME_TRIG
    echo = VOLUME_ECHO

    # Send 10us pulse to trigger
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)

    # Measure pulse duration
    start_time = time.time()
    stop_time = time.time()
    while GPIO.input(echo) == 0:
        start_time = time.time()
    while GPIO.input(echo) == 1:
        stop_time = time.time()

    # Calculate pulse duration (in seconds)
    us_elapsed = 1000000*(stop_time - start_time)
    distance_cm = us_elapsed / 58  # from datasheet

    return distance_cm
