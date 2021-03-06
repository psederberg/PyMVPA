# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Unit test interface for PyMVPA"""

import unittest
import numpy as np
from mvpa2 import _random_seed, cfg
from mvpa2.base import externals, warning


def collect_unit_tests(verbosity=1):
    """Runs over all tests it knows and composes a dictionary with test suite
    instances as values and IDs as keys. IDs are the filenames of the unittest
    without '.py' extension and ``test_`` prefix.

    During collection this function will run a full and verbose test for all
    known externals.
    """
    # list all test modules (without .py extension)
    tests = [
        # Basic data structures/manipulators
        'test_externals',
        'test_dochelpers',
        'test_som',
        'test_state',
        'test_params',
        # Misc supporting utilities
        'test_config',
        'test_support',
        'test_verbosity',
        'test_report',
        'test_cmdline',
        'test_args',
        'test_meg',
        # Classifiers (longer tests)
        'test_clf',
        'test_regr',
        'test_knn',
        'test_gnb',
        'test_svm',
        'test_plr',
        'test_smlr',
        # Various algorithms
        'test_svdmapper',
        'test_procrust',
        'test_hyperalignment',
        'test_transformers',
        'test_searchlight',
        'test_rfe',
        'test_ifs',
        'test_perturbsensana',
        # And the suite (all-in-1)
        'test_suite',
        ]

    __optional_tests = [ ('scipy', 'ridge'),
                         ('scipy', 'gpr'),
                         (['cPickle', 'gzip'], 'hamster'),
                       ]

    # and now for the optional tests
    optional_tests = []

    for external, testname in __optional_tests:
        if externals.exists(external):
            optional_tests.append('test_%s' % testname)
        elif verbosity:
            print('T: Tests from "test_%s" are skipped due to missing externals: %s'
                  % (testname, external))

    # finally merge all of them
    tests += optional_tests
    return tests

def collect_test_suites(verbosity=1):
    tests = collect_unit_tests(verbosity=verbosity)
    # import all test modules
    for t in tests:
        # TODO: exclude tests which fail to import: e.g. on Windows
        # could get WindowsError due to missing msvcr90.dll
        exec 'import mvpa2.tests.' + t

    # instantiate all tests suites and return dict of them (with ID as key)
    return dict([(t[5:], eval('mvpa2.tests.' + t + '.suite()')) for t in tests ])


def collect_nose_tests(verbosity=1):
    """Return list of tests which are pure nose-based
    """
    tests = [
        # Basic data structures/manipulators
        'test_base',
        'test_collections',
        'test_attrmap',

        # Datasets
        'test_datasetng',
        'test_datasetfx',
        'test_dataset_formats',
        'test_splitter',
        'test_generators',
        'test_niftidataset',
        'test_eepdataset',
        'test_erdataset',

        # Misc supporting
        'test_neighborhood',
        'test_stats',
        'test_stats_sp',

        # Mappers
        'test_mapper',
        'test_mapper_sp',
        'test_arraymapper',
        'test_boxcarmapper',
        'test_prototypemapper',
        'test_fxmapper',
        'test_zscoremapper',
        'test_waveletmapper',
        'test_mdp',
        'test_filters',

        # Learners
        'test_enet',
        'test_spam',
        'test_lars',
        'test_glmnet',
        'test_kernel',
        'test_svmkernels',

        # Algorithms
        'test_emp_null',
        'test_clfcrossval',

        # IO
        'test_iohelpers',
        'test_hdf5',
        'test_hdf5_clf',

        # Measures
        'test_transerror',
        'test_datameasure',
        ]

    if not cfg.getboolean('tests', 'lowmem', default='no'):
        tests += ['test_atlases']

    return tests


