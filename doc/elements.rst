Elements
========

.. _construct_elems:

Construction Element
--------------------

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

Input elements specify the values to be read from the provided files and
identify the type of value expected. The type of this element is specified in
the type key.

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
    Numerical expressions permitting standard mathematical operations.

    The required additional keys are keys are:

    expr
        Mathematical expression used to compute the new value.

fmt
    String formatting expressions based using python format language with
    the element names as key.

fname
    Identical to ``fmt`` except with some basic standard replacements for
    filename construction (ie ``.``, ``/`` and spaces are replaced with
    underscores.

.. _location_elems:

Location Elements
-----------------

loc


