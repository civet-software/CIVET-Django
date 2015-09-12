##	views.py
##
##  Django 'views.py' file for CIVET system
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
##	14-March-15:	Initial version
##  4-August-15:    Beta 0.7
##  31-August-15:   Beta 0.9
##
##	----------------------------------------------------------------------------------

from __future__ import print_function

from django.core.servers.basehttp import FileWrapper
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File
from django.conf import settings
from django import forms

from .models import Collection, Text, Case
from .forms import PrefsForm, CodingForm 

from copy import deepcopy
import datetime
import shutil
import zipfile
import StringIO
import os
import ast

import civet_utilities
import civet_settings
import civet_form	


# ======== global initializations ========= #

# Global variables that are set during a session are 'CamelCase'

ActiveCollection = ''
CollectionList = []  # list of available collections in workspace 

WorkspaceName = ''
CurCollectionIndex = 0  # CollectionList index of most recently coded collection  
SaveFiles = {}  # contents of files other than .yml indexed by the file name

CKEditor_Styles = ''  # default and category styles for CKEditor

PageIndex = 0
InitalFormVals = {}   # copy of FormFields with the initial values
HeaderInfo = {}  # information for document header
CurVars = []
Deletelist = ''
CoderText = ''  # text block in coder
TermStyles = '' # term styles in coder

# ================ static file utilities ================= #

def online_manual(request):
    """ Goes to index.html of on-line docs """
    return HttpResponseRedirect(civet_settings.ONLINE_DOCS_URL)
        
def download_pdfdocs(request):
    """ downloads the main documentation or redirects if it can't be found """
#    print('DPD: entry')
    if os.path.isfile('docs/_build/latex/civetdoc.pdf'):  # leave this path hard-coded for the time being
#        print('DPD: docs download')
        f = open('docs/_build/latex/civetdoc.pdf', "r")
    elif os.path.isfile(civet_settings.STATIC_FILE_PATH + civet_settings.DOCUMENTATION):
#        print('DPD: STATIC_FILE_PATH download')
        f = open(civet_settings.STATIC_FILE_PATH + civet_settings.DOCUMENTATION, "r")
    else:
