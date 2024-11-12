from pyo import *

def get_correction_factor(freq):
    f = freq
    numerator = 12194**2 * f**4
    denominator = (f**2 + 20.6**2) * ((f**2 + 107.7**2) * (f**2 + 737.9**2))**0.5 * (f**2 + 12194**2)
    R = numerator / denominator
    # return unscaled version
    return 1 / R

loudness_low_freq_threshold = 200
max_correction_factor = get_correction_factor(loudness_low_freq_threshold)

# Function that returns the factor we need to multiply amplitude by,
# to ensure an equal perceptual volume for various frequencies
# This is based on A-weighting dB corrections
def loudness_correction_factor(freq):
    # calculate amplitude scaling factor
    unscaled = get_correction_factor(freq)
    scaled = unscaled / max_correction_factor
    clamped = min(0.8, scaled)
    return clamped


def standard(freq, volume):
    high_harmonic = 3
    harmonics = [freq * i for i in range(1, high_harmonic)]
    amps = [volume * 0.33 / i for i in range(1, high_harmonic)]
    return Sine(freq=harmonics, mul=amps)

def sine(freq, volume):
    return Sine(freq=freq, mul=volume)