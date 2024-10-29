import pyaudio
import numpy as np

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32, channels=1,
                rate=44100, output=True)

frames_per_buffer = 1024
for _ in range(1000):
    audio_data = np.random.randn(frames_per_buffer).astype(np.float32)
    stream.write(audio_data.tobytes())

stream.stop_stream()
stream.close()
p.terminate()
