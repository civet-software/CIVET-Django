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
##
##	----------------------------------------------------------------------------------

from django.conf import settings

ONLINE_DOCS_URL = 'http://civet.parusanalytics.com/civetdocs/index.html'
PDF_DOC_URL = 'http://civet.parusanalytics.com/CIVET.Documentation.pdf'

DEFAULT_CKEDITOR_STYLES = "{ name: 'Named Entity',	element: 'span', styles: { 'class':'nament', 'color': 'blue' }  },\n \
            { name: 'Number',	element: 'span', styles: { 'class':'number', 'color': 'green' }  },\n \
            { name: 'Date',	element: 'span', styles: { 'class':'date', 'color': 'coral' }  },"
            
PRODUCTION_MODE = False

STATIC_FILE_PATH = settings.BASE_DIR + '/djciv_data' + settings.STATIC_URL + 'djciv_data/' # path for files referenced in views.py

if PRODUCTION_MODE:
    settings.DEBUG = False
    STATIC_SOURCE = "http://civet.parusanalytics.com/civet_static/"
else:
    STATIC_SOURCE = "/static/djciv_data/"
    STATIC_SOURCE = "http://civet.parusanalytics.com/civet_static/"
    
