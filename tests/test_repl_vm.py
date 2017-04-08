"""
test_vm_compiler.py
----------------------------------------

The implementation of the runner function(see test_cases_utils.py)
for Schemey's REPL.
"""

import sys
from src import virtual_machine
from test_cases_utils import run_all_test_cases

# our virtual machine is not properly tail recursive. We
# need to set the recursion limit higher.
sys.setrecursionlimit(500000)


def runner(code, out_stream):
    repl_vm = virtual_machine.ReplVM()
    expr_repr = repr(repl_vm.run_code(code))
    out_stream.write(expr_repr)

run_all_test_cases(runner)