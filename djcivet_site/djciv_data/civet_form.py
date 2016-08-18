##	civet_form.py
##
##  Code for handling the CIVET template files
##
##	Error handling:
##	Errors are reported in the 'output' string: they are prefixed with '~Error~' and terminate with '\n'. 
##	These are reported to the user via the template_error.html page, which is rendered by read_template()
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
##  Directorate for Social, Behavioral & Economic Sciences, Award 1338470 and the Odum Institute</a> at the University of 
##  North Carolina at Chapel Hill with additional assistance from Parus Analytics.
##
##  This code is covered under the MIT license: http://opensource.org/licenses/MIT
##
##	Report bugs to: schrodt735@gmail.com
##
##	REVISION HISTORY:
##	14-Mar-15:	 Initial version
##  04-Aug-15:   Beta 0.7
##  31-Aug-15:   Beta 0.9
##  31-Oct-15:   Minerva modifications
##
##	----------------------------------------------------------------------------------

""" Rough guide to processing of forms 

1. get_commlines() takes the text input from the template file and returns a list with a standard set of fields

2. do_command() looks at the type of command and either adds HTML to FormContent or inserts markers for widgets and creates a 
   list that can be passed to  forms.CodingForm

3. forms.CodingForm both creates the various input widgets using Django standards, and stores the current variable values  
   between page changes. These are accessed locally in FormFields

4. get_current_form() uses form.as_p() to get the widgets and current values and replaces the markers with these to produce 
   FormContent, a list of the individual pages which will be displayed as form_content in civet_coder.html.
   
5. Cases store all variable values as a dictionary in the field casevalues -- this is only modified when the cases are 
   read or saved. caselocs is a dictionary which saves the locations of the extracted texts so these can be highlighted 
   during review. 
   
"""


from __future__ import print_function
from django.utils.html import escape
import datetime
import time
import json
import sys

from django.utils import encoding   # used for utf-8 -> ascii conversion

from .models import Collection, Text, Case
from .forms import CodingForm

import civet_settings

# ======== global initializations ========= #

SaveList = []   # variables to write 
SaveTypes = []   # full variable string with optional label for values 
SpecialVarList = ['_coder_', '_date_', '_time_']
MetaVarList    = ['_collection_', '_publisher_', '_biblioref_']
VarList = []    # variables which have entry boxes
TempData = ''   # output string for form-only mode
CoderName = '---' 
ConstVarDict = {}  # holds the variables set by constant:
UserCategories = {} # holds user categories as list [color, vocabulary...]
CategoryCodes = {} # dictionary of dictionaries for category codes, if these are present
CheckboxValues = {} # dictionary of lists of values for checkboxes in order [F,T]; index is variable name
LinkedFields = {} # holds info linked fields

FormContent = ['']  # list containing html strings for the coding form pages
FormFields = {} # dictionary containing the type of field, title, current value and ancillary information, indexed by var name
FormCSS = ''  # css for the coding form

WorkspaceFileName = ''
CollectionId = ''
CollectionComments = ''

EditorSize = '' # size for CKEditor

CatColorList = ['Magenta', 'SeaGreen',  'Orchid', 'Brown', 'Purple', 'Gold', 'Olive', 'Slateblue', 'Cyan', 'Thistle',
                'CornflowerBlue', 'DarkGray', 'Lime', 'Turquoise', 'SlateGray', 'Tan']
CurColor = 0
""" this might be a better palette:
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),  
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),  
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),  
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),  
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]  
http://www.randalolson.com/2014/06/28/how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/"""

CategoryDict = {}  # this will be set in civet_utilities.read_YAML_file()


# ============ function definitions ================ #

"""def imalive(): # debugging
    print('Hello from CIV_template')"""

    
def get_text_metadata(commd, active_collection):
    if commd == '_collection_':
        return active_collection
    else:
        retstr = ''
        curtexts = Text.objects.filter(textparent__exact=active_collection)
        for ct in curtexts:
            if commd == '_publisher_':
                retstr += ct.textpublisher + ', '
            elif commd == '_biblioref_':
                retstr += ct.textbiblio + ', '
    #    print('GTM:',retstr)
        return retstr[:-2]   # remove final comma+space

def split_options(commst):
    """ splits the options for select, option, checkbox, SaveList """
    vlist = []
    for ele in commst.split(','):
        vlist.append(ele.strip())
    return vlist

def get_special_var(avar):
    """ returns values of the _*_ variables """
    if avar == '_coder_':
        return CoderName
    elif avar == '_date_':
        return time.strftime("%Y-%m-%d")
    elif avar == '_time_':
        return time.strftime("%H:%M:%S")
    else: # shouldn't hit this
        return '---'

