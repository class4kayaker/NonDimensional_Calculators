Non-Dimensional Parameter Calculation Script
====

For many problems with mathematical descriptions, it is possible to classify
the probable behaviour by examining a non-dimensional parameter formulated from
the provided dimensional (with units) constants.

Frequently it is desirable to quickly and accurately identify what values these
have for a given problem parameter definition file supplied to a scientific
code.

This utility is designed to handle general computation of the correct values
from a parameter file using an appropriate configuration file as specified in
the documentation. Currently only deal.II prm file format is supported, but the
modular design should make it simple to extend to other formats when
appropriate parsers have been added.
