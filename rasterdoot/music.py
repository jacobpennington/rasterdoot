import numpy as np
import music21
from music21.note import Note
from music21.scale import MajorScale
from music21.stream import Stream


def dootify(data, ms_per_bin, spike_times=False, interpolate=True,
            instrument='Piano', min_octave=2, max_octave=8):

    if spike_times:
        spike_times_in_seconds = data
    else:
        notes_needed, _ = data.shape
        spike_times_in_seconds = [
            data[i].nonzero()[0] * (ms_per_bin/1000)
            for i in range(notes_needed)
            ]

    # Pick range of notes
    # Initial idea: stick to within a few octaves of the C major scale so
    # that the pitches aren't absurdly low/high
    letters = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    octaves = [
        [f'{letter}{number}' for letter in letters]
        for number in range(min_octave, max_octave+1)
    ]
    total_notes = len(letters) * (max_octave - min_octave + 1)

    # Map note range onto shape of data: one note per row
    pitch_map = []
    if notes_needed > total_notes:
        # TODO: repeated notes, different instruments?
        pass
    else:
        while len(octaves) > 0:
            # start with "middle" octave, rounding down if even number.
            octave_idx = int(len(octaves)/2)
            current_octave = octaves.pop(octave_idx)
            while (len(pitch_map) < notes_needed) and (len(current_octave) > 0):
                # Add pitches from that octave in order until depleted
                # or until all pitches filled
                pitch = current_octave.pop(0)
                pitch_map.append(pitch)

    # TODO: Incorporate instrument choices somehow?

    # Create Stream, 
    stream = Stream()
    if isinstance(instrument, str):
        # Replace string with Instrument instance.
        instrument = getattr(music21.instrument, instrument, None)()
    if instrument is None:
        raise ValueError(f'Unrecognized instrument name: {instrument}.')
    stream.insert(0, instrument)
    
    # Add notes, all notes for one neuron same pitch.
    for times, pitch in zip(spike_times_in_seconds, pitch_map):
        # Round to 1/100th of a second, toss duplicated spike times
        times = set([round(t,1) for t in times])
        for t in times:
            stream.insert(round(t,1), Note(pitch))

    return stream
