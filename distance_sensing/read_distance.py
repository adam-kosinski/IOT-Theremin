import RPi.GPIO as GPIO
import time

TRIG_PIN = 24
ECHO_PIN = 23


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

try:
    while True:
        distance = distance_measurement()
        print("Distance:", distance, "cm")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()