*****************************************************
Appendix 3: Supporting Files and Source Code Settings
*****************************************************

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


Modify at your own risk
----------------------------------------------

ckeditor:
    This is a “CKEditor” file downloaded from
    http://ckeditor.com/: if you would like additional features you
    should be able to create your own and swap it in here.


CIVET Logo
----------

civet_logo.png:
    Don’t like our little guy, or want to put your own mascot here?—this
    is the place to make the change

================================================================
Additional settings that can be changed in ``civet_settings.py``
================================================================

These are global options but do not appear in the “Preferences” menu since there
is little reason to change them dynamically (and usually plenty of reasons not to)

    
**Hide ‘Read coding form’**
    Hide the ‘Read coding form’ button on the home screen: this can be used if you
    only intend coders to be using workspaces. 
    
    - Default: ``False``
    - **civet_settings.py** variable: ``HIDE_READ_CODING_FORM``

    
**Hide ‘Read workspace’**
    Hide the ‘Read workspace’ button on the home screen: this can be used if you
    only intend coders to be using coding forms. 
    
    - Default: ``False``
    - **civet_settings.py** variable: ``HIDE_READ_WORKSPACE``
    
**Hide ‘Preferences’**
    Hide the ‘Preferences’ button on the home screen: this can be used if you 
    don't want coders changing these. 
    
    - Default: ``False``
    - **civet_settings.py** variable: ``HIDE_PREFERENCES``


==============
Documentation
==============

CIVET's documentation is maintained using the Sphinx http://sphinx-doc.org/ system. 
The files are found in the ``docs`` directory at the outer-most level of the system. 
The commands::

    make html
    make latexpdf

are used to generate the on-line and PDF documentation; the files are found in the 
``_build/html`` and ``_build/latex`` directories.

Because of the images and the redundant files in the “_build” directory, 
“djcivet_site/docs” is a very large directory, about 70% of the size of the 
full “djcivet_site” directory, and can be removed in deployments where you are 
just planning to use the on-line documentation. In that situation, the roughly 1 Mb file 
“djcivet_site/djciv_data/static/djciv_data/civdocs.pdf” can also be removed, 
to the code for the system itself is only about 2 Mb.
