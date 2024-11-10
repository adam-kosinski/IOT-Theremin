import pygame
import numpy as np
import time

# Initialize Pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)

# Define parameters
frequency = 440  # Frequency of the sine wave (Hz)
sample_rate = 44100  # Sample rate (samples per second)
duration = 1.0  # Duration of the sound (seconds)

# Generate the sine wave
n_samples = int(sample_rate * duration)
x = np.linspace(0, duration, n_samples, endpoint=False)
samples = (np.sin(2 * np.pi * frequency * x) * 32767).astype(np.int16)

# Convert the samples to a Pygame sound object
sound = pygame.sndarray.make_sound(samples)

# Play the sound
sound.play()

# Keep the script running to allow sound to play
time.sleep(duration)

# Quit the mixer after playing the sound
pygame.mixer.quit()
