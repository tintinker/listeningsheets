"""
Copyright (C) 2017 - Justin Tinker
This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 United States License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/3.0/us/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

import os
from datetime import datetime

default_midi_filename = "output.mid"
default_pdf_filename = "output.pdf"

temp_directory = "temp"
pdf_directory = "pdf"
midi_directory = "midi"

default_option = os.path.join("resources","default_options.xml")
triplets_option = os.path.join("resources","with_triplets.xml")

def get_date_time_filename(fileextension):
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S"+fileextension)

def note_name_to_midi(note_name):
    """Takes note name as string ie C4 or D#5 and converts it to midi"""
    ##Copied from stack overflow: https://stackoverflow.com/questions/13926280/musical-note-string-c-4-f-3-etc-to-midi-note-value-in-python
    Notes = [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
    answer = 0
    i = 0
    #Note
    letter = note_name[:-1].upper()
    for note in Notes:
        for form in note:
            if letter.upper() == form:
                answer = i
                break;
        i += 1
    #Octave
    answer += (int(note_name[-1]))*12
    return answer

def note_name_to_keysignature(note_name):
    """Converts note to key signature ie C#4 or D5 to C# or D"""
    return note_name[:-1]

def note_name_to_midi_and_keysig(note_name):
    """Ex. Eb6 -> (72, 'Eb')"""
    return (note_name_to_midi(note_name), note_name_to_keysignature(note_name))
