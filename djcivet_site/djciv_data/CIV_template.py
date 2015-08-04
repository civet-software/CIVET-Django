##	CIVET.templates.py
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
##				http://eventdata.parusanalytics.com
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
##	14-March-15:	Initial version
##
##	----------------------------------------------------------------------------------

from __future__ import print_function
import datetime
import time
import sys

from .models import Collection, Text, Case


# ======== global initializations ========= #

_html_escapes = { #'&': '&amp;',   # this allows entities
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&rsquo;'}

# Escape every ASCII character with a value less than 32. 
_html_escapes.update(('%c' % z, '\\u%04X' % z) for z in xrange(32))

HTML_OK = True   # allow html: command?
#HTML_OK = False

SaveList = []   # variables to write 
SaveTypes = []   # full variable string with optional label for values 
SpecialVarList = ['_coder_', '_date_', '_time_']
VarList = []    # variables which have entry boxes
TempData = ''   # output string for form-only mode
UncheckedValues = {}  # values to output for unchecked checkboxes
CoderName = '---' 
ConstVarDict = {}  # holds the variables set by constant:
DefaultFileName = 'civet.output.txt'  # holds the value set by filename:
UserCategories = {} # holds user categories as list [color, vocabulary...]
CategoryCodes = {} # dictionary of dictionaries for category codes, if these are present
FormContent = ''  # html for the coding form

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


# ============ function definitions ================ #

"""def imalive(): # debugging
    print('Hello from CIV_template')"""
    
def escapehtml_filter(value):
    """ Nice little filter I modified slightly from the code in 
    http://stackoverflow.com/questions/12339806/escape-strings-for-javascript-using-jinja2 
    jinja2 apparently has a more robust function for this. """
    retval = []
    for letter in value:
            if _html_escapes.has_key(letter):
                    retval.append(_html_escapes[letter])
            else:
                    retval.append(letter)

    return "".join(retval)

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
        return time.strftime("%d-%b-%Y")
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
    
    
def read_codes_file(fin, filename):
    """ reads the codes.file fin and stores results in CategoryCodes """ 
    global CategoryCodes           
    newcat = filename[filename.index('codes.')+6:].partition('.')[0]  # category name follows 'codes.' in filename
    CategoryCodes[newcat] = {}
    line = fin.readline() 
    while len(line) > 0:
#        print('GC1:',line)
        if not line.startswith('#'):
            [vocab, capvocab, code] = parse_codes(line)
            CategoryCodes[newcat][vocab] = code
            if len(capvocab) > 0:
                CategoryCodes[newcat][capvocab] = code               
        line = fin.readline()
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


def make_checkbox(commlines):
    """ creates a checkbox entry: """
    global UncheckedValues
    valuelist = split_options(commlines[4])
#    contrstr = '\n' + commlines[1] + '<input name = "' + commlines[2] + '" type="hidden" value="' + valuelist[0] + '">\n' # seems this old trick won't work at least on the GAE Flask
    UncheckedValues[commlines[2]] =  valuelist[0]
    contrstr = '\n' + commlines[1] +'<input name = "' + commlines[2] + '" type="checkbox" value="'
    if valuelist[1][0] == '*':
        contrstr +=  valuelist[1][1:] + '" checked="checked" >\n'
    else:
        contrstr +=  valuelist[1] + '">\n'
    return contrstr 

def make_textline(commlines, widthstr='24'):
    """ creates a text input entry """
    widthstr = '24'  # not needed, right?
    optstr = commlines[3] + ' '
    if 'width' in optstr:
        tarsta = optstr[optstr.index('width'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here
        widthstr = tarst[:tarst.index(' ')]  # check if this is an integer
    return '\n' + commlines[1] + '<input name = "' + commlines[2] + '" type="text" value="' + commlines[4] + '" size = ' + widthstr + '>\n'

def make_textclass(commlines, widthstr='24'):
    """ creates a text input entry attached to a category """
    widthstr = '24'  # not needed, right?
#    print('MTc-1:',commlines)
    optstr = commlines[3] + ' '
    if 'width' in optstr:
        tarsta = optstr[optstr.index('width'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here; also if no embedded blanks we don't need the lstrip
        widthstr = tarst[:tarst.index(' ')]  # check if this is an integer
    if 'category' in optstr:  # this is required, so throw an error if it isn't here
        tarsta = optstr[optstr.index('category'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here
        classstr = tarst[:tarst.index(' ')] 
        if classstr not in ['nament','date','num']:
            classstr = '=^=' + classstr + '=^='   # these will be replaced by termstNN
#        print('MTc-2:',classstr)
    return '\n' + commlines[1] + '<input name = "' + commlines[2] + '" id = "' + commlines[2] + '" type="text" value="' + commlines[4] + \
           '" size = ' + widthstr + ' onfocus="coloraclass(\'' + classstr + '\', \'' + commlines[2] + '\')" ' +\
           ' onblur="cancelclass()">\n'

def make_textarea(commlines):
    """ creates a text area entry """
    rowstr = '4'  # set the defaults
    colstr = '64'
    optstr = commlines[3] + ' '
    if 'rows' in optstr:
        tarsta = optstr[optstr.index('rows'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here
#        print('MT1',tarst)
        rowstr = tarst[:tarst.index(' ')]  # check if this is an integer
    if 'cols' in optstr:
        tarsta = optstr[optstr.index('cols'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here
#        print('MT2',optstr[optstr.index('cols'):])
#        print('MT4',tarst)
        colstr = tarst[:tarst.index(' ')]  # check if this is an integer
        
    return '\n' + commlines[1] + '<BR><TEXTAREA name = "' + commlines[2] + '" rows ="' + rowstr + '" cols = ' + colstr + '>' + commlines[4] + '</TEXTAREA>\n'

def make_select(commlines):
    """ creates a pull-down menu entry """
    title = commlines[1]
    valuelist = split_options(commlines[4])
    contrstr = commlines[1] + '\n<select name = "' + commlines[2] + '">\n'
    for val in valuelist:
        if val[0] == '*':
            contrstr += '<option value="' + val[1:] + '" selected = "selected">' + val[1:] + '</option>\n'
        else:
            contrstr += '<option value="' + val + '">' + val + '</option>\n'
    contrstr += '</select>\n\n'
    return contrstr 

def make_radio(commlines):
    """ creates a radio button entry """
    title = commlines[1]
    valuelist = split_options(commlines[4])
    if title[-1] == '/':
        contrstr = title[:-1] + '<br>\n'
    else:
        contrstr = title + '\n'        
    for val in valuelist:
        if val == '/':
            contrstr += '<br>\n'
        else:
            contrstr += '<input type="radio" name="' + commlines[2] + '"'
            if val[0] == '*':
                contrstr += ' value="' + val[1:] + '" checked>' + val[1:] + '\n'
            else:
                contrstr += ' value="' + val + '">' + val +'\n'
    contrstr += '\n'
    return contrstr 

def make_text(commst, content):
    """ processes the h*, p commands. In a Flask implementation, there is probably a better way to escape the html  """
    if commst[0] == 'h':
        return '<'+ commst + '>' + escapehtml_filter(content) + '</'+ commst + '>\n'
    else:
        return '<p>'+ escapehtml_filter(content) + '</p>\n'

def make_html(content):
    """ processes the html command, simply writing the text. If the global HTML_OK = False, just writes a comment  """
    if HTML_OK:
        return content + '\n'
    else:
        return '<!-- Requested HTML code not allowed -->\n'

def make_newline():
    """ processes newline command  """
    return '\n<br>\n'

def get_commlines(fin):
    """ reads a command; filters out comments and initial '+'; skips command on '-', returns list in commlines. 
        Standard content of commlines:
            0: name of the command
            1: title text for this command
            2: name of the variable
            3: options (often empty) 
        the remaining content is specific to each command and will be interpreted by those functions
        An empty list indicates EOF """
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

        if  line[0] == '-':  # cancel a command
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
    if retlist[0] == 'save':
        if len(commline) > 1:
            retlist.append(commline[1])
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
    title = escapehtml_filter(theline[:theline.index('[')].strip())  # title text
    title = title.replace('~1~','[')
    title = title.replace('~2~',']')
    retlist.append(title)
    theline = theline[theline.index('[')+1:]
    retlist.append(theline[:theline.index(']')].strip()) # var name
    if retlist[0] == 'constant':
        return retlist
    retlist.append(theline[theline.index(']')+1:].strip()) # options
    retlist.append(commline[1])
    return retlist
    
def do_command(commln):
    """ Calls various `make_*' routines, adds variables to VarList, forwards any errors from parse_command() """
    global VarList, SaveList, SaveTypes, DefaultFileName
    if commln[0] == '-':
        return ''
    commlines = parse_command(commln)
#    print('DC1:',commlines)
    if len(commlines) == 0:
        return ''
    commst = commlines[0]
    if 'Error 1' in commst:
        outline = '~Error~<p>No ":" in command line:<br>'+escapehtml_filter(commlines[1])+'<br>\n'
        return outline
    outline = ''
    if commst[0] == 'h':
        if len(commst) == 2:
            outline = make_text(commst,commlines[1])
        else:
            outline = make_html(commlines[1])
    elif commst == 'p':
        outline = make_text(commst,commlines[1])
    elif commst == 'newline':
            outline = make_newline()   # just make this in-line....
    elif commst == 'save':
        varlist = split_options(commlines[1])
        if len(varlist) > 0:
    #        print('DC2.1:',varlist)
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
#        print('SV:',SaveList)
    elif commst == 'constant':
        ConstVarDict[commlines[2]] = commlines[1]
        VarList.append(commlines[2])
        outline = ' ' 
    elif commst == 'filename':
        DefaultFileName = commlines[1]
        outline = ' ' 
    elif commst == 'category':
        try:
            make_category(commlines)
            outline = ' ' 
        except Exception, e:
            outline = '~Error~<p>' + str(e) + '<br>\n'

    if len(outline) == 0:   # remaining commands specify variables 
        if commst == 'radio':
            outline = make_radio(commlines)
        elif commst == 'select':
            outline = make_select(commlines)
        elif commst == 'checkbox':
            outline = make_checkbox(commlines)
        elif commst == 'textline':
            outline = make_textline(commlines)
        elif commst == 'textclass':
            outline = make_textclass(commlines)
        elif commst == 'textarea':
            outline = make_textarea(commlines)
        if len(outline) > 0:  # record variable name
            VarList.append(commlines[2])
        else:
            outline = '~Error~<p>Command "' + commst + '" not implemented.<br>\n'
    return outline

def init_template():
    global VarList, SaveList, UserCategories, codename, FormContent
    VarList = []
    VarList.extend(SpecialVarList) 
    SaveList = []  
    SaveTypes = []  
    CoderName = '---' 
    UserCategories = {}
    FormContent = ''       

#  ================  Data saving  ================

def save_case(request, active_collection, case_id = ''):
    """ saves (case_id empty) or replaces case for active_collection """
    valdict = {}
#    print('SC-1',SaveList, active_collection)
    for avar in SaveList: 
#        print('STT2:',avar)
        if avar in SpecialVarList: 
            valdict[avar] =  get_special_var(avar)
        elif avar in ConstVarDict.keys(): 
            valdict[avar] =  ConstVarDict[avar]
        elif avar in request.POST:
            valdict[avar] =  request.POST[avar]
        else:
            valdict[avar] =  UncheckedValues[avar]

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
        st = valdict[key].replace("'","\\'")
        valst += "'" + key + "': '" + st + "', "
    valst += '}'
    newcase = Case.objects.create_case(
        caseparent = active_collection,
        caseid = theser,
        casedate = datetime.datetime.now(),
        casecoder = CoderName,  
        casecmt = '',
        casevalues = valst,
        )
    newcase.save()

def save_to_TempData(request):
    """ adds the variables from the basic.html form to the TempData string  """
    global TempData
    for avar in SaveList: 
#        print('STT2:',avar)
        if avar in SpecialVarList: 
            TempData += get_special_var(avar) + '\t'
        elif avar in ConstVarDict.keys(): 
            TempData += ConstVarDict[avar] + '\t'
        elif avar in request.POST:
            TempData += request.POST[avar]+'\t'
        else:
            TempData += UncheckedValues[avar] + '\t'
    TempData = TempData[:-1] + '\n'

def create_TempData_header():
    """ initializes TempData, writing the variable name header from the basic.html form to the TempData string  """
    global TempData
    TempData = ''
    for avar in SaveList:  # write the header
        TempData += avar+'\t'
    TempData = TempData[:-1] + '\n'

   