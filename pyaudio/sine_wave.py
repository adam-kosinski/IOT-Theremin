import pyaudio
import numpy as np
import time

SAMPLE_RATE = 44100
freq = 440  # hz of sine wave

signal_index = 0

def callback(in_data, frame_count, time_info, status):
    global signal_index

    # get time values
    t = (signal_index + np.arange(frame_count)) / SAMPLE_RATE

    # generate waveform - samples must have magnitude <= 1 or will get clipping
    data = np.sin(2 * np.pi * freq * t).astype(np.float32)

    # update signal index
    signal_index += frame_count

    return (data, pyaudio.paContinue)


p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1,
                rate=SAMPLE_RATE, output=True, stream_callback=callback)

start_time = stream.get_time()

for f in [440.0, 554.365, 659.255, 880.0]:
    print(f"freq {f}")
    freq = f
    time.sleep(1)

stream.stop_stream()
stream.close()
p.terminate()
