def dootify(data, ms_per_bin, interpolate=True, instrument='oscilloscope'):
    # Determine minimum and maximum tones / frequency range
    # TODO: have to learn more about musical scales I guess... 
    #       then pick a standard

    # Map axis 1 onto that tone range. If axis 1 larger than the number
    # of tones, either interpolate or have duplicates.
    # TODO: would this actually sound good though, with interpolation?
    #       Could end up with some very odd-sounding instruments. May be better
    #       to stick with duplicates and focus on forming chords somehow.

    # Generate .wav data for instrument, one per data channel with frequency
    # modulated appropriately.
    # TODO: how to make an instrument library? Lots of resources for python
    #       synthesizers, but that's not really the sound I'm going for.
    #       Oscilloscope can be a literal recording that gets repeated, but
    #       doing that for every instrument could be a lot of data.

    pass
