.. Schemey documentation master file, created by
   sphinx-quickstart on Mon Feb  6 00:25:42 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Schemey's documentation!
===================================

Schemey is a subset of the Scheme language written in Python. It currently includes:

* A compiler from Scheme to Schemey VM bytecode
* An implementation of a stack-based virtual machine called "Schemey VM"
* A serializer and deserializer for Schemey VM bytecode

All code is in this project is in the public domain.

I would also like to thank `Eli Bendersky`_, for his own project similar to mine;
`bobscheme`_. I greatly benefited from his code, and sometimes even directly incorporated
ideas and implementations from his code into my own. This project would not have been possible
without his project. I highly suggest taking a peek at it.

.. _Eli Bendersky: http://eli.thegreenplace.net/
.. _bobscheme: https://github.com/eliben/bobscheme

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Introduction
------------

.. toctree::
   :maxdepth: 1

   What is schemey
   License
   References


Getting Started
---------------

.. toctree::
   :maxdepth: 1

   Documentation
   Dependencies
   Structure of the source
   Basic usage


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
