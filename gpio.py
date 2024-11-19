import RPi.GPIO as GPIO
import time

PITCH_TRIG = 24
PITCH_ECHO = 23

VOLUME_ECHO = 17
VOLUME_TRIG = 27

t_start = {}
def handle_edge(pin):
    print("pin", pin, "value", GPIO.input(pin))
    if GPIO.input(pin) == 1:
        t_start[pin] = time.time()
        print("rising")
    else:
        print(t_start)
        # print(1000*(time.time() - t_start[pin]))


def init():
    # Initialize GPIO pins
    
    GPIO.setmode(GPIO.BCM)  

    GPIO.setup(PITCH_TRIG, GPIO.OUT)
    GPIO.setup(PITCH_ECHO, GPIO.IN)

    GPIO.setup(VOLUME_TRIG, GPIO.OUT)
    GPIO.setup(VOLUME_ECHO, GPIO.IN)



def cleanup():
    GPIO.cleanup()


class DistanceMeasurement():
    distance_cm = None
    t0 = None
    saw_rising = False
    saw_falling = False

    def __init__(self, trigger_pin, echo_pin, max_dist_cm=50):
        self.echo_pin = echo_pin
        self.max_pulse_duration_s = (max_dist_cm * 58) / 1000000

        # Send 10us pulse to trigger
        GPIO.output(trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(trigger_pin, False)
    
    def check_result(self):
        # called continuously until we get an answer

        if self.distance_cm is not None:
            return

        value = GPIO.input(self.echo_pin)

        # on rising edge, record start time
        if not self.saw_rising and value == 1:
            self.saw_rising = True
            self.t0 = time.time()

        # on falling edge, measure distance using elapsed us
        if self.saw_rising and not self.saw_falling and value == 0:
            self.saw_falling = True
            us_elapsed = 1000000*(time.time() - self.t0)
            self.distance_cm = us_elapsed / 58  # from datasheet
        
        # if time waited would exceed max distance, stop waiting and use infinite distance
        # this considerably speeds up how long it takes to read the sensors, allowing
        # us to run a blocking loop without an issue
        if self.distance_cm is None and self.t0 is not None and time.time() - self.t0 > self.max_pulse_duration_s:
            self.distance_cm = float("inf")


def get_distances(max_dist_cm=50):
    # t0 = time.time()

    pitch = DistanceMeasurement(PITCH_TRIG, PITCH_ECHO, max_dist_cm)
    volume = DistanceMeasurement(VOLUME_TRIG, VOLUME_ECHO, max_dist_cm)
    while True:
        pitch.check_result()
        volume.check_result()
        if pitch.distance_cm is not None and volume.distance_cm is not None:
            break
    
    # print(f"sensor read time {1000*(time.time() - t0)} ms")
    return pitch.distance_cm, volume.distance_cm
