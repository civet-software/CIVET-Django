****************************
Introduction
****************************


This is the documentation for 
CIVET\  [#f1]_—Contentious Incident Variable Entry Template—customizable
data entry system. CIVET was developed by the NSF-sponsored project
titled “A Method for Leveraging Public Information Sources for Social
Science Research” which is creating tools to improve the efficiency of
data generation in the social sciences. The project had an initial focus
on coding event data in the domain of contentious politics, but we
expect that these tools will be relevant in a number of data-generation
domains.

The core objective of CIVET is to provide a reasonably simple—yes,
simple—set of commands that will allow a user to set up a web-based
coding environment without the need to master the likes of HTML, CSS and
Javascript. As currently implemented, the system is a rather ugly
prototype; it will also be evolving as we add additional elements.
Nonetheless, the system should now be useable for coding.

CIVET is implemented in the widely-used and well documented
Python-based Django system [#f2]_ which is widely available on various
cloud platforms: a rather extended list of “Django-friendly” hosting
services can be found at

    https://code.djangoproject.com/wiki/DjangoFriendlyWebHosts

The complete CIVET code is licensed as open source under the MIT
license and provided on GitHub at https://github.com/civet-software .

CIVET currently has two modes:

**Coding form template:**
    This is a template-based for setting up a web-based coding form
    which implements several of the common HTML data entry formats and
    exports the resulting data as a tab-delimited text file. This is
    fully functional and should be useable for small projects.

**Text annotation/extraction:**
    This uses CIVET “workspaces” which combine related texts, their
    metadata, and the coding form. Workspaces allow for manual and
    automated text annotation, then the ability to extract various types
    of information into the fields of a coding form.

Program Navigation Placeholders
==================================

CIVET is still under development and not all of the options have
been fully implemented. If you see a page with a message of the form

    ``The option [something] has yet to be implemented. Use the back arrow in your browser to return to the previous screen.``

you have encountered one of those options: as noted, just use the “Back”
option in your browser to return to the previous screen. These are primarily
in the “Workspace Management” papge.


Status of the Program: 31 August 2015
=====================================

The NSF funding for the project ended on this date. At this point, all of
the documented features of the program should be working except as
noted above. However, we are just beginning the process of 
operational field testing and it is likely—which is to say, inevitable—
that some additional bugs will be found, hence this is still considered
“Beta-0.9” rather than “1.0.” We currently have two field tests underway,
and are hoping to get some additional ones going, and will be posting
bug fixes to GitHub promptly as these appear and are resolved.

At present, we have not developed any software for generating the 
workspace files, though we expect to have at least a couple programs 
available in the next few months. The problem here is that identifying
the various metadata and components in a set of texts is highly 
specific to the text source, and to date we've not found general 
solutions for this. As noted in the final chapter of this document, 
over the next year or so we will be seeking additional funding for
tool development for these “front-end” tasks, though given the very 
slow pace of the public funding cycle, this is unlikely to occur until 
late in 2016 at the earliest. In the meantime, we will be leveraging
tools developed in existing projects and, of course, would very 
much appreciate the contribution of any ancillary tools that the user
community develops, particularly for common sources such as Lexis-Nexis,
Factiva, ProQuest, LDC Gigaword, and various news feeds and social 
media.


Status of the Program: August 2016
=====================================

Over the past year, CIVET has been used in two projects, though both with 
my assistance in generating the YAML files and with some additional
customization, much of which has been incorporated into the general 
system. 

To my knowledge, however—and if you know of some project using this,
please let me know—it has not been used for the originally intended 
purpose of providing a platform which would allow someone with relatively
limited programming knowledge to create a web-based form. I suspect this
is due to one or more of the following factors:

-  The process of getting Django installed, while thoroughly documented, 
   apparently can require some experimentation and tweaking. That
   said, one of the projects decided to install Django on laptops
   used by the coders rather than through a server: this 
   allowed the coders to work anywhere.
   
-   When using workspaces, which allow access to the most sophisticated 
    parts of the system, the texts must be converted to the YAML
    format, a task for which I've yet to see a general solution and
    almost certainly requires Python, perl or Java programming skills
    
-   Realistically, there are only a small number of new projects starting in any given
    year which are sufficiently large that existing tools such as 
    spreadsheets or Google Forms are inadequate. And many of those,
    of course, will have resources to directly develop customized 
    pages rather than working within the constraints of CIVET   

So, this is essentially just an open-source version of a codebase that 
I can customize to generate coding forms. Which I'm realizing is 
probably pretty much what about 95% of open-source projects are, though
that still gives the client a whole lot more knowledge and power than
they have with a proprietary system, even if they never change a line 
of code. Whatever.

Some random observations from those two deployments:

-   Additional customization of the code has gone quite smoothly, even 
    allowing for the inevitable decay of my comprehension of the 
    system. Granted, even when I've forgotten the details of the code
    I'm still working with my programming idioms, but it does seem like as a 
    base, this is quite solid. The same can be said for the YAML
    workspace format. 
    
-   Neither of the two installations made any use of the manual 
    annotation, and in the second, the ``NEVER_ANNOTATE`` option was
    added to bypass this entirely: annotation is either handled
    automatically using vocabulary files, or directly putting the 
    HTML into the YAML files.
    
-   More generally, though completely expected, the deployment have
    generated a number of interesting ideas for new features that
    did not emerge in the abstract design phase. I've also left 
    in some custom code—commented-out or otherwise deactivated—
    that could be used for examples of further possible extensions.  
    
-   On two occasions over the past year there were changes to 
    Django that required minor changes—one or two lines of code—
    to CIVET in order to keep it running. Unsurprisingly, we have 
    also found that Django is more likely to be fully compatible 
    with up-to-date hardware
    and operating systems: in particular, one project ran into some
    issues running it on some old copies of Windows. Once again, this is
    less of a turn-key system than I'd hoped.
      

Documentation
=============

Documentation is maintained using the `Sphinx <http://http://sphinx-doc.org/>`_ system, which provides both an 
`on-line version <http://civet.parusanalytics.com/civetdocs/index.html>`_ and a reasonably-well-formatted PDF version. There
are links to both of these compiled versions on the home page; the ``.rst`` source texts for the documentation are in the
directory *djcivet_site/docs*. That directory contains a Sphinx *Makefile* so revisions can be compiled using the standard 
command ``make html latexpdf``.

The on-line documentation currently resides at the site http://civet.parusanalytics.com/civetdocs/; [#f3]_ a PDF version can 
be downloaded by clicking the ``Download PDF`` link on the home page. [#f4]_

.. rubric:: Footnotes

.. [#f1] http://en.wikipedia.org/wiki/CIVET

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