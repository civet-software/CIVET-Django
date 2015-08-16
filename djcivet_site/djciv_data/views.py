from __future__ import print_function

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File
from django.conf import settings

from .models import Collection, Text, Case
#import csv
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

# Note: I'm 'CamelCasing' the global variables that are set during a session

DEFAULT_COLLECTION_DIR = 'civet_input_files'

ActiveCollection = ''
# tempdata = '' # can be deleted?
CoderContext = {} # this is global since we may be returning to the same page after a save

CollectionList = []  # list of available collections in workspace 

WorkspaceName = ''
CurCollectionIndex = 0  # CollectionList index of most recently coded collection  
SaveFiles = {}  # contents of files other than .yml indexed by the file name

CKEditor_Styles = ''  # default and category styles for CKEditor


# ================ static file utilities ================= #

def index(request):
    print('BXSE_DIR:',settings.BASE_DIR)
    print('STATIC_URL:',settings.STATIC_URL)
#    print('Hey, this is da place!')
    return render(request, 'djciv_data/index.html',{'staticpath':civet_settings.STATIC_SOURCE})

def online_manual(request):
    """ Goes to index.html of on-line docs """
    # 15.08.10 pas: okay folks, give me a hand here: there's got to be a way of accessing these at 
    # djcivet_site/docs/_build/html/ in a manner that has them are correctly rendered, but I haven't figured it out yet. 
#    print ("Current working dir:", os.getcwd())
    return HttpResponseRedirect(civet_settings.ONLINE_DOCS_URL)
        
def download_pdfdocs(request):
    """ downloads the main documentation or redirects if it can't be found """
    print('DPD: entry')
    if os.path.isfile('docs/_build/latex/civetdoc.pdf'):  # leave this path hard-coded for the time being
        print('DPD: docs download')
        f = open('docs/_build/latex/civetdoc.pdf', "r")
    elif os.path.isfile(civet_settings.STATIC_FILE_PATH + 'civetdoc.pdf'):
        print('DPD: STATIC_FILE_PATH download')
        f = open(civet_settings.STATIC_FILE_PATH + 'civetdoc.pdf', "r")
    else:
        print('DPD: remote download')
        return HttpResponseRedirect(civet_settings.PDF_DOC_URL)
    response = HttpResponse(FileWrapper(f), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=CIVET.Documentation.pdf'
    f.close()
    return response

def download_demotemplate(request):
    """ downloads the demo template """
    f = open(civet_settings.STATIC_FILE_PATH + 'CIVET.demo.template.txt', "r")
    response = HttpResponse(FileWrapper(f), content_type='text/plain')
    response ['Content-Disposition'] = 'attachment; filename=CIVET.demo.template.txt'
    f.close()
    return response

def download_demo_workspace(request):
    """ downloads the demo template """
    f = open(civet_settings.STATIC_FILE_PATH + 'CIVET.workspace.demo.zip', "r")
    response = HttpResponse(FileWrapper(f), content_type='application/x-zip-compressed')
    response ['Content-Disposition'] = 'attachment; filename=CIVET.workspace.demo.zip'
    f.close()
    return response


# ================ editor system ================= #

def get_CKEditor_context():
    """ sets context for calls to civet_ckeditor.html """
    context = {}
    context['current_collection'] = ActiveCollection
    context['thetext'] = get_collection_markup()
    context['the_styles'] = CKEditor_Styles
    context['staticpath'] = civet_settings.STATIC_SOURCE
    return context

def get_collection_markup():
    """ return a string containing all of the textmkup fields from ActiveCollection """
    curtexts = Text.objects.filter(textparent__exact=ActiveCollection)
    stx = ''
    for ct in curtexts:
#        print('ED-Mk2:',ct.textmkup)
#        print(ct.get_markup()[:128])
        temp = ct.get_markup()
        stx += make_markup_string(temp) + '<br>'
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
        

def make_markup_string(theinfo):
    """ create a markup string containing from [textid, textlede, textcontent] by adding the <div>s """
    return  '<div class = "textblock" data-textid = "' + theinfo[0] + '">' + \
            '<div class = "textlede" style="color:green; font-weight: bold;">' + theinfo[1] + '</div> ' + \
            '<div class = "textcontent" >' + theinfo[2] + '</div>' + \
            '</div>'

def get_blocks(thestring):
    """ return dictionary of text blocks keyed by textid, and containing [textlede,textcontent] """
    curdiv = thestring.find('<div')
    textblock = {}
    while curdiv >= 0:
        endtag = thestring.find('>',curdiv)
        tagst = thestring[curdiv:endtag]
        if '"textlede"' in tagst:
            enddiv = thestring.find('</div>',endtag+1)
            thelede = thestring[endtag+1:enddiv]
            textblock[theid] = [thelede,'']
            curdiv = thestring.find('<div',enddiv+4)
        elif '"textcontent"' in tagst:
            enddiv = thestring.find('</div>',endtag+1)
    #        print'Content:',thestring[endtag+1:enddiv]
            thecontent = thestring[endtag+1:enddiv]
            textblock[theid][1] = thecontent
            curdiv = thestring.find('<div',enddiv+4)
        elif '"textblock"' in tagst:
            part = tagst.partition('data-textid="')
            theid = part[2][:part[2].find('"')]
            curdiv = thestring.find('<div',endtag+1)
        else:
            curdiv = thestring.find('<div',endtag+1)
    return textblock
    
def save_edits(request):
    """ saves current markup to the DB """
#    print('SE-Mk0:')
    thestring = request.POST['editor1']
    textblock = get_blocks(thestring)
    for st in textblock:
        print('\nID:',st)
        print('Lede:',textblock[st][0])
        print('Content:',textblock[st][1])
        curtext = Text.objects.get(textid__exact=st)
        curtext.textlede = textblock[st][0]
        curtext.textmkup = textblock[st][1]
        curtext.textmkupdate = datetime.datetime.now()
        curtext.textmkupcoder = civet_form.CoderName
        curtext.save()
 
#    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})   
#    return HttpResponse("exiting save_edits: Just use the back key")

def more_edits(request):
    """ saves edits, then goes back to the collection selection """
    save_edits(request)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})