#        print('DPD: remote download')
        return HttpResponseRedirect(civet_settings.PDF_DOC_URL)
    response = HttpResponse(FileWrapper(f), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=CIVET.Documentation.pdf'
    f.close()
    return response

def download_demotemplate(request):
    """ downloads the demo template """
    f = open(civet_settings.STATIC_FILE_PATH + civet_settings.DEMO_TEMPLATE, "r")
    response = HttpResponse(FileWrapper(f), content_type='text/plain')
    response ['Content-Disposition'] = 'attachment; filename=CIVET.demo.template.txt'
    f.close()
    return response

def download_demo_workspace(request):
    """ downloads the demo template """
    f = open(civet_settings.STATIC_FILE_PATH + civet_settings.DEMO_WORKSPACE, "r")
    response = HttpResponse(FileWrapper(f), content_type='application/x-zip-compressed')
    response ['Content-Disposition'] = 'attachment; filename=CIVET.workspace.demo.zip'
    f.close()
    return response


# ================ authentication ================= #

def civet_gateway(request):
    """ Goes to login or home page depending on value of civet_settings.REQUIRE_LOGIN"""
#    print("At gateway")
    logout(request)
    if civet_settings.REQUIRE_LOGIN:
        return HttpResponseRedirect('/login')    
    else:
        return HttpResponseRedirect('/djciv_data/home')    
        
def index(request):
    """ home page """    
    if civet_settings.REQUIRE_LOGIN and not request.user.is_authenticated(): # this is used instead of a decorator to allow checking REQUIRE_LOGIN
        return HttpResponse("You must be logged in to access this page.") 

#    print('BASE_DIR:',settings.BASE_DIR)
#    print('STATIC_URL:',settings.STATIC_URL)
    return render(request, 'djciv_data/index.html',
        {'staticpath':civet_settings.STATIC_SOURCE,
         'login':civet_settings.REQUIRE_LOGIN }
    )

def handle_logout(request):
    logout(request)
    return render(request,'djciv_data/civet_logout.html',{})
        
def preferences(request):
    # there's a slightly different and currently more popular idiomatic way to do this now: substitute it at some point
    if request.method == 'POST': # If the form has been submitted...
        form = PrefsForm(request.POST) 
        if form.is_valid(): 
#            print('PREFS:',form.cleaned_data)
            civet_settings.set_preferences(form.cleaned_data)
            return HttpResponseRedirect('/djciv_data/home') 
    else:
        form = PrefsForm(initial = civet_settings.get_preferences()) 

    return render(request, 'djciv_data/preferences.html', {'form': form})


# ================ editor system ================= #

# General comment re: development: This started out with CKEditor and the coder sharing the same text format.
# As things have developed, the environment in CKEditor has sufficient differences from a standard HTML
# environment that it makes more sense to have pre-processing for these done by different routines.


def make_ckeditor_markup_string(theinfo, index):
    """ create a markup string containing from information from [textid, textlede, textdate, textcmt, textcontent] by adding 
        the <div>s and toggle controls 
    """
    ledest = '<div class = "textlede" textid = "' + theinfo[0] + '" style = "' + civet_settings.EDITOR_LEDE_STYLE + \
            '">' + civet_settings.EDITOR_LEDE_LABEL + theinfo[1] + '</div> '
    datest = '<div class = "textdate" style = "' + civet_settings.EDITOR_CONT_STYLE + \
            '">' + civet_settings.EDITOR_DATE_LABEL + theinfo[2] + '</div> '
    commst = '<div class = "textcomm" style = "' + civet_settings.EDITOR_CONT_STYLE + \
            '">' + civet_settings.EDITOR_COMM_LABEL + theinfo[3] + '&rdquo;</div> '
    contst = '<div class = "textcontent" style = "' + civet_settings.EDITOR_CONT_STYLE + \
            '">' + civet_settings.EDITOR_CONTENT_LABEL + theinfo[4] + '</div> '
    return ledest + datest + commst + contst       


def get_CKEditor_context(mkst = ''):
    """ sets context for calls to civet_ckeditor.html """
    context = {}
    context['current_collection'] = ActiveCollection        
    if mkst:
        context['thetext'] = mkst
    else:
        context['thetext'] = get_editor_markup()
    context['the_styles'] = CKEditor_Styles
    context['staticpath'] = civet_settings.STATIC_SOURCE
    if civet_form.EditorSize:
        context['editor_size'] = civet_form.EditorSize
    return context

def get_editor_markup():
    """ return a string containing all of the textmkup fields from ActiveCollection """
    curtexts = Text.objects.filter(textparent__exact=ActiveCollection)
    stx = ''
    for ka, ct in enumerate(curtexts):
#        print('GEM-Mk2:',ct.textmkup)
        temp = ct.get_text_fields()
#        print('GEM-Mk3:',temp)
        if civet_settings.ALWAYS_ANNOTATE and 'class:nament' not in temp[4]:  # a robust, if not quite guaranteed, telltale that there has been no markup
            temp[1] = civet_utilities.do_markup(temp[1])
            temp[4] = civet_utilities.do_markup(temp[4])
        stx += make_ckeditor_markup_string(temp,ka)
    return stx


def edit_collection(request):
    """ sets context and calls civet_ckeditor.html """
    global ActiveCollection
#    print('ED-Mk1:',request.POST['current_collection'])
    ActiveCollection = request.POST['current_collection']
    context = get_CKEditor_context()    
    if len(context['thetext']) > 0:
#    print('EC1:',civet_form.FormContent)
        return render(request,'djciv_data/civet_ckeditor.html',context)
    else:
        return HttpResponse("No collection was selected: use the back key to return to the collection selection page.")
        

def get_editor_blocks(thestring):
    """ return dictionary of text blocks keyed by textid, and containing [textlede, textdate, textcomm, textcontent] """
    curdiv = thestring.find('<div')
    textblock = {}
    textid = ''
    while curdiv >= 0:
        endtag = thestring.find('>',curdiv)
        attr = civet_utilities.get_attributes(thestring[curdiv:endtag])
        enddiv = thestring.find('</div>',endtag+1)
        content = thestring[endtag+1:enddiv]
        if attr['class'] =='textlede':
            textid = attr['textid']
            textblock[textid] = [content[len(civet_settings.EDITOR_LEDE_LABEL):]]
        elif attr['class'] == 'textdate':
            textblock[textid].append(content[len(civet_settings.EDITOR_DATE_LABEL):])
        elif attr['class'] == 'textcomm':
            textblock[textid].append(content[len(civet_settings.EDITOR_COMM_LABEL)+1:-len('&rdquo;')])  # don't copy the quotes
        elif attr['class'] == 'textcontent':
            textblock[textid].append(content[len(civet_settings.EDITOR_CONTENT_LABEL):])            
        curdiv = thestring.find('<div',endtag+1)

#    print('GEB:',textblock)
    return textblock
    
def save_edits(request):
    """ saves current markup to the DB """
#    print('SE-Mk0:')
    thestring = request.POST['civ_editor']
    textblock = get_editor_blocks(thestring)
    for st in textblock:
#        print('\nID:',st,'\nLede:',textblock[st][0],'\nContent:',textblock[st][1])
        curtext = Text.objects.get(textid__exact=st)
        curtext.textlede = textblock[st][0]
        curtext.textdate = textblock[st][1]
        curtext.textcmt = textblock[st][2]
        curtext.textmkup = textblock[st][3]
        curtext.textmkupdate = datetime.datetime.now()
        curtext.textmkupcoder = civet_form.CoderName
        curtext.save()
 

def more_edits(request):
    """ saves edits, then goes back to the collection selection """
    save_edits(request)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})


