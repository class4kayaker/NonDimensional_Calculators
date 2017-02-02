Printing Values From Parameter Files
====================================

Calling the Utility
-------------------

``sci_parameter_utils print -d CONFIG_FILE PRMFILES...``

Writing the YAML Configuration Files
------------------------------------

In order to be able to identify where the relevant parameter file entries are
and construct the necessary derived quantitys, a configuration file is
required. The configuration file may be in YAML or JSON, and consists of three
sections. The example structure will be given using the YAML format due to
being more readable.

Elements
^^^^^^^^

The first section identifies elements which will be used to construct the
output. An example of this section is

| elems:
|     elem_name1:
|         type: float
|     elem_name2:
|         type: float
|     elem_name3:
|         type: expr
|         expr: "2*elem_name1+elem_name2`
|         fmt: "{:.4g} units"

The elements are specified in :ref:`_construct_elems`

Note that any circular dependencies will produce an error, so it is not
possible to specify elements which are each dependent on the output of the
other.

Locations
^^^^^^^^^

The second section specifies where in the parameter file the input values are
defined.

| locs:
|     elem_name1:
|         type: loc
|         key: "Path:to:location1"
|     elem_name2:
|         type: loc
|         key: "Path:to:location2"

The elements are specified in :ref:`_location_elems`

Printing Sections
^^^^^^^^^^^^^^^^^

| print:
|     group1:
|         [List, of, elements1]
|     group2:
|         [List, of, elements2]
