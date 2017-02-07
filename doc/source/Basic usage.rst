Basic Usage
===========

Command line Flags
------------------

While it is certainly not necessary to know all possible command line
flags for Schemey, there are some which are important and it wouldn't
hurt to memorize them.

Schemey offers several different flags for use on the command line.
The full list is:

* ``-c`` ``--compile``: Given the path to a source file, compile the source file into
                        bytecode, and write it to a file. If a second argument is given
                        the bytecode will be written to that file, otherwise a file is created
                        in the same directory as the source file, and the bytecode is written
                        there.
* ``-d`` ``--decompile``: Given the path to a compiled bytecode file, decompile the bytecode in
                          the file, and display a helpful representation of the bytecode structure.
* ``-e`` ``--execute``: Given the path to a compiled bytecode file, load in the file and execute it
                       via the virtual machine.
* ``-rn`` ``--run``: Given the path to a bytecode file, compile the file to
                    bytecode, write the bytecode to a file, load the
                    file back in, and run the file via the virtual machine. This
                    is basically a combination off the functionality of all the above
                    flags.
* ``-r`` ``--repl``: Run the REPL for Schemey(See *Running the REPL* below).
* ``-t`` ``--test``: Run the tests for the Schemey interpreter.


Running the REPL
----------------

The REPL is a powerful feature which allows you to quickly test your
code, without having to recompile a source file over and over.

To use the REPL, navigate to the ``Schemey/src/`` directory, in the source
and run the ``schemey.py`` file. This is the main file of the source code and
used to run Schemey from the command line. After running the file, the REPL
will open with a greeting message, some brief instructions on usage, and a prompt
eg:

.. code-block:: console

    C:\Schemey\src> python schemey.py
    Welcome to the Schemey repl. Type in expressions and press
    enter to evaluate them, or type in "exit" to quit.

   [schemey]>

After the REPL is open, you can type in an expression and see it
evaluated immediately:

.. code-block:: console

    [schemey]> (+ 1 2)
    => 3
    [schemey]> (+ 1 2 3 4 5 6 7 8 9 10)
    => 55

To "break" out of the REPL, you can type in the ``exit`` command. This will return you back
into the command prompt:

.. code-block:: console

    [schemey]> exit

    C:\Schemey\src>

The REPL offers the distinct advantage of being able to quickly and easily test expressions,
and see their results immediately, instead of having to re-compile a source file
again and again to see the updated changes.

.. warning::
   Multi-line expressions(expression which span multiple lines) are currently not allowed in the REPL.
   eg.

   .. code-block:: console

       [schemey]> (+ 1

       At line 1:

       (+ 1
           ^

       Unmatched parentheses at end of input
       [schemey]>


Compiling & Decompiling source files
------------------------------------

As said above, the flags ``-c`` ``--compile`` and ``-d`` ``--decompile`` correspond to
compiling and decompiling a source file respectively.

To compile a source file, pass the ``-c`` or ``--compile`` flag to
``schemey.py``, along with *at least* on argument to the flag which
is the source file to be compiled. If a second argument is given, the
bytecode will be written to that path. Otherwise, a file is created with
the same name as the source file's, with a  ``.pcode`` extension.

To decompile a file into human-readable output, pass the ``-d`` or ``--decompile``
flag ``schemey.py``. One argument is required, which is the path to the compiled
bytecode file. After de-compilation, a helpful representation of the structure of
the bytecode file is printed out(the output is actual ``repr(CodeObject())``. See
``bytecode.py`` for the implementation of ``CodeObject``).


Executing a source file
-----------------------

There are two ways one can execute a source file.

* You can first compile the source file(see *Compiling & Decompiling source files*),
  then use the ``-e`` or ``--execute`` flags to execute the bytecode file. The one
  argument the two flags take is the path to a bytecode file.

  You might wonder why one would want to compile a program in this manner,
  when they could simply do everything all at once using the ``--run`` flag
  (see below).

  The reason for this design is so SchemeyVM is able to execute bytecode
  compiled by compilers other than the one in this project. In other words,
  this design allows anyone to create a compiler which targets SchemeyVM's
  bytecode, and the virtual machine will be able to execute files created
  by those compilers.

* The second way you can run a source file - and will probably the most common - is
  using the ``-rn`` ``--run`` flags, which require one argument; the path to the
  source file. The source file will then be automatically compiled and executed.


.. note::
   all output by the virtual machine is directed to ``sys.stdout``. If you would
   like this changed, the ``VirtualMachine`` class's constructor allows you to specify
   an output stream(see ``virtual_machine.py`` for more details).