def apply_markup(request):
    """ calls civet_utilities.do_markup() for each text block in the collection. """
    textblock = get_blocks(request.POST['editor1'])
    newstr = ''
    for st in textblock:
        newstr += make_markup_string([st,textblock[st][0],civet_utilities.do_markup(textblock[st][1])])
    context = get_CKEditor_context()
    context['thetext'] = newstr
    return render(request,'djciv_data/civet_ckeditor.html',context)


def cancel_edits(request):
    """ Goes back to the collection selection without saving edits """
# might be useful to include a warning here...
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})

    
def select_collection(request): 
    """ collection selection """
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})

#def operating_instructions(request):  # 15.08.10 this is no longer used
    """ display page with basic instructions """
#    return HttpResponse(civet_utilities.unimplemented_feature("operating instructions"))
        #return render(request,'djciv_data/operating_instructions.html',{})


# ================ basic coding form system (no mark-up) ================= #

def read_template(fin):
    """ reads a template (or the error strings from same) from the file handle fin into civet_form.FormContent """
    civet_form.init_template()
    thecontent = ''
    commln = civet_form.get_commlines(fin)
    while len(commln) > 0:
        thecontent += civet_form.do_command(commln)
        commln = civet_form.get_commlines(fin)
        
#    print('thecontent:',thecontent)
    if len(civet_form.SaveList) == 0:
        thecontent += '~Error~<p>A "save:" command is required in the template<br>\n'
    else:
        misslist = []
        for ele in civet_form.SaveList:
            if ele not in civet_form.VarList:
                misslist.append(ele)
        if len(misslist) > 0:
            thecontent += '~Error~<p>The following variables are in the "save:" command but were not declared in a data field<br>' + str(misslist) + '\n'

#    print('RT1:',thecontent)
    if '~Error~' in thecontent:
        errortext = '&Errors:'
        indx = thecontent.find('~Error~')
        while indx >= 0:
            indy = thecontent.find('\n',indx)
            errortext += thecontent[indx+7:indy+1]
            indx = thecontent.find('~Error~',indy)
        civet_form.FormContent = thecontent = errortext
    else:    
        civet_form.FormContent = thecontent


def select_template(request):
    """ template selection in form-only mode """
    return render(request,'djciv_data/template_select.html',{})
    

def read_template_only(request, isdemo = False):
    """ reads a simple template (not a collection), checks for errors, and then either renders the form or lists the errors.
        if isdemo, reads the demo template """
#    civet_form.init_template()
    if 'codername' in request.POST:
        civet_form.CoderName = request.POST['codername']        
    if isdemo:
        st = open(civet_settings.STATIC_FILE_PATH + 'CIVET.demo.template.txt','r')  
    else: 
        if 'template_name' in request.FILES:
#            print('RTO2:',request.FILES['template_name'])        
            st = request.FILES['template_name']
        else:
            return HttpResponse("No file was selected: please go back to the previous page and select a file")

    read_template(st)
    if civet_form.FormContent.startswith('&Errors:'):
        return render(request,'djciv_data/template_error.html', {'form_content' :  civet_form.FormContent[8:]})
    else:
        civet_form.create_TempData_header()
        context = {}
        context['form_content'] = civet_form.FormContent
        context['page_title'] = civet_form.FormPageTitle       
        return render(request,'djciv_data/basic_form.html', context)
    

def save_basic(request):
    """ save data then return to template-based form """
    civet_form.save_to_TempData(request)
    return render(request,'djciv_data/basic_form.html', {'form_content' : civet_form.FormContent})


