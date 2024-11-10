from pyo import *

# Function that returns the factor we need to multiply amplitude by,
# to ensure an equal perceptual volume for various frequencies
# This is based on A-weighting dB corrections
def loudness_correction_factor(freq):
    # calculate amplitude scaling factor
    f = freq
    numerator = 12194**2 * f**4
    denominator = (f**2 + 20.6**2) * ((f**2 + 107.7**2) * (f**2 + 737.9**2))**0.5 * (f**2 + 12194**2)
    R = numerator / denominator
    return 0.5 / R


def basic(freq, volume):
    high_harmonic = 4
    harmonics = [freq * i for i in range(1, high_harmonic)]
    correction = loudness_correction_factor(freq) 
    amps = [volume * correction * 0.33 / i for i in range(1, high_harmonic)]
    return Sine(freq=harmonics, mul=amps)