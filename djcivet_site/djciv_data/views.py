from __future__ import print_function

from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files import File

from .models import Collection, Text, Case
#import csv
import shutil
import zipfile
import StringIO
import os

import CIVET_utilities
import CIV_template	


# ======== global initializations ========= #

# Note: I'm 'CamelCasing' the global variables that are set during a session

DEFAULT_COLLECTION_DIR = 'civet_input_files'

ActiveCollection = ''
ActiveTemplate = ''
tempdata = ''
CoderContext = {}

CollectionForm = ''  # file name for the form used with this collection
CollectionList = []  # list of available collections   

# ======== data read/write ========= #

def read_collection_directory(request, dirname):
    """ Loads a set of collections from dirname; replaces anything already in Collection, Text  """
    global CollectionForm, CollectionList
    
    Collection.objects.all().delete()
    Text.objects.all().delete()
    Case.objects.all().delete()     # <15.07.09: Warn first on this?
    CollectionForm = ''    
    ka = 0
#    CIVET_utilities.hello()
    filelist = os.listdir(dirname)
    for file in filelist:
        ka += 1
        if file.endswith('.yml'):
            if ka <= 4:            # DEBUG
#                print('RCD-1:',file)
                collinfo, textlist = CIVET_utilities.get_YAML_file(dirname + '/' + file)
                collentry = Collection.objects.create_coll(
                    collid = collinfo['collid'],
                    collfilename = collinfo['collfilename'],
                    colldate = collinfo['colldate'],
                    colledit = collinfo['colledit'],
                    collcmt = collinfo['collcmt']
                    )
                collentry.save()
 
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
                
                    # NEED TO ADD READING CASES HERE!
                
        elif file.startswith('form'):
            CollectionForm = dirname + '/' + file
#            print('RCD-2:',CollectionForm)
        
        # otherwise ignore file, so other things can be in there
        # error check on empty CollectionForm 

    CollectionList = []  # list of available collections   
    for tup in Collection.objects.values_list('collid'):
        CollectionList.append(tup[0])
        
#    return HttpResponse("Reading input directory %s." % dirname)

    
def select_template(request):
    CIV_template.BasicMode = True
    return render(request,'djciv_data/template_select.html',{})
    
def download_data(request):
    """ writes all cases to a tab-delimited file """
    # need a time option here to just get the new cases
    CIV_template.SaveList = [u'typeincid', u'_date_', u'authreport', u'location', u'descrp']  # DEBUGGING   
    tempdata = '\t'.join(CIV_template.SaveList) + '\n'     
    for acase in Case.objects.all():
        values = acase.get_values()
#        print('DD-Mk-1:',values)
#        print('DD-Mk-2:', CIV_template.SaveList)
        if len(values) >= len(CIV_template.SaveList): # skips blank records, I hope
            for avar in CIV_template.SaveList: 
#                print('STT2:',avar)
                if avar in CIV_template.SpecialVarList: 
                    tempdata += CIV_template.get_special_var(avar) + '\t'
                elif avar in CIV_template.ConstVarDict.keys(): 
                    tempdata += CIV_template.ConstVarDict[avar] + '\t'
                elif avar in values:
                    tempdata += values[avar]+'\t'
                else:
                    tempdata += CIV_template.unchecked[avar] + '\t'
        tempdata = tempdata[:-1] + '\n'
    curfilename = request.POST['filename']
    if curfilename[-4:] != ".txt":
        curfilename += '.txt'
#    print('DD1:',curfilename)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + curfilename + '"'
    response.write(tempdata)        
    return(response)
    
def basicmode_download_data(request):
    """ in CIV_template.BasicMode, writes cases from the TempData list to a tab-delimited file """
    # 15.07.08: I'm currently maintaining parallel versions of this, one using the DB and one using a simple string, until we
    #           figure out whether we want to keep the Flask version that does not use a DB. Other the BasicMode should be 
    #           merged to write into Case and then just use download_data
    curfilename = request.POST['filename']
    if curfilename[-4:] != ".txt":
        curfilename += '.txt'
#    print('BDD1:',curfilename)
    print(CIV_template.TempData)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="' + curfilename + '"'
    print(response['Content-Disposition'])
    response.write(CIV_template.TempData)  
    print(response)          
    return response

   
