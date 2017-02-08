Printing Values From Parameter Files
====================================

Scientific models often depend on a number of input parameters that due to
designing for more general use, are frequently not identical to the parameters
of interest for a particular application. It is therefore desirable to have a
means of easily and rapidly obtaining derived quantities from such an input
parameter file. Given that such files are already constructed for the purpose
of being machine interpreted, this can be expected to be possible. However,
generality of application will require relatively complex configuration.

Calling the Utility
-------------------

.. program-output:: sci_parameter_utils print --help

The utility is used with a standard command line call of the form:

``sci_parameter_utils print -d CONFIG_FILE PRMFILES...``

This results in the computation of the values specified in ``CONFIG_FILE`` and
writing the specified values to STDOUT in a reasonably readable form.

In the case where only a subset of the output sections are desired, a list of
sections to be printed may be specified using the form:

``sci_parameter_utils print -d CONFIG_FILE -p "section,list" PRMFILES...``

Writing the YAML/JSON Configuration Files
-----------------------------------------

In order to be able to identify where the relevant parameter file entries are
and construct the necessary derived quantitys, a configuration file is
required. The configuration file may be in YAML or JSON, and consists of three
sections. The example structure will be given using the YAML format due to
being more readable.

Elements
^^^^^^^^

The first section identifies elements which will be used to construct the
output. An example of this section is

::

    elems:
        elem_name1:
            type: float
        elem_name2:
            type: float
        elem_name3:
            type: expr
            expr: "2*elem_name1+elem_name2`
            fmt: "{:.4g} units"

The elements are specified in :ref:`construct_elems`

Note that any circular dependencies will produce an error.

Locations
^^^^^^^^^

The second section specifies where in the parameter file the input values are
defined.

::

    locs:
        elem_name1:
            type: loc
            key: "Path:to:location1"
        elem_name2:
            type: loc
            key: "Path:to:location2"

The elements are specified in :ref:`location_elems`

Printing Sections
^^^^^^^^^^^^^^^^^

::

    print:
        group1:
            [List, of, elements1]
        group2:
            [List, of, elements2]