def parse_codes(st):
    """ parse a word[ ] code string and returns [word, Word, code] """
    parts = st.partition('[')
    vocab = parts[0].strip()
    if vocab[0].islower():  # create capitalized version if needed
        capvocab = vocab[0].upper() + vocab[1:]
    else:
        capvocab = ''
    if ']' in parts[2]:
        code = parts[2][:parts[2].index(']')]
    else:
        code = parts[2]
    return [vocab, capvocab, code]
    
def check_integer(numst, labelst):
    """ checks if numst is a valid integer. ValueError will be caught in do_commands."""
    try:
        int(numst)
    except ValueError as e:
        e.args += (labelst + ' is not a valid integer in ',) 
        raise

def check_for_equalchar(targst, labelst):
    """ checks if '=' is in targst. Exception will be caught in do_commands."""
    if '=' not in targst:
        raise Exception('','No "' + labelst + '=" was found in ',)

def get_integer(optstr, tarst):
    """ returns integer following 'tarst = ...' """
    optstr += ' '
    tarsta = optstr[optstr.index(tarst):]
    check_for_equalchar(tarsta,tarst)
    tarst = tarsta[tarsta.index('=')+1:].lstrip()
    rowstr = tarst[:tarst.index(' ')] 
    check_integer(rowstr,tarst.capitalize())
    return rowstr        

    
def read_codes_file(fin, filename):
    """ reads the codes.file fin and stores results in CategoryCodes 
        This converts utf-8 to ASCII, which needs to be changed in the relatively near future, though probably not until
        we convert the whole thing to Python 3.0
    """ 
    global CategoryCodes 
              
    def create_ascii(str):
        return encoding.smart_str(str, encoding='ascii', errors='ignore')

    newcat = filename[filename.index('codes.')+6:].partition('.')[0]  # category name follows 'codes.' in filename
    CategoryCodes[newcat] = {}
    line = create_ascii(fin.readline())             
    while len(line) > 0:
#        print('GC1:',line)
        if not line.startswith('#'):
            [vocab, capvocab, code] = parse_codes(line)
            CategoryCodes[newcat][vocab] = code
            if len(capvocab) > 0:
                CategoryCodes[newcat][capvocab] = code               
        line = create_ascii(fin.readline())             
#    print('RCF:',newcat, CategoryCodes[newcat])
        

def make_category(commlines):
    """ adds an annotation category to UserCategories, handling various contingencies in the [color] field  """
    """ UserCategories is indexed by category name and consists of lists containing
        color
        internal name of the form termstNN
        list of vocabulary for the category"""
    global UserCategories, CurColor, CategoryCodes
#    print('MC-entry:',commlines)
    newcat = commlines[1]
    if newcat in UserCategories:
        raise Exception('Category "' + newcat + '" is already defined; use a different name.')  # this is caught in do_command
    if len(commlines[2]) < 3:  # handle numbered color from the palette
        try:
            colindex = int(commlines[2]) - 1
        except Exception as e:
#            print('MC01:',e)
            colindex = -1  # force use of default color
        if colindex < 0 or colindex >= len(CatColorList):
            commlines[2] = ''  # force use of default color
        if len(commlines[2]) == 0:
            UserCategories[newcat] = [CatColorList[CurColor]]  # get the next color from the list
            if CurColor < len(CatColorList):
                CurColor += 1
        else:
            UserCategories[newcat] = [CatColorList[colindex]]      
    else:
        UserCategories[newcat] = [commlines[2]]  # this handles named and hex colors
    UserCategories[newcat].append('termst{:02d}'.format(len(UserCategories)))  # internal class name for category

    if commlines[4].startswith('codes.'):       # make sure we read this earlier, then copy vocabulary to UserCategories
        if newcat in CategoryCodes:
            for vocab in CategoryCodes[newcat]:
                UserCategories[newcat].append(vocab)
        else:
            raise Exception('The file "' + commlines[4] + '" was not found in the zipped collections file containing the form')  # this is caught in do_command

    elif '[' in commlines[4]:                       # read values and codes from commlines[4]
        CategoryCodes[newcat] = {}
        for st in split_options(commlines[4]):
            [vocab, capvocab, code] = parse_codes(st)
            CategoryCodes[newcat][vocab] = code
            UserCategories[newcat].append(vocab)
            if len(capvocab) > 0:
                UserCategories[newcat].append(capvocab)
