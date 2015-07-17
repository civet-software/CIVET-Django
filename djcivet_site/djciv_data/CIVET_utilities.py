from __future__ import print_function
import datetime
import re

from .models import Collection, Text, Case

import CIV_template

collfields = ['collid','colldate','colledit', 'collcmt']
textfields = ['textid','textdate','textpublisher','textpubid','textlicense', 'textlede', 'textcmt','textmkupdate','textmkupcoder']
casefields = ['casedate', 'casecoder', 'casecmt']

thetext = ''

def get_YAML_file(filename):
    """ Reads a YAML file from filename; returns dictionary from Collection; lists of dictionaries for Text, Case"""
    ## STILL NEED TO ADD CASE INPUT
    collinfo = {}
    collinfo['collfilename'] = filename[:-4]
    collinfo['collid'] = filename[:-4]  # default 

    textdicts = []

    fin = open(filename,'r')
    line = fin.readline() 
    while not line.startswith('texts:'):  # could doc, headline, source info here
#        print('>>',line[:-1])
        if len(line) > 4 and line[:line.find(':')] in collfields:
            collinfo[line[:line.find(':')]] =  line[line.find(':')+1:-1].strip()
        line = fin.readline() 
                
    """print('GYF-1:')
    for k,v in collinfo.iteritems(): 
        print(k, v)"""      
    
    while len(line) > 0 and not line.strip().startswith('-'):  
        line = fin.readline()
    curinfo = {} # read the text blocks
    while len(line) > 0:
        if line.strip().startswith('-'):
#            print('Mk2',line[:-1]) 
            if 'textparent' in curinfo: # don't write until we've got something
                curinfo['textdate'] = '2000-01-01'  # temporary                
                textdicts.append(curinfo) 
                curinfo = {}
 
            for st in textfields:  # also initialize mkup and original
                curinfo[st] = ''
            curinfo['textparent'] = collinfo['collid']
            curinfo['textid'] = line[line.find(':')+1:-1]

        if line.strip().startswith('textmkup:') or line.strip().startswith('textoriginal:'): 
#            print('Mk2',line[:-1]) 
            field = line[:line.find(':')].strip()
            line = fin.readline() 
            indentst = line[:len(line) - len(line.lstrip())]
            alltext = ''
            while line.startswith(indentst):  # add the markup
        #        print('>>>>',line[:-1])
                alltext += line
                line = fin.readline() 
            curinfo[field] = alltext 
        elif line[:line.find(':')].strip() in textfields:
            curinfo[line[:line.find(':')].strip()] = line[line.find(':')+1:-1].strip()
    #        print('>>>',line[:-1])
            line = fin.readline()
        else:
             line = fin.readline()

    textdicts.append(curinfo) 
    """print("GYF-2: Texts:\n")
    for dc in textdicts:
        print()
        for k in textfields:
            if k in dc: print(k, dc[k])
        print('textoriginal:', dc['textoriginal'])"""
            
    return collinfo, textdicts

def write_YAML_file(thecoll, filehandle):
    """ writes the Collection thecoll to filehandle in YAML format"""
