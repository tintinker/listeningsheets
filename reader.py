"""
Copyright (C) 2017 - Justin Tinker
This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 United States License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/3.0/us/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

from pydub import AudioSegment
from matplotlib import pyplot as plt
from listeningsheets import exporter
import sys
from tempfile import NamedTemporaryFile

def read(file):
    audio = None
    try:
        audio = AudioSegment.from_file(file, file[-3:])
    except Exception as e:
        print("Error reading file. Extension may not be supported: {}".format(str(e)))
        sys.exit(0)

    if(audio.channels == 1):
        return audio
    elif(audio.channels == 2):
        return audio.split_to_mono()[0]
    else:
        print("Error getting audio channels")
        sys.exit(0)



def sample_rate(segment):
    return segment.frame_rate

def plot(samples):
    plt.plot(samples)
    plt.show()

def drop_negatives(samples):
    for i in range(len(samples)):
        if samples[i] < 0:
            samples[i] = 0
    return samples

def peak(samples):
    peakd = [0] * len(samples)
    for i in range(len(samples)-1):
        if abs(samples[i]*2) < abs(samples[i+1]):
            peakd[i] = samples[i]
        else:
            peakd[i] = 0

    avg = non_zero_avg(peakd)
    for i in range(len(peakd)):
        if(peakd[i] < avg):
            peakd[i] = 0

    return peakd

def trim(samples, precision = 3):

    for i in range(precision):
        avg = non_zero_avg(samples)
        for i in range(len(samples)):
            if(samples[i] < avg/2):
                samples[i] = 0

    return samples

def normalize(samples):
    minimum = non_zero_min(samples)
    for i in range(len(samples)):
        if samples[i] > minimum:
            samples[i] = minimum
    return samples

def to_binary(samples, sample_size=1):
    binary = [False] * int(len(samples)/sample_size)
    for i in range(len(samples) - sample_size):
        if i % sample_size == 0:
            if(sum(samples[i:i+sample_size]) > 0):
                binary[int(i/sample_size)] = True
    return binary

def from_binary(samples_in_binary):
    samples = []
    for sample in samples_in_binary:
        if sample:
            samples.append(50)
        else:
            samples.append(0)
    return samples

def non_zero_avg(samples):
    total = sum(samples)
    non_zeros = 0
    for sample in samples:
        if sample > 0:
            non_zeros = non_zeros + 1
    return total/non_zeros

def non_zero_min(samples):
    minimum = max(samples)
    for sample in samples:
        if sample > 0:
            if sample < minimum:
                minimum = sample
    return minimum

def resolution(segment, sample_size, tempo):
    """Calculate Pulses per Quarter"""
    ticks_per_second = segment.frame_rate / sample_size
    beats_per_second = tempo / 60
    return (ticks_per_second / beats_per_second) #ticks per beat

def to_taps(samples_in_binary, resolution, fill=False):

    tap_downs = []
    tap_lengths = []

    if not fill:
        counter = None
        if(samples_in_binary[0]):
            tap_downs.append(0)
            counter = 0
        for i in range(1, len(samples_in_binary)):
            if(samples_in_binary[i] and not samples_in_binary[i-1]):
                tap_downs.append(i)
                counter = i
            elif(not samples_in_binary[i] and samples_in_binary[i-1]):
                tap_lengths.append(i - counter)
                counter = None
    else:
        for i in range(1, len(samples_in_binary)):
            if(samples_in_binary[i] and not samples_in_binary[i-1]):
                tap_downs.append(i)
                if len(tap_downs) > 1:
                    tap_lengths.append((i - tap_downs[-2]))
        tap_lengths.append(len(samples_in_binary)-tap_downs[-1])

    taps = []

    for i in range(len(tap_downs)):
        tap = (tap_downs[i], tap_lengths[i])
        taps.append(tap)

    return taps

def snap_to_duration(new_resolution, resolution, samples_in_binary):
    """Makes output more even (less weirdly timed notes)
       New Resolution: (beat division) 4 for Quarter, 8 for Eigth, 16 for 16th"""

    constant = resolution / new_resolution # constant used for changing resolution (ticks per beat)

    snapped_samples = [False] * round(len(samples_in_binary) / constant)

    ons = []
    for i in range(len(samples_in_binary)):
        if(samples_in_binary[i]):
            ons.append(i)

    ons = [round(on / constant) for on in ons] # divide

    for on in ons:
        snapped_samples[on] = True

    return snapped_samples, new_resolution

def process(samples):
    samples = drop_negatives(samples)
    samples = peak(samples)
    samples = trim(samples, precision=5)
    samples = normalize(samples)
    return samples