#        print('MC-codes:',newcat, vocab, CategoryCodes[newcat])
    else:                                           # no codes, just save the vocabulary
        for st in split_options(commlines[4]):
            UserCategories[newcat].append(st)
            if st[0].islower():  # create capitalized version if needed
                UserCategories[newcat].append(st[0].upper() + st[1:])
#    print('MC1:',newcat, UserCategories[commlines[1]])

def make_link(commlines):
    """ checks that all variables are defined, then adds to LinkedFields """
    global LinkedFields
    vars = commlines[1].split()
    if len(vars) > 4:
        raise Exception('A link: command has more than the maximum of four destination fields')  # this is caught in do_command
    for vi in vars:
        if vi not in VarList:
            raise Exception('The destination field "' + vi + '" in a link: command has not been defined prior to the command') 
    if commlines[2] not in VarList:
            raise Exception('The source field "' + commlines[2] + '" in a link: command has not been defined prior to the command') 
    LinkedFields[commlines[2]] = vars

def make_checkbox(commlines):
    """ creates a checkbox entry """
    valuelist = split_options(commlines[4])
    CheckboxValues[commlines[2]] = []   # save values without marker
    for ele in valuelist:
        if ele[0] == '*':
            CheckboxValues[commlines[2]].append(ele[1:])
        else:
            CheckboxValues[commlines[2]].append(ele)
    if valuelist[1][0] == '*':
        return [commlines[2], 'checkbox', commlines[1], True]
    else:
        return [commlines[2], 'checkbox', commlines[1], False]

def make_textline(commlines, widthstr='24'):
    """ creates a text input entry """
    if 'width' in commlines[3]:
        widthstr = get_integer(commlines[3], 'width')
    return [commlines[2], 'textline', commlines[1], commlines[4], widthstr] 

def make_textsource(commlines, widthstr='24'):
    """ creates a source entry """
    if 'width' in commlines[3]:
        widthstr = get_integer(commlines[3], 'width')
    return [commlines[2], 'textsource', commlines[1], commlines[4], widthstr] 

def make_date(commlines):
    """ creates a date input entry: implementation delayed until such point that system is responding 
        plausibly to invalid field entries
    """
#    print('MD-1:',commlines)
    return [commlines[2], 'date', commlines[1]] 

def make_textclass(commlines, widthstr='24'):
    """ creates a text input entry attached to a category. The various errors are caught in do_command """
#    print('MTc-1:',commlines)
    optstr = commlines[3] + ' '
    if 'width' in commlines[3]:
        widthstr = get_integer(commlines[3], 'width')
    if 'category' in commlines[3]:  # this is required, so throw an error if it isn't here
        optstr = commlines[3] + ' '
        tarsta = optstr[optstr.index('category'):]
        check_for_equalchar(tarsta,'category')
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here
        classstr = tarst[:tarst.index(' ')]  # we added a terminal blank so this will always be okay
        if classstr not in ['nament','geogent','date','num']:  # this list should probably be a civet_settings global
            classstr = '=^=' + classstr + '=^='   # these will be replaced by termstNN
#        print('MTc-2:',classstr)
    else:
        raise Exception('','No "category" in ')
    return  [commlines[2], 'textclass', commlines[1], commlines[4], widthstr, classstr] 

def make_textarea(commlines):
    """ creates a text area entry """
    rowstr = '4'  # set the defaults
    colstr = '64'
    if 'rows' in commlines[3]:
        rowstr = get_integer(commlines[3], 'rows')
    if 'cols' in commlines[3]:
        colstr = get_integer(commlines[3], 'cols')
    return [commlines[2], 'textarea', commlines[1], commlines[4], rowstr, colstr] 

def make_select(commlines):
    """ creates a pull-down menu entry """
    choices = []
    init = ''
    for val in split_options(commlines[4]):
        if val[0] == '*':
            init = val[1:]
            choices.append((val[1:],val[1:]))
        else:
            choices.append((val,val))

    return [commlines[2], 'select', commlines[1], init, choices]

 
def make_dynselect(commlines):
    """ creates a dynamic pull-down menu entry """
    choices = []
    init = ''
    choices.append(('=*=DYN:' + commlines[4] + '=*=','---')) # placeholder which will be modified when a collection is read
    return [commlines[2], 'dynselect', commlines[1], init, choices]

 
def make_radio(commlines):
    """ creates a radio button entry; linebrks indicates whether a <br> will be added """
    if commlines[1][-1] == '/':
        linebrks = [True]
        commlines[1] = commlines[1][:-1]
    else:
        linebrks = [False]
    choices = []
    init = ''
    for val in split_options(commlines[4]):
        if val == '/':
            linebrks[-1] = True
        else:
            linebrks.append(False)
            if val[0] == '*':
                init = val[1:]
                choices.append((val[1:],val[1:]))
            else:
                choices.append((val,val))
    return [commlines[2], 'radio', commlines[1], init, choices, linebrks]


