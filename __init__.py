"""
Copyright (C) 2017 - Justin Tinker
This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 United States License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/3.0/us/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

from listeningsheets import reader
from listeningsheets import exporter
import sys
import argparse
import os

def convert(soundFile, tempo, precision, thirds=False, sample_size=0.01, filename=None, show_graphs=False, fill=True, view=False, save_midi=True, midifilename=None, pitch = 60,
time_signature=(4,4), key_signature="C", testing=True):
    """Wrapper for the conversion from audio to sheet music (Main Loop)
    @param soundFile: file containing the audio
    @param tempo: beats per minute of rhythym
    @param sample_size: size of chunks used to process audio, expressed in seconds (0.1 = 1/10th-second chunks)
    @param precision: smallest note than can occur in the sheet music, expressed in fractions of a quarter note (1 = quarter, 2 = eighth, 4 = sixteenth...)
    @param filename: output file
    @param show_graphs: essentially debugging
    @param fill: if false, preserve the rests in the rhythym
    @param view: open pdf after finishing
    @param save_midi: save the midi file to the midi directory
    @param thirds: allow for triplets
    @param pitch: the note at which the rhythyms are transcribed, given in midi format. Note conversion found in listeningsheets.constants
    @param time_signature: tuple in form (numerator, denominator)
    @param key_signature: string giving key signature, usually same key as pitch, examples found in listeningsheets.constants
    """


    graphs = []

    segment = reader.read(soundFile)
    sample_size = round(sample_size * reader.sample_rate(segment))
    resolution = round(reader.resolution(segment, sample_size=sample_size, tempo=tempo))

    samples = reader.process(segment.get_array_of_samples())
    samples = reader.to_binary(samples, sample_size=sample_size)

    if show_graphs:
        graphs.append(reader.from_binary(samples))

    (samples, resolution) = reader.snap_to_duration(precision, resolution, samples)

    if show_graphs:
        graphs.append(reader.from_binary(samples))

    taps = reader.to_taps(samples, fill=fill, resolution=resolution)

    midifile = exporter.tapsToMidi(taps, resolution=resolution, tempo=tempo, pitch=pitch,
    time_signature=time_signature, key_signature=key_signature)

    if filename == None:
        filename = os.path.splitext(os.path.basename(soundFile))[0] + ".pdf"

    pdf = exporter.to_pdf(midifile, filename=filename, thirds=thirds, testing=testing)

    if save_midi:
        midi_filename = os.path.splitext(os.path.basename(filename))[0] + ".mid"
        exporter.to_midi(midifile, filename=midi_filename)

    if show_graphs:
        for graph in graphs:
            reader.plot(graph)

    if view:
        os.system("start %s" % pdf)

    raw_data = None
    with open(pdf, 'rb') as raw:
        raw_data = raw.read()

    return (taps, pdf, raw_data)

def analyze(segment, tempo, precision, sample_size=0.01, fill=True):
    sample_size = round(sample_size * reader.sample_rate(segment))
    resolution = round(reader.resolution(segment, sample_size=sample_size, tempo=tempo))

    samples = reader.process(segment.get_array_of_samples())
    samples = reader.to_binary(samples, sample_size=sample_size)

    pre_snap_taps = reader.to_taps(samples, fill=fill, resolution=resolution)

    (samples, resolution) = reader.snap_to_duration(precision, resolution, samples)

    post_snap_taps = reader.to_taps(samples, fill=fill, resolution=resolution)

    return (post_snap_taps, pre_snap_taps)
