import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np

from IPython.display import display

from scipy.optimize import curve_fit
from scipy.signal import find_peaks


from pycftool_Backend import *
from pycftool_Frontend import *
from pycftool_Fit import *
from pycftool_FitModel import *


def open_results(filename):

    return pickle.load( open( filename, "rb" ) )


class CFTool:

    def __init__(self, **kwargs):

        '''
            kwargs can contain either sets of input:
                {
                    fit_models : List of fit models to load
                    data_x     : An ndarray of x data
                    data_y     : An ndarray of y data
                    fit_class  : Class of pycftool.Fit object which which to
                                 save results
                    metadata   : Dictionary of metadata for the dataset
                }

                OR

                {
                    fit_models : List of fit models to load
                    fit_class  : Class of pycftool.Fit object which which to
                                 save results
                    spectrum   : A Spectrum object from imported data
                    name       : [OPTIONAL] name for set to override filename
                }

        '''


        try:
            self.cftool_backend = Backend(**kwargs)

        except:
            print('Loading from spectrum object...')

            spectrum = kwargs['spectrum']

            # Get metadata as `__dict__` of Spectrum object
            metadata = spectrum.__dict__

            # Get the x and y data from the first frame
            # And remove it from the metadata
            data_x = metadata.pop('wavelength')
            data_y = metadata.pop('int')

            # Remove the spectrum data from the metadata
            del metadata['data']

            # Change the filename to remove directory information
            filename = metadata['filename'].split('/')[-1]
            # Remove the .SPE
            metadata['filename'] = filename.split('.')[0]

            # Add a name key in case it is desired
            metadata['name'] = name

            # Instantiate the backend
            self.cftool_backend = Backend(
                fit_models = kwargs['fit_models'],
                data_x = data_x,
                data_y = data_y,
                fit_class = kwargs['fit_class'],
                metadata = spectrum.__dict__
            )

    def close(self):
        '''
            This method closes the gui
        '''

        self.cftool_backend.frontend.gui.close()