def make_discard(commlines):
    """ creates a discard entry: """
    return ['_discard_', 'checkbox', commlines[1], False]


def make_comments(commlines):
    """ creates a comment entry: """
    return make_textarea(['', commlines[1], '_comments_', commlines[3],''])


def make_text(commst, content):
    """ processes the h*, p commands, with linefeeds html escaping  """
    content = escape(content) + '<'  # assumes idx+1 reference won't cause error and we need it anyway
    strg = ''
    endx = 0
    idx = content.find('/')
    while idx >= 0:
        if content[idx+1] == '/':    # escaped //
            strg += content[endx:idx+1]
            endx = idx + 2
        else:
            strg += content[endx:idx] + '<br>'
            endx = idx + 1       
        idx = content.find('/',endx)
    strg += content[endx:]
    if commst[0] == 'h':
        return '<'+ commst + '>' + strg + '/' + commst + '>\n'
    else:
        return '<p>'+ strg + '/p>\n'

def make_header(commlines):
    """ processes the header command """
    global WorkspaceFileName, CollectionId, CollectionComments
    if len(commlines) < 2:
       return '~Error~<p>Missing text and field name in \"header: command <br>\n'  # <15.11.02> not sure this can even happen but better safe than sorry
    elif len(commlines) < 3:
       return '~Error~<p>Missing field name in \"header: ' + escape(commlines[1]) + '<br>\n'
    restr = ' '
    if commlines[2] == 'workspace':
        WorkspaceFileName = commlines[1] 
    elif commlines[2] == 'collection':
        CollectionId = commlines[1] 
    elif commlines[2] == 'comments':
        CollectionComments = commlines[1] 
    else:
       restr = '~Error~<p>' + commlines[2] + ' is not a valid field name in \"header: ' +\
              escape(commlines[1]) + ' [' + commlines[2] + ']\"<br>\n'
    return restr
        
def make_html(content):
    """ processes the html command, simply writing the text. If the global HTML_OK = False, just writes a comment  """
#    print('MH:',content)
    if civet_settings.HTML_OK:
        return '\n'.join(content)
    else:
        return '<!-- Requested HTML code not allowed -->\n'

def make_newline():
    """ processes newline command  """
    return '\n<br>\n'

def make_size(commlines):
    """ processes size command. Per the documentation, this does not throw errors when the
        division name or length specification is incorrect: these are just ignored. 
        The -size prefix is used to allows the size to be reset while effectively inheriting 
        the other style specification, getting CSS to act like it has object inheritance
        even though it doesn't. The civ-editor case is post-processed in make_editor_size()
    """
    if commlines[2] == 'body':
        cssst = '\nbody {\n'
    elif commlines[2] in ['civ-editor','civ-text-display','civ-form']:
        cssst = '\n.' + commlines[2] + '-size {\n'    
    else:
        return '' # could throw an error here but it is harmless to ignore it
    tarst = commlines[3].strip() + ';'
    tarst = tarst.replace('=',':')
    tarst = tarst.replace('wid','; wid')
    tarst = tarst.replace('hei','; hei')
    if 'width' in tarst:
        cssst += '    ' + tarst[tarst.index('width'): tarst.index(';',tarst.index('width'))+1] + '\n'
    if 'height' in tarst:
        cssst += '    ' + tarst[tarst.index('height'): tarst.index(';',tarst.index('height'))+1] + '\n'
#    print('msz:', cssst)
    return cssst + '}\n'
    
def set_editor_size(cssstr):
    """ sets EditorSize to the size in the CSS strg """
    global EditorSize
    strg = "CKEDITOR.config.width = '"
    part = cssstr.partition('hei')
    strg += part[0][part[0].index(':')+1:part[0].index(';')] + "';\nCKEDITOR.config.height = '"
    strg += part[2][part[2].index(':')+1:part[2].index(';')] + "';\n"
    print('MES:',strg)
    EditorSize = strg

def get_commlines(fin):
    """ reads a command; filters out comments and initial '+'; skips command on '-', returns list in commlines. 
        Standard content of commlines:
            0: name of the command
            1: title text for this command
            2: name of the variable
            3: options (often empty) 
        the remaining content is specific to each command and will be interpreted by those functions
        An empty list indicates EOF 
        Sort of bug <15.10.26>: The check "line[0] == '-' and ':' in line" would still fail on an entry line of the form 
            ---:Enter data here
        This has been documented but maybe to make it really robust we should check a list of actual commands.
        """
    commlines = []
    line = fin.readline() 
    while len(line) > 0:
#        print('GC1:',line)
        if len(line.strip()) == 0:
            if len(commlines) > 0:
                return commlines  # normal exit
            else:
                line = fin.readline()  # keep going since we've just got comments so far
                continue 
                
        if '#' in line:
            line = line[:line.index('#')]
            if len(line) == 0:
                line = fin.readline()
                continue 

        if  line[0] == '-' and ':' in line:  # cancel a command
            line = fin.readline() 
            while len(line.strip()) > 0:
                line = fin.readline()
            return ['-']
        commlines.append(line[:-1])
        line = fin.readline()
       
#    print('GC3: hit EOF')
    return commlines  # [] signals EOF 

def parse_command(commline):
    """ parses command line, returning a list containing [command, title, value, options, vallist]  """
#    print('PC1:',commline)
    theline = commline[0]
    if theline[0] == '+':
        theline = theline[1:]
    if theline.find(':') < 0:  
        return ['Error 1', theline]
    retlist = [theline[:theline.index(':')]]
    if retlist[0] in ['discard','comments']:
        st = theline[theline.index(':')+1:].strip()
        if '[' in st:
            st = st[:st.find('[')]
        retlist.append(st)
        retlist.append('_' + retlist[0] + '_')
        if ']' in theline:
            retlist.append(theline[theline.index(']')+1:])
        else:
            retlist.append('')
        return retlist        
    if retlist[0] in ['save', 'css', 'html']:
        if len(commline) > 1:
            if retlist[0] == 'save':
                retlist.append(commline[1])
            else:
                retlist.append(commline[1:])
            return retlist
        else:
            return []   # this triggers an error
    theline = theline[theline.index(':')+1:]
    theline = theline.replace('\[','~1~')
    theline = theline.replace('\]','~2~')
    if theline.find('[') < 0:  # simple command so done
        title = theline.strip().replace('~1~','[')
        title = title.replace('~2~',']')
        retlist.append(title)
        return retlist
    title = theline[:theline.index('[')].strip()  # title text
    if retlist[0] not in ['header']:
        title = escape(title) 
    title = title.replace('~1~','[')
    title = title.replace('~2~',']')
    retlist.append(title)
    theline = theline[theline.index('[')+1:]
    retlist.append(theline[:theline.index(']')].strip()) # var name
    if retlist[0] in ['link', 'constant']:
        return retlist
    retlist.append(theline[theline.index(']')+1:].strip()) # options
    if len(commline) > 1:
        retlist.append(commline[1])

    if retlist[0].startswith('//'):  # move line feeds to title field
        retlist[0] = retlist[0][2:]
        retlist[1] = '//' + retlist[1]
    elif retlist[0].startswith('/'):
        retlist[0] = retlist[0][1:]
        retlist[1] = '/' + retlist[1]
#    print('PC2:',retlist)
    return retlist

    
def do_command(commln):
    """ Calls various `make_*' routines, adds variables to VarList, forwards any errors from parse_command() """
    global VarList, SaveList, SaveTypes, FormCSS, FormFields
    if commln[0] == '-':
        return ''
    commlines = parse_command(commln)
#    print('DC1:',commlines)
    if len(commlines) == 0:
        return ''
    commst = commlines[0]
    if 'Error 1' in commst:
        outline = '~Error~<p>No ":" in command line:<br>'+escape(commlines[1])+'<br>\n'
        return outline
    outline = ''
    if commst[0] == 'h':
        if len(commst) == 2: # handles all of the <h*> commands
            outline = make_text(commst,commlines[1])
        elif commst == 'header':
            outline = make_header(commlines)
        elif commst == 'html':
            outline = make_html(commlines[1])
        else:
            outline = ''  # throw an error
    elif commst == 'p':
        outline = make_text(commst,commlines[1])
    elif commst == 'newline':
            outline = make_newline()   # just make this in-line....
    elif commst == 'newpage':
        outline = '~NewPage~'         
    elif commst == 'save':
        varlist = split_options(commlines[1])  # bad choice of local variable name here...
        if len(varlist) > 0:
#            print('DC2.1:',varlist)
            SaveList = []
            SaveTypes = [] 
            for st in varlist:
                if '[' in st:
                    parts = st.partition('[')
                    SaveList.append(parts[0].strip())
                    try:
                        parts[2].index(']')
                    except:
                        outline += '~Error~<p>Missing closing bracket in save: ' + commlines[1] + '<br>\n'
                else:
                    SaveList.append(st)
                SaveTypes.append(st)
        else:            
            outline += '~Error~<p>Missing variable list on the line following ' + commlines[0] + '<br>\n'
        outline += ' '  # show something was processed
