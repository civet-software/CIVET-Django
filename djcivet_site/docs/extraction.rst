***************************
Coding and Text Extraction
***************************

The CIVET coding form screen in the demonstration version is shown below. [#f1]_

.. figure:: civetcoder.png
   :width: 80%
   :alt: CIVET Coder

The general operation of the coder/extractor is described below:

#. Unless ``civet_settings.SHOW_ALL_CONTENT = True``, only the content 
   of the first text will be expanded; to expand or collapse these,
   click on the lede (green text). [#f2]_ The date of the 
   article follows the lede in brackets.
   
   Shift-click on the lede will *delete* the text: the lede and text 
   disappear and from any subsequent codings. The text actually remains 
   in the workspace file until it is permanently removed (or the 
   deletion is reversed) in the workspace management. See the notes
   below for more details on this operation.
   
#. There are three controls at the top of the text display:

    - ``Show/hide comments``: toggles the display of the comments for
       each text: these are initially hidden.
       
    - ``Show all content``: shows the content for all of the ledes
       
    - ``Hide all content``: hides the content for all of the ledes
              

#. Clicking a text entry boxes associated with an annotation category
   will highlight the relevant words in text: In the demonstration
   version these are

   Location:
       named-entities

   Maximal injuries:
       actions

   Who was involved:
       people

   The ‘tab’ key cycles between the coding fields, or an option can be
   selected using the mouse.

#. When an annotated category field is active, all of the words and
   phrases in the text for that category are changed to red, with the
   first word highlighted using a green background. The arrow keys can
   be used to move the highlighted text into the field. These operate as
   follows:

   Right arrow:
       Highlight the next text in the category

   Left arrow:
       Highlight the previous text in the category

   Down arrow:
       *Replace* the contents of the field with the highlighted
       text. 

   Up arrow:
       *Append* the contents of the field with the highlighted text.
       The appended texts are comma-delimited.

#. Copy-and-paste from the text to the data fields work as you would
   expect; text can also be entered and edited manually.

#. If bracketed values are included in the string, the system takes
   the value from within a set of brackets that is the final item [#f3]_
   in the phrase: earlier sets are
   assumed to be part of the text. For example, the value of the
   phrase ``Islamic State [ISIS][mnsa]`` will be “mnsa”; the value 
   of the phrase ``Islamic State [ISIS] militia`` will be 
   “Islamic State [ISIS] militia”.

#. To save a set of coded fields, click one of the buttons along the
   bottom. At present, all three buttons save; later versions add
   "cancel“ and "reset” options. The options are:

   Continue coding this collection:
       Save the data internally, then return to the same text to code
       additional cases.

   Code next collection:
       Save the data internally, then select the next collection in the
       workspace and go to the annotation screen.

   Select new collection:
       Save the data internally, then select a new collection

   Download workspace and return to home screen:
        This downloads the workspace with the coded cases to the local
        machine. The :ref:`Manage workspace <sec-management>` facility  can then be used to download any coded cases.

Note on deleting texts
----------------------

Deleting a text changes the value of the ``textdelete`` field to 
``True``: the text remains in the workspace file but will not be
displayed again. Deletion also generates a case with the standard
``casedate`` and ``casecoder`` fields and the following fields in the
``casevalues`` dictionary

::

_delete_ : True
_textid_ : textid for the deleted text

This can be used to track the deletion of specific texts. version
Beta-0.9 does not have any internal utilities for using this 
information but those functions may be added in a later version.

Deletion is tracked through the hidden text field ``deletelist`` 
in *civet_coder.html.*
    

.. rubric:: Footnotes

.. [#f1]
   The form displayed is specified in the file
   
   ``djcivet_site/djciv_data/static/djciv_data/CIVET.demo.coder.template.txt``
   
   and can be modified if you want to experiment.

.. [#f2]
   If you are switching back to the text from a text-extraction box,
   you will need to double-click: the first click switches the focus
   to the text; the second toggles the content

.. [#f3]
   Specifically, the system checks whether the final character in the
   string that is not whitespace is ‘]’. The output when the system is
   expecting to find a bracketed value and does not is controlled by
   the preference ``civet_settings.USE_TEXT_FOR_MISSING`` which can be 
   changed on the “Preferences” screen.

   


