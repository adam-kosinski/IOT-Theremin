import pyaudio
import numpy as np
import time

amplitude = 0.005

def callback(in_data, frame_count, time_info, status):
    data = amplitude * np.random.randn(frame_count).astype(np.float32)
    return (data, pyaudio.paContinue)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1,
                rate=44100, output=True, stream_callback=callback)

for i in range(4):
    amplitude *= 2
    print(f"{i} sec")
    time.sleep(1)

stream.stop_stream()
stream.close()
p.terminate()
