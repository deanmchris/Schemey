"""
schemey.py
----------------------------------------

This is the main file in the Schemey project. It implements
command line arguments which encapsulates the functionality of
Schemey. If your interested in using Schemey, or you just want to
mess around with the repl, this is the file that should be run.

When running this file, pass in the "--help" or "-h" flag for
a full list of the command line flags which can be passed in,
and find out more information.

"""

import argparse
import os
import sys
import ntpath
from .compiler import compile_source
from .bytecode import Serializer, Deserializer
from .virtual_machine import VirtualMachine
from .interpreter import Interpreter
from ._parser import Parser

from .context import tests
from tests import test_vm_compiler, test_interpreter

# our virtual machine is not properly tail recursive. We
# need to set the recursion limit higher.
sys.setrecursionlimit(500000)


class FileDoesNotExistsError(Exception):
    pass


def check_if_file_exists(filepath):
    """
    Check if the file at the given path exists.
    """
    if not os.path.isfile(filepath):
        raise FileDoesNotExistsError("File \"{}\" cannot be found and/or does not exists.".format(filepath))


def balenced_parens(string):
    lparen_cnt = 0
    rparen_cnt = 0
    for char in string:
        if char == '(':
            lparen_cnt += 1
        elif char == ')':
            rparen_cnt += 1
    return lparen_cnt == rparen_cnt


def compile_file(file, outfile=None):
    """
    Given a filename and a outfile destination,
    compile the source code in the file, and
    write the resulting bytecode to outfile. If
    an outfile is not specified, the current directory
    is used.
    """
    with open(file) as f:
        source = f.read()

    co = compile_source(source)
    bytecode = Serializer(co).serialize()

    if not outfile:
        directory, filename = ntpath.split(file)
        outfile = directory + "/{}.pcode".format(filename[:-4])

    with open(outfile, 'wb') as f:
        f.write(bytecode)


def decompile_file(bytecode_file):
    """
    Given a file containing, serialized bytecode,
    Decompile it, by displaying the repr of the top-level
    codeobject.
    """
    with open(bytecode_file, 'rb') as f:
        bytecode = f.read()
    co = Deserializer(bytecode).deserialize()
    print(repr(co))


def execute_file(bytecode_file):
    """
    Given a file containing, serialized bytecode,
    read in the bytecode and execute using the virtual
    machine.
    """
    with open(bytecode_file, 'rb') as f:
        bytecode = f.read()
    co = Deserializer(bytecode).deserialize()
    VirtualMachine().run_code(co)


def run_file(file):
    """
    First compile the given file, serialize it,
    and write it to a bytecode file.

    Afterwards, read in the bytecode file, deserialize it,
    and then execute it using the virtual machine.
    """
    with open(file) as f:
        source = f.read()

    co = compile_source(source)
    bytecode = Serializer(co).serialize()

    directory, filename = ntpath.split(file)
    outfile = directory + "/{}.pcode".format(filename[:-4])
    with open(outfile, 'wb') as f:
        f.write(bytecode)

    with open(outfile, 'rb') as f:
        bytecode = f.read()

    co = Deserializer(bytecode).deserialize()
    VirtualMachine().run_code(co)


def run_tests():
    print('\nVirtual machine & compiler tests:\n')
    vm_runner = test_vm_compiler.runner
    test_vm_compiler.run_all_test_cases(vm_runner)
    
    print('\nInterpreter tests:\n')
    inter_runner = test_interpreter.runner
    test_interpreter.run_all_test_cases(inter_runner)


def run_repl():
    interpreter = Interpreter(sys.stdout)
    ln = 0

    print('Schemey REPL v0.2.1\nenter a scheme expression to evaluate it '
          'or "exit" to quit.\n')

    while True:
        code_str = input('[{}]> '.format(ln))
        while not balenced_parens(code_str):
            code_str += input('...  ')

        if code_str == 'exit': 
            break

        try:
            exprs = Parser(code_str).parse()
            if exprs:
                value = interpreter.run(exprs[0])
            else:
                value = None
            
            if value is not None:
                print('=> {}'.format(value))
        except Exception as err:
            print(err.args[0])
        ln += 1

    
def main():
    """
    The main function in this module. This provides definitions of all the
    command line flags, and calls the correct functions which correspond to those
    flags.
    """
    description = """
    Schemey is a subset of Scheme language written in Python. It currently includes: A Scheme interpreter
, An implementation of a stack-based virtual machine called "Schemey VM"
, A compiler from Scheme to Schemey VM bytecode
, and A serializer and deserializer for Schemey VM bytecode.
Documentation concerning the usage of Schemey can be found in the ``doc/`` directory
in the source.
        """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--compile', type=str, help='Given a source file name, compile the file to bytecode'
                                                          'and write the bytecode to a .pcode file.', nargs='+')

    parser.add_argument('-d', '--decompile', type=str, help='Given the path to a bytecode file, de-compile it,'
                                                            'and display the representation of the top-level '
                                                            'codeobject.')

    parser.add_argument('-e', '--execute', type=str, help='Given the path to a bytecode file, load the file'
                                                          'and run the file via the virtual machine.')

    parser.add_argument('-rn', '--run', type=str, help='Given the path to a bytecode file, compile the file to'
                                                       'bytecode, write the bytecode to a .pcode file, load the'
                                                       'file back in, and run the file via the virtual machine.')

    parser.add_argument('-r', '--repl', help='Run the read-eval-print-loop.', action='store_true')

    parser.add_argument('-t', '--test', help='Execute the given test files for the interpreter.', action='store_true')
    args = parser.parse_args()

    if args.compile:
        if len(args.compile) == 2:
            outfile = args.compile[1]
        elif len(args.compile) > 2:
            raise parser.error("--compile expected two arguments at most.")
        else:
            outfile = None
        check_if_file_exists(args.compile[0])
        print("Compiling file \"{}\"".format(args.compile[0]))
        compile_file(args.compile[0], outfile=outfile)
    elif args.decompile:
        check_if_file_exists(args.decompile)
        print("De-compiling file \"{}\"\n".format(args.compile))
        decompile_file(args.decompile)
    elif args.execute:
        check_if_file_exists(args.execute)
        execute_file(args.execute)
    elif args.run:
        check_if_file_exists(args.run)
        run_file(args.run)
    elif args.test:
        run_tests()
    elif args.repl:
        run_repl()
    else:
        # if not arguments are given, the default is to open the repl
        run_repl()


if __name__ == '__main__':
    main()
