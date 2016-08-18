##	civet_utilities.py
##
##  Assorted utilities for CIVET, mostly handling workspace files
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
import datetime
import json
import sys
import ast
import re

from django.utils import encoding   # used for utf-8 -> ascii conversion

from .models import Collection, Text, Case

import civet_settings
import civet_form

collfields = ['collid','colldate','colledit', 'collcmt']
textfields = ['textid','textdate', 'textdelete', 'textpublisher','textpubid', 'textbiblio', 'textlicense', 
              'textgeogloc', 'textlede', 'textcmt','textmkupdate','textmkupcoder']
casefields = ['casedate', 'casecoder', 'casecmt']

thetext = ''
StopList = []  # words that will not be marked as NEs if capitalized in isolation
NumberDict = {} # words referring to numbers and their values

catindent = '    '

AttrPattern = re.compile('(\S*)\s?=\s?\"(.*?)\"\s*')  # regular expression used in get_attributes()

# ======== YAML I/O ========= #

def read_YAML_file(fin,filename):
    """ Reads a single collection YAML file from filename; returns dictionary from Collection; 
        lists of dictionaries for Text, Case
        This converts utf-8 to ASCII, which needs to be changed in the relatively near future, though probably not until
        we convert the whole thing to Python 3.0
    """
        
    def create_ascii(str):
        return encoding.smart_str(str, encoding='ascii', errors='ignore')

    collinfo = {}
    collinfo['collfilename'] = filename[:-4]
    collinfo['collid'] = filename[:-4]  # default 

    textdicts = []
    casedicts = []
    civet_form.CategoryDict = {}

#    fdbg = open('../debugging.txt','w')
#    print('GYF-0:')

    line = create_ascii(fin.readline())             
     
    while len(line) > 0 and not line.startswith('texts:'):  # could doc, headline, source info here
#        print('>>',line[:-1])
#        fdbg.write('>>'+line)
        if len(line) > 4 and line[:line.find(':')] in collfields:
            thefield = line[:line.find(':')].strip()
            collinfo[thefield] = line[line.find(':')+1:-1].strip()
            if 'date' in thefield and ':' in collinfo[thefield]:  # temporary fix removing times from the dates
                collinfo[thefield] = collinfo[thefield][:collinfo[thefield].find(' ')]
        elif line.startswith('categories:'):
            line = create_ascii(fin.readline())
            while line.startswith(catindent):
#                fdbg.write('-->>'+line)
                if line.startswith(catindent + '- '):
                    civet_form.CategoryDict[curcat].append(line[6:-1])
                else:
                    curcat = line[4:line.find(':')]
                    civet_form.CategoryDict[curcat] = []                                
                line = create_ascii(fin.readline())             
        
            """for la in civet_form.CategoryDict:  # DEBUG
                print(la,civet_form.CategoryDict[la])"""
#                fdbg.write(la + ' : ' + str(CategoryDict[la]) + '\n')
            catst = json.dumps(civet_form.CategoryDict)
#            print('##:',catst)
            collinfo['collcat'] = catst
         
        line = create_ascii(fin.readline())             

    if 'collcat' not in collinfo:
        collinfo['collcat'] = ''        
               
    if len(line) == 0:
        raise Exception('No "texts:" segment found')
                
    """print('GYF-1:')
    for k,v in collinfo.iteritems(): 
        print(k, v)"""     
    
    while len(line) > 0 and not line.strip().startswith('-'):  
        line = create_ascii(fin.readline())
    curinfo = {} # read the text blocks
    while len(line) > 0 and not line.startswith('cases:'):
        if line.strip().startswith('-'):
#            print('Mk2',line[:-1]) 
            if 'textparent' in curinfo: # don't write until we've got something
                curinfo['textdate'] = '2000-01-01'  # temporary                
                textdicts.append(curinfo) 
                curinfo = {}
 
            for st in textfields:  # also initialize mkup and original
                curinfo[st] = ''
            curinfo['textparent'] = collinfo['collid']
            curinfo['textid'] = line[line.find(':')+1:-1].strip()
            curinfo['textmkup'] = ''  # set these to defaults
            curinfo['textmkupdate'] = '1900-01-01'

        if line.strip().startswith('textmkup:') and '|' not in line:  # textmkup can be null, so just use the defaults
            line = create_ascii(fin.readline())             
        elif line.strip().startswith('textmkup:') or line.strip().startswith('textoriginal:'): 
