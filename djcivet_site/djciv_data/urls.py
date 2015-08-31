##	urls.py
##
##  Django 'urls.py' file for CIVET system
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

from django.conf.urls import url

from . import views

# General note: evaluate the longer strings first (or terminate shorter strings with $)

urlpatterns = [
    url(r'^$', views.index),
    url(r'home', views.index),
    url(r'preferences', views.preferences),
    url(r'handle_logout', views.handle_logout),

    url(r'download_pdfdocs', views.download_pdfdocs),
    url(r'online_manual', views.online_manual),
    url(r'download_demotemplate', views.download_demotemplate),
    url(r'download_demo_workspace', views.download_demo_workspace),

    url(r'select_template', views.select_template),
    url(r'read_template_only$', views.read_template_only),
    url(r'read_template_only/demo', views.read_template_only, {'isdemo': True}), 
    url(r'save_basic', views.save_basic),
    url(r'setup_basic_data_download', views.setup_basic_data_download),
    url(r'download_basic_data', views.download_basic_data),
    url(r'reset_basic_data', views.continue_basic_coding, {'reset': True}),
    url(r'continue_basic_coding', views.continue_basic_coding),    
    url(r'next_form_page', views.change_form_page, {'basic':True}),
    url(r'prev_form_page', views.change_form_page, {'incr':-1, 'basic':True}),  

    url(r'select_collection', views.select_collection),
    url(r'edit_collection', views.edit_collection),
    url(r'apply_markup', views.apply_editor_markup),
    url(r'save_and_code', views.save_and_code),
    url(r'more_edits', views.more_edits),
    url(r'cancel_edits', views.cancel_edits),

    url(r'select_workspace$', views.select_workspace),
    url(r'select_workspace/manage', views.select_workspace, {'manage': True}),
    url(r'read_workspace$', views.read_workspace),
    url(r'read_workspace/manage', views.read_workspace, {'manage': True}),
    url(r'read_workspace/demo$', views.read_workspace, {'isdemo': True}),
    url(r'read_workspace/demo-manage', views.read_workspace, {'isdemo': True, 'manage': True}),
    url(r'write_workspace', views.write_workspace),

    url(r'code_collection', views.code_collection),
    url(r'save_and_return', views.save_and_return),
    url(r'save_and_next', views.save_and_next),
    url(r'save_and_new', views.save_and_new),
    url(r'setup_workspace_download$', views.setup_workspace_download),
    url(r'setup_workspace_download/coding', views.setup_workspace_download, {'iscoding': True}),  
    url(r'setup_workspace_data_download', views.setup_workspace_data_download),
    url(r'download_workspace_data$', views.download_workspace_data),  # see note on eventually re-routing of this
    url(r'download_workspace_data/select', views.download_workspace_data, {'select_variables': True}),  # see note on eventually re-routing of this
    url(r'next_coder_page', views.change_form_page),
    url(r'prev_coder_page', views.change_form_page, {'incr':-1}),  
 
    url(r'edit_metadata', views.edit_metadata),
    url(r'add_workspace_comments', views.add_workspace_comments),

    url(r'make_color_list', views.make_color_list),
    url(r'test_page', views.test_page),

]