def get_new_case(request):
    civet_form.save_to_TempData(request)
    return render(request,'djciv_data/file_select.html')


def setup_basic_data_download(request):
    """ add a description here """
    civet_form.save_to_TempData(request)
    return render(request,'djciv_data/setup_basic_data_download.html',{'filename': civet_form.DefaultFileName})


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

def reset_basic_data(request):
    civet_form.create_TempData_header()
    return render(request,'djciv_data/basic_form.html',  {'form_content' : civet_form.FormContent})

def continue_basic_coding(request):
    return render(request,'djciv_data/basic_form.html',  {'form_content' : civet_form.FormContent})


# ================ coder with mark-up ================= #


def code_collection(request):
    """ Assembles content for civet_coder.html: """
    """  theform: Replaces category class placeholders in civet_form.FormContent with the internal termstNN classes
         termstyles: Creates the category style list with the appropriate colors
         cktext: Replaces the category class <span>s created by manual annotation with the internal termstNN classes and 
                 removes color field from automatic annotation, allowing color to be controlled by class css in civet_coder.html. 
    """
# Still need to do:
# 1. Add document ID and comments
# 2. <15.07.22>: Those long cktext.replace() statements seem a little brittle, and in particular were thrown off by ";color" vs.
#    "; color" -- probably need something better
    global ActiveCollection, CoderContext
    """context = {}
    context['docidst'] = 'Document ID'
    context['doccmtst'] = 'Document comments'  # this is apparently handled elsewhere now?"""
#    context['markedtext'] = 'This is <span style="class:date;color:red">some</span> text with a <span class="date">date</span> and a <span class="nament">Named Entity</span>'
    if 'editor1' in request.POST:
        cktext =  request.POST['editor1']  # called following editing
    else:
        if 'current_collection' in request.POST:
            ActiveCollection = request.POST['current_collection']
        cktext = get_collection_markup()  # called directly from a select
        if len(cktext) == 0:
            return HttpResponse("No collection was selected: use the back key to return to the collection selection page.")

                                                                                    # do the standard replacements
    cktext = cktext.replace('style="class:nament;color:blue"','class="nament"') 
    cktext = cktext.replace('style="class:num;color:green"','class="num"')
#    print('CC Incoming:\n',cktext)
    termstyles = ''  # generate the new termst styles
    theform = civet_form.FormContent  # also replace these in the form
#    print('CC-1:',theform)
    for cat in civet_form.UserCategories:
        termstyles += '.' + civet_form.UserCategories[cat][1] + '  {color:' + civet_form.UserCategories[cat][0] + ';}\n'
        cktext = cktext.replace('style="class:' + cat + ';color:' + civet_form.UserCategories[cat][0] + ';"',\
                                'class="' + civet_form.UserCategories[cat][1] + '"') #   # standardize manual annotation <span> markup 
        cktext = cktext.replace('style="class:' + civet_form.UserCategories[cat][1] + ';color:' + civet_form.UserCategories[cat][0] + '"',\
                                'class="' + civet_form.UserCategories[cat][1] + '"') #   # remove color from automatic annotation <span> markup 
        theform = theform.replace('=^=' + cat + '=^=',civet_form.UserCategories[cat][1]) # replace the categories in the form with internal termstNN 
     
    CoderContext['form_content'] = theform
    CoderContext['markedtext'] = cktext
    CoderContext['newterm'] = termstyles
    CoderContext['page_title'] = civet_form.FormPageTitle       
#    print('CC0 - theform:',theform)
#    print('CC1 - cktext:',cktext)
#    print('CC2 - termstyles',termstyles)
#    return HttpResponse("End of code_collection(); see Terminal for output")
    return render(request,'djciv_data/civet_coder.html',CoderContext)


def save_and_return(request):
    civet_form.save_case(request, ActiveCollection)
    return render(request,'djciv_data/civet_coder.html',CoderContext)

    
def save_and_new(request):
    civet_form.save_case(request, ActiveCollection)
    print('SaN-Mk1:',CollectionList)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace': WorkspaceName})    

def save_and_next(request):
    global ActiveCollection
    civet_form.save_case(request, ActiveCollection)
#    print('SaNext-Mk1:',CollectionList)
    idx = CollectionList.index(ActiveCollection) + 1
    if idx < len(CollectionList):
        ActiveCollection = CollectionList[idx]    
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
    # 15.07.28 pas: Those massive blocks of code creating record should probably by methods in models.py
    global CollectionList, SaveFiles, WorkspaceName, CKEditor_Styles        
