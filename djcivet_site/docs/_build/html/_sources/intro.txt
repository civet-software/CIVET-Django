****************************
Introduction
****************************


This is the documentation for the beta version of the
Civet\  [#f1]_—Contentious Incident Variable Entry Template—customizable
data entry system. Civet is being developed by the NSF-sponsored project
titled “A Method for Leveraging Public Information Sources for Social
Science Research” which is creating tools to improve the efficiency of
data generation in the social sciences. The project has an initial focus
on coding event data in the domain of contentious politics, but we
expect that these tools will be relevant in a number of data-generation
domains.

The core objective of Civet is to provide a reasonably simple—yes,
simple—set of commands that will allow a user to set up a web-based
coding environment without the need to master the likes of HTML, CSS and
Javascript. As currently implemented, the system is a rather ugly
prototype; it will also be evolving as we add additional elements.
Nonetheless, the system should now be useable for coding.

Civet is implemented in the widely-used and well documented
Python-based Django system [#f2]_ which is widely available on various
cloud platforms: a rather extended list of “Django-friendly” hosting
services can be found at

    https://code.djangoproject.com/wiki/DjangoFriendlyWebHosts

The complete Civet code is licensed as open source under the MIT
license and provided on GitHub at https://github.com/civet-software .

Civet currently has two modes:

**Coding form template:**
    This is a template-based for setting up a web-based coding form
    which implements several of the common HTML data entry formats and
    exports the resulting data as a tab-delimited text file. This is
    fully functional and should be useable for small projects.

**Text annotation/extraction:**
    This uses Civet “workspaces” which combine related texts, their
    metadata, and the coding form. Workspaces allow for manual and
    automated text annotation, then the ability to extract various types
    of information into the fields of a coding form.

Program Navigation Placeholders
==================================

Civet is currently under development and not all of the options have
been fully implemented. If you see a page with a message of the form

    ``The option [something] has yet to be implemented. Use the back arrow in your browser to return to the previous screen.``

you have encountered one of those options: as noted, just use the “Back”
option in your browser to return to the previous screen.


Documentation
=============

Documentation is maintained using the `Sphinx <http://http://sphinx-doc.org/>`_ system, which provides both an 
`on-line version <http://civet.parusanalytics.com/civetdocs/index.html>`_ and a reasonably-well-formatted PDF version. There
are links to both of these compiled versions on the home page; the ``.rst`` source texts for the documentation are in the
directory *djcivet_site/docs*. That directory contains a Sphinx *Makefile* so revisions can be compiled using the standard 
command ``make html latexpdf``.

The on-line documentation currently resides at the site http://civet.parusanalytics.com/civetdocs/; [#f3]_ a PDF version can 
be downloaded by clicking the ``Download PDF`` link on the home page. [#f4]_


.. only:: html

    Footnotes
    ---------

.. [#f1] http://en.wikipedia.org/wiki/Civet

.. [#f2] An earlier prototype was implemented in the ``Flask`` framework: see
   Appendix 4

.. [#f3]
   This is a bug, not a feature: there is presumably a way of accessing these at *djcivet_site/docs/_build/html/*, or 
   somewhere else within the *djcivet_site/* directory
   in a manner that has them correctly rendered, but I haven't figured it out yet. Fixes are welcome.
   
.. [#f4]
   This is handled in ``views.download_pdfdocs()``: it first looks for the PDF version of the documentation in 
   *docs/_build/latex/civetdoc.pdf*, which is where the most current version is likely to be located when the 
   documentation was produced using the ``make latexpdf`` command in the *docs/* directory. If that isn't present,
   it checks the */static/* directory: this can be used in deployments in order to avoid uploading  *docs/*. If neither
   is available, it gets the copy posted at http://civet.parusanalytics.com/, which may or may not correspond exactly to the 
   version being used depending on what modifications have been made. The command ``make movepdf`` will copy *civetdoc.pdf* from 
   *_build/latex* to */static/*