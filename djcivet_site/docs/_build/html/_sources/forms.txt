.. _sec-forms:

****************************
CIVET Coding Form Templates
****************************

A CIVET template file specifies the individual components of the form:
these are the familiar components from web forms but the syntax used to
specify them is simpler than what you will find in HTML.

CIVET is simply adding these controls to an HTML ``<form>`` and, as with
all things HTML, most of the placement of the fields is handled by the
browser. [#f1]_ CIVET provides some limited formatting through the
insertion of text and line breaks, and with some experimenting you
should be able to keep the form from being too ugly.

The template file should be a simple text file—most systems are happier
if this ends in the suffix ``.txt``—similar to that used in an *R*
or *Stata* script (that is, not a formatted file such as that
produced by *MS-Word*). Appendix 1 gives an example of a template
file, and the code for this can also be downloaded from a link in the
program.


======================================
Simple Template-Based Data Entry Form
======================================

The basic data entry form just uses the presumably familiar standard
HTML data entry fields and should be self-explanatory. 

To save a set of coded fields, click one of the buttons which follow the
title ``Options after saving:``

Code another case:
    Save, then return to the same form

Download data:
    Save, then download data as a tab-delimited text file

The ``Download CIVET data`` page  provides a
text box for a file name, and the ``Download file`` button downloads the
coded data. Use the *Start new data file* link to re-start the coding
and the *Continue coding with this file* link to continue adding to the
existing records.

-  The .txt file is tab-delimited and contains the variable names in the
   first line.

-  If the file name does not end in “.txt,” this suffix will be added.

.. figure:: download.png
   :alt: CIVET Data download page



================
Command formats
================

Commands generally have the following format

::

          command: entry-title [var-name] options
          comma-delimited list

Commands vary in how many of these components they have, but all follow
this general pattern.

Each command ends with a blank line (or, if you prefer, the commands are
separated by blank lines.)

Commands can also be cancelled by adding a “-” in front of the command:
this will cancel the entire command, that is, all of the lines
associated with the command, not just the first line. For visual
symmetry, a “+” in front of the command “activates” it, though the
command will also be active without the plus.

“#” denotes a comment: anything following a “#” is ignored, so lines
beginning with “#” are completely ignored.

Items in template specification
-------------------------------

The commands involve one or more of the following items:

entry-title
    This is the title of data entry field. If this ends with ``/`` a
    line-break (``<br>``) is inserted after the text. The titles are
    escaped: at present the characters <, >and the single and double
    quotes are replaced with the equivalent HTML entities
    ``&lt;, &gt; &quot;`` and ``&rsquo;``. [#f2]_ The **entry-title**
    field cannot contain the characters “[” or “]”—if these are present
    they will be interpreted as bounding the **var-name** field—but the
    escaped versions “\\[” and “\\]” are allowed.

var-name
    The text of the variable name for this field; this will be used in
    the first line of the ``.csv`` output file

comma-delimited-option-list
    A list of the items that can be selected, separated by commas. A
    ‘\*’ at the beginning of the item means that it will be initially
    selected.

comma-delimited-var-name-list
    A list of items which appear in **var-name** fields, separated by
    commas.

page-text
    Any text

number
    An integer
    
Errors in template commands
---------------------------

There is a fair amount of error trapping as the commands are processed;
any problems will reported on a web page. Generally the system will 
stop after it has encountered the first error rather than reporting
all of the errors in the file.

===============================
Templates: Specifying variables
===============================

Specifying variables to save
----------------------------

This command gives the variables that will be saved; these can be in any
order but each of these must correspond to a ``var-name`` somewhere in
the form, or are one of the special variables discussed below. A
tab-delimited version of this list will be the first line of the output
file. The command can occur anywhere in the file.

    | **save:**
    | comma-delimited-var-name-list

If the variable name has brackets following it, the *value* of the
variable rather than the literal text will be written when the data are
written to a tab-delimited file: the value is the string in brackets
``[…]`` in the annotated coding mode. If there is a variable name inside
the brackets, that will be used as the column name for the values;
otherwise the regular name will be used: this allows both the literal
text and the value to be saved, as in the third example below. If
``save`` specifies a value output and not is found, a missing value will
be used.

**Example:**

    | ``save: worldregion, eyewit, groupname, comments``
    | ``save: worldregion [regioncode], eyewit, groupname[], comments``
    | ``save: worldregion, eyewit, groupname, groupname [groupcode], comments``

constant
--------

Sets the value of a variable to a constant; this can be used in a
``save:``

    | **constant:** page-text [varname]

**Example:**

    ``constant: Data set 0.2 [data_id]``

filename
--------

Sets the default file name for the downloads: this can be changed before
downloading. [Beta 0.7: Not yet implemented]

    | **filename:** page-text

**Example:**

    ``filename: our_wonderful_data.csv``

Special variables
-----------------

\_coder\_
    : Text entered in the *CIVET template selection* page

\_date\_
    : Current date. this is currently in the form DD-mmm-YYYY but later
    versions of the system will allow other formats

\_time\_
    : Current time in hh:mm:ss format


============================
Templates: Data Entry Fields
============================

Checkbox
--------

A simple binary check-box. The value of the variable will be first item
in the list when the box is not checked; the second item when the box is
checked. The \* notation on the second item can be used to specify
whether or not the box is initially checked.

    | **select:** entry-title [var-name]
    | comma-delimited-option-list

**Example:**

    ``select: Eyewitness report? [eyewit] no,*yes``

Select from pull-down menu
--------------------------

Pull-down menus—which are called a “select” in HTML—are specified with
the syntax

    | **select:** entry-title [var-name]
    | comma-delimited-option-list

**Example:**

    ``select: Region [worldregion] North America, South America, Europe, *Africa, Middle East, Asia``

Radio buttons
-------------

A series of radio buttons are specified with the syntax

    | **radio:** entry-title [var-name]
    | comma-delimited-option-list

The entry ``/`` in the option list causes a line-break (``<br>``) to be
inserted

**Example:**

    ``radio: Region/ [worldregion] North America, South America, Europe, *Africa, /,Middle East, Asia``

Enter single line of text
-------------------------

This creates a box for a single line of text (HTML `` type=text``). The
``width = number`` is optional and specifies the size of the text entry
box in characters: the default is ``width = 32``

    | **textline:** entry-title [var-name] width = number
    | initial-text

**Example:**

    ``textline: Name of group [groupname] <enter name>``

Extract single line from annotated text
---------------------------------------

This creates a box for a single line of text (HTML `` type=text``) that
will interact with annotated text; in addition information can be
manually entered or cut-and-pasted into this box. If this command is
used in a form that does not have associated annotated text, it behaves
the same as ``textline`` and the ``class`` information is ignored.

The ``class=class-name`` is required and specifies the name of the
annotation class that the text-entry box is connected with; a class can
be associated with multiple text-entry boxes. There are three standard
classes:

-  ``nament``: named-enties, which are determined by capitalization

-  ``num``: numbers

-  ``date``: dates

The ``width = number`` is optional and specifies the size of the text
entry box in characters: the default is ``width = 32``

    | **textclass:** entry-title [var-name] class=class-name
      width=number
    | initial-text

**Example:**

    ``textclass: Name of city [cityname] class=nament <enter city>``

Enter multiple lines of text
----------------------------

This corresponds to an HTML “TEXTAREA” object. The
``rows = number cols = number`` is optional and specifies the size of
the text entry box in characters: the default is ``rows = 4 cols = 80``

    | **textarea:** entry-title [var-name] rows = number cols = number
    | initial-text

**Example:**

    ``textarea: Comments [comments] rows = 2 cols = 64 – put any additional comments here –``

==========================================
Templates: Additional Web Page Formatting
==========================================

Set page title
--------------

Sets the title of the web page: that is, the HTML``<title>...</title>`` 
section of the header.

    | **title:** page-text

**Example:**

    ``title: CIVET-based coding form``

Insert text
-----------

Adds text to the form: the various options follow the usual HTML
formats. In interests of simplicity, text is “escaped” so that special
characters are not interpreted as HTML: note that this means that
in-line mark-up such as ``<i>``, ``<b>`` and ``<tt>`` will not work,
so if you need this activate and use the ``html:`` command. Also keep in
mind that these commands need to be separated by a blank line.

    | **h1:** page-text
    | **h2:** page-text
    | **h3:** page-text
    | **h4:** page-text
    | **p:** page-text

**Example:**

::

        h1: Primary data set coding form

        p:Please enter data in the fields below, and be really, really careful!

The simple command

::

    p:

is useful for putting some space between form elements.

Insert HTML
-----------

[This command may or may not be included in the operational version of
the system, as it provides some opportunities for mischief. Stay tuned.
It is in the code but currently deactivated; if you are installing your
own version of the system, it can be activated by changing a single
character in the source code.]

Adds arbitrary HTML code without escaping.

    | **html:** page-text

Insert a line break
-------------------

Adds a new line in the form

    **newline:**

.. rubric:: Footnotes

.. [#f1]
   Writing in HTML5 and CSS, one can actually exercise a very fine
   degree of control over the placement, but if you are comfortable with
   that sort of code, you presumably aren’t using CIVET in the first
   place. That said, you can see the HTML generated by CIVET by using
   the *View source* option in your browser, then save it as a file
   using *Save Page As...* and that could provide a starting point for
   creating prettier code.

.. [#f2]
   In the current implementation, named HTML entities such as ``&copy;``
   and ``&euro;`` can be included and should produce the correct
   character. At present numbered entities such as ``&#91;``—the HTML
   equivalent of ’]’—do not work since the # is interpreted as a comment
   delimiter: depending on whether there is demand for this feature, the
   system could provide a way around this.

