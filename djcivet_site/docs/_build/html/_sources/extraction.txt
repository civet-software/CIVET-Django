***************************
Coding and Text Extraction
***************************

The CIVET coding form screen in the demonstration version is shown below. [#f1]_

.. figure:: civetcoder.png
   :width: 80%
   :alt: CIVET Coder

The general operation of the coder/extractor is described below:

#. Clicking a text entry boxes associated with an annotation category
   will highlight the relevant words in text: In the demonstration
   version these are

   Location:
       named-entities

   Maximal injuries:
       actions

   The ‘tab’ key cycles between the coding fields, or an option can be
   selected using the mouse.

#. When an annotated category field is active, all of the words and
   phrases in the text for that category are changed to red, with the
   first word highlighted using a green background. The arrow keys can
   be used to move the highlighted text into the field. These operate as
   follows:

   Right arrow:
       Highlight the next text in the category [#f2]_

   Left arrow:
       Highlight the previous text in the category

   Down arrow:
       *Replace* the contents of the field with either the currently
       selected text—this is effectively a single-key shortcut for a
       copy-and-paste—or, if no text is selected, the highlighted
       text. [#f3]_

   Up arrow:
       *Append* the contents of the field with either the currently
       selected text or, if no text is selected, the highlighted text

#. Copy-and-paste from the text to the data fields work as you would
   expect; text can also be entered manually.

#. To save a set of coded fields, click one of the buttons along the
   bottom. At present, all three buttons save; later versions add
   "cancel“ and "reset” options. The options are:

   Continue coding this collection:
       Save the data internally, then return to the same text to code
       additional cases.

   Code next collection:
       Save the data internally, then select the next collection in the
       workspace and go to the annotation screen. [#f4]_

   Select new collection:
       Save the data internally, then select a new collection

   Download workspace and return to home screen:
        This downloads the workspace with the coded cases to the local
        machine. The :ref:`Manage workspace <sec-management>` facility  can then be used to download any coded cases.

.. rubric:: Footnotes

.. [#f1]
   The form displayed is specified in the file
   
   ``djcivet_site/djciv_data/static/djciv_data/CIVET.demo.coder.template.txt``
   
   and can be modified if you want to experiment.

.. [#f2]
   Occasionally you will need to hit the key twice when changing
   directions: this is a bug, not a feature, and may be corrected at
   some point. Usually it works the first time. If you would like to try
   to fix this, look at the Javascript in the file ``civet_coder.html``

.. [#f3]
   If you are tabbing between fields and extracting the first
   highlighted text, you will need to hit down arrow twice: also a bug
   rather than a feature.

.. [#f4]
   Beta 0.7: In the final version of the program, there will be an
   option for going to either the annotation or coding screen; the
   annotation screen will also have a “Next” button.

