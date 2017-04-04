"""
test cases_utils.py
----------------------------------------

A file that implements utility functions and classes to
load and run test cases.
"""

import os
from io import StringIO


class TestCase:
    """
    An object for holding information about
    each test case.
    """
    def __init__(self, name, code, expected):
        self.name = name
        self.code = code
        self.expected = expected


def percentage(part, whole):
    """
    Calculate the percentage of a number.
    """
    return 100 * float(part)/float(whole)


def all_test_cases(path_to_tests='all_tests/', path_to_expected_results='all_tests_expected_results/'):
    """
    Yield each test case.
    """
    test_files = sorted(os.listdir(path_to_tests))
    expected_result_files = sorted(os.listdir(path_to_expected_results))

    for test_file, expected_results_file in zip(test_files, expected_result_files):
            yield path_to_tests + test_file, path_to_expected_results + expected_results_file


def run_all_test_cases(runner):
    """
    Given a runner function, use the function to run each
    test case.

    A runner function is a function with a code parameter,
    which is the code that the function will run, and a
    outstream parameter, which the stream in which all
    output(calls to print), will be written.
    """
    number_of_tests = 0
    fail_count = 0
    for test_file, expected_result_file in all_test_cases():
        number_of_tests += 1
        with open(test_file, 'r') as a, open(expected_result_file) as b:
            test_case = TestCase(test_file, a.read(),  b.read())

        out_stream = StringIO()
        runner(test_case.code, out_stream)
        if out_stream.getvalue() == test_case.expected:
            print('Test [{}] ran OK'.format(test_case.name))
        else:
            fail_count += 1
            print('Test [{}] Failed'.format(test_case.name))
    print('------------------------------------------\n')
    print('{} test(s) ran.'.format(number_of_tests))
    print('{}[{}%] of the tests ran ok.'.format(number_of_tests - fail_count,
                                                percentage(number_of_tests - fail_count, number_of_tests)))
    print('{}[{}%] of the tests failed'.format(fail_count,
                                               percentage(fail_count, number_of_tests)))
