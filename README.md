# CIVET-Django

This is the documentation for a prototype of the CIVET -- Contentious Incident Variable Entry Template -- customizable data entry system running in the Django web framework. CIVET is being developed by the NSF-sponsored project titled "A Method for Leveraging Public Information Sources for Social Science Research" which is creating tools to improve the efficiency of data generation in the social sciences. The project has an initial focus on coding event data in the domain of contentious politics, but we expect that these tools will be relevant in a number of data-generation domains.


CIVET, which is implemented in the Django web framework, currently has the following features

* A YAML-based document management format designed for storing collections of relatively short texts such as news articles together with metadata and cases coded from these texts. We expect to build a series of additional tools using this format.
* A system for creating web-based data coding forms with standard HTML components such as checkboxes, pull-down selection menus and text entry, without the need to know HTML or web programming
* Automatical annotation of texts to identify named entities and numbers; the release version will also allow the user to specify sets of words to be annotated. 
* Integration of the annotated texts with the web form so that data fields can be extracted by going through a specific set of annotated words. Simple data entry and select/paste from the texts are also supported.


The file *CIVET.Documentation.pdf* provides information on installing and operating the system. We expect to have a fully operational version available by the end of August 2015.



###Acknowledgements
The development of CIVET is funded by the U.S. National Science Foundation Office of Multidisciplinary Activities
 in the Directorate for Social, Behavioral & Economic Sciences, Award 1338470 and the <a href="http://www.odum.unc.edu/odum/home2.jsp">Odum Institute</a> at the University of North Carolina at Chapel Hill with additional assistance from <a href="http://parusanalytics.com/">Parus Analytics</a>.

For suggestions and further information, contact schrodt735@gmail.com 
