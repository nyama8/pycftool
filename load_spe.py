'''
    LOAD_SPE.PY

    Nicholas S. Yama
    Fu Group, University of Washington, Seattle

    Last modified: May 2022

    A series of functions for reading Princeton instruments .SPE files
    (for version 2.xx) and storing the data in a Python-usable format.

    The following code is largely based off of code from others, particularly:
        -> https://leonvv.me/spe-images.html
            - Core functionality for reading .SPE v2.xx files in Python

        -> https://www.mathworks.com/matlabcentral/fileexchange/55665-loadspe-filename
            - Getting wavelength calibration data

    Integrates with the Spectrum class for quick plotting of data as well as
    simple interfacing with analysis and downstream processing.
'''


import struct
import numpy as np
import matplotlib.pyplot as plt


from Spectrum import *






def from_bytes(b, fmt, offset):
    # Simple helper function taken from https://leonvv.me/spe-images.html
    # Given string of bytes b and data format fmt, reads the bytes at offset,
    # interpreting it as the desired format.
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, b[offset:offset+size])[0]






def load_SPE(filename):
    # Opens and loads a single .SPE (v2.xx) file with name filename
    # Returns a Spectrum object that contains the (meta)data of the
    # corresponding file.

    # Open the file
    try:
        with open(filename, 'rb') as f:
            b = f.read()
    except:
        with open(filename + '.SPE', 'rb') as f:
            b = f.read()

    # Get the metadata  ==================================== #
    SPE_version = from_bytes(b, "<f", 1992)
    num_frames = from_bytes(b, "i", 1446)
    exposure = from_bytes(b, "<f", 10)

    # Convert to normal string and strip extra characters
    date_collected = b[20:30].decode('utf-8').rstrip('\x00')
    time_collected = b[172:179].decode('utf-8').rstrip('\x00')

    xdim = from_bytes(b, "H", 42)  # These two are frame width/height
    ydim = from_bytes(b, "H", 656)


    startx = from_bytes(b, "h", 1512)
    calibpoly0 = from_bytes(b, "<d", 3263)
    calibpoly1 = from_bytes(b, "<d", 3271)
    calibpoly2 = from_bytes(b, "<d", 3279)

    # For SPE 2.X, the wavelength is determined from a quadratic taylor expansion
    wavelength = calibpoly0 + calibpoly1 * (np.arange(xdim)+startx) + calibpoly2 * (np.arange(xdim)+startx)**2


    # Get the data ==================================== #
    # Determine the size of the image data
    datatype = from_bytes(b, "h", 108)
    to_np_type = [np.float32, np.int32, np.int16, np.uint16, None, np.float64, np.uint8, None, np.uint32]
    np_type = to_np_type[datatype]
    itemsize = np.dtype(np_type).itemsize

    # Pixels per image
    count = xdim * ydim

    # The parser then reads each frame consecutively from the buffer,
    # shifting by the number of bytes per each frame = pixels * bytes_per_pixel.

    data = []

    for i in range(0, num_frames):

        # Read out the frame from the buffer
        frame = np.frombuffer(b, dtype=np_type, count=count, offset=4100 + i*count*itemsize)

        # Convert to proper image shape if necesary
        if ydim > 1:
            frame = np.reshape(frame, (ydim, xdim))

        # Append to list of data
        data.append(frame)


    # Generate and return spectrum  ==================================== #
    return Spectrum(
        filename = filename,
        wavelength = wavelength,
        data = data,
        xdim = xdim,
        ydim = ydim,
        num_frames = num_frames,
        exposure = exposure,
        date_collected = date_collected,
        time_collected = time_collected,
        SPE_version = SPE_version
    )







def load_SPEs(filenames):
    # Loads multiple SPE files provided list of filenames
    # Returns the corresponding Spectra as a list of Spectrum objects

    if type(filenames) is not list:
        filenames = [ filenames ]

    spectra = []

    for filename in filenames:
        spectrum = load_SPE(filename)
        spectra.append(spectrum)

    return spectra