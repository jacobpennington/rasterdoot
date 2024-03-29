# Not working yet, but this script sketches out what the package is intended
# to do eventually.
from pathlib import Path
# import sys
# sys.path.append('C:/code/rasterdoot')  # TODO: set up actual install, remove this

import numpy as np
from sklearn.manifold import TSNE

# Set paths to MuseScore (or other program) and directory where midis will
# be stored
from music21 import environment
us = environment.UserSettings()
us['musicxmlPath'] = 'C:/Program Files/MuseScore 3/bin/MuseScore3.exe'
us['musescoreDirectPNGPath'] = 'C:/Program Files/MuseScore 3/bin/MuseScore3.exe'
midi_dir = Path('C:/code/midis/')

# TODO; set up installation 
from rasterdoot.music import dootify, multi_doot

# Assume user has loaded some data, formatted as a
# 2D numpy array with shape (N neurons, T time bins).
# (originally just had spiking in mind, but could also be non-binary and use
#  value to control amplitude)
# data = np.random.choice([0,1], size=(32,10000), p=[0.95, 0.05])

with np.load("C:/code/lbhb_data/flat.npz") as f:
    data = f['response']
# Select subset of time points, first 32 neurons
data = data[:1000, :6].T  # flip time and neuron axis

# Sort neurons using tSNE (optional, use 3rd party)
model = TSNE(n_components=1, learning_rate='auto', init='random')
embedded_data = model.fit_transform(data)
sorted_indices = np.argsort(embedded_data, axis=0).flatten()
data = data[sorted_indices]

# List of instruments:
# https://web.mit.edu/music21/doc/moduleReference/moduleInstrument.html
# stream = dootify(data, ms_per_bin=100, instrument='Piano')  # single instrument
instrument_list = ['Piano', 'Viola', 'Violoncello', 'Tambourine', 'Guitar',
                   'Saxophone']
instrument_data_mapping = {
    instrument: data[i:i+1, ...] for i, instrument in enumerate(instrument_list)
    }
stream = multi_doot(instrument_data_mapping, ms_per_bin=100)

# TODO: This method is the major speed bottleneck at the moment. Any way to show
#       a progress bar for this? Would have to be through the musci21 library.
stream.show('midi')

# TODO: with real data, even 32 neurons ends up being a rapid-fire mess.
#       need to artificially separate the spikes somehow? the multiple instruments
#       idea would help, but then there's still 40-80 neurons per site in this data.


stream.write('midi', fp='C:/code/midi_test.midi')
