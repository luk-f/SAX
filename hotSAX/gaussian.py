from numpy import exp as np_exp
from numpy import power as np_power
from numpy import array as np_array
from numpy import arange as np_arange

from scipy.stats import norm


##
# Utilisation d'un décorateur sous forme de closure
# (impressionné par cette posssibilité...)
##
def singleton(cls):
    instance = None

    def ctor(*args, **kwargs):
        nonlocal instance
        if not instance:
            instance = cls(*args, **kwargs)
        return instance

    return ctor


# @singleton
class NormalGaussian:

    ##
    # TODO - séparer normalBreakpoint avec les breakpoints de la serie (pour pouvoir instantier plusieurs fois la classe avec des arbres différents)

    normalBreakpointsByCardinality = {}

    breakpointsByCardinality = {}
    lastBreakpointsByCardinality = {}

    # to find this
    # use from scipy.stats import norm
    # norm.ppf([0.25, 0.5, 0.75])
    # same as qnorm(c(.25,.50,.75)) in R
    """
    normalBreakpointsByCardinality[2] = np_array([0.])
    lastBreakpointsByCardinality[2] = np_array([0.])
    breakpointsByCardinality[4] = np_array([-0.67448975, 0., 0.67448975])
    lastBreakpointsByCardinality[4] = np_array([-0.67448975, 0.67448975])
    breakpointsByCardinality[8] = np_array([-1.15034938037601, -0.674489750196082, -0.318639363964375, 0,
                                            0.318639363964375, 0.674489750196082, 1.15034938037601])
    lastBreakpointsByCardinality[8] = np_array([-1.15034938037601, -0.318639363964375, 0.318639363964375,
                                                1.15034938037601])
    breakpointsByCardinality[16] = np_array([-1.53412054435255, -1.15034938037601, -0.887146559018876,
                                             -0.674489750196082, -0.488776411114669, -0.318639363964375,
                                             -0.157310684610171, 0, 0.157310684610171, 0.318639363964375,
                                             0.488776411114669, 0.674489750196082, 0.887146559018876, 1.15034938037601,
                                             1.53412054435255])
    lastBreakpointsByCardinality[16] = np_array([-1.53412054435255,  -0.887146559018876, -0.488776411114669,
                                                 -0.157310684610171, 0.157310684610171, 0.488776411114669,
                                                 0.887146559018876, 1.53412054435255])
    """

    def __init__(self, mean, std):

        print("init normal gaussian")
        self.mean = mean
        self.std = std

        """
        for key, _ in self.breakpointsByCardinality.items():
            self.breakpointsByCardinality[key] *= self.std
            self.breakpointsByCardinality[key] += self.mean

        for key, _ in self.lastBreakpointsByCardinality.items():
            self.lastBreakpointsByCardinality[key] *= self.std
            self.lastBreakpointsByCardinality[key] += self.mean
        """

    def getBreakpointsByCardinality(self, cardinality):

        if cardinality not in self.breakpointsByCardinality:
            frac = 1.0/cardinality
            list_percent = []
            for i_fl in np_arange(frac, 1.0, frac):
                list_percent.append(i_fl)
            self.breakpointsByCardinality[cardinality] = (np_array(norm.ppf(list_percent))*self.std+self.mean)

        return self.breakpointsByCardinality[cardinality]

    def getOnlyLastBreakpointsByCardinality(self, cardinality):

        if cardinality not in self.lastBreakpointsByCardinality:
            array_n = self.getBreakpointsByCardinality(cardinality)
            array_m = self.getBreakpointsByCardinality(int(cardinality/2))
            self.lastBreakpointsByCardinality[cardinality] = np_array([x for x in array_n if x not in array_m])

        return self.lastBreakpointsByCardinality[cardinality]


# Fonction gaussienne suivant moyenne (mu) et variance(sig)
def gaussian(x, mu, sig):
    return np_exp(-np_power(x - mu, 2.) / (2 * np_power(sig, 2.)))
