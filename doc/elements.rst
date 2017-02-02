Elements
========

.. _construct_elems:

Construction Elements
---------------------

Construction elements specify what values should be provided and what internal
processing of those elements will be necessary. All of these accept a ``fmt``
key specifying how the element should be formatted when printed. Using YAML
syntax the basic structure is

| elem_name:
|     type: type_name
|     fmt: fmt_string
|     # additional keys

Input Elements
^^^^^^^^^^^^^^

Input elements specify required input values and identify the type of value
expected. The type of this element is specified in the type key.

The permitted types are

int
    An integer value
float
    A floating point value
str
    A string value

Expression Elements
^^^^^^^^^^^^^^^^^^^

Expression elements are used to construct an quantities derived from the input
values.

expr
    Numerical expressions permitting standard mathematical operations. This is
    not required to depend on any other elements, and may therefore be used to
    specify constant values as expressions.

    The required additional keys are keys are:

    expr
        Mathematical expression used to compute the new value.

fmt
    String formatting expressions based using python format language with
    the element names as key.

fname
    Identical to ``fmt`` except with some basic standard replacements for
    filename construction (ie ``.``, ``/`` and spaces are replaced with
    underscores.)

.. _location_elems:

Location Elements
-----------------


Using YAML syntax the basic structure is

| elem_name:
|     type: type_name
|     # additional keys

loc:
    Value is specified as a key-value pair in the parameter file.

    Required keys:

    key
        Path to correct key-value pair in parameter file using appropriate
        syntax for interacting with said file.
