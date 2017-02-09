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
import ntpath
from compiler import compile_source
from bytecode import Serializer, Deserializer
from virtual_machine import VirtualMachine, ReplVM


class FileDoesNotExistsError(Exception):
    pass


def check_if_file_exists(filepath):
    """
    Check if the file at the given path exists.
    """
    if not os.path.isfile(filepath):
        raise FileDoesNotExistsError("File \"{}\" cannot be found and/or does not exists.".format(filepath))


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


def repl(prompt='[schemey]> '):
    """
    Create a Scheme repl.
    """
    print("Welcome to the Schemey repl. Type in expressions and press")
    print("enter to evaluate them, or type in \"exit\" to quit.\n")
    vm = ReplVM()
    while True:
        line = input(prompt)
        if line == 'exit':
            break
        try:
            co = compile_source(line)
            expr_repr = repr(vm.run_code(co))
            if expr_repr != repr('<#undef>'):
                print('=> {}'.format(expr_repr))
        except Exception as error:
            print(error.args[0])


def run_tests():
    test_filepath = os.getcwd()[:-4] + '\\tests\\test.scm'
    with open(test_filepath) as f:
        source = f.read()

    co = compile_source(source)
    bytecode = Serializer(co).serialize()

    directory, filename = ntpath.split(test_filepath)
    outfile = directory + "/{}.pcode".format(filename[:-4])
    with open(outfile, 'wb') as f:
        f.write(bytecode)

    with open(outfile, 'rb') as f:
        bytecode = f.read()

    co = Deserializer(bytecode).deserialize()
    print("\n---------------------Program------------------------:\n")
    VirtualMachine().run_code(co)
    print("\n---------------------CodeObject-----------------------:\n")
    print(repr(co))


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
        repl()
    else:
        # if not arguments are given, the default is to open the REPL.
        repl()


if __name__ == '__main__':
    main()