def save_and_code(request):
    """ saves edits, then goes to the coder """
    global CoderText
#    print('SAC0:')
    save_edits(request)
    CoderText = ''  # triggers re-reading from db
    return HttpResponseRedirect('code_collection')    
# return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})


def apply_editor_markup(request):
    """ calls civet_utilities.do_markup() to lede and content. """
    textblock = get_editor_blocks(request.POST['civ_editor'])
    newstr = ''
    ka = 0
    for idst, lst in textblock.iteritems():
        print('AEM1',ka, idst,lst)
        newstr += make_ckeditor_markup_string(
                 [idst, civet_utilities.do_markup(lst[0]), lst[1], lst[2], civet_utilities.do_markup(lst[3])],
                 ka)
        print('AEM2',newstr)
        ka += 1
    context = get_CKEditor_context(newstr)
    return render(request,'djciv_data/civet_ckeditor.html',context)


def cancel_edits(request):
    """ Goes back to the collection selection without saving edits """
# might be useful to include a warning here...
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})

    
def select_collection(request): 
    """ collection selection """
    global PageIndex 
    PageIndex = 0
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})


# ================ form paging ================= #

def update_values(request):
    global Deletelist
    """ update the value field of civet_form.FormFields with POST data for the fields in CurVars """
#    print('UV1:',civet_form.FormFields)
#    print('UV1:',request.POST)
    if 'deletelist' in request.POST and request.POST['deletelist']:
        Deletelist += request.POST['deletelist'] + ' '
    form = CodingForm(request.POST,fields = civet_form.FormFields)
    if form.is_valid():
#        print('UV1-2',form.cleaned_data)
        fcd = form.cleaned_data
        for fld in fcd:
            if fld in CurVars:
                civet_form.FormFields[fld][2] = fcd[fld] 
#    else:
#        print(form.as_ul())  # need to do something meaningful here...  
#    for key, val in civet_form.FormFields.iteritems():
#        print('UV2',key, val[2])          

                            
def change_form_page(request, incr = 1, basic = False):
    global PageIndex 
    update_values(request)
    PageIndex += incr
    if basic:
        return render(request,'djciv_data/basic_form.html', get_form_context())
    else:
        return render(request,'djciv_data/civet_coder.html', get_coder_context())


# ================ basic coding form system (no mark-up) ================= #

def select_template(request):
    """ template selection in form-only mode """
    if civet_settings.REQUIRE_LOGIN and not request.user.is_authenticated():
        return HttpResponse("You must be logged in to access this page.") # need to set up a page to deal with this. Also note there is a decorator for this
    return render(request,'djciv_data/template_select.html',{})    


def get_form_context():
    global CurVars
#    print('GFC0:',PageIndex, civet_form.FormFields)
    context = {}
    context['form_content'], CurVars = civet_form.get_current_form(PageIndex)
#    print('GFC1:',context['form_content'])            
    context['form_css'] = civet_form.FormCSS
    context['page_title'] = civet_settings.FORM_PAGETITLE        
    context['page_index'] = PageIndex # not actually using this right now
    flen = len(civet_form.FormContent)
    if flen > 1:
        context['show_prev'] = (PageIndex > 0)
        context['show_next'] = (PageIndex < flen - 1)         
    return context
    
def read_template_only(request, isdemo = False):
    global PageIndex, InitalFormVals
    """ reads a simple template (not a collection), checks for errors, and then either renders the form or lists the errors.
        if isdemo, reads the demo template """
    if 'codername' in request.POST:
        civet_form.CoderName = request.POST['codername']        
    if isdemo:
        st = open(civet_settings.STATIC_FILE_PATH + civet_settings.DEMO_TEMPLATE,'r')  
    else: 
        if 'template_name' in request.FILES:
#            print('RTO2:',request.FILES['template_name'])        
            st = request.FILES['template_name']
        else:
            return HttpResponse("No file was selected: please go back to the previous page and select a file")

    civet_form.read_template(st)
    if civet_form.FormContent[0].startswith('&Errors:'):
        return render(request,'djciv_data/template_error.html', {'form_content': civet_form.FormContent[0][8:]})
    else:
        civet_form.create_TempData_header()
        PageIndex = 0
        InitalFormVals = deepcopy(civet_form.FormFields)
        return render(request,'djciv_data/basic_form.html', get_form_context())
    

