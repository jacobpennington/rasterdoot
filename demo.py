# Not working yet, but this script sketches out what the package is intended
# to do eventually.

import numpy as np
from rastermap import mapping

# Assume user has loaded some data, formatted as a
# 2D time x neurons numpy array.
# (originally just had spiking in mind, but could also be non-binary and use
#  value to control amplitude)
data = np.load('my_data.npy')

# Sort neurons using tSNE, rastermap etc (optional, use 3rd party)
# (I think this is the basic workflow for Rastermap but not tested)
model = mapping.Rastermap(n_components=1, n_Y=100).fit(data)
sorted_indices= np.argsort(model.embedding[:,0])
sorted_data = data[sorted_indices]

# Convert the array data into a sheet-music-like interpretation
sheet = make_music(sorted_data, **options_tbd)

# Generate a sound file (probably .wav) from the sheet music for a selected
# instrument. Want to support oscilloscope, trumpet, percussion... others.
wav = dootify(sheet, instrument='oscilloscope')