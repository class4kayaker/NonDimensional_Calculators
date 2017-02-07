Generating Parameter Files From Templates
=========================================

Under a number of circumstances, the generation of a number of similar
parameter files with relatively small modifications are desired. While hand
creating these files is possible, as the number of required files increases the
number of expected minor errors increases rapidly. Additionally, in some cases
the values of interest are not directly entered into the parameter file but
instead used to generate a set of derived quantities, increasing the likelihood
of minor errors. Therefore, the use of some automated utility for generating
such files is quite useful.

Calling the Utility
-------------------

The utility is called as a standard command line utility.

The parameters specified by the

params
    Parameter configuration file as described in :ref:`generator_config_file`.

    Used to specify relation between the input values and the values to be
    entered in the parameter file.

ifile
    File used to specify lists of values for input parmeters as described in
    :ref:`generator_input_file`.
    
    If a value is required but not specified and the interactive option is
    enabled, the value will be requested from the user, otherwise the utility
    will exit with an error.

TEMPLATE
    Template parameter file used to generate the

.. _generator_input_file:

Creating an Input Value File
----------------------------

.. _generator_template_file:

Creating a Template
-------------------

.. _generator_config_file:

Writing the YAML/JSON Configuration File
----------------------------------------
