# Not working yet, but this script sketches out what the package is intended
# to do eventually.

import numpy as np
from sklearn.manifold import TSNE

from .music import dootify

# Assume user has loaded some data, formatted as a
# 2D time x neurons numpy array.
# (originally just had spiking in mind, but could also be non-binary and use
#  value to control amplitude)
data = np.random.choice([0,1], size=(10000,100), p=[0.95, 0.05])

# Sort neurons using tSNE (optional, use 3rd party)
# TODO: double check this. With random data was hard to tell
#       if it's actually working as intended.
model = TSNE(n_components=2, learning_rate='auto', init='random')
embedded_data = model.fit_transform(data)
sorted_indices = np.argsort(embedded_data, axis=0).flatten()
sorted_data = data[sorted_indices]

# Generate a sound file (probably .wav) from the sheet music for a selected
# instrument. Want to support oscilloscope, trumpet, percussion... others.
wav = dootify(sorted_data, ms_per_bin=10, interpolate=True,
              instrument='oscilloscope')