def update_collections(request):
    # need a time option here
    """ActiveCollection = 'TestTexts_000'
    filehandle = open('not_really_a_file.txt','w')
    CIVET_utilities.write_YAML_file(ActiveCollection, filehandle)
    filehandle.close()
    return HttpResponse("So far so good")"""
    tempdirname = 'update'
    CollectionList = ['TestTexts_000','TestTexts_001']
    filenames = []
    thedir = ''
    print('UC-1:',CollectionList)
    if not os.path.exists(tempdirname):
        os.mkdir(tempdirname)
    for collst in CollectionList:
        thecoll = Collection.objects.get(collid__exact=collst)
        fdir, filename = os.path.split(thecoll.collfilename)
        filename = tempdirname + '/' + filename + '.yml'
        if len(thedir) == 0:
            thedir = fdir
        filehandle = open(filename,'w')
        CIVET_utilities.write_YAML_file(thecoll, filehandle)
        filehandle.close()
        filenames.append(filename)
        
# code below shamelessly copied from:
#http://stackoverflow.com/questions/67454/serving-dynamically-generated-zip-archives-in-django    

    # Folder name in ZIP archive which contains the above files
    zip_subdir = thedir
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()
    
    shutil.rmtree(tempdirname, ignore_errors=True)

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp
#    return HttpResponse("So far so good")


# ======== static file utilities ========= #

def index(request):
    return render(request, 'djciv_data/index.html',{})

def download_pdfdocs(request):
    """ downloads the main documentation """
    f = open('djciv_data/static/djciv_data/CIVET.Documentation.pdf', "r")
    response = HttpResponse(FileWrapper(f), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=CIVET.Documentation.pdf'
    f.close()
    return response
    
def download_demotemplate(request):
    """ downloads the demo template """
    f = open('djciv_data/static/djciv_data/CIVET.demo.template.txt', "r")
    response = HttpResponse(FileWrapper(f), content_type='text/plain')
    response ['Content-Disposition'] = 'attachment; filename=CIVET.demo.template.txt'
    f.close()
    return response


# ======== editor system ========= #

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
    context = {}
    print('ED-Mk1:',request.POST['current_collection'])
    ActiveCollection = request.POST['current_collection']
    context['current_collection'] = ActiveCollection
    """curtexts = Text.objects.filter(textparent__exact=ActiveCollection)
    stx = ''
    for ct in curtexts:
#        print('ED-Mk2:',ct.textmkup)
#        print(ct.get_markup()[:128])
        temp = ct.get_markup()
        stx += make_markup_string(temp)"""
    context['thetext'] = get_collection_markup()
#    context['thetext'] = 'This is <span style="class:date;color:red">some</span> text with a <span class="date">date</span> and a <span style="class:nament;color:blue">Named Entity</span>'
    return render(request,'djciv_data/civet_ckeditor.html',context)

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
#        print('\nID:',st)
#        print('Lede:',textblock[st][0])
#        print('Content:',textblock[st][1])
        curtext = Text.objects.get(textid__exact=st)
        curtext.textlede = textblock[st][0]
        curtext.textmkup = textblock[st][1]  # need to add datetime and coder
        curtext.save()
 
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList})   
#    return HttpResponse("exiting save_edits: Just use the back key")

def more_edits(request):
    """ saves edits, then goes back to the collection selection """
    save_edits(request)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList})

def apply_markup(request):
    """ calls CIVET_utilities.do_markup() for each text block in the collection. """
    textblock = get_blocks(request.POST['editor1'])
    newstr = ''
    for st in textblock:
        newstr += make_markup_string([st,textblock[st][0],CIVET_utilities.do_markup(textblock[st][1])])
    context = {}
    context['current_collection'] = 'marked document'
    
    context['thetext'] = newstr
#    context['thetext'] = 'This is <span style="class:date;color:red">some</span> text with a <span class="date">date</span> and a <span style="class:nament;color:blue">Named Entity</span>'
    return render(request,'djciv_data/civet_ckeditor.html',context)

#    return HttpResponse("exiting apply_markup: Just use the back key")

def cancel_edits(request):
    """ Goes back to the collection selection without saving edits """
# might be useful to include a warning here...
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList})

    
def select_collection(request):
    """ case file selection for the text-extraction demo """
    CIV_template.BasicMode = False
    read_collection_directory(request, DEFAULT_COLLECTION_DIR)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList})

