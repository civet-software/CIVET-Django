from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index),

    url(r'select_template', views.select_template),
    url(r'download_pdfdocs', views.download_pdfdocs),
    url(r'download_demotemplate', views.download_demotemplate),

    url(r'read_template', views.read_template),
    url(r'save_basic', views.save_basic),
    url(r'download_basic_data', views.download_basic_data),
    url(r'reset_data', views.reset_data),
    url(r'continue_coding', views.continue_coding),
    url(r'update_collections', views.update_collections),

    url(r'collection_options', views.collection_options),
    url(r'select_collection', views.select_collection),
    url(r'operating_instructions', views.operating_instructions),

    url(r'edit_collection', views.edit_collection),
    url(r'apply_markup', views.apply_markup),
    url(r'save_edits', views.more_edits),
    url(r'cancel_edits', views.cancel_edits),
    url(r'texteditor', views.edit_collection),

    url(r'code_collection', views.code_collection),
    url(r'save_and_return', views.save_and_return),
    url(r'save_and_new', views.save_and_new),
    url(r'download_data', views.download_data),

    url(r'sort_collections', views.sort_collections),
    url(r'save_collection', views.save_collection),
    url(r'save_data', views.save_data),
    url(r'save_all', views.save_all),

    """ Examples from start-up
    # ex: /polls/5/results/
    url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<dirname>.+)/readfiles/$', views.readdir),"""
]