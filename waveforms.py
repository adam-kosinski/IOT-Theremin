from pyo import *

# attempt to equalize perceived loudness across pitches --------------------------------------
# this had some problems with distortion

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


# waveform definitions --------------------------------------------

def standard(freq, volume):
    # uses subtle vibrato
    vibrato = 1 + 0.006*LFO(freq=6, type=3)
    signal = Blit(freq=freq*vibrato, harms=3, mul=volume)
    return Freeverb(signal, size=0, damp=0, bal=0.1)

def tremolo(freq, volume):
    signal = standard(freq, volume)
    lfo = LFO(4, type=3, sharp=1)
    return Mix(signal, mul=lfo)

def supersaw(freq, volume):
    mix = Mix([
        LFO(freq, mul=volume, type=0, sharp=0.4),
        LFO(2*freq, mul=0.3*volume, type=0, sharp=0.2),
        ])
    return Freeverb(Chorus(mix), size=0, damp=0, bal=0.25)

def supertriangle(freq, volume):
    mix = Mix([
        LFO(freq, mul=volume, type=3),
        LFO(2*freq, mul=0.4*volume, type=3),
        ])
    db_compress = 20
    ratio = 5
    autogain_db = db_compress * (1 - (1/ratio))
    compressed = Compress(mix, thresh=-db_compress, ratio=ratio, mul=10**(autogain_db/20))
    return Freeverb(Chorus(compressed), size=0, damp=0, bal=0.1)

def flute(freq, volume):
    high_harmonic = 12
    harmonics = [freq * i for i in range(1, high_harmonic)]
    amps = [volume * 0.3**i for i in range(high_harmonic)]
    vibrato = 1 + 0.15*LFO(freq=6, type=3)
    mix = Mix([
        Sine(freq=harmonics, mul=amps),
        Biquad(Noise(mul=0.7*volume), freq=2*freq, q=100, type=2, mul=10)
    ], mul=vibrato)
    return Freeverb(mix, size=0, damp=0, bal=0.25)

def harmonic_rainbow(freq, volume):
    mix = Mix([
        LFO(0.5*freq, type=3, sharp=0, mul=0.1*volume*LFO(freq=2, type=2)),
        Sine(freq, mul=0.5*volume*LFO(freq=2, type=3)),
        Sine(2*freq, mul=0.4*volume*LFO(freq=1.2, type=2)),
        Sine(3*freq, mul=0.2*volume*LFO(freq=1.4, type=2)),
        LFO(4*freq, type=3, sharp=0, mul=0.05*volume*LFO(freq=1.7, type=2)),
    ])
    return Freeverb(mix)
    
def sine(freq, volume):
    return Sine(freq=freq, mul=volume)


waveform_dict = {
    "standard": standard,
    "tremolo": tremolo,
    "super saw": supersaw,
    "super triangle": supertriangle,
    "flute": flute,
    "harmonic rainbow": harmonic_rainbow,
    "sine": sine,
}