#    print('WYF-1:', collid)
#    thecoll = Collection.objects.get(collid__exact=collid)
    colldict = thecoll.__dict__
    for flst in collfields:
        if flst == 'colldate' or flst == 'colledit':
            filehandle.write(flst+ ': ' + colldict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
        else:
            filehandle.write(flst+ ': ' + colldict[flst] + '\n')
#    print('WYF-2:', colldict)
    filehandle.write('\ntexts\n')
    
    curtexts = Text.objects.filter(textparent__exact=thecoll.collid)  # write the texts
    for ct in curtexts:
        textdict = ct.__dict__
        filehandle.write('\n  - textid: ' + textdict['textid'] + '\n')
        print('WYF-3:', textdict)
        for flst in textfields[1:-2]:
            if flst in textdict:
                if flst == 'textdate':
                    if textdict[flst]:  # allow possibility of no markup date
                        filehandle.write('    ' + flst + ': ' + textdict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
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
    
    curcases = Case.objects.filter(caseparent__exact=thecoll.collid)  # write the texts
    if len(curcases) > 0:
        filehandle.write('\ncases\n')   
        for ct in curcases:
            casedict = ct.__dict__
            print('WYF-4:', casedict)
            filehandle.write('\n  - caseid: ' + casedict['caseid'] + '\n')
            for flst in casefields:
                if flst in casedict:
                    if flst == 'casedate':
                        if casedict[flst]:  # not needed when everything is operational
                            filehandle.write('    ' + flst + ': ' + casedict[flst].strftime("%Y-%m-%d %H:%M:%S") + '\n')
                    else:
                        filehandle.write('    ' + flst + ': ' + casedict[flst] + '\n')
        
            filehandle.write('    casevalues: \n')
            caseval = ct.get_values()
            CIV_template.set_SaveList()  # DEBUG
            print('WYF-5:', CIV_template.SaveList)
            for st in CIV_template.SaveList:
                filehandle.write('        ' + st + ': ' + caseval[st] + '\n')


def hello():
    print('Hey, I\'m here!')
    
    
# ============ apply_markup functions ================ #

def add_span_tag(telltale,classt, colorst):
    """ Replaces telltale with a span tag with classt: colorst""" 
    global thetext
    idx = thetext.find(telltale)
    while idx > 0:
        indb = thetext.find(telltale,idx+3)
        thetext = thetext[:idx] + '<span style="class:' + classt +'; color:' + colorst + '">' + thetext[idx+3:indb] + "</span>" + thetext[indb+3:]  
#                    print(line)                                        
        idx = thetext.find(telltale,indb+3)

def do_NE_markup():
# this does an initial search for words that are not at the beginning of the sentences, which for ADS is preceded by two 
# blanks: this will need to be generalized. Saves these and then does a second search to catch proper nouns that could be
# at the beginning.
# also this is assuming the 4-char indent 
    global thetext
    newords = []
    pat1 = re.compile(r' [A-Z]')    
    idx = 0
    curmatch = pat1.search(thetext, idx)
    while curmatch:
#        print(thetext[curmatch.start()-1:curmatch.start()+8])
        if thetext[curmatch.start()-1] != ' ': # only look at words not at beginning of sentence
#            print('Mk1')
            endx = thetext.find(' ',curmatch.start()+1)
            if thetext[endx-1] in [',','.','?','"','\'','!','\n','\t']:
                endx -= 1
            if endx - curmatch.start() > 4:
                stem = ' ' + thetext[curmatch.start()+1:curmatch.start()+5] 
                if stem not in newords: # shorter strings are probably abbreviations
                    newords.append(stem)
            thetext = thetext[:curmatch.start()+1] + '=~=' + thetext[curmatch.start()+1:endx]  + '=~=' + thetext[endx:]
            idx = endx
        else:
            idx = curmatch.end()
#            print('Mk2', curmatch.start(),curmatch.end(),idx, thetext[idx:idx+8])
        curmatch = pat1.search(thetext, idx)
    for st in newords:
#        print(st)
        idx = thetext.find(st)
        while idx > 0:
            endx = thetext.find(' ',idx+1)
            thetext = thetext[:idx+1] + '=~=' + thetext[idx+1:endx]  + '=~=' + thetext[endx:]
            idx = thetext.find(st,endx)
    
    thetext = thetext.replace('=~= =~=',' ')
    add_span_tag('=~=','nament', 'blue')

def do_number_markup():
    global thetext
    pat1 = re.compile(r' [1-9]')    
    idx = 0
    curmatch = pat1.search(thetext, idx)
    while curmatch:
        endx = thetext.find(' ',curmatch.start()+1)
        if thetext[endx-1] in [',','.','?','"','\'','!']:
            endx -= 1
        thetext = thetext[:curmatch.start()+1] + '=+=' + thetext[curmatch.start()+1:endx]  + '=+=' + thetext[endx:]
        idx = endx
        curmatch = pat1.search(thetext, idx)
    add_span_tag('=+=','num', 'green')
    
def do_string_markup(category,termlist, termcolor):
    global thetext
    marklist = []
    for st in termlist:
        marklist.append(' ' + st)
        marklist.append(' ' + st[0].upper() + st[1:])
    for st in marklist:
#        print(st)
        idx = thetext.find(st)
        while idx > 0:
            endx = thetext.find(' ',idx+1)
            if thetext[endx-1] in [',','.','?','"','\'','!','\n','\t']:
                endx -= 1
            thetext = thetext[:idx+1] + '=$=' + category + '=$=' + thetext[idx+1:endx]  + '=$=' + thetext[endx:]
            idx = thetext.find(st,endx+len(category)+6)

    idx = thetext.find('=$=')
    while idx > 0:
        indb = thetext.find('=$=',idx+3)
        indc = thetext.find('=$=',indb+3)
        thetext = thetext[:idx] + '<span style="class:termst; color:' + termcolor + '" title="' + thetext[idx+3:indb] + '">'  + thetext[indb+3:indc] + "</span>" + thetext[indc+3:] 
        idx = thetext.find('</span>',idx+3)
        idx = thetext.find('=$=',idx+3)


def do_markup(oldtext):
    global thetext
    actionterms = ['killed','wounded','bombed', 'clashed','injured','attacked','assaulted']
    peopleterms = ['civilians','workers','authorities', 'groups','troops','soldiers','rebels']
    thetext = oldtext + ' '
    do_NE_markup()
    do_number_markup()
    do_string_markup('whacked',actionterms,'red')
    do_string_markup('people',peopleterms, 'cyan')
    print(thetext)
    return thetext