def run_tests_using_nose(limit=None, verbosity=1, exit_=False):
    """Run nose-based tests -- really really silly way, just to get started

    TODO: just switch to using numpy.testing framework, for that
          unittests need to be cleaned and unified first
    """
    nosetests = collect_nose_tests(verbosity=verbosity)

    if not externals.exists('nose'):
        warning("You do not have python-nose installed.  Some unittests were "
                "skipped: %s" % (', '.join(nosetests)))
        return

    from nose import main
    import nose
    import nose.config

    tests = collect_unit_tests(verbosity=verbosity) + nosetests

    config = nose.config.Config(
        verbosity=max(0, verbosity-1),
        plugins=nose.plugins.DefaultPluginManager())
    if limit is None:
        # Lets see if we aren't missing any:
        if verbosity:
            import os, glob
            testfiles = glob.glob('%s%stest_*.py'
                                  % (os.path.dirname(__file__), os.path.sep))
            not_tested = set([os.path.basename(f) for f in testfiles]) \
                         - set(['%s.py' % f for f in tests])
            if len(not_tested):
                print("T: Warning -- following test files were found but will "
                      "not be tested: %s" % ', '.join(not_tested))
        config.testNames = ['mvpa2.tests.' + nt for nt in tests]
    else:
        config.testNames = ['mvpa2.tests.' + nt for nt in tests
                            if nt[5:] in limit]

    # run the tests
    _ = main(defaultTest=(), config=config, exit=exit_)


def run(limit=None, verbosity=None, exit_=False):
    """Runs the full or a subset of the PyMVPA unittest suite.

    Parameters
    ----------
    limit : None or list
      If None, the full test suite is run. Alternatively, a list with test IDs
      can be provides. IDs are the base filenames of the test implementation,
      e.g. the ID for the suite in 'mvpa2/tests/test_niftidataset.py' is
      'niftidataset'.
    verbosity : None or int
      Verbosity of unittests execution. If None, controlled by PyMVPA
      configuration tests/verbosity.  Values >=3 enable all Python,
      and PyMVPA warnings, >=4 adds NumPy warnings, >=5 -- nose debug info.
    exit_ : bool, optional
      Either to exit with an error code upon the completion.
    """
    if __debug__:
        from mvpa2.base import debug
        # Lets add some targets which provide additional testing
        debug.active += ['CHECK_.*']

    if verbosity is None:
        verbosity = int(cfg.get('tests', 'verbosity', default=1))

    # provide people with a hint about the warnings that might show up in a
    # second
    if verbosity:
        print("T: MVPA_SEED=%s" % _random_seed)
        if verbosity > 1:
            print('T: Testing for availability of external software packages.')

    # So we could see all warnings about missing dependencies
    maxcount = warning.maxcount
    warning.maxcount = 1000

    # fully test of externals
    externals.test_all_dependencies(verbosity=max(0, verbosity-1))

    if verbosity < 3:
        # no MVPA warnings during whole testsuite (but restore handlers later on)
        handler_backup = warning.handlers
        warning.handlers = []

        # No python warnings (like ctypes version for slmr)
        import warnings
        warnings.simplefilter('ignore')

    if verbosity < 4:
        # No NumPy
        np_errsettings = np.geterr()
        np.seterr(**dict([(x, 'ignore') for x in np_errsettings]))

    try:
        if externals.exists('nose'):
            # Lets just use nose
            run_tests_using_nose(limit=limit,
                                 verbosity=verbosity,
                                 exit_=exit_)
        else:
            print("T: Warning -- major bulk of tests is skipped since nose "
                  "is unavailable")
            # collect all tests
            suites = collect_test_suites(verbosity=verbosity)

            if limit is None:
                # make global test suite (use them all)
                ts = unittest.TestSuite(suites.values())
            else:
                ts = unittest.TestSuite([suites[s] for s in limit])


            class TextTestRunnerPyMVPA(unittest.TextTestRunner):
                """Extend TextTestRunner to print out random seed which was
                used in the case of failure"""
                def run(self, test):
                    """Run the bloody test and puke the seed value if failed"""
                    result = super(TextTestRunnerPyMVPA, self).run(test)
                    if not result.wasSuccessful():
                        print "MVPA_SEED=%s" % _random_seed

            # finally run it
            TextTestRunnerPyMVPA(verbosity=verbosity).run(ts)
    finally:
        # restore warning handlers
        warning.maxcount = maxcount

    if verbosity < 3:
        # restore warning handlers
        warning.handlers = handler_backup

    if verbosity < 4:
        # restore numpy settings
        np.seterr(**np_errsettings)


# to avoid nosetests running the beasts defined in this file
__test__ = False

if __name__ == "__main__":
    run(exit_=True)
