from pyo import *

def basic(freq, volume):
    high_harmonic = 4
    harmonics = [freq * i for i in range(1, high_harmonic)]
    amps = [volume * 0.33 / i for i in range(1, high_harmonic)]
    return Sine(freq=harmonics, mul=amps)