def save_basic(request):
    """ save data then return to basic form """
    global PageIndex
    update_values(request)
    civet_form.save_to_TempData()
    PageIndex = 0
    civet_form.FormFields = deepcopy(InitalFormVals)
    return render(request,'djciv_data/basic_form.html', get_form_context())


def setup_basic_data_download(request):
    """ add a description here """
    update_values(request)
    civet_form.save_to_TempData()
    return render(request,'djciv_data/setup_basic_data_download.html',{'filename': civet_settings.DEFAULT_FILENAME})


def download_basic_data(request):
    """ Writes cases from the TempData list to a tab-delimited file """
    curfilename = request.POST['filename']
    if curfilename[-4:] != ".txt":
        curfilename += '.txt'
#    print('DBD1:',civet_form.TempData)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + curfilename + '"'
    response.write(civet_form.TempData)  
    return response

def continue_basic_coding(request, reset = False):
    """ option in setup_basic_data_download.html """  
    global PageIndex
    if reset:
        civet_form.create_TempData_header()    
    PageIndex = 0
    civet_form.FormFields = deepcopy(InitalFormVals)
    return render(request,'djciv_data/basic_form.html', get_form_context())


# ================ coder with mark-up ================= #

def make_coder_markup_string(theinfo, index):
    """ create a markup string containing from information from [textid, textlede, textdate, textcmt, textcontent] by adding 
        the <div>s and toggle controls 
    """
    ledest = '<div class = "textlede" id = "ldtext-'+ str(index) + \
            '" textid = "' + theinfo[0] + '">' + theinfo[1] + ' [' + theinfo[2] + ']</div> '
    commst = '<div class = "textcomm" id = "cmtext-'+ str(index) + '" style="display:none;">Comment: --' + theinfo[3] + '--</div>'
    contst = '<div class = "textcontent" id = "text-'+ str(index) + '" style="display:'
    if index == 0 or civet_settings.SHOW_ALL_CONTENT:
        contst += 'block'
    else:
        contst += 'none'
    contst += ';">' + theinfo[4] + '</div>'
    return ledest + commst + contst       


def make_listeners(length):
    """ returns a .addEventListener() function linked to the <div>s in the markup: this is needed to get around 
        the Chrome XSS Auditor and is probably good practice in any case.
    """
    strg = ''
    for ka in range(length):
        strg += '     document.getElementById("ldtext-' + str(ka) + '")' + \
           '.addEventListener("click", function(event) {togglecontent(event,"text-' + str(ka) + '");});\n' 
    return strg      


def get_coder_markup():
    """ return a string containing all of the textmkup fields from ActiveCollection """
    global HeaderInfo
    thecoll = Collection.objects.get(collid__exact=ActiveCollection)
    HeaderInfo['collid'] = thecoll.collid
    HeaderInfo['collcmt'] = thecoll.collcmt
    curtexts = Text.objects.filter(textparent__exact=ActiveCollection)
    stx = ''
    for ka, ct in enumerate(curtexts):
#        print('ED-Mk2:',ct.textmkup)
        if not ct.textdelete:
            temp = ct.get_text_fields()
            if civet_settings.ALWAYS_ANNOTATE and 'class:nament' not in temp[4]:  # a robust, if not quite guaranteed, telltale that there has been no markup
                temp[1] = civet_utilities.do_markup(temp[1])
                temp[4] = civet_utilities.do_markup(temp[4])
            stx += make_coder_markup_string(temp,ka)
    return stx

    
def get_coder_context():
    global CurVars
    theform, CurVars = civet_form.get_current_form(PageIndex)
    for cat in civet_form.UserCategories:
        theform = theform.replace('=^=' + cat + '=^=',civet_form.UserCategories[cat][1]) # replace the categories in the form with internal termstNN 
    context = {}
    context['document_header'] = civet_form.WorkspaceFileName.replace('_text_',WorkspaceName) +\
                                 civet_form.CollectionId.replace('_text_',HeaderInfo['collid']) +\
                                 civet_form.CollectionComments.replace('_text_',HeaderInfo['collcmt'])
    context['form_content'] = theform
    context['form_css'] = civet_form.FormCSS
    context['markedtext'] = CoderText
    context['newterm'] = TermStyles
    context['page_title'] = civet_settings.FORM_PAGETITLE        
    context['listeners'] = make_listeners(CoderText.count('<div class = "textlede"'))    
    context['page_index'] = PageIndex # not actually using this right now
    flen = len(civet_form.FormContent)
    if flen > 1:
        context['show_prev'] = (PageIndex > 0)
        context['show_next'] = (PageIndex < flen - 1)         
    return context


