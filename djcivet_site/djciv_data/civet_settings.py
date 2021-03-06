##	civet_settings.py
##
##  The usual collection of global settings
##
##	PROVENANCE:
##	Programmer: Philip A. Schrodt
##				Parus Analytics
##				Charlottesville, VA, 22901 U.S.A.
##				http://parusanalytics.com
##
##	Copyright (c) 2015	Philip A. Schrodt.	All rights reserved.
##
##  The development of CIVET is funded by the U.S. National Science Foundation Office of Multidisciplinary Activities in the 
##  Directorate for Social, Behavioral & Economic Sciences, Award 1338470 and the Odum Institute at the University of 
##  North Carolina at Chapel Hill with additional assistance from Parus Analytics.
##
##  This code is covered under the MIT license: http://opensource.org/licenses/MIT
##
##	Report bugs to: schrodt735@gmail.com
##
##	REVISION HISTORY:
##	14-August-15:	Initial version
##  31-August-15:   Beta 0.9
##
##	----------------------------------------------------------------------------------

from django.conf import settings

            
# ============= File locations  ============= #

ONLINE_DOCS_URL = 'http://civet.parusanalytics.com/civetdocs/index.html'
PDF_DOC_URL = 'http://civet.parusanalytics.com/CIVET.Documentation.pdf'
STATIC_FILE_PATH = settings.BASE_DIR + '/djciv_data' + settings.STATIC_URL + 'djciv_data/' # path for files referenced in views.py


# ============= Editor styles  ============= #

DEFAULT_CKEDITOR_STYLES = "{ name: 'Named Entity',	element: 'span', styles: { 'class':'nament', 'color': 'blue' }  },\n \
            { name: 'Location',	element: 'span', styles: { 'class':'geogent', 'color': 'brown' }  },\n \
            { name: 'Number',	element: 'span', styles: { 'class':'num', 'color': 'green' }  },\n \
            { name: 'Date',	element: 'span', styles: { 'class':'date', 'color': 'coral' }  },\n \
"

EDITOR_LEDE_STYLE = 'color:green; font-weight:bold; padding-top: 8px;'
EDITOR_CONT_STYLE = 'padding-top: 4px;'
EDITOR_LEDE_LABEL = 'Lede: '
EDITOR_LABEL_STYLE = '<span style="color:blue;">'
EDITOR_DATE_LABEL =  EDITOR_LABEL_STYLE + 'Date:&nbsp;</span>'
EDITOR_COMM_LABEL =  EDITOR_LABEL_STYLE + 'Comments:&nbsp;</span>&ldquo;&nbsp;'
EDITOR_CONTENT_LABEL =  EDITOR_LABEL_STYLE + 'Content:<br /></span>'  # <br /> rather than <br> is required for consistency with CKEditor

# ============= Annotation details  ============= #

GEOG_PREPOSITIONS = ['at','to','in','from']

# ============= Downloadable files  ============= #

#DEMO_TEMPLATE = 'CIVET.exper.template.txt'  # DEBUG
DEMO_TEMPLATE = 'CIVET.demo.template.txt'
#DEMO_WORKSPACE = 'CIVET.workspace.exper.zip' # DEBUG
DEMO_WORKSPACE = 'CIVET.workspace.demo.zip'
DOCUMENTATION = 'civetdoc.pdf'            
            
# ============= General Preferences  ============= #

HTML_OK = True   # allow html: command?
HTML_OK = False

DEFAULT_FILENAME = 'civet.output.txt'  # holds the value set by filename:
FORM_PAGETITLE = 'CIVET Data Entry Form'   # holds the value set by title:

MISSING_VALUE = '*' # used only if values are missing
USE_TEXT_FOR_MISSING = True   # substitute text rather than MISSING_VALUE if [value] is absent

SHOW_ALL_CONTENT = False  # initially expand all content in coder
ALWAYS_ANNOTATE = True   # 
NEVER_ANNOTATE = False   # never annotate: HTML markup has been provided in the YAML file
SKIP_EDITING = False
USE_GEOG_MARKUP = True  # do geographical markup before named entity
HIGHLIGHT_NAMENT = True  # highlight the nament class during annotation
HIGHLIGHT_NUM = True  # highlight the num class during annotation

USE_TEXTBIBLIO_IN_SOURCE = False  # source includes textbiblio field
USE_TEXTID_IN_SOURCE = False # source includes textid field

# controls for options on the home screen:
HIDE_READ_CODING_FORM = False
HIDE_READ_WORKSPACE = False
HIDE_PREFERENCES = False

REQUIRE_LOGIN = False  
#REQUIRE_LOGIN = True

CLEAR_DATABASE = True  # clears database before reading workspace              
            
# ============= Custom Preferences  ============= #

# UNCC-SmARTT summer-2016
 
MAKE_MAPS = True 
MAP_KEY = '<put the free key you get from Google here>'


# ============= Production mode  ============= #

PRODUCTION_MODE = False

if PRODUCTION_MODE:
    settings.DEBUG = False
    REQUIRE_LOGIN = True  
    STATIC_SOURCE = "http://civet.parusanalytics.com/civet_static/"
else:
    STATIC_SOURCE = "/static/djciv_data/"
    
            
# ============= get/set  ============= #

def get_preferences():
    prefs = {}
    prefs['alwaysannotate'] = ALWAYS_ANNOTATE
    prefs['neverannotate'] = NEVER_ANNOTATE
    prefs['showallcontent'] = SHOW_ALL_CONTENT
    prefs['skipediting'] = SKIP_EDITING
    prefs['textmissing'] = USE_TEXT_FOR_MISSING
    prefs['missingvalue'] = MISSING_VALUE
    prefs['geogmarkup'] = USE_GEOG_MARKUP
    prefs['sourcetextbiblio'] = USE_TEXTBIBLIO_IN_SOURCE
    prefs['sourcetextid'] = USE_TEXTID_IN_SOURCE
    return prefs
    
def set_preferences(form):
    global ALWAYS_ANNOTATE, NEVER_ANNOTATE, SKIP_EDITING, SHOW_ALL_CONTENT, USE_TEXT_FOR_MISSING, MISSING_VALUE,\
           USE_TEXTBIBLIO_IN_SOURCE, USE_TEXTID_IN_SOURCE, HIDE_READ_CODING_FORM, HIDE_READ_WORKSPACE, HIDE_PREFERENCES
    ALWAYS_ANNOTATE = form['alwaysannotate']
    NEVER_ANNOTATE = form['neverannotate']
    SHOW_ALL_CONTENT = form['showallcontent']
    SKIP_EDITING = form['skipediting']
    USE_TEXT_FOR_MISSING = form['textmissing']
    MISSING_VALUE = form['missingvalue']
    USE_GEOG_MARKUP = form['geogmarkup']
    USE_TEXTBIBLIO_IN_SOURCE = form['sourcetextbiblio']
    USE_TEXTID_IN_SOURCE = form['sourcetextid']
    

