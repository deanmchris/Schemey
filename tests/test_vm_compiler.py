"""
test_vm_compiler.py
----------------------------------------

The implementation of the runner function(see test_cases_utils.py)
for Schemey's compiler and virtual machine.
"""

import sys
from src import compiler
from src import virtual_machine
from test_cases_utils import run_all_test_cases

# our virtual machine is not properly tail recursive. We
# need to set the recursion limit higher.
sys.setrecursionlimit(500000)


def runner(code, out_stream):
    """
    The runner function of Schemey's compiler and virtual machine.
    """
    code_obj = compiler.compile_source(code)
    vm = virtual_machine.VirtualMachine(out_stream)
    vm.run_code(code_obj)

run_all_test_cases(runner)