def code_collection(request):
    """ Assembles content for civet_coder.html: """
    """  theform: Replaces category class placeholders in civet_form.FormContent with the internal termstNN classes
         termstyles: Creates the category style list with the appropriate colors
         cktext: Replaces the category class <span>s created by manual annotation with the internal termstNN classes and 
                 removes color field from automatic annotation, allowing color to be controlled by class css in civet_coder.html. 
    """
# <15.07.22> pas: Those long cktext.replace() statements seem a little brittle, and in particular were thrown off by ";color" vs.
#    "; color" -- probably need something better
    global ActiveCollection, CoderText, TermStyles, PageIndex, Deletelist

#    print('CC0:', request.POST)
    if 'current_collection' in request.POST:   # when called directly from select
        if request.POST['current_collection']:
            ActiveCollection = request.POST['current_collection']
        else:
            return HttpResponse("No collection was selected: use the back key to return to the collection selection page.")
        
    if not CoderText:
        CoderText = get_coder_markup()
        if len(CoderText) == 0:
            return HttpResponse("No collection was selected: use the back key to return to the collection selection page.")

                                                                                        # do the standard replacements
        PageIndex = 0
        Deletelist = ''
        CoderText = CoderText.replace('style="class:nament;color:blue"','class="nament"') 
        CoderText = CoderText.replace('style="class:num;color:green"','class="num"')
    #    print('CC Incoming:\n',cktext)
        TermStyles = ''  # generate the new termst styles
        styles = civet_settings.DEFAULT_CKEDITOR_STYLES.split("{ 'class':")
        for strg in styles[1:]:
#            print('CC-0:',strg)
            strg = strg[:strg.find('}')+1].replace("'",'').replace('}',';}')
            ### TEMPORARY ###
            #strg = strg.replace('number','num')
            ### TEMPORARY ###
#            print('CC-00:',strg)
            TermStyles += '.' + strg[:strg.find(',')] + ' {' + strg[strg.find(',')+1:] + '\n'
    #    print('CC-1:',theform)
#        print('CC-1:',TermStyles)
        for cat in civet_form.UserCategories:
            fontstrg = civet_form.UserCategories[cat][0]
#            print('==',cat,fontstrg)
            styst = ''
            if ' bold' in fontstrg:
                styst += ' font-weight: bold;'
            if ' under' in fontstrg:
                styst += ' text-decoration: underline;'
            if ' italic' in fontstrg:
                styst += '  font-style: italic;'
#            print('++',cat,styst)
            if styst:
                TermStyles += '.' + civet_form.UserCategories[cat][1] + '  {color:' + fontstrg[:fontstrg.find(' ')] + \
                                ';' + styst + '}\n'
            else:              
                TermStyles += '.' + civet_form.UserCategories[cat][1] + '  {color:' + fontstrg + ';}\n'
            CoderText = CoderText.replace('style="class:' + cat + ';color:' + civet_form.UserCategories[cat][0] + ';"',\
                                    'class="' + civet_form.UserCategories[cat][1] + '"') #   # standardize manual annotation <span> markup 
            CoderText = CoderText.replace('style="class:' + civet_form.UserCategories[cat][1] + ';color:' + civet_form.UserCategories[cat][0] + '"',\
                                    'class="' + civet_form.UserCategories[cat][1] + '"') #   # remove color from automatic annotation <span> markup       
#        print('CC-2:',TermStyles)
    return render(request,'djciv_data/civet_coder.html',get_coder_context())


def save_and_return(request):
    global PageIndex 
    update_values(request)
    civet_form.save_case(ActiveCollection, Deletelist)
    PageIndex = 0
    civet_form.FormFields = deepcopy(InitalFormVals)
    return render(request,'djciv_data/civet_coder.html',get_coder_context())

    
def save_and_new(request):
    update_values(request)
    civet_form.save_case(ActiveCollection, Deletelist)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})    


def save_and_next(request):
    global ActiveCollection, CoderText
    update_values(request)
    civet_form.save_case(ActiveCollection, Deletelist)
#    print('SaNext-Mk1:',CollectionList)
    idx = CollectionList.index(ActiveCollection) + 1
    if idx < len(CollectionList):
        ActiveCollection = CollectionList[idx] 
        civet_form.FormFields = deepcopy(InitalFormVals)
        if civet_settings.SKIP_EDITING:
            CoderText = ''
            return HttpResponseRedirect('code_collection')
        else:   
            return render(request,'djciv_data/civet_ckeditor.html', get_CKEditor_context())
    else:
        return HttpResponse(civet_utilities.unimplemented_feature("you've reached the end of the list"))


