from django.conf.urls import url

from . import views

# General note: evaluate the longer strings first (or terminate shorter strings with $)

urlpatterns = [
    url(r'^$', views.index),
    url(r'home', views.index),
    url(r'set_preferences', views.set_preferences),
    url(r'reset_preferences', views.reset_preferences),

    url(r'download_pdfdocs', views.download_pdfdocs),
    url(r'download_demotemplate', views.download_demotemplate),
    url(r'download_demo_workspace', views.download_demo_workspace),

    url(r'select_template', views.select_template),
    url(r'read_template_only$', views.read_template_only),
    url(r'read_template_only/demo', views.read_template_only, {'isdemo': True}),  
    url(r'save_basic', views.save_basic),
    url(r'setup_basic_data_download', views.setup_basic_data_download),
    url(r'download_basic_data', views.download_basic_data),
    url(r'reset_basic_data', views.reset_basic_data),
    url(r'continue_basic_coding', views.continue_basic_coding),

    url(r'collection_options', views.collection_options),
    url(r'select_collection', views.select_collection),
    url(r'operating_instructions', views.operating_instructions),

    url(r'edit_collection', views.edit_collection),
    url(r'apply_markup', views.apply_markup),
    url(r'more_edits', views.more_edits),
    url(r'cancel_edits', views.cancel_edits),
    url(r'texteditor', views.edit_collection),

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
 
    url(r'edit_metadata', views.edit_metadata),
    url(r'add_workspace_comments', views.add_workspace_comments),

    url(r'sort_collections', views.sort_collections),
    url(r'save_collection', views.save_collection),
    url(r'save_data', views.save_data),
    url(r'save_all', views.save_all),

    url(r'make_color_list', views.make_color_list),
    url(r'test_page', views.test_page),
]