#            print('Mk2',line[:-1]) 
            field = line[:line.find(':')].strip()
            line = create_ascii(fin.readline()) 
            indentst = line[:len(line) - len(line.lstrip())]
            alltext = ''
            while line.startswith(indentst):  # add the markup
        #        print('>>>>',line[:-1])
                if line[:-1] == indentst:
                    alltext +=' <br> '
                else:
                    alltext += line
                line = fin.readline()
                line = create_ascii(fin.readline())              
            curinfo[field] = alltext 
        elif line[:line.find(':')].strip() in textfields:
            thefield = line[:line.find(':')].strip()
            curinfo[thefield] = line[line.find(':')+1:-1].strip()
            if 'textdelete' in thefield:  # temporary fix removing times from the dates
                if 'False' in curinfo[thefield]:
                    curinfo[thefield] = False
                else:
                    curinfo[thefield] = True                    
            elif 'date' in thefield and ':' in curinfo[thefield]:  # temporary fix removing times from the dates
                curinfo[thefield] = curinfo[thefield][:curinfo[thefield].find(' ')]

    #        print('>>>',line[:-1])
            line = create_ascii(fin.readline())

        else:
            line = create_ascii(fin.readline())


    textdicts.append(curinfo) 
# --    print("GYF-2: Texts:\n")  # -- DEBUG
    for dc in textdicts:
        """if dc['textid'] == '2014-06-20_LBY_NR000':
            for k in textfields:
                if k in dc: print(k, dc[k])
            print('textoriginal:', dc['textoriginal'])
            print('textmkup:', dc['textmkup'])"""
            
    if len(line)>0: # get the previously coded cases
        while len(line) > 0 and not line.strip().startswith('-'):  
            line = create_ascii(fin.readline())
        curinfo = {} # read the case blocks
        while len(line) > 0:
            if line.strip().startswith('-'):
    #            print('Mk2',line[:-1]) 
                if 'caseparent' in curinfo: # don't write until we've got something
                    curinfo['textdate'] = '2000-01-01'  # temporary                
                    casedicts.append(curinfo) 
                    curinfo = {}
 
                for st in casefields:  # also initialize mkup and original
                    curinfo[st] = ''
                curinfo['caseparent'] = collinfo['collid']
                curinfo['caseid'] = line[line.find(':')+1:-1]

            if line.strip().startswith('casevalues:'): 
    #            print('Mk2',line[:-1]) 
                line = create_ascii(fin.readline()) 
                indentst = line[:len(line) - len(line.lstrip())]
                alltext = ''
                while line.startswith(indentst):  # add the markup
            #        print('>>>>',line[:-1])
                    alltext += line.strip()
                    line = create_ascii(fin.readline())
                try:
                    caseval = ast.literal_eval(alltext)
                except:
                    raise Exception('The following string of variable values in caseid ' + curinfo['caseid'] + '<blockquote>' + alltext + \
                                    '</blockquote>cannot be processed because it contains a formatting error. This case occurs ')
                curinfo['casevalues'] = alltext 
            
            elif line[:line.find(':')].strip() in casefields:
                thefield = line[:line.find(':')].strip()
                curinfo[thefield] = line[line.find(':')+1:-1].strip()
                if 'date' in thefield and ':' in curinfo[thefield]:  # temporary fix removing times from the dates
                    curinfo[thefield] = curinfo[thefield][:curinfo[thefield].find(' ')]

                line = create_ascii(fin.readline())

            else:
                line = create_ascii(fin.readline())

        casedicts.append(curinfo) 
        
        """print("GYF-3: Cases:\n")
        for dc in casedicts:
            print()
            for k in casefields:
                if k in dc: print(k, dc[k])
            print('casevalues:', dc['casevalues'])"""

#    print("RYF-exit\n")
    """fdbg.write("RYF-exit\n")
    fdbg.close()"""
    return collinfo, textdicts, casedicts

def write_YAML_file(thecoll, filehandle):
    """ writes the Collection thecoll to filehandle in YAML format"""
    indent1 = '    '
