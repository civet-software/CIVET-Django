****************************
Appendix 3: Supporting Files
****************************

===============================
Files in ``/static/djciv_data``
===============================

Files that can be modified using a text editor
----------------------------------------------

CIVET.demo.template.txt:
    Demonstration template file for simple coding

CIVET.workspace.demo.zip:
    Demonstration workspace with sample collections, coding form and
    user-specified coding categories

CIVET.stopwords.txt:
    Stop words for automatic named-entity annotation

CIVET.numberwords.txt:
    Number words and phrases for automatic number annotation

civetstyle.css:
    Style sheet for some of the program (this is modified with the
    user-specified categories)

Modify at your own risk
----------------------------------------------

ckeditor:
    This is a ``ckeditor`` file downloaded from
    http://ckeditor.com/: if you would like additional features you
    should be able to create your own and swap it in here.


CIVET Logo
----------

civet_logo.png:
    Don’t like our little guy, or want to put your own mascot here?—this
    is the place to make the change

==============
Documentation
==============

CIVET's documentation is maintained using the Sphinx http://sphinx-doc.org/ system. 
The files are found in the ``docs`` directory at the outer-most level of the system. 
The commands::

    make html
    make latexpdf

are used to generate the on-line and PDF documentation; the files are found in the 
``\_build/html`` and ``\_build/latex`` directories.