#        print('DC2.2:',SaveList)
    elif commst == 'constant':
        ConstVarDict[commlines[2]] = commlines[1]
        VarList.append(commlines[2])
        outline = ' ' 
    elif commst == 'title':
        civet_settings.FORM_PAGETITLE = commlines[1]
        outline = ' ' 
    elif commst == 'filename':
        civet_settings.DEFAULT_FILENAME = commlines[1]
        outline = ' ' 
    elif commst == 'css':
        FormCSS += '\n'.join(commlines[1])
#        print('css:',FormCSS)
        outline = ' ' 
    elif commst == 'size':
        strg = make_size(commlines)
        if commlines[2] == 'civ-editor':
            set_editor_size(strg)
        else:
            FormCSS += strg
        outline = ' ' 
    elif commst == 'category':
        try:
            make_category(commlines)
            outline = ' ' 
        except Exception, e:
            outline = '~Error~<p>' + str(e) + '<br>\n'
    elif commst == 'link':
        try:
            make_link(commlines)
            outline = ' ' 
        except Exception, e:
            outline = '~Error~<p>' + str(e) + '<br>\n'

    if not outline:   # remaining commands specify variables 
        field = []
        try:
            if commst == 'radio':
                field = make_radio(commlines)
            elif commst == 'select':
                field = make_select(commlines)
            elif commst == 'dynselect':
                field = make_dynselect(commlines)
            elif commst == 'checkbox':
                field = make_checkbox(commlines)                
            elif commst == 'textline':
                field = make_textline(commlines)
            elif commst == 'textclass':
                field = make_textclass(commlines)
            elif commst == 'textsource':
                field = make_textsource(commlines)
            elif commst == 'textarea':
                field = make_textarea(commlines)
#           elif commst == 'date':
#                field = make_date(commlines) # not implemented in Version 1.0: see note in function 
            elif commst == 'discard':
                field = make_discard(commlines)
            elif commst == 'comments':
                field = make_comments(commlines)
        except IndexError: # missing line will usually be the cause here...I hope...
            outline = '~Error~<p>Second line is missing for the command "' + commln[0] + '"<br>\n'
        except Exception as e:
            outline = '~Error~<p>' + str(e[1]) + '"' + commln[0] + '"<br>\n'
            
        if field:
            if field[2].startswith('//'):  # process line feeds
                outline = '<p></p>'
                field[2] = field[2][2:]
            elif field[2].startswith('/'):
                outline = '<br>'
                field[2] = field[2][1:]
            else:
                outline = ''
            FormFields[field[0]] = field[1:]
            outline += '{==' + field[0] + '==}' 

        if outline:  # record variable name
            VarList.append(commlines[2])
        else:
            outline = '~Error~<p>Command "' + commst + '" not implemented.<br>\n'
#    print('DC2:',outline)
    return outline


def radio_format(djst, linebrks):
    """ converts the forms.ChoiceField  <ul> list to in-line with <br> determined by linebrks """
#    print('CFI0:',djst, linebrks)
    idx = djst.find('<ul')
    radst = djst[:idx]
    if linebrks[0]:
        radst += '<br>'        
    idx = djst.find('<li>')
    ka = 0
    while idx > 0:  # ReGex would also work here but this is easy enough
        endx = djst.find('</li>',idx)
        radst += djst[idx + 4: endx]
        ka += 1
        if linebrks[ka]:
            radst += '<br>'
        idx = djst.find('<li>',endx)
#    print('CFI:',radst)
    return radst   

def get_current_form(pageindex):
    """ Create the form HTML for pageindex. This is effectively a template inside a template, replacing the {==<var_id>==} 
        tokens with the corresponding widget HTML, sometimes modified. 
    """
    formstrg = FormContent[pageindex]
    form = CodingForm(fields = FormFields)
#                                   get the variables that are used in this form
#    curvars = ['deletelist']  
    curvars = []  
    alist = formstrg.split('{==')
    for st in alist[1:]:
        curvars.append(st[:st.find('==}')]) 