def operating_instructions(request):
    """ display page with basic instructions """
    return render(request,'djciv_data/operating_instructions.html',{})


# ======== basic coding template system (no mark-up) ========= #

def read_template(request):
    """ main routine for setting up a template: reads a file, checks for errors, and then either renders the form or 
        lists the errors """
    global ActiveTemplate
    CIV_template.init_template()
    if 'codername' in request.POST:
        CIV_template.codername = request.POST['codername']        
    if 'template_name' in request.FILES:
#        print('RT2:',request.FILES['template_name'])        
        st = request.FILES['template_name']
    else:
#        print('RT: Use demo')
        st = open('djciv_data/static/djciv_data/CIVET.demo.template.txt','r')
    thecontent = ''
    commln = CIV_template.get_commlines(st)
    while len(commln) > 0:
        thecontent += CIV_template.do_command(commln)
        commln = CIV_template.get_commlines(st)

#    print('thecontent:',thecontent)
    if len(CIV_template.SaveList) == 0:
        thecontent += '~Error~<p>A "save:" command is required in the template<br>\n'
    else:
        misslist = []
        for ele in CIV_template.SaveList:
            if ele not in CIV_template.VarList:
                misslist.append(ele)
        if len(misslist) > 0:
            thecontent += '~Error~<p>The following variables are in the "save:" command but were not declared in a data field<br>' + str(misslist) + '\n'

    if '~Error~' in thecontent:
        errortext = ''
        indx = thecontent.find('~Error~')
        while indx >= 0:
            indy = thecontent.find('\n',indx)
            errortext += thecontent[indx+7:indy+1]
            indx = thecontent.find('~Error~',indy)
        return render(request,'djciv_data/template_error.html', {'form_content' :  errortext})
    else:
        ActiveTemplate = thecontent
        CIV_template.create_TempData_header()
        CIV_template.BasicMode = True
        return render(request,'djciv_data/basic_form.html', {'form_content' : thecontent})
    
def save_basic(request):
    """ save data then return to template-based form """
    global ActiveTemplate
    CIV_template.save_to_TempData(request)
    return render(request,'djciv_data/basic_form.html', {'form_content' : ActiveTemplate})

def get_new_case(request):
    CIV_template.save_to_TempData(request)
    return render(request,'djciv_data/file_select.html')

def setup_download(request):
    print('SD-1: ',CIV_template.BasicMode,CIV_template.TempData[:128])
    context = {}
    context['filename'] = CIV_template.DefaultFileName
    if CIV_template.BasicMode:
        CIV_template.save_to_TempData(request)
        context['download_action'] = 'download_basicmode'
    else:
        CIV_template.save_case(request, ActiveCollection)
        context['download_action'] = 'download_data'
    print(context)
    return render(request,'djciv_data/setup_download.html',context)

"""def do_download(request):
    print('DD-1: ',CIV_template.BasicMode,CIV_template.TempData)
    if CIV_template.BasicMode:
        basicmode_download_data(request)
    else:
        download_data(request)
    return render(request,'djciv_data/setup_download.html',{'filename' :CIV_template.DefaultFileName})"""

def reset_data(request):
    """ 15.07.09: This needs to be broken into different sets of options for collections, basic mode """
    if CIV_template.BasicMode:
        CIV_template.create_TempData_header()
        return render(request,'djciv_data/basic_form.html',  {'form_content' : ActiveTemplate})
    else:
        Case.objects.all().delete()
        return render(request,'djciv_data/select_collection.html',{'files' : CollectionList})

def continue_coding(request):
    """ 15.07.09: This needs to be broken into different sets of options for collections, basic mode """
    if CIV_template.BasicMode:
        return render(request,'djciv_data/basic_form.html',  {'form_content' : ActiveTemplate})
    else:
        return render(request,'djciv_data/civet_coder.html',CoderContext)


# ======== coder with mark-up ========= #

def get_coder_template(request):
    """ main routine for setting up a template: reads a file, checks for errors, and then either renders the form or 
        lists the errors """
    global ActiveTemplate

    CIV_template.init_template()
#    print('GCT-1: ',CollectionForm)
    if len(CollectionForm) > 0:
        st = open(CollectionForm,'r')
    else:
#        print('RT: Use demo')
        st = open('djciv_data/static/djciv_data/CIVET.demo.coder.template.txt','r')
    thecontent = ''
    commln = CIV_template.get_commlines(st)
    while len(commln) > 0:
        thecontent += CIV_template.do_command(commln)
        commln = CIV_template.get_commlines(st)

#    print('thecontent:',thecontent)
    if len(CIV_template.SaveList) == 0:
        thecontent += '~Error~<p>A "save:" command is required in the template<br>\n'
    else:
        misslist = []
        for ele in CIV_template.SaveList:
            if ele not in CIV_template.VarList:
                misslist.append(ele)
        if len(misslist) > 0:
            thecontent += '~Error~<p>The following variables are in the "save:" command but were not declared in a data field<br>' + str(misslist) + '\n'

    if '~Error~' in thecontent:
        errortext = ''
        indx = thecontent.find('~Error~')
        while indx >= 0:
            indy = thecontent.find('\n',indx)
            errortext += thecontent[indx+7:indy+1]
            indx = thecontent.find('~Error~',indy)
        return render(request,'djciv_data/template_error.html', {'form_content' :  errortext})
    else:
        ActiveTemplate = thecontent
        return  thecontent

def code_collection(request):
    """ Translates the style/title-based <span> markup used in ckeditor into the class-based markup used by civet_coder """
# Still need to do:
# 1. Add document ID and comments
# 2. Integrate with the form
    global ActiveCollection, CoderContext
    context = {}
#    print('CC-Mk1:')
#    print('CC-Mk1:',request.POST['current_collection'])
#    context['current_collection'] = request.POST['current_collection']
    context['docidst'] = 'Document ID'
    context['doccmtst'] = 'Document comments'
#    context['markedtext'] = 'This is <span style="class:date;color:red">some</span> text with a <span class="date">date</span> and a <span class="nament">Named Entity</span>'
    if 'editor1' in request.POST:
        cktext =  request.POST['editor1']  # called following editing
    else:
        if 'current_collection' in request.POST:
            ActiveCollection = request.POST['current_collection']
        cktext = get_collection_markup()  # called directly from a select
    # do the standard replacements
    cktext = cktext.replace('style="class:nament; color:blue"','class="nament"') 
    cktext = cktext.replace('style="class:num; color:green"','class="num"')
#    print('Incoming:\n',cktext)
#   replace each unique termst/style/title combination with a class=termstNN 
    termdict = {}
    idx = cktext.find('style="class:termst')
    while idx >= 0:
        tag = cktext[idx: cktext.find('>',idx)]  # not absolutely necessary but probably clearer and safer...
        title = tag.partition('title="')[2][:-1]
        if title not in termdict:
            colorst = tag.partition('color:')[2]
            termdict[title] = [tag,colorst[:colorst.find('"')]]
        idx = cktext.find('style="class:termst',idx+8)
    kterm = 1
    termstyles = ''  # generate the new termst styles
    theform = get_coder_template(request)  # also replace these in the form
    for ti in termdict:
#        print(ti, termdict[ti])
        newterm = 'termst{:02d}'.format(kterm)
        kterm += 1
        termstyles += '.' + newterm + '  {color:' + termdict[ti][1] + ';}\n'
        cktext = cktext.replace(termdict[ti][0],'class="' + newterm + '"') # <span> markup 
        theform = theform.replace('=^=' + ti + '=^=',newterm) # <span> markup 
     
    CoderContext['form_content'] = theform
#    cktext = cktext.replace('style="class:termst; color:red"','class="termst"') 
#    print('Styles:\n',termstyles)
#    print('Edited:\n',cktext)
    CoderContext['markedtext'] = cktext
    CoderContext['newterm'] = termstyles
    return render(request,'djciv_data/civet_coder.html',CoderContext)

def save_and_return(request):
    CIV_template.save_case(request, ActiveCollection)
    return render(request,'djciv_data/civet_coder.html',CoderContext)
    
def save_and_new(request):
    CIV_template.save_case(request, ActiveCollection)
    print('SaN-Mk1:',CollectionList)
    return render(request,'djciv_data/select_collection.html',{'files' : CollectionList})
    
    


# ======== navigation placeholders and utilities ========= #

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
        