# ================ workspace read/write and management system ================= #

def select_workspace(request, manage = False):
    if manage: 
        return render(request,'djciv_data/select_workspace.html',{'docoding':False})
    else:
        return render(request,'djciv_data/select_workspace.html',{'docoding':True})
    
    
def read_workspace(request, isdemo = False, manage = False):
    """ Loads a workspace zipped file; replaces anything already in Collection, Text  
        If isdemo, reads the demo collections
        If docoding, go to select_collection.html, otherwise manage_collections.html"""
    # 15.07.28 pas: Those massive blocks of code creating records should probably be methods in models.py
    global CollectionList, SaveFiles, WorkspaceName, CKEditor_Styles, ActiveCollection, CoderText, TermStyles, InitalFormVals        
#    print('RW0',isdemo, manage)
    if 'codername' in request.POST:
        civet_form.CoderName = request.POST['codername']        
    if isdemo:
        zipfilename = civet_settings.STATIC_FILE_PATH + civet_settings.DEMO_WORKSPACE
        WorkspaceName = 'Demonstration file'         
    else: 
        if 'filename' in request.FILES:
            zipfilename = request.FILES['filename']
            WorkspaceName = str(zipfilename)
        else:
            return HttpResponse("No file was selected: please go back to the previous page and select a file")
       
    zf = zipfile.ZipFile(zipfilename, 'r')
#    print('RW1:',zf.namelist())
 
    ActiveCollection = ''
    CoderText = ''
    TermStyles = ''
    Collection.objects.all().delete()
    Text.objects.all().delete()
    Case.objects.all().delete()     # <15.07.09: Warn first on this?
    civet_form.FormContent = ['']  # should this be initialized here?
    error_string = ''    
    ka = 0  # DEBUG
    for file in zf.namelist():  # get the codes. files first, since civet_form.read_template() will need this info
        if file.startswith('__'):
            continue
        try:
            filename = file[file.index('/')+1:]  # zipped file names may or may not have internal /
        except ValueError:
            filename = file
#        print('RW1:',file,filename)
        if filename.find('codes.') == 0:
            SaveFiles[filename] = zf.read(file)
            fin = zf.open(file,'r')
            civet_form.read_codes_file(fin, file)
            fin.close()
        
    CollectionList = []  # list of available collections   
    for file in zf.namelist():
#        print('RDC1:',file)
        if file.startswith('__'):
            continue
        try:
            filename = file[file.index('/')+1:]
        except ValueError:
            filename = file
        if file.endswith('.yml'):
            ka += 1
            if ka > 0: # <= 4:            # DEBUG
#                print('RCD-1:',file)
                fin = zf.open(file,'r')
                try:
                    collinfo, textlist, caselist = civet_utilities.read_YAML_file(fin, file)
                except Exception as e:
 #                   print('Error:' + str(e) + ' in ' + file)
                    error_string += '<p>' + str(e) + ' in the file "' + filename + '"'
                    continue

                collentry = Collection.objects.create_coll(
                    collid = collinfo['collid'],
                    collfilename = collinfo['collfilename'],
                    colldate = collinfo['colldate'],
                    colledit = collinfo['colledit'],
                    collcmt = collinfo['collcmt']
                    )
                collentry.save()
                CollectionList.append(collinfo['collid'])

                for dc in textlist:
                    textentry = Text.objects.create_text(
                        textparent = dc['textparent'],
                        textid = dc['textid'],
                        textdelete = dc['textdelete'],
                        textdate = dc['textdate'],
                        textpublisher = dc['textpublisher'],
                        textpubid = dc['textpubid'],
                        textbiblio = dc['textbiblio'],
                        textlicense = dc['textlicense'],
                        textgeogloc = dc['textgeogloc'],
                        textlede = dc['textlede'],
                        textcmt = dc['textcmt'],
                        textoriginal = dc['textoriginal'],
                        textmkup = dc['textmkup'],
                        textmkupdate = dc['textmkupdate'],
                        textmkupcoder = dc['textmkupcoder']
                        )
                    textentry.save()
                    
                if len(caselist) > 0:
                    for dc in caselist:
                        caseentry = Case.objects.create_case(
                                    caseparent = dc['caseparent'],
                                    caseid = dc['caseid'],
                                    casedate = dc['casedate'],
                                    casecoder = dc['casecoder'],
                                    casecmt = dc['casecmt'],
                                    casevalues = dc['casevalues']
                                    )
                        caseentry.save()
                
                fin.close()
                
        elif filename.find('form.') == 0:  
            SaveFiles[filename] = zf.read(file)
            fin = zf.open(file,'r')
#            print('RCD-2:',file)
            civet_form.read_template(fin)
            fin.close()
#            print('RW savelists:\n',civet_form.SaveList,'\n',civet_form.SaveTypes)
            CKEditor_Styles = civet_utilities.get_styles()
        else:
            if len(filename)> 0:
                SaveFiles[filename] = zf.read(file)

    if not manage and len(civet_form.FormContent[0]) == 0:
        error_string += "<p>No 'form.*' file was found in the workspace: This is required for coding."
    if civet_form.FormContent[0].startswith('&Errors:'):
        if len(error_string) > 0:
            error_string = '<h3>Form errors:</h3>' + civet_form.FormContent[0][8:] + '<h3>Collection errrors:</h3>' + error_string
        else:
             error_string = '<h3>Form errors:</h3>' + civet_form.FormContent[0][8:]        
    if len(error_string) > 0:
        context = {}
        context['workspace'] = WorkspaceName
        context['errors'] = error_string
        if manage:
            context['docoding'] = False
        else:
            context['docoding'] = True            
        return render(request,'djciv_data/collection_error.html', context)
    
    if manage: 
        return render(request,'djciv_data/manage_workspace.html',{'workspace' : WorkspaceName})
    else:
        InitalFormVals = deepcopy(civet_form.FormFields)
#        print('==',InitalFormVals)
        return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace' : WorkspaceName})
        
def setup_workspace_download(request, iscoding = False):
    """ Get file name for workspace download."""
    if iscoding:
        update_values(request)
        civet_form.save_case(ActiveCollection, Deletelist)
    else:
        save_edits(request)
    context = {}
    if WorkspaceName == 'Demonstration file':
        context['filename'] = 'CIVET.workspace.default.zip' # prevent overwriting the demonstration file
    else:
        context['filename'] = WorkspaceName
    return render(request,'djciv_data/setup_workspace_download.html',context)


def write_workspace(request):
    """ Downloads the workspace as a zipped file."""
#    print('WW0:',CollectionList)
    tempdirname = 'update271828' # we will trust this is safe
    filenames = []
    thedir = request.POST['filename']  
#    thedir = 'test123' ### debug
    if thedir[-4:] == ".zip":
        thedir = thedir[:-4]   # suffix is added below
    if not os.path.exists(tempdirname):
        os.mkdir(tempdirname)  # need to get rid of this later
    for collst in CollectionList:  
        thecoll = Collection.objects.get(collid__exact=collst)
        fdir, filename = os.path.split(thecoll.collfilename)
#        print('WW1:',collst, fdir,filename)
        filename = tempdirname + '/' + filename + '.yml'
        filehandle = open(filename,'w')
        civet_utilities.write_YAML_file(thecoll, filehandle)
        filehandle.close()
        filenames.append(filename)
        
    # code below shamelessly copied from:
    #http://stackoverflow.com/questions/67454/serving-dynamically-generated-zip-archives-in-django
    # 15.07.29 pas: It sure seems like there would be a very simple way to write the results of civet_utilities.write_YAML_file(thecoll, filehandle)
    # directly into the zip file, but I'm not groking ZipFile sufficiently well to see it right now -- though writing this comment,
    # I'm now guessing it would involve some appropriate use of that StringIO object -- and the current method works. So, later...  

    # Folder name in ZIP archive which contains the above files
    zip_subdir = thedir
    zip_filename = "%s.zip" % zip_subdir
#    print('WW2:',thedir,zip_filename,filenames)

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:  # add the YAML files
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
#        zip_path = os.path.join(zip_subdir, fname) 
        zip_path = fname

        # Add file, at correct path
        zf.write(fpath, zip_path)

    for filest in SaveFiles: # add all of the other files
#        print('WW2.1:',filest)
        zf.writestr(filest,SaveFiles[filest])
        
    # Must close zip for all contents to be written
    zf.close()
    
    shutil.rmtree(tempdirname, ignore_errors=True)  # remove the temporary directory

    # Grab ZIP file from in-memory, make response with correct MIME-type
    response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return response
#    return HttpResponse("So far so good")
    
def setup_workspace_data_download(request):
    """ Get file name for workspace data download."""
    context = {}
    context['workspace'] = WorkspaceName
    if WorkspaceName == 'Demonstration file':
        context['filename'] = 'CIVET.demonstration.data.txt' # prevent overwriting the demonstration file
    else:
        context['filename'] = WorkspaceName + '.data.txt'
    return render(request,'djciv_data/setup_workspace_data_download.html',context)

def download_workspace_data(request, select_variables = False):
    """ writes all cases to a tab-delimited file """
    # need a time option here to just get the new cases