#    print('IFF0:',curvars)
#    print('IFF:',form.as_p())
#    print('IFF1:',FormFields)
#                                   get the widgets that are used in this form
    fielddict = {} 
    for strg in form.as_p().split('</p>\n'):  # still need to get rid of terminal </p>, though it appears harmless
        for fld in curvars:
            if 'id_' + fld + '"' in strg:           # ids generated by Django have the format 'id_'+<name>
                if FormFields[fld][0] == 'radio':
                    fielddict[fld] = radio_format(strg,FormFields[fld][4] )
                elif FormFields[fld][0] == 'textarea':
                    parts = strg[3:].partition('</label> ')
                    fielddict[fld] = parts[0] + '</label><br>' + parts[2]
                elif FormFields[fld][0] == 'textclass':
                    fielddict[fld] = strg[3:].replace('&#39;',"'").replace('id="id_','id="')  # switch from Django to CIVET id style
                elif FormFields[fld][0] == 'textsource':
                    fielddict[fld] = strg[3:].replace('id="id_','id="')  # switch from Django to CIVET id style
#                    print('========GCF Mk1: ', fld, fielddict[fld] )
                else:
                    fielddict[fld] = strg[3:]
                break
#                                    do the substitutions            
    idx = formstrg.find('{==')
    while idx >=0:
        endx = formstrg.find('==}',idx) 
        fld = formstrg[idx+3:endx]
        formstrg = formstrg[:idx] + fielddict[fld] + formstrg[endx+3:]
        idx = formstrg.find('{==')
    return formstrg, curvars


def init_template():
    global VarList, SaveList, UserCategories, FormContent, FormCSS, EditorSize, FormFields
    VarList = []
    VarList.extend(SpecialVarList) 
    VarList.extend(MetaVarList) 
    SaveList = []  
    SaveTypes = []  
    UserCategories = {}
    FormContent = ['']
#    FormFields = {'deletelist': ['hidden','','']}       
    FormFields = {}       
    FormCSS = '' 
    EditorSize = '' # size for CKEditor      


def read_template(fin):
    """ reads a template (or the error strings from same) from the file handle fin into civet_form.FormContent """
    global FormContent
    init_template()
    thecontent = ''
    commln = get_commlines(fin)
    while len(commln) > 0:
        thecontent += do_command(commln)
        commln = get_commlines(fin)
        
#    print('thecontent:',thecontent)
    if len(SaveList) == 0:
        thecontent += '~Error~<p>A "save:" command is required in the template<br>\n'
    else:
#        print('RT1:',SaveList)
#        print('RT2:',VarList)
        misslist = []
        for ele in SaveList:
            if ele not in VarList:
                misslist.append(ele)
        if len(misslist) > 0:
            thecontent += '~Error~<p>The following variables are in the "save:" command but were not declared in a data field<br>' + str(misslist) + '\n'

    if '~Error~' in thecontent:
        errortext = '&Errors:'
        indx = thecontent.find('~Error~')
        while indx >= 0:
            indy = thecontent.find('\n',indx)
            errortext += thecontent[indx+7:indy+1]
            indx = thecontent.find('~Error~',indy)
        thecontent = errortext
        
    if '~NewPage~' in thecontent:
        FormContent = thecontent.split('~NewPage~') 
    else:    
        FormContent[0] = thecontent
            
#  ================  Data saving  ================

def delete_texts(active_collection, deletelist):
    """ for each text in deletelist, sets the textdelete to true, generates a delete case """
    print('DT1:',deletelist)
    for txt in deletelist.split(' '):
#        print('DT1.5:',txt)
        save_newcase(active_collection, '', '', {'_delete_' : True, '_textid_' : txt})
        txtrec = Text.objects.get(textid__exact=txt)
#        print('DT2-2:',txtrec.textid, txtrec.textlede, txtrec.textdelete)
        txtrec.textdelete = True
        txtrec.save(update_fields=['textdelete'])


def get_data():
    """ get the values from FormFields """
    vals = {}
    for key, val in FormFields.iteritems():
        vals[key] = val[2]
    return vals
    
def save_newcase(active_collection, case_id, cmtstr, valdict):
    """ save or replaces case """
    if len(case_id) == 0:
        maxser = '000'
        for ct in Case.objects.filter(caseparent__exact=active_collection):
            if ct.caseid > maxser:
                maxser = ct.caseid
        theser = '{:03d}'.format(int(maxser)+1)
    else:
        theser = case_id

    # convert valdict to a string: in fact we could probably skip making the dictionary first but at one point it was stored as such
    valst = "{"
    for key in valdict:
        st = str(valdict[key]).replace("'","\\'")  # str converts any Booleans
        valst += "'" + key + "': '" + st + "', "
    valst += '}'
    newcase = Case.objects.create_case(
        caseparent = active_collection,
        caseid = theser,
        casedate = datetime.datetime.now().isoformat(),
        casecoder = CoderName,  
        casecmt = cmtstr,
        casevalues = valst,
        )
    newcase.save()