#    print('RW0',isdemo, manage)
    if 'codername' in request.POST:
        civet_form.CoderName = request.POST['codername']        
    if isdemo:
        zipfilename = civet_settings.STATIC_FILE_PATH + 'CIVET.workspace.demo.zip'
        WorkspaceName = 'Demonstration file'         
    else: 
        if 'filename' in request.FILES:
            zipfilename = request.FILES['filename']
            WorkspaceName = str(zipfilename)
        else:
            return HttpResponse("No file was selected: please go back to the previous page and select a file")
       
    zf = zipfile.ZipFile(zipfilename, 'r')
#    print('RW1:',zf.namelist())
 
    Collection.objects.all().delete()
    Text.objects.all().delete()
    Case.objects.all().delete()     # <15.07.09: Warn first on this?
    civet_form.FormContent = ''
    error_string = ''    
    ka = 0  # DEBUG
    for file in zf.namelist():  # get the codes. files first, since read_template() will need this info
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
                        textdate = dc['textdate'],
                        textpublisher = dc['textpublisher'],
                        textpubid = dc['textpubid'],
                        textlicense = dc['textlicense'],
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
            read_template(fin)
            fin.close()
#            print('RW savelists:\n',civet_form.SaveList,'\n',civet_form.SaveTypes)
            CKEditor_Styles = civet_utilities.get_styles()
        else:
            if len(filename)> 0:
                SaveFiles[filename] = zf.read(file)

    if not manage and len(civet_form.FormContent) == 0:
        error_string += "<p>No 'form.*' file was found in the workspace: This is required for coding."
    if civet_form.FormContent.startswith('&Errors:'):
        if len(error_string) > 0:
            error_string = '<h3>Form errors:</h3>' + civet_form.FormContent[8:] + '<h3>Collection errrors:</h3>' + error_string
        else:
             error_string = '<h3>Form errors:</h3>' + civet_form.FormContent[8:]        
    if len(error_string) > 0:
        context = {}
        context['workspace'] = WorkspaceName
        context['errors'] = error_string
        if manage:
            context['docoding'] = False
        else:
            context['docoding'] = True            
        return render(request,'djciv_data/collection_error.html', context)
    

    """print('RW4:',CollectionList)
    for st in savefiles:
        print('>>',st)"""
    
#    return render(request,'djciv_data/test_page.html',{})  # DEBUG
    if manage: 
        return render(request,'djciv_data/manage_workspace.html',{'workspace' : WorkspaceName})
    else:
        return render(request,'djciv_data/select_collection.html',{'files' : CollectionList, 'workspace' : WorkspaceName})
        
def setup_workspace_download(request, iscoding = False):
    """ Get file name for workspace download."""
    if iscoding:
        civet_form.save_case(request, ActiveCollection)
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
    
def collection_manager(request):  # is this still used?
    return render(request,'djciv_data/collection_options.html',{'files' : CollectionList})

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
#        print('==: ',acase.casevalues)
        values = ast.literal_eval(acase.casevalues)  # probably should be a case method
#        print('DD-Mk-1:',values)
#        print('DD-Mk-2:', civet_form.SaveList)
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
                if usevalue[ka]:
                    if '[' in values[avar]:  ##   CHECK FOR ESCAPE
                        try:
                            thevalue = values[avar][values[avar].find('[')+1:values[avar].index(']')].strip()
                        except:
                            thevalue = civet_utilities.MissingValue
                    else:
                            thevalue = civet_utilities.MissingValue 
                    tempdata += thevalue +'\t'
                else:
                     if '[' in values[avar]:  ##   CHECK FOR ESCAPE
                        tempdata +=  values[avar][:values[avar].find('[')].strip() +'\t'
                     else:
                        tempdata +=  values[avar] +'\t'
            else:
 #               tempdata += civet_form.UncheckedValues[avar] + '\t'
                tempdata += avar + ' unchecked\t'
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
    return render(request,'djciv_data/collection_options.html',{'ActiveCollection' : ActiveCollection})

def add_workspace_comments(request):
    return HttpResponse(civet_utilities.unimplemented_feature("add_workspace_comments"))
    return render(request,'djciv_data/collection_options.html',{'ActiveCollection' : ActiveCollection})


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

def set_preferences(request):
    return render(request,'djciv_data/preferences.html', civet_utilities.get_preferences())
    
def reset_preferences(request):
    civet_utilities.set_preferences()
    return render(request,'djciv_data/basic_form.html', {})

def collection_options(request):
    return render(request,'djciv_data/collection_options.html',{'ActiveCollection' : ActiveCollection})

def sort_collections(request):
    return render(request,'djciv_data/sorting_placeholder.html',{})

def save_collection(request):
    return render(request,'djciv_data/save_collection_placeholder.html',{})

def save_data(request):
    return render(request,'djciv_data/save_data_placeholder.html',{})

def save_all(request):
    return render(request,'djciv_data/save_all_placeholder.html',{})

def test_page(request):
    return render(request,'djciv_data/test_page.html',{})
        