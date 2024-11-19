
import signal
import sys
import RPi.GPIO as GPIO
import time

PITCH_ECHO = 23

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):
    print("Button pressed!")

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(PITCH_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PITCH_ECHO, GPIO.RISING, 
            callback=button_pressed_callback, bouncetime=100)
    
    GPIO.output(24, True)
    time.sleep(0.00001)
    GPIO.output(24, False)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        print("boo")
        time.sleep(1)