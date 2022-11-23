from enum import Enum

import numpy as np
import music21
from music21.note import Note
from music21.stream import Stream


def dootify(data, data_type, ms_per_bin, instrument='Piano', scale_pitch='c',
            scale_type='Major'):
    """TODO: docs
    
    Parameters
    ----------
    data : np.ndarray.
        Recorded data to convert to notes, with shape (N, T) where N is the number
        of neurons or recording channels and T is the number of time points.
    data_type : str.
        Specifiy starting format of data. Accepted values are (case-insensitive):
        "raster": entries are 1 or 0 to indicate spike / no spike.
        "continuous": real-valued entries, like instantaneous firing rate.
        "discrete": integer entries representing discretized firing rate.
    ms_per_bin : int.
        E.g. sampling rate of 100hz -> use `ms_per_bin=10` for real-time,
        `ms_per_bin=100` for 10x slowdown.
    downsampling_ratio :
    instrument : str or music21.instrument.Instrument; default='Piano'.
        Specifies which instrument to render notes as. Strings will be converted
        to a corresponding Instrument object. See docs here for valid names:
        https://web.mit.edu/music21/doc/moduleReference/moduleInstrument.html
    scale_pitch : str; default='c'.
        Tonic pitch for the scale that notes are generated from. See `get_scale`.
    scale_type : str; default='Major'.
        Type of scale to use, such as 'Major' or 'Minor'. See `get_scale`.

    Returns
    -------
    music21.stream.Stream

    """

    # Get list of pitches based on scale, e.g. C major or B minor.
    pitches = get_scale(scale_pitch, type=scale_type)
    pitches.insert(0, None)  # indicates silence
    
    # Determine starting point for data conversions.
    steps = {'spike times': 0, 'raster': 1, 'continuous': 2, 'discrete': 3}
    data_step = steps[data_type.lower()]
    if data_step == 0:
        # Spike times -> raster
        data = rasterize(data, ms_per_bin)
    if data_step == 1:
        # Raster -> Continuous
        data = raster_to_continuous(data, ms_per_bin)
        data_step += 1
    if data_step == 2:
        # Continuous -> Discrete
        data = discretize_to_scale(data, pitches)
        data_step += 1

    # Create Stream, 
    stream = Stream()
    if isinstance(instrument, str):
        # Replace string with Instrument instance.
        instrument = getattr(music21.instrument, instrument, None)()
    if instrument is None:
        raise ValueError(f'Unrecognized instrument name: {instrument}.')
    stream.insert(0, instrument)
    
    # Add notes to stream
    n_pitches = len(pitches)
    n_channels = data.shape[0]
    for t in range(data.shape[1]):
        notes = [pitches[data[n,t] % n_pitches] for n in range(n_channels)]
        time = round((t*ms_per_bin)/1000, 2)  # nearest 1/100th second
        for note in notes:
            if note is not None: stream.insert(time, Note(note))

    return stream


def get_scale(pitch, type='Major'):
    """Get a list of pitch names belonging to a music21 Scale.
    
    Parameters
    ----------
    pitch : str.
        Tonic pitch for the scale.
    type : str; default='Major'.
        Type of scale to use, like 'Major' or 'Minor'.
        See music21.scale documentation for more options:
        https://web.mit.edu/music21/doc/moduleReference/moduleScale.html

    Returns
    -------
    list of str.
        All pitches belonging to the scale.
    
    """
    # All end in 'Scale' except RagAsawari, RagMarwa, and WeightedHexatonicBlues
    if ('rag' not in type and 'Blues' not in type) and not (type.endswith('Scale')):
        type = f'{type}Scale'
    scale = getattr(music21.scale, type)(music21.pitch.Pitch(pitch))

    return [str(p) for p in scale.getPitches()]


def rasterize(spike_times, ms_per_bin):
    # TODO
    pass


def raster_to_continuous(raster, ms_per_bin):
    # Compute instantaneous spike rate, divide each bin by bin width in seconds.
    instantaneous = raster / (ms_per_bin/1000)
    # Smooth somehow so it's not so choppy
    # TODO

    return instantaneous


def discretize_to_scale(continuous, pitches):
    # Normalize to min 0 max 1
    continuous -= continuous.min()
    continuous /= continuous.max()

    # Given smooth/cts signal, map ranges to discrete pitches on scale
    # TODO: might need different scales, like log?
    bins = np.arange(len(pitches)) / (len(pitches)-1)  # 0 to 1
    discretized = np.digitize(continuous, bins) - 1
    
    return discretized


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
        # TODO: no, this appends in time
        # big_stream.append(s)
        big_stream.insert(0, s)

    return big_stream
