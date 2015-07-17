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
    collfilename = models.CharField(max_length=100,blank=True)  # need this for migrate but in fact it is set by program and will never  be blank
    colldate = models.DateField()
    colledit = models.DateTimeField()  # allow this to be blank
#    collcoded = models.DateTimeField() # same
    collcmt = models.CharField(max_length=100)

    objects = CollManager()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.collfilename + ' : ' + self.collid + ': ' + self.collcmt


class TextManager(models.Manager):
    def create_text(self, textparent, textid, textdate, textpublisher, textpubid, textlicense, textlede, textcmt,
                    textoriginal, textmkup, textmkupdate, textmkupcoder):
        textentry = self.create(
            textparent = textparent,
            textid = textid,
            textdate = textdate,
            textpublisher = textpublisher,
            textpubid = textpubid,
            textlicense = textlicense,
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
    textparent = models.CharField(max_length=100,blank=True)  # hmmm, needed that for migrate but in fact it never should be blank
    textid = models.CharField(max_length=100)
    textdate = models.DateField()
    textpublisher = models.CharField(max_length=100)
    textpubid = models.CharField(max_length=100)
    textlicense = models.CharField(max_length=100)   
    textlede = models.CharField(max_length=100) 
    textcmt = models.CharField(max_length=255,blank=True) 
    textoriginal = models.TextField()
    textmkup = models.TextField()     
    textmkupdate = models.DateTimeField()
    textmkupcoder = models.CharField(max_length=32)

    objects = TextManager()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.textparent + ': ' + self.textid

    def get_markup(self):
        return [self.textid, self.textlede, self.textmkup]



class CaseManager(models.Manager):
    def create_case(self, caseparent, caseid, casedate, casecoder, casecmt,
                    casevaluedict):
        valst = ''  # convert dictionary to string
        for st in casevaluedict:
            valst += '==$$==' + st + '=$$=' + casevaluedict[st]  # there's undoubtedly a more robust way to do this
        caseentry = self.create(
            caseparent = caseparent,
            caseid = caseid,
            casedate = casedate,
            casecoder = casecoder,
            casecmt = casecmt,
            casevalues = valst,
            )
        return caseentry

class Case(models.Model):
# need to add allowing blanks to lots of these
    caseparent = models.CharField(max_length=100,blank=True)
    caseid = models.CharField(max_length=100)
    casedate = models.DateTimeField()
    casecoder = models.CharField(max_length=32)
    casecmt = models.CharField(max_length=255,blank=True) 
    casevalues = models.TextField()
    
    objects = CaseManager()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.caseparent + ': ' + self.caseid

    def get_values(self):
        valdict = {}
        fields = self.casevalues.split('==$$==')
        for st in fields:
            part = st.partition('=$$=')
            valdict[part[0]] = part[2]
        return valdict
