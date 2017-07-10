"""
Copyright (C) 2017 - Justin Tinker
This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 United States License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/3.0/us/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from listeningsheets import constants
import os

def fillInGaps(note_lengths):
    taps = []
    for i in range(len(note_lengths)):
        time = 0
        if i > 0:
            for j in note_lengths[:i]:
                time += j
        taps.append((time, note_lengths[i]))
    return taps

def tapsToMidi(taps, tempo = 60, pitch = 60, velocity = 100, resolution = 4, time_signature=(4,4), key_signature="C"):
    """Converts Taps to Midi Format (Rhythyms -> Sheet Music)
    @param taps: an array of tuples containing the time a note occurs and the length of the note (both in ticks)
    @param tempo: number of beats per minute
    @param pitch: the note to use when converting the rhythyms to sheet music (expressed using midi numbers)
    @param key_signature: String expressing the key signature the sheet music will be in (usually the same note as the pitch)
    @param time_signature: tuple containing numerator first, denominator seconds
    @param velocity: loudness of the note, expressed using MIDI convention
    """

    track = MidiTrack()

    track.append(MetaMessage('key_signature', key=key_signature))
    track.append(MetaMessage('time_signature', numerator=time_signature[0], denominator=time_signature[1]))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(tempo)))


    (_, duration) = taps[0]
    track.append(Message('note_on', note=pitch, velocity=velocity, time=0))
    track.append(Message('note_off', note=pitch, velocity=velocity, time=duration))

    for i in range(1, len(taps)):
        (current_time, duration) = taps[i]
        (last_time, last_duration) = taps[i-1]
        from_last = current_time - (last_time + last_duration)
        track.append(Message('note_on', note=pitch, velocity=velocity, time=from_last))
        track.append(Message('note_off', note=pitch, velocity=velocity, time=duration))

    midi = MidiFile(ticks_per_beat=resolution)
    midi.tracks.append(track)

    return midi

def to_midi(midi, filename=constants.default_midi_filename, testing=True):

    if not os.path.exists(constants.midi_directory):
        os.makedirs(constants.midi_directory)

    if testing:
        location = os.path.join(constants.midi_directory, filename)
    else:
        location = filename

    midi.save(location)

    return os.path.abspath(os.path.join(constants.midi_directory, filename))

def to_pdf(midi, filename=constants.default_pdf_filename, thirds=False, testing=True):

    midifilename = constants.get_date_time_filename(".mid")

    if not os.path.exists(constants.temp_directory):
        os.makedirs(temp_directory)

    midi.save(os.path.join(constants.temp_directory, midifilename))

    if not os.path.exists(constants.pdf_directory):
        os.makedirs(constants.pdf_directory)

    if not thirds:
        option = constants.default_option
    else:
        option =  constants.triplets_option

    if testing:
        location = os.path.join(constants.pdf_directory, filename)
    else:
        location = filename


    command = 'MuseScore.exe --export-to "'+location+'" "'+os.path.join(constants.temp_directory, midifilename)+'" --midi-operations "'+option+'"'

    print(command)

    os.system(command)

    os.remove(os.path.join(constants.temp_directory, midifilename))

    return os.path.abspath(os.path.join(constants.pdf_directory, filename))

if __name__ == "__main__":
    taps = [(5, 2), (10, 2), (15, 2), (20, 2)]
    midifile = tapsToMidi(taps)
    export(midifile)
