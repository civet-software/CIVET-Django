##	forms.py
##
##  Django 'forms.py' file for CIVET system
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
##	14-August-15:	Initial version
##  31-August-15:   Beta 0.9
##
##	----------------------------------------------------------------------------------

from django import forms

class PrefsForm(forms.Form):
    alwaysannotate = forms.BooleanField(label='Always apply annotation',required=False, error_messages={})
    showallcontent = forms.BooleanField(label='Show all content in coder',required=False, error_messages={})
    skipediting = forms.BooleanField(label='Skip editing',required=False, error_messages={})
    textmissing = forms.BooleanField(label='Use text if value is missing',required=False, error_messages={})
    sourcetextid = forms.BooleanField(label='Use textid in source citation',required=False, error_messages={})
    sourcetextbiblio = forms.BooleanField(label='Use textbiblio in source citation',required=False, error_messages={})
    geogmarkup = forms.BooleanField(label='Use preposition-based geographical markup',required=False, error_messages={})
    missingvalue = forms.CharField(label='Missing value:', widget=forms.TextInput(attrs={'size':'8'}),
                                   required=False, error_messages={})

class CodingForm(forms.Form):
    # Dynamic form generation code thanks to https://jacobian.org/writing/dynamic-form-generation/
#    deletelist = forms.<input type="hidden" id="deletelist" name="deletelist" value=""> # then needs to do a .as_hidden

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields')
        super(CodingForm, self).__init__(*args, **kwargs)
        
        for fld, info in fields.iteritems():
            if info[0] == 'checkbox':
                self.fields[fld] = forms.BooleanField(label=info[1],initial=info[2],required=False, error_messages={})            
            elif info[0] == 'textline':
                self.fields[fld] = forms.CharField(label=info[1],initial=info[2],
                                   widget=forms.TextInput(attrs={'size':info[3]}),
                                   required=False, error_messages={})
            elif info[0] == 'textclass':
                self.fields[fld] = forms.CharField(label=info[1],initial=info[2],
                                    widget=forms.TextInput(attrs={
                                    'size':info[3],
                                    'onfocus': 'coloraclass(\'' + info[4] + '\', \'' + fld + '\')',
                                    'onblur' : 'cancelclass()',
                                    'autocomplete' : 'off'
                                    }),
                                   required=False, error_messages={})
            elif info[0] == 'textsource':
                self.fields[fld] = forms.CharField(label=info[1],initial=info[2],
                                    widget=forms.TextInput(attrs={
                                    'size':info[3],
                                    'autocomplete' : 'off'
                                    }),
                                   required=False, error_messages={})
            elif info[0] == 'textarea':
                self.fields[fld] = forms.CharField(label=info[1],initial=info[2],
                                   widget=forms.Textarea(attrs={'rows':info[3],'cols':info[4]}),
                                   required=False, error_messages={})
            elif info[0] == 'select':
                self.fields[fld] = forms.ChoiceField(label=info[1],initial=info[2],choices=info[3], 
                                   required=False, error_messages={})
            elif info[0] == 'radio':
                self.fields[fld] = forms.ChoiceField(label=info[1],initial=info[2],choices=info[3], 
                                    widget=forms.RadioSelect(),
                                    required=False, error_messages={})                                    
            """elif info[0] == 'date':
                self.fields[fld] = forms.DateField(label=info[1],required=False, error_messages={}) # not implemented in 1.0 """            
               
