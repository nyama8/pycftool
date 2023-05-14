import numpy as np

class FitModel():

    def __init__(self,
                 name,                 # Name
                 param_names,          # name of parameters
                 param_default,        # Default values of parameters
                 param_min,            # Parameter minimum possible
                 param_max,            # Parameter maximum possible
                 param_dict = None     # Parameter dictionary ``{'param': '[description]'}``
                ):

        self.name = name
        self.param_names = param_names
        self.param_default = param_default
        self.param_min = param_min
        self.param_max = param_max

        self.num_params = len(param_names)



    def f(self, x, *params):
        pass





class Lorentzian_p1(FitModel):

    def __init__(self):
        super().__init__(
            name = 'Lorentzian_poly1',
            param_names = ['a', 'mu', 'gamma', 'p0', 'p1'],
            param_default = [1, 0, 1, 0, 0],
            param_min = [-np.inf, 0, 0, -np.inf, -np.inf],
            param_max = [np.inf, np.inf, np.inf, np.inf, np.inf],
            param_dict = {
                            'a':     'peak amplitude',
                            'mu':    'peak center' ,
                            'gamma': 'peak width (FWHM)',
                            'p0':    '0th order poly coeff (constant)',
                            'p1':    '1st order poly coeff (linear)'
                         }
        )

    def f(self, x, *params):
        a, mu, gamma, p0, p1 = params

        lorentzian = a * (gamma**2/4) / ( (x - mu)**2 + gamma**2/4 )
        background = p0 + p1 * (x - mu)

        return lorentzian + background


class Lorentzian_p2(FitModel):

    def __init__(self):
        super().__init__(
            name = 'Lorentzian_poly2',
            param_names = ['a', 'mu', 'gamma', 'p0', 'p1', 'p2'],
            param_default = [1, 0, 1, 0, 0, 0],
            param_min = [-np.inf, 0, 0, -np.inf, -np.inf, -np.inf],
            param_max = [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
            param_dict = {
                            'a':     'peak amplitude',
                            'mu':    'peak center' ,
                            'gamma': 'peak width (FWHM)',
                            'p0':    '0th order poly coeff (constant)',
                            'p1':    '1st order poly coeff (linear)',
                            'p2':    '2nd order poly coeff (quadratic)'
                         }
        )

    def f(self, x, *params):
        a, mu, gamma, p0, p1, p2 = params

        lorentzian = a * (gamma**2/4) / ( (x - mu)**2 + gamma**2/4 )
        background = p0 + p1 * (x - mu) + p2 * (x - mu)**2

        return lorentzian + background
