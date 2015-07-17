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

#class DupError(Exception):
#	pass

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
SpecialVarList = ['_coder_', '_date_', '_time_']
VarList = []    # variables which have entry boxes
TempData = ''   # output string for BasicMode
UncheckedValues = {}  # values to output for unchecked checkboxes
codername = '---' 
ConstVarDict = {}  # holds the variables set by constant:
DefaultFileName = 'civet.output.txt'  # holds the value set by filename:

BasicMode = True   # system is working with a simple template rather than CMS and annotation: this invokes a simpler download routine

# ============ function definitions ================ #

def set_SaveList():
# debugging function
    global SaveList
    SaveList = "_date_, typeincid, natincid, authreport, location, injuries, descrp".split(', ')

def imalive(): # debugging
    print('Hello from CIV_template')
    
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
        return codername
    elif avar == '_date_':
        return time.strftime("%d-%b-%Y")
    elif avar == '_time_':
        return time.strftime("%H:%M:%S")
    else: # shouldn't hit this
        return '---'
    

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
    """ creates a text input entry """
    widthstr = '24'  # not needed, right?
#    print('MTc-1:',commlines)
    optstr = commlines[3] + ' '
    if 'width' in optstr:
        tarsta = optstr[optstr.index('width'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here; also if no embedded blanks we don't need the lstrip
        widthstr = tarst[:tarst.index(' ')]  # check if this is an integer
    if 'class' in optstr:  # this is required, so throw an error if it isn't here
        tarsta = optstr[optstr.index('class'):]
        tarst = tarsta[tarsta.index('=')+1:].lstrip()  # need to catch error here
        classstr = tarst[:tarst.index(' ')] 
        if classstr not in ['nament','date','num']:
            classstr = '=^=' + classstr + '=^='   # these will be replaced by termstNN
#        print('MTc-2:',classstr)
    return '\n' + commlines[1] + '<input name = "' + commlines[2] + '" id = "' + commlines[2] + '" type="text" value="' + commlines[4] + \
           '" size = ' + widthstr + ' onfocus="coloraclass(\'' + classstr + '\', \'' + commlines[2] + '\')">\n'
#<input type="text" name="NE1" id="NE1" value="" onfocus="coloraclass('nament', 'NE1')">

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
            1: text that precedes the command and 
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
    global VarList, SaveList, DefaultFileName
    commlines = parse_command(commln)
#    print('DC1:',commlines)
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
        SaveList = split_options(commlines[1])
        outline = ' '  # show something was processed
#        print('SV:',SaveList)
    elif commst == 'constant':
        ConstVarDict[commlines[2]] = commlines[1]
        VarList.append(commlines[2])
        outline = ' ' 
    elif commst == 'filename':
        DefaultFileName = commlines[1]
        outline = ' ' 
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
    global VarList, SaveList
    VarList = []
    VarList.extend(SpecialVarList) 
    SaveList = []  
    codername = '---'        

#  ================  Data saving  ================

def save_case(request, active_collection, case_id = ''):
    """ saves (case_id empty) or replaces case for active_collection """
    valdict = {}
    print('SC-1',SaveList, active_collection)
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
        
    newcase = Case.objects.create_case(
            caseparent = active_collection,
            caseid = theser,
            casedate = datetime.datetime.now(),
            casecoder = '',  # fill this in later
            casecmt = '',
            casevaluedict = valdict,
            )
    newcase.save()
    print('SC-2: ' + theser + '\n',valdict)

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

   