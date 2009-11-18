# -*- coding: utf-8 -*-

import doctest
import glob
import os
import os.path
import sys
import unittest

import flickrapi

failure = False
def exit(statuscode):
    '''Replacement for sys.exit that records the status code instead of
    exiting.
    '''

    global failure

    if statuscode:
        failure = True

def run_in_module_dir(module):
    '''Runs the decorated function in the directory of the given module.'''

    directory = os.path.dirname(module.__file__)

    def decorator(func):
        '''Runs the decorated function in some directory.'''

        def wrapper():
            curdir = os.getcwd()
            try:
                if directory:
                    print 'Changing to %s' % directory
                    os.chdir(directory)
                return func()
            finally:
                os.chdir(curdir)

        return wrapper

    return decorator

run_in_test_dir = run_in_module_dir(sys.modules[__name__])
run_in_code_dir = run_in_module_dir(flickrapi)

def load_module(modulename):
    '''load_module(modulename) -> module'''

    __import__(modulename)
    return sys.modules[modulename]

@run_in_test_dir
def run_unittests():
    '''Runs all unittests in the current directory.'''

    filenames = glob.glob('test_*.py')
    modules = [fn[:-3] for fn in filenames]

    for modulename in modules:
        module = load_module('%s.%s' % (__name__, modulename))
        print '----------------------------------------------------------------------'
        print module.__file__
        print
        unittest.main(module=module)

    if failure:
        print 'Unittests: there was at least one failure'
    else:
        print 'Unittests: All tests ran OK'

@run_in_code_dir
def run_doctests():
    '''Runs all doctests in the flickrapi module.'''

    # First run the flickrapi module
    (failure_count, test_count) = doctest.testmod(flickrapi)

    # run the submodules too.
    filenames = glob.glob('[a-z]*.py')
    modules = [fn[:-3] for fn in filenames]

    # Go to the top-level source directory to ensure relative path names are
    # correct.
    os.chdir('..')

    for modulename in modules:
        # Load the module
        module = load_module('%s.%s' % (flickrapi.__name__, modulename))

        # Run the tests
        (failed, tested) = doctest.testmod(module)

        failure_count += failed
        test_count += tested

    if failure_count:
        print 'Doctests: %i of %i failed' % (failure_count, test_count)

        global failure
        failure = True
    else:
        print 'Doctests: all of %i OK' % test_count

def run_tests():
    '''Runs all unittests and doctests.'''

    # Prevent unittest.main from calling sys.exit()
    orig_exit = sys.exit
    sys.exit = exit

    try:
        run_unittests()
        run_doctests()
    finally:
        sys.exit = orig_exit

    sys.exit(failure)

if __name__ == '__main__':
    run_tests()
