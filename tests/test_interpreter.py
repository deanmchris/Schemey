"""
test_interpreter.py
----------------------------------------

The implementation of the runner function(see test_cases_utils.py)
for Schemey's interpreter.
"""

from .context import src
from .test_cases_utils import run_all_test_cases

from src import interpreter


def runner(code, out_stream):
    """
    The runner function of Schemey's interpreter.
    """
    interpreter.interpret_expressions(code, out_stream)

