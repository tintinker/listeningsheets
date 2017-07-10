"""
Copyright (C) 2017 - Justin Tinker
This work is licensed under the Creative Commons Attribution-NonCommercial 3.0 United States License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/3.0/us/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

import listeningsheets
import listeningsheets.reader as reader
from matplotlib import pyplot as plt

def tempoCompare(soundFile, precision=4, pre_snap=False, tempo_range=(40,208), show_data=True, show_progress=False):
    segment = reader.read(soundFile)
    taps = []

    for tempo in range(tempo_range[0], tempo_range[1], 2):
        if show_progress:
            print("Tempo %d in range %d to %d. %f percent" % (tempo, tempo_range[0], tempo_range[1], (100*(tempo-tempo_range[0])/(tempo_range[1]-tempo_range[0]))))

        if not pre_snap:
            (tap_sequence, _) = listeningsheets.analyze(segment, tempo, precision)
        else:
            (_, tap_sequence) = listeningsheets.analyze(segment, tempo, precision)
        taps.append(tap_sequence)

    analyzed_taps = []

    for tap_sequence in taps:
        i = 0
        for length in tap_sequence:
            i += length % 2
        analyzed_taps.append(i)

    if show_data:
        avg = sum(analyzed_taps)/len(analyzed_taps)
        minimum = (analyzed_taps.index(min(analyzed_taps))+tempo_range[0], min(analyzed_taps))
        maximum = (analyzed_taps.index(max(analyzed_taps))+tempo_range[0], max(analyzed_taps))
        print("Most Simple Tempo: %d Score: %d" % (minimum))
        print("Most Complicated Tempo: %d Score: %d" % (maximum))
        print("Average: %d" % avg)
        print("Plotting Graph:")
        plt.plot(analyzed_taps)
        plt.show()
    return analyzed_taps

def viewMultiplePrecisions(soundFile, precisions, tempo, show_progress=False):
    segment = reader.read(soundFile)
    taps = []
    for precision in precisions:
        if show_progress:
            print("%d percent" % (100*precisions.index(precision)/len(precisions)))
        (tap_sequence, _) = listeningsheets.analyze(segment, tempo, precision)
        tap_sequence = [t[1] for t in tap_sequence]
        taps.append((tap_sequence, precision))
    return taps


def precisionCompare(soundFile, tempo, show_data=True, show_progress=False):
    segment = reader.read(soundFile)
    taps = []

    for precision in range(4, 32, 2):
        if show_progress:
            print("precision %d in range %d to %d. %f percent" % (precision, 4, 32, (100*(precision-4)/(32-4))))

        (tap_sequence, _) = listeningsheets.analyze(segment, tempo, precision)
        tap_sequence = [t[1] for t in tap_sequence]
        taps.append((tap_sequence, precision))

    quarters = []
    eighths = []
    sixteenths = []

    for (tap_sequence, precision) in taps:
        num_quarters = 0
        num_eighths = 0
        num_sixteenths = 0
        for length in tap_sequence:
            if length % precision == 0:
                num_quarters = num_quarters + 1
            elif length % (precision / 2) == 0:
                num_eighths = num_eighths + 1
            elif length % (precision / 4) == 0:
                num_sixteenths = num_sixteenths + 1
        quarters.append((num_quarters, precision))
        eighths.append((num_eighths, precision))
        sixteenths.append((num_sixteenths, precision))


    weighted_combined = []
    for i in range(len(taps)):
        score = quarters[i][0]*32 + eighths[i][0]*8 + sixteenths[i][0]*1
        print("Score %d precision %d" % (score, quarters[i][1]))
        weighted_combined.append((score, quarters[i][1]))


    if show_data:
        fig = plt.figure()

        qs = fig.add_subplot(4, 1, 1)
        ys = [q[0] for q in quarters]
        xs = [q[1] for q in quarters]
        qs.set_title("Quarter Notes")
        qs.plot(xs, ys)

        es = fig.add_subplot(4, 1, 2)
        ys = [e[0] for e in eighths]
        xs = [e[1] for e in eighths]
        es.set_title("Eigth Notes")
        es.plot(xs, ys)

        ss = fig.add_subplot(4, 1, 3)
        ys = [s[0] for s in sixteenths]
        xs = [s[1] for s in sixteenths]
        es.set_title("Sixteenth Notes")
        ss.plot(xs, ys)

        ws = fig.add_subplot(4, 1, 4)
        ys = [w[0] for w in weighted_combined]
        xs = [w[1] for w in weighted_combined]
        ws.set_title("Weighted-Combined Notes")
        ws.plot(xs, ys)

        plt.show()

    return (weighted_combined, quarters, eighths, sixteenths)