#    print('DWD0-entry:')

    def get_missing(textstr):
        if civet_settings.USE_TEXT_FOR_MISSING:
            return textstr
        else:
            return civet_settings.MISSING_VALUE
    
    if select_variables: 
        return HttpResponse(civet_utilities.unimplemented_feature("download selected variables"))
        # in final routing, this probably should go to a dialog for selecting a variable list, which will then be passed
        # here either as a global or arg: hmmm, yeah, so we will still have something like a if select but now select will contain that list
    else:
        writelist = civet_form.SaveList
        
#    print('DWD0:',writelist)
    tempdata = ''
    usevalue = []
    for ka, savename in enumerate(civet_form.SaveList): # write variable labels
        if '[' in civet_form.SaveTypes[ka]:
            usevalue.append(True)
            parts = civet_form.SaveTypes[ka].partition('[')
            varname = parts[2][:parts[2].find(']')].strip()
            if len(varname) == 0:
                varname = savename
            tempdata += varname + '\t'  # there was a check earlier that this existed
        else:
            tempdata += savename + '\t'
            usevalue.append(False)

    tempdata = tempdata[:-1] + '\n'     
    for acase in Case.objects.all():
        values = ast.literal_eval(acase.casevalues)  # read the dictionary as a dictionary init; probably should be a case method
#        print('DD-Mk-1:',values)
#        print('DD-Mk-2:', civet_form.SaveList)
        if '_discard_' in values and values['_discard_']:
            continue
        if '_delete_' in values:
            continue
        for ka, avar in enumerate(writelist):
            """if avar in values:
                print(' >> :',values[avar])
            else:
                print(' >> : variable not found') """               
            if avar in civet_form.SpecialVarList: 
                tempdata += civet_form.get_special_var(avar) + '\t'
            elif avar in civet_form.ConstVarDict.keys(): 
                tempdata += civet_form.ConstVarDict[avar] + '\t'
            elif avar in values:
                if values[avar]:  # go to missing if a null string
                    if usevalue[ka]:
                        if ']' == values[avar].rstrip()[-1]:
                            try:
                                thevalue = values[avar][values[avar].find('[')+1:values[avar].index(']')].strip()
                            except:
                                thevalue = get_missing(values[avar])
                        else:
                                thevalue = get_missing(values[avar]) 
                        tempdata += thevalue +'\t'
                    else:
                        if ']' == values[avar].rstrip()[-1]:
                            tempdata +=  values[avar][:values[avar].find('[')].strip() +'\t'
                        else:
                            tempdata +=  values[avar] +'\t'
                else:
                    thevalue = get_missing('')
            else:
                tempdata += avar + ' unchecked\t'  # shouldn't hit this, but probably still worth an error check
        tempdata = tempdata[:-1] + '\n'
    curfilename = request.POST['filename']
    if curfilename[-4:] != ".txt":
        curfilename += '.txt'
#    curfilename = 'test_data1.txt'  # debug
#    print('DD1:',curfilename)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + curfilename + '"'
    response.write(tempdata)        
    return(response)

def edit_metadata(request):
    return HttpResponse(civet_utilities.unimplemented_feature("edit_metadata"))

def add_workspace_comments(request):
    return HttpResponse(civet_utilities.unimplemented_feature("add_workspace_comments"))


# ================ navigation placeholders and other utilities ================= #

def make_color_list(request):
    defaults = [['Plain text','black'],['Named entity','blue'],['Number','green'],['Date','Coral']]
    thecontent = ''
    thecontent += '<h2>Demonstration page for CIVET text category colors</h2><br><table border="1"><caption><h3>CIVET Default Category Colors</h3></caption><tr>'
    for ka, colorname in enumerate(civet_form.CatColorList):
        if (ka)%4 == 0:
            thecontent += '</tr><tr>'
        thecontent += '<td><span style="color:' + colorname + '; font-size: large">' + str(ka+1) + ': ' + colorname	 + '</span></td>'
    thecontent += '</tr></table><h2>Colors shown as text</h2>'        
    for lst in defaults:
        thecontent += '<span style="color:' + lst[1] + '">' + lst[0] + ' </span> '
    for color in civet_form.CatColorList:
        thecontent += '<span style="color:' + color + '">' + color + ' </span> '
        if color == 'Brown' or color == 'DarkGray' :  # magic number, or rather color, here...
            thecontent += '<br>' 
    thecontent += '<h3>Close the window to exit</h3><p>&nbsp;'        
    return render(request,'djciv_data/basic_form.html', {'form_content' : thecontent})

def test_page(request):
    return render(request,'djciv_data/test_page.html',{})

