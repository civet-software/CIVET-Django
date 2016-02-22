##	models.py
##
##  Django 'models.py' file for CIVET system
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

from django.db import models

class CollManager(models.Manager):
    def create_coll(self, collid, collfilename, colldate, 
        colledit, collcmt):
        coll = self.create(
            collid = collid,
            collfilename = collfilename, 
            colldate = colldate, 
            colledit = colledit, 
            collcmt = collcmt)
        return coll

class Collection(models.Model):
    collid = models.CharField(max_length=100)
    collfilename = models.CharField(max_length=100,blank=True)  # need blank=True for migrate but in fact it is set by program and will never  be blank
    colldate = models.DateField()
    colledit = models.DateTimeField()  # allow this to be blank
    collcmt = models.CharField(max_length=500)

    objects = CollManager()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.collfilename + ' : ' + self.collid + ': ' + self.collcmt


class TextManager(models.Manager):
    def create_text(self, textparent, textid, textdelete, textdate, textpublisher, textpubid, textbiblio, textlicense, 
                    textgeogloc, textlede, textcmt, textoriginal, textmkup, textmkupdate, textmkupcoder):
        textentry = self.create(
            textparent = textparent,
            textid = textid,
            textdelete = textdelete,
            textdate = textdate,
            textpublisher = textpublisher,
            textpubid = textpubid,
            textbiblio = textbiblio,
            textlicense = textlicense,
            textgeogloc = textgeogloc,
            textlede = textlede,
            textcmt = textcmt,
            textoriginal = textoriginal,
            textmkup = textmkup,
            textmkupdate = textmkupdate,
            textmkupcoder = textmkupcoder
            )
        return textentry

class Text(models.Model):
# need to add allowing blanks to lots of these
    textparent = models.CharField(max_length=100,blank=True)  # needed blank=True for migrate but in fact it never should be blank
    textid = models.CharField(max_length=100)
    textdelete = models.BooleanField()
    textdate = models.DateField()
    textpublisher = models.CharField(max_length=100)
    textpubid = models.CharField(max_length=100)
    textbiblio = models.CharField(max_length=100)
    textlicense = models.CharField(max_length=100)   
    textgeogloc = models.CharField(max_length=100)   
    textlede = models.CharField(max_length=100) 
    textcmt = models.CharField(max_length=500,blank=True) 
    textoriginal = models.TextField()
    textmkup = models.TextField()     
    textmkupdate = models.DateTimeField()
    textmkupcoder = models.CharField(max_length=32)

    objects = TextManager()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.textparent + ': ' + self.textid

    def get_text_fields(self):
        """ returns textmkup if it is not null, otherwise textoriginal"""
        if len(self.textmkup) > 64:  ### <16.02.11> THIS IS A KLUDGE FOR THE ALBANY PROJECT: CORRECT IT
            return [self.textid, self.textlede, str(self.textdate), self.textcmt, self.textbiblio, self.textmkup]
        else:
            return [self.textid, self.textlede, str(self.textdate), self.textcmt, self.textbiblio, self.textoriginal]



class CaseManager(models.Manager):
    def create_case(self, caseparent, caseid, casedate, casecoder, casecmt,
                    casevalues):
        """valst = ''  # convert dictionary to string
        for st in casevaluedict:
            valst += '==$$==' + st + '=$$=' + casevaluedict[st]  # there's undoubtedly a more robust way to do this"""
        caseentry = self.create(
            caseparent = caseparent,
            caseid = caseid,
            casedate = casedate,
            casecoder = casecoder,
            casecmt = casecmt,
            casevalues = casevalues,
            )
        return caseentry

class Case(models.Model):
# need to add allowing blanks to lots of these
    caseparent = models.CharField(max_length=100,blank=True)
    caseid = models.CharField(max_length=100)
    casedate = models.DateTimeField()
    casecoder = models.CharField(max_length=32)
    casecmt = models.CharField(max_length=500,blank=True) 
    casevalues = models.TextField()
    
    objects = CaseManager()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.caseparent + ': ' + self.caseid

