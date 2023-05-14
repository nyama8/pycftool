import numpy as np

from pycftool_FitModel import *


class Fit(object):

    def __init__(self,
                 x,
                 y,
                 fit_model,
                 fit_y,
                 fit_params,
                 fit_covmat,
                 meta=None
                ):

        self.x = x
        self.y = y
        self.fit_model = fit_model
        self.fit_y = fit_y
        self.fit_params = fit_params
        self.fit_covmat = fit_covmat

        self.meta = meta

class ResonanceFit1(Fit):

    '''
    Fit object for use with single-peak Lorentzian
    '''

    def __init__(self,
                 x,
                 y,
                 fit_model,
                 fit_y,
                 fit_params,
                 fit_covmat,
                 meta=None
                ):

        super().__init__(x,
                         y,
                         fit_model,
                         fit_y,
                         fit_params,
                         fit_covmat,
                         meta
                        )

        self.Q = fit_params[1] / fit_params[2]

    # Functions to compare the Q factors directly
    def __eq__(self, other):
        return self.Q == other.Q

    def __lt__(self, other):
        return self.Q < other.Q