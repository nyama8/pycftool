'''
    SPECTRUM.PY

    Nicholas S. Yama
    Fu Group, University of Washington, Seattle

    Last modified: May 2022

    The Spectrum class.

    Stores spectral data as a Python class with direct methods for quick
    visualization and manipulation.

    Ideally the Spectrum class is never created by the user directly. Instead,
    the user can generate Spectrum objects via additional methods (e.g. the
    load_SPE() function).

    The Spectrum function is designed to be simple to interface with, enabling
    future integration with analysis modules for fitting and other processing.
'''

import numpy as np
import matplotlib.pyplot as plt

class Spectrum:

    def __init__(
        self,
        filename = None,
        wavelength = None,
        data = None,
        xdim = None,
        ydim = None,
        num_frames = None,
        exposure = None,
        date_collected = None,
        time_collected = None,
        SPE_version = None
    ):

        self.filename = filename
        self.date_collected = date_collected
        self.time_collected = time_collected
        self.SPE_version = SPE_version

        self.wavelength = wavelength
        self.xdim = xdim
        self.ydim = ydim
        self.num_frames = num_frames
        self.exposure = exposure

        # Spectrum.data structured as a list containing each frame.
        self.data = data

        # In common usage, this can be inconvenient as one may want to access
        # the data directly (without having to use Spectrum.data[0]).
        # To facilitate this we define Spectrum.int which contains only the
        # first frame of the dataset:
        self.int = data[0]



    def quick_plot(self, frames=[0], figsize=(8,5)):

        # Plot each of the desired frames
        for frame in frames:
            plt.figure(figsize=figsize)
            plt.plot(self.wavelength, self.data[frame])
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Intensity (a.u.)')
            plt.title(self.filename + ', frame ' + str(frame))
            plt.show()


    def to_image(self):
        # Converts a sequence of frames with shape (xdim,) into an image (num_frames, xdim)
        # Returns the image directly (it is not stored in the Spectrum instnace)

        if self.ydim == 1:
            return np.stack(self.data)
        else:
            raise ValueError('Cannot stack image data')


    def quick_plot_image(self, figsize=(8,5), **kwargs):
        img = self.to_image()
        y = np.arange(self.num_frames) * self.exposure
        x = self.wavelength

        xx, yy = np.meshgrid(x, y)

        plt.figure(figsize=figsize)
        p = plt.pcolormesh(xx, yy, img, **kwargs)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Time (s)')
        plt.colorbar(p)
        plt.show()