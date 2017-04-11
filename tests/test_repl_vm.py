"""
test_vm_compiler.py
----------------------------------------

The implementation of the runner function(see test_cases_utils.py)
for Schemey's REPL.
"""

from .context import src
from .test_cases_utils import run_all_test_cases

from src import virtual_machine


def runner(code, out_stream):
    repl_vm = virtual_machine.ReplVM()
    expr_repr = repr(repl_vm.run_code(code))
    out_stream.write(expr_repr)
