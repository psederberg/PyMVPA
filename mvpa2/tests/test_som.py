# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Unit tests for PyMVPA SOM mapper"""


import unittest
import numpy as np
from mvpa2 import cfg
from mvpa2.mappers.som import SimpleSOMMapper
from mvpa2.datasets.base import dataset_wizard

class SOMMapperTests(unittest.TestCase):

    def test_simple_som(self):
        colors = np.array([[0., 0., 0.], [0., 0., 1.], [0., 1., 0.],
                          [1., 0., 0.], [0., 1., 1.], [1., 0., 1.],
                          [1., 1., 0.], [1., 1., 1.]])

        # only small SOM for speed reasons
        som = SimpleSOMMapper((10, 5), 200, learning_rate=0.05)

        # no acces when nothing is there
        self.failUnlessRaises(RuntimeError, som._access_kohonen)

        som.train(colors)

        fmapped = som.forward(colors)
        self.failUnless(fmapped.shape == (8, 2))

        # reverse mapping
        rmapped = som.reverse(fmapped)

        if cfg.getboolean('tests', 'labile', default='yes'):
            # should approximately restore the input, but could fail
            # with bad initialisation
            self.failUnless((np.round(rmapped) == colors).all())


def suite():
    return unittest.makeSuite(SOMMapperTests)


if __name__ == '__main__':
    import runner

