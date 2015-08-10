********************************************************
Appendix 4: Prototype on Google Application Engine
********************************************************

An earlier demonstration version of the program, written in the Flask
framework, is deployed as an application on the Google App Engine at
http://ace-element-88313.appspot.com/. The “Coding Form Template” option
in this program works as described :ref:`here <sec-forms>`. The code
for this version can be downloaded from https://github.com/philip-schrodt/CIVET-Flask

The other option in the program is the “Text-Extraction Demonstration
Form” which was a prototype of the full annotation/extraction system. To
activate the demo, from the home page, click the link in the line *See a
demo of the text-highlighting system by clicking here*

#. Select a text file to edit: you can use either the pull-down menu or
   radio boxes, then click the ``Edit the file button``.

#. Click one of the text entry boxes will highlight the relevant words
   in text: For demonstration purposes these are words beginning with
   the letters ’a’, ’c’, ’d’, ’e’ and ’s’. The ‘tab’ key cycles between
   these options, or an option can be selected using the mouse.

#. When a text entry box is active, the first relevant word in the text
   is highlighted. The right-arrow key will cycle the highlighted word.
   To copy a highlighted word into the text box, use the down-arrow key.

#. Text can also be selected using the mouse: To copy the selected text
   into the text box, use the left-arrow key.

#. Cut-and-paste from the text to the date fields work as you would
   expect 

#. Text can also be entered manually.

#. To save a set of coded fields, click one of the buttons along the
   bottom. 

   Return to this case:
       Save, then return to the same text

   Select new case:
       Save, then return to the same text

   Download data:
       Save, then download data as a text file

#. The "CIVET Download" page provides a text box for a file name, and
   the ``Download file`` button downloads the coded data. Use the *Start
   new data file* link to re-start the coding and the *Continue coding
   with this file* link to continue adding to the existing records.

   -  The .txt file contains the variable names in the first line.

   -  If the file name does not end in ".txt", this will be
      added.

#. To quit the program, just close the window: This is a HTML/Javascript security feature which
   prevents rogue websites from closing windows unless they have created
   the window.