#    print('WYF-1:', collid)
#    thecoll = Collection.objects.get(collid__exact=collid)
    colldict = thecoll.__dict__
    for flst in collfields:
        if flst == 'colldate' or flst == 'colledit':
            filehandle.write(flst+ ': ' + colldict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
        else:
            filehandle.write(flst+ ': ' + colldict[flst] + '\n')
#    print('WYF-2:', colldict)

    if colldict['collcat']:
        catdict = json.loads(colldict['collcat'])
        filehandle.write('\ncategories:\n')
        for cati in catdict:
            filehandle.write(indent1 + cati + ':\n')
            for li in catdict[cati]:
                filehandle.write(indent1 + '- ' + li + '\n')
            
    filehandle.write('\ntexts:\n')
    
    curtexts = Text.objects.filter(textparent__exact=thecoll.collid)  # write the texts
    for ct in curtexts:
        textdict = ct.__dict__
        filehandle.write('\n  - textid: ' + textdict['textid'] + '\n')
#        print('WYF-3:', textdict)
        for flst in textfields[1:-2]:
            if flst in textdict:
                if flst == 'textdate':
                    if textdict[flst]:  # allow possibility of no markup date
                        filehandle.write('    ' + flst + ': ' + textdict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
                elif flst == 'textdelete':
                    filehandle.write('    ' + flst + ': ' + str(textdict[flst]) + '\n')
                else:
                    filehandle.write('    ' + flst + ': ' + textdict[flst] + '\n')
        filehandle.write('    textoriginal: |\n')
        for ls in textdict['textoriginal'].split('\n'):
            filehandle.write('        ' + ls + '\n')
        filehandle.write('    textmkup: |\n')
        for ls in textdict['textmkup'].split('\n'):
            filehandle.write('        ' + ls + '\n')
        for flst in textfields[-2:]:
            if flst in textdict:
                if flst == 'textmkupdate':
                    if textdict[flst]:  # allow possibility of no markup date
                        filehandle.write('    ' + flst+ ': ' + textdict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
                else:
                    filehandle.write('    ' + flst+ ': ' + textdict[flst] + '\n')
    
    curcases = Case.objects.filter(caseparent__exact=thecoll.collid)  # write the cases
    if len(curcases) > 0:
        filehandle.write('\ncases:\n')   
        for ct in curcases:
            casedict = ct.__dict__
#            print('WYF-4:', casedict)
            filehandle.write('\n  - caseid: ' + casedict['caseid'] + '\n')
            for flst in casefields:
                if flst in casedict:
                    if flst == 'casedate':
                        if casedict[flst]:  # not needed when everything is operational
                            filehandle.write('    ' + flst + ': ' + casedict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
                    else:
                        filehandle.write('    ' + flst + ': ' + casedict[flst] + '\n')
        
            filehandle.write('    casevalues: >\n        {\n')
#            print('-->',casedict['casevalues'])
            caseval = ast.literal_eval(casedict['casevalues'])  # this was checked for errors at the input level
#            print('WYF-5:', caseval)
            if '_discard_' in caseval and caseval['_discard_']:
                 filehandle.write("        '_discard_': 'True'\n")
            elif '_delete_' in caseval:
                for avar, st in caseval.iteritems():  # this does the output in the order given in the template
                    filehandle.write("        '" + avar + "': '" + st + "',\n")
            else: 
                """print('WFY-6', civet_form.SaveList)
                print('WFY-7', caseval)"""
                for avar in civet_form.SaveList:  # this does the output in the order given in the template
                    if avar in civet_form.CheckboxValues:  # translate T/F to values for checkboxes
                        if caseval[avar] == 'True':
                            st = civet_form.CheckboxValues[avar][1]
                        else:
                            st = civet_form.CheckboxValues[avar][0]                      
                    else:
                        st = caseval[avar].replace("'","\\'")
                    filehandle.write("        '" + avar + "': '" + st + "',\n")
            filehandle.write("        }\n")
    
    
# ============ apply_markup functions ================ #

def read_stoplist():
    """ read standard stoplist from the static directory """
    with open(civet_settings.STATIC_FILE_PATH + 'CIVET.stopwords.txt','r') as fin:
        for line in fin:
            if len(line) > 1:
                if line[0] != '#':
                    if '#' in line:   # deal with possible comments
                        word = line.partition('#')[0].strip()
                    else:
                        word = line.strip()                
                    if len(word) > 1:  # or we could just put 'A' and 'I' in there and save a conditional...
                        StopList.append(word[0].upper() + word[1:])
                    else:
                        StopList.append(word.upper())            
  
def read_numberlist():
    """ read standard number list from the static directory """
    """ 15.08.11 p.a.s. Various notes on this:
    1. Since this is an internal file, I'm just ignoring lines with missing [] rather than reporting an error, though at some 
    point that might be a good idea. 
    2. It may or may not be appropriate to make sure these are actually numbers, or at least warn when they aren't.
    3. Because a terminal space is added to the word (in order to avoid partial matches), these  words won't match before 
    punctuation, though that is unusual for number-words.
    """
    with open(civet_settings.STATIC_FILE_PATH + 'CIVET.numberwords.txt','r') as fin:
        for line in fin:
            if len(line) > 1:
                if line[0] != '#':
                    if '#' in line:   # deal with possible comments
                        phrase = line.partition('#')[0].strip()
                    else:
                        phrase = line.strip()
                    if '[' in phrase:
                        part = line.partition('[')
                        if ']' in part[2]:
                            word = part[0].strip() + ' '
                            value = part[2][:part[2].find(']')].strip()
                            NumberDict[word[0].upper() + word[1:]] = value
                            NumberDict[word] = value                
                        else:
                            pass # error messages could eventually go here               
                    else:
                        pass
                        # put some sort of error message here               
#    print(NumberDict) 
  

def make_oktext():
    """ splits thetext into a list that separates out <span></span> blocks and returns same """
    """ pas 15.07.23: This is used to avoid marking text that has already been marked, thus prevented, e.g. "killed" being marked 
    in "shot and killed", assuming the longer phrase had been coded first (and conversely, if "killed" had precedence, 
    "shot and killed" would not be matched, which could also be a useful feature. There is probably some more elegant
    way to do this but this works.
    """ 
    global thetext 
    oktext = []
    indc = 0
    idx = thetext.find('<span')
    while idx > 0:
        oktext.append(thetext[indc:idx])
        indc = thetext.find('</span>',idx)
        oktext.append(thetext[idx:indc+7])
        indc += 7
        idx = thetext.find('<span',indc)
    oktext.append(thetext[indc:])
    """print('\n-------------')
    for st in oktext:
        print(st)"""
    return oktext


def add_span_tag(curtext,telltale,classt, colorst):
    """ Replaces telltale in curtext with a span tag with classt: colorst""" 
    idx = curtext.find(telltale)
    while idx > 0:
        indb = curtext.find(telltale,idx+3)
        curtext = curtext[:idx] + '<span style="class:' + classt +';color:' + colorst + ';">' + curtext[idx+3:indb] + "</span>" + curtext[indb+3:]  
        idx = curtext.find(telltale,indb+3)
    return curtext


def do_geog_markup():
    """ Mark geographical entities based on preceding preposition and capitalization """
    global thetext
    if len(StopList) == 0:
        read_stoplist()
    geogwords = []
    strg = '|'.join(civet_settings.GEOG_PREPOSITIONS)
#    print('DGM-enter',strg)
    pat1 = re.compile(r' (' + strg + ') [A-Z]') ## make this a global
    """tarst = ' in Yemen from Aden to Sanaa at Taiz '
    idx = 0
    curmatch = pat1.search(tarst,idx)
    while curmatch:
        print('DGM-0',idx, tarst[curmatch.start():curmatch.end()],curmatch.group())
        idx = curmatch.end()
        curmatch = pat1.search(tarst,idx)"""
       
    oktext = make_oktext()
    for curtext in oktext: 
        if curtext.startswith('<span'):  # do not try to code anything that has already been marked
            continue
#        print('DGM-1.0 \"'+curtext+'\"')
        idx = 0
        curmatch = pat1.search(curtext, idx)
        while curmatch:
            wordstart = curtext.find(' ',curmatch.start()+1)  # skip the preposition
            endx = curtext.find(' ',wordstart+1)  # go to end of capitalized word
            if endx < 0:
                endx = len(curtext)-1
            while endx < len(curtext)-1:  # check for subsequent cap words
                if curtext[endx-1] in [',','.','?','"','\'','!','\n','\t']:
                    endx -= 1
                    break
                elif curtext[endx+1].isupper():
                    endx = curtext.find(' ',endx+1)  # go to end of capitalized word
                    if endx < 0:
                        break                    
                else:
                    break
#            print('DGM-1.1',curtext[wordstart:endx])
            if curtext[wordstart+1:endx] not in StopList:
                geogwords.append(curtext[wordstart:endx])
                    
            idx = endx + 1
            curmatch = pat1.search(curtext, idx)
    
#        print('DGM-2:',geogwords)
        
        for ka, curtext in enumerate(oktext):  # enumerate because we need to change oktext[ka]
            for word in geogwords:
                idx = 0
                while word in curtext[idx:]:  # leading blank in word will not match marked cases
                    idx = curtext.find(word,idx)
                    if curtext[idx+len(word)] in [' ',',','.','?','"','\'','!','\n','\t']:
                        curtext = curtext[:idx+1] + '=~=' + word[1:] + '=~=' + curtext[idx+len(word):]
#                        print('DGM-3: "' + curtext + '\"')
                    else:
                        idx += 1
            oktext[ka] = add_span_tag(curtext,'=~=','geogent', 'brown')

    thetext = ''.join(oktext) 


def do_NE_markup():
    """ Mark named-entities based on capitalization """
    global thetext
#    print('DNM-entry')
    if len(StopList) == 0:
        read_stoplist()
    pat1 = re.compile(r' (al-|bin-|ibn-|)?[A-Z]') # make this a global   
    oktext = make_oktext()
    for ka, curtext in enumerate(oktext):
        if curtext.startswith('<span'):  # do not try to code anything that has already been marked
            continue
        idx = 0
        curmatch = pat1.search(curtext, idx)
        while curmatch:
#            print('DNM1:',curtext[curmatch.start()-1:curmatch.start()+8])
            endx = curtext.find(' ',curmatch.start()+1)
            while curtext[endx-1] in [',','.','?','"','\'','!','\n','\t']:
                endx -= 1
            curtext = curtext[:curmatch.start()+1] + '=~=' + curtext[curmatch.start()+1:endx]  + '=~=' + curtext[endx:]
            idx = endx
            curmatch = pat1.search(curtext, idx)
    
        curtext = curtext.replace('=~= =~=',' ')
#        print('DNM2:',curtext)
        idx = curtext.find('=~=')
        while idx >= 0:
            idend = curtext.find('=~=',idx+1)
            if idend < 0:
                break
            else:
                idend += 3
#            print('DMN3: ',curtext[idx:idend],':',curtext[idx+3:idend-3])
            if ' ' not in curtext[idx+3:idend] and curtext[idx+3:idend-3] in StopList: # remove markup from single-word stopwords
                curtext = curtext[:idx] + curtext[idx+3:idend-3] + curtext[idend:]
#                print('  ==>',curtext[idx:idend])
            idx = curtext.find('=~=',idend+1)
#            print('  ++>',idx)            

        oktext[ka] = add_span_tag(curtext,'=~=','nament', 'blue')

    thetext = ''.join(oktext) 

def do_numberword_markup():
    """ Annotate number words with their values in brackets """
    global thetext
    if len(NumberDict) == 0:
        read_numberlist()
    oktext = make_oktext()
    for ka, curtext in enumerate(oktext):
        if curtext.startswith('<span'):  # do not try to code anything that has already been marked
            continue
        endx = 0
        for tar in NumberDict:
            curmatch = curtext.find(tar)
            if curmatch >= 0:
                endx = curmatch + len(tar)
                phrase = tar
                break
        while curmatch >=0:       
            if curmatch == 0 or curtext[curmatch-1] == ' ':  # space is the initial boundary condition
                curtext = curtext[:curmatch] + '=~=' + phrase + ' [' + NumberDict[phrase]  + '] =~=' + curtext[endx:]
                endx = curtext.find('=~=',endx+6) # this should get us to a point where we catch the second =~=
            for tar in NumberDict:
                curmatch = curtext.find(tar,endx)
                if curmatch >= 0:
                    endx = curmatch + len(tar) + 1
                    phrase = tar
                    break
            if len(curtext) > 256:
                curmatch = -1
        oktext[ka] = add_span_tag(curtext,'=~=','num', 'green')

    thetext = ''.join(oktext) 

def do_number_markup():
    """ annotate numbers """
    global thetext
    pat1 = re.compile(r' [1-9]')    
    oktext = make_oktext()
    for ka, curtext in enumerate(oktext):
        idx = 0
        curmatch = pat1.search(curtext, idx)
        while curmatch:
            endx = curtext.find(' ',curmatch.start()+1)
            if curtext[endx-1] in [',','.','?','"','\'','!']:
                endx -= 1
            curtext = curtext[:curmatch.start()+1] + '=+=' + curtext[curmatch.start()+1:endx]  + '=+=' + curtext[endx:]
            idx = endx
            curmatch = pat1.search(curtext, idx)
        oktext[ka] = add_span_tag(curtext,'=+=','num', 'green')

    thetext = ''.join(oktext) 

    
def do_string_markup(category):
    """ annotate the user-specified categories """ 
    # pas 15.07.23: The two-step process of using tell-tales '=$=' probably isn't needed -- one could go directly to the 
    # eventual <span></span> version -- but it keeps the first loop a bit simpler  
    global thetext
    marklist = []
    for st in civet_form.UserCategories[category][2:]:
        marklist.append(' ' + st)
    for st in marklist:
        allup = st.isupper()
        if not allup:
            lowst = st.lower()
        oktext = make_oktext()
        for ka, curtext in enumerate(oktext):
            if curtext.startswith('<span'):  # do not try to code anything that has already been marked
                continue
            if allup:
                idx = curtext.find(st)
            else:
                idx = curtext.lower().find(lowst)
            while idx > 0:
#                print('DSM1:',st)
                endx = curtext.find(' ',idx+len(st))
                if endx < 0:
                    endx = len(curtext) - 1
                while curtext[endx-1] in [',','.','?','"','\'','!','\n','\t']:
                    endx -= 1
                if endx == idx+len(st):  # only use complete matches except for punctuation: dropping this would allow stemming and that could be added as a option at some point
                    if category in civet_form.CategoryCodes:
                        code = ' [' + civet_form.CategoryCodes[category][st.strip()] + ']'
                        if code == ' []':
                            code = ''
                    else:
                        code = ''
                    curtext = curtext[:idx+1] + '=$=' + category + '=$=' + st[1:] + code  + '=$=' + curtext[endx:]
                    idx = curtext.find(st,endx+len(category+code)+6)
                else:
                    idx = curtext.find(st,endx+1)

            idx = curtext.find('=$=')
            while idx > 0:
                indb = curtext.find('=$=',idx+3)
                indc = curtext.find('=$=',indb+3)
                curtext = curtext[:idx] + '<span style="class:' + civet_form.UserCategories[category][1] + ';color:' + \
                        civet_form.UserCategories[category][0] +  '">'  + curtext[indb+3:indc] + "</span>" + curtext[indc+3:] 
                idx = curtext.find('</span>',idx+3)
                idx = curtext.find('=$=',idx+3)
                
            oktext[ka] = curtext
                
        thetext = ''.join(oktext) 


def do_markup(oldtext):
    global thetext
#    print('DM-entry',oldtext)
    thetext = oldtext + ' '
    for cat in civet_form.UserCategories:
        do_string_markup(cat)
    if civet_settings.HIGHLIGHT_NUM:
        do_numberword_markup()    
    if civet_settings.USE_GEOG_MARKUP:
        do_geog_markup()
    if civet_settings.HIGHLIGHT_NAMENT:
        do_NE_markup()
    if civet_settings.HIGHLIGHT_NUM:
        do_number_markup()
#    print('DM-exit:',thetext)
    return thetext

    
def get_styles():
    """ creates the civet_styles for ckeditor """
    thestyles = civet_settings.DEFAULT_CKEDITOR_STYLES
    for cat in civet_form.UserCategories:
        thestyles += "\n{ name: '" + cat + "', element: 'span', styles: { 'class':'" + cat + \
         "', 'color': '"
        if ' ' in civet_form.UserCategories[cat][0]:
            thestyles +=  civet_form.UserCategories[cat][0][:civet_form.UserCategories[cat][0].find(' ')] + "' }  },"
        else:
            thestyles +=  civet_form.UserCategories[cat][0] + "' }  },"
    return thestyles


# ======== Miscellaneous utilities ========= #

def get_attributes(strg):
    """ returns a dictionary of the attributes and their values from an HTML tag string; 'tag' is the tag itself 
        This is not a generic tag parser: it is meant to be used on tags generated internally so these follow a known format 
    """
    attr = {}
    strg = strg.strip()
    attr['tag'] = strg[strg.find('<')+1:strg.find(' ')]
    for m in AttrPattern.finditer(strg):
        tag, value = m.groups()
        attr[tag] = value
    return attr
    
def unimplemented_feature(st):
    return '<h2>The option "' + st + '" has yet to be implemented.</h2><p><h3>Use the back arrow in your browser to return to the previous screen.</h3>'
    
'''def hello():
    print('Hey, I\'m here!')'''
