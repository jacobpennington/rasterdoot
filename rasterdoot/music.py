import numpy as np
import music21
from music21.note import Note
from music21.scale import MajorScale
from music21.stream import Stream


def dootify(data, ms_per_bin, spike_times=False, interpolate=True,
            instrument='Piano', min_octave=2, max_octave=8):
    """TODO: docs
    
    Parameters
    ----------
    data : np.ndarray.
        Spike raster to convert to notes.
        TODO: currently always quarter notes, would like to be able to specify.
    ms_per_bin : int.
        E.g. sampling rate of 100hz -> use `ms_per_bin=10` for real-time,
        `ms_per_bin=100` for 10x slowdown.
    spike_times : bool; default=False.
        Indicate if `data` is already in spike-time format. If False, data
        should be a raster.
    interpolate : bool; default=True.
        TODO, does nothing yet.
    instrument : str or music21.instrument.Instrument; default='Piano'.
        Specifies which instrument to render notes as. Strings will be converted
        to a corresponding Instrument object. See docs here for valid names:
        https://web.mit.edu/music21/doc/moduleReference/moduleInstrument.html
    min_octave : int; default=2.
        Lowest octave to use. With the default value of 2, the lowest note will
        be C2.
    max_octave : int; default=8.
        Highest octave to use. With the default value of 8, the highest note will
        be B8.

    """

    if spike_times:
        spike_times_in_seconds = data
    else:
        notes_needed, _ = data.shape
        spike_times_in_seconds = [
            data[i].nonzero()[0] * (1000/ms_per_bin)
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
        times = set([round(t,2) for t in times])
        for t in times:
            stream.insert(t, Note(pitch))

    return stream


def multi_doot(doot_dict, *doot_args, **doot_kwargs):
    """Dootify multiple arrays using different instruments.
    
    Parameters
    ----------
    doot_dict : dict of np.ndarray.
        Dictionary of the form: {'instrument_name': data}
    doot_args : N-tuple.
        Positional arguments for dootify, like `ms_per_bin`.
    doot_kwargs : dict; optional.
        Keyword arguments for dootify, like `min_octave`.

    Returns
    -------
    music21.stream.Stream
    
    """
    big_stream = Stream()
    little_streams = [dootify(v, *doot_args, instrument=k, **doot_kwargs)
                      for k, v in doot_dict.items()]
    for s in little_streams:
        # TODO: no, thisd appends in time
        # big_stream.append(s)
        big_stream.insert(0, s)

    return big_stream
