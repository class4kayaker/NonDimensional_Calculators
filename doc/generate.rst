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

.. program-output:: sci_parameter_utils template --help

More detailed descriptions of the input parameters are given below.

params
    Parameter configuration file as described in :ref:`generator_config_file`.

    Used to specify relation between the input values and the values to be
    entered in the parameter file.

ifile
    File used to specify lists of values for input parmeters as described in
    :ref:`generator_input_file`.

    This approach is useful when generating large sets of parameter files
    where all required input parameters are known.

TEMPLATE
    Template parameter file as described in :ref:`generator_template_file`.

.. _generator_input_file:

Creating an Input Value File
----------------------------

An input value file consists of a yaml or json file which has a list of key
value pairs. The keys are the input values specified in the :ref:`config file
<generator_config_file>`.

An example yaml file is

::
    -   
        input_int: 16
        input_float: 2.5
        input_string: Example
    -   
        input_int: 8
        input_float: 4.0
        input_string: Example2

If a value is required but not specified and the interactive option is
enabled, the value will be requested from the user, otherwise the utility
will exit with an error.

.. _generator_template_file:

Creating a Template
-------------------

.. _generator_config_file:

Writing the YAML/JSON Configuration File
----------------------------------------
