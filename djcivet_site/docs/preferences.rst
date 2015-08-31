************
Preferences
************

This page has standard HTML check-boxes for setting the status of some of the
variables affecting the work flow and initial presentation of the texts. 

**Always apply annotation**
    Always apply automatic annotation to texts that have not been previously 
    annotated. 
    
    - Default: ``True``
    - “civet_settings.py” variable: ``ALWAYS_ANNOTATE``

**Show all content in coder**
    In the coder, initially expand the content of all of the ledes. 
    
    - Default: Only expand the first lede.
    - “civet_settings.py” variable: ``SHOW_ALL_CONTENT``

**Skip editing**
    When reading a collection, skip the editing screen and go directly to the 
    coder: this is typically used when dealing with texts that have already 
    been annotated or where the form does not have any fields that use 
    annotation. 
    
    When combined with ``Always apply annotation: True``, the 
    “Code next collection” button in the coding screen will read the next 
    collection, apply the automatic annotation, and display the annotated 
    text with the form. In this mode, the automatic annotation is not 
    saved.
    
    - Default: ``False``
    - “civet_settings.py” variable: ``SKIP_EDITING``
    
**Use text if value is missing:**
    This controls the output when ``save`` specifies a value output and a  
    bracketed value is not the final element of the text string.  If ``True``, 
    the text will be
    used; otherwise the MISSING_VALUE string will be used.
    
    When combined with ``Always apply annotation: True``, the 
    “Code next collection” button in the coding screen will read the next 
    collection, apply the automatic annotation, and display the annotated 
    text with the form. In this mode, the automatic annotation is not 
    saved.
    
    - Default: ``True``
    - “civet_settings.py” variable: ``USE_TEXT_FOR_MISSING``

**Missing value**
    Sets the missing value. 
    
    - Default: *
    - “civet_settings.py” variable: ``MISSING_VALUE``
    

Programming note
================

We eventually expect to implement an option for setting initial preferences 
through a configuration file in the workspace, but in the meantime the default 
values of various global variables are set in the file 
*civet_settings.py* and should be reasonably well documented there; in most 
cases these take the values ``True`` or ``False``; those values are 
case-sensitive.

The preferences page is implemented through those global variables, a very 
minimal Django form class ``PrefsForm`` in *forms.py*, and the ``set_preferences()`` 
and ``get_preferences()`` functions in *civet_settings.py.*  If you wish 
to make additional global variables modifiable from this screen,  you will probably be able to 
customize it just by following the examples in the existing code.