def save_case(active_collection, deletelist, case_id = ''):
    """ saves (case_id empty) or replaces case for active_collection """
    vals = get_data()
    if deletelist:
        delete_texts(active_collection, deletelist.strip())
    valdict = {}
#    print('SC-1',vals, active_collection)
#    print('SC-1.1',FormFields)
    if '_discard_' in vals and vals['_discard_']:
        valdict['_discard_'] = True
    else:
        for avar in SaveList: 
#            print('STT2:',avar)
            if avar in SpecialVarList: 
                valdict[avar] =  get_special_var(avar)
            elif avar in MetaVarList: 
                valdict[avar] =  get_text_metadata(avar, active_collection)
            elif avar in ConstVarDict.keys(): 
                valdict[avar] =  ConstVarDict[avar]
            elif avar in vals:
                valdict[avar] = vals[avar]

    if '_comments_' in vals:
        cmtstr = vals['_comments_']
    else:
        cmtstr = ''

    save_newcase(active_collection, case_id, cmtstr, valdict)
        

def save_to_TempData():
    """ adds the variables from the basic.html form to the TempData string  """
    global TempData
    vals = get_data()
    for avar in SaveList: 
#        print('STT2:',avar)
        if avar in SpecialVarList: 
            TempData += get_special_var(avar) + '\t'
        elif avar in ConstVarDict.keys(): 
            TempData += ConstVarDict[avar] + '\t'
        elif avar in vals:
            TempData += str(vals[avar]) + '\t'
#        print('STT3:',avar,str(vals[avar]))

    TempData = TempData[:-1] + '\n'

def create_TempData_header():
    """ initializes TempData, writing the variable name header from the basic.html form to the TempData string  """
    global TempData
    TempData = ''
    for avar in SaveList:  # write the header
        TempData += avar+'\t'
    TempData = TempData[:-1] + '\n'

def add_dynselect(newform, active_collection):
    """ adds the current dynamic categories to the dynselect fields """
    thecoll = Collection.objects.get(collid__exact=active_collection)
#    print('AD-0',thecoll.collcat) 
    catdict = json.loads(thecoll.collcat)   
    curloc = 0
#    print('AD-1',newform[:64], active_collection)
    while newform.find('=*=DYN:',curloc) > 0:
        curloc = newform.find('=*=DYN:',curloc)
#        print('AD-2',curloc, newform[curloc:curloc+24])
        brk1 = newform.find('<option ',curloc - 16)
        brk2 = newform.find('</option>',curloc) + 9
#        print('AD-2',curloc, brk1, brk2, newform[curloc:curloc+24])
        instrg = ''
        catstrg = newform[curloc + 7:newform.index('=*=',curloc + 7)]
        if catstrg not in catdict:
            instrg += '<option value="---">---</option>\n'
        else:
            for optstrg in catdict[catstrg]:
                if optstrg[0] == '*':
                    instrg += '<option value="' + optstrg[1:] + '" selected >' + optstrg[1:] + '</option>\n'
                else:
                    instrg += '<option value="' + optstrg + '">' + optstrg + '</option>\n'
#        print('AD-3',instrg)
        newform = newform[:brk1] + instrg + newform[brk2:]
#        print('AD-4',newform[curloc-16:curloc+16])
    return newform

def make_map_info(active_collection):
    """ generates Google maps calls for countries which have more than one location, adds to CategoryDict """
    thecoll = Collection.objects.get(collid__exact=active_collection)
    if not thecoll.collcat:
        return ''
    catdict = json.loads(thecoll.collcat)   
    if 'loccat' not in catdict:
        return '' 
    gotlst = []
    allmaps = ''           
    for la in catdict['loccat']:
        targ = la[la.index('['):la.index('[')+5]
        if targ in gotlst:
            continue
        ct = sum([1 if targ in lb else 0 for lb in catdict['loccat']]) # Pythonic or what! And worked the first time!
        if ct > 1:
            gotlst.append(targ)
#            print('==++',targ)
            mapstrg = '<h2>Map of locations in ' + targ[1:-1] + '</h2><p><img alt="' + targ[1:-1] + \
                      ' map" src="https://maps.googleapis.com/maps/api/staticmap?size=400x400&maptype=roadmap' 
            ka = 0
            for li in catdict['loccat']:
                if targ in li:
                    mapstrg += '&markers=color:red%7Clabel:' + chr(65+ka) + '%7C' + li[li.index('(') + 1:li.index(')')]
                    ka += 1
            mapstrg += '&key=' + civet_settings.MAP_KEY + '"> '
            allmaps += mapstrg
            
    return allmaps
                
        