*******************************************
Appendix 5: Installing in AWS-EB and Docker
*******************************************

Amazon Web Services Elastic Beanstalk
=====================================

“Cloud” servers are an increasingly popular low-cost alternative to locally-administered servers. A large number of these 
options are available; [#f7]_ I'm focusing on the Amazon Web Services “Elastic Beanstalk” (AWS-EB) for the simple reason that at the time 
of this writing AWS provides a generous free trial option, and their instructions worked the first time I tried. [#f4]_

A coherent set of instructions can be found at 
http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html. Then follow these steps:

1. Get an AWS account: https://aws.amazon.com/ 

2. In the instructions, skip the steps prior to the
heading **Configure your Django application for AWS Elastic Beanstalk** unless you also want to try out the system
locally (which is probably a good idea)

3. Download the CIVET system from GitHub: https://github.com/civet-software/CIVET-Django [#f8]_

4. In the file *djcivet_site/djciv_data/civet_settings.py* set ``PRODUCTION_MODE = True`` [#f9]_

5. Create a directory that you will use to deploy the system: for consistency with the remaining instructions it should be 
called *AWS-CIVET* though once you are comfortable with these instructions it could be named something different.

6. In that directory, copy the directory *djcivet_site*. Following the instructions, create directories named *.elasticbeanstalk*
and *.ebextensions* [#f10]_ 
and create a file named *requirements.txt* Just copy the contents from the section below; you don't need the ``pip freeze``
step. Copy the code in the **AWS-EB Configuration Files** section below into the various files  

    Your directory will now look like

    .. code::

        AWS-CIVET
        |-- .ebextensions
        |   `-- 01-django_eb.config
        |-- .elasticbeanstalk
        |   `-- config.yml
        |-- djcivet_site
        |   |-- db.sqlite3
        |   |-- djcivet_data
        |   |-- docs
        |   |-- djcivet_site
        |   |   |-- __init__.py
        |   |   |-- settings.py
        |   |   |-- urls.py
        |   |   |-- wsgi.py
        |   `-- manage.py
        `-- requirements.txt

7. Install the “eb” command-line tool per the instructions found at 
http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html. Initializing this will require AWS access credentials, a 
process described at http://docs.aws.amazon.com/general/latest/gr/getting-aws-sec-creds.html.

8. Follow the instructions in the **Deploy your site using AWS Elastic Beanstalk** section to use “eb” in a terminal 
application. It will take a minute or so for the ``eb create`` process to complete—there's plenty of feedback—and there is an
additional lag before the URL will be recognized.

9. You should now see the CIVET home page at the URL http://aws-civet-dev.elasticbeanstalk.com. This should take you to the 
login page unless you've set ``REQUIRE_LOGIN = False``. Run through the options with the demonstration files to make sure
the site is working. If the site doesn't come up at your first attempt, try reloading a couple of times until AWS 
recognizes the URL.

10. When you are finished, enter ``eb terminate`` and respond to the confirmation prompt with “AWS-CIVET-dev” in order to 
stop the program.


AWS-EB Configuration Files
--------------------------

In 

.. code::

    Django==1.8.3

In *AWS-CIVET/.elasticbeanstalk/* create the file *config.yml* 

.. code::

    branch-defaults:
      default:
        environment: AWS-CIVET-dev
    global:
      application_name: AWS_CIVET
      default_ec2_keyname: aws-civet
      default_platform: Python 2.7
      default_region: us-east-1
      profile: eb-cli
      sc: null

In *AWS_CIVET/.ebextensions/* create the file *01-djcivet_site.config*

.. code::

    container_commands:
        01_collectstatic:
          command: "source /opt/python/run/venv/bin/activate && python djcivet_site/manage.py collectstatic --noinput"
  
    option_settings:
      "aws:elasticbeanstalk:application:environment":
        DJANGO_SETTINGS_MODULE: "djcivet_site.settings"
        PYTHONPATH: "/opt/python/current/app/djcivet_site:$PYTHONPATH"
      "aws:elasticbeanstalk:container:python":
        WSGIPath: "djcivet_site/djcivet_site/wsgi.py"

In *djcivet_site/djcivet_site/settings.py*

- Set ``DEBUG = False``
- Change SECRET_KEY since the downloaded version isn't exactly secret

Handling of *static* files
--------------------------

As even a brief perusal of the web will affirm, the handling of *static* files in production versions of
Django is, well, complicated. After joining legions of programmers past, present and future in beating my head against
the wall on trying to get CIVET to access files internally in production as it does in the development mode, I gave up [#f5]_ 
and put the static resources referenced from inside templates on a directory on an external server, specifically 
*http://civet.parusanalytics.com/civet_static/*  Files that are read in *views.py* remain in the *static/djciv_data* 
folder, which works in both the development and production modes.

If you would like to modify the static files in the system—the main target would be *CKEditor*, unless you find our 
mascot too insufferably cute—you can move this material (the contents of the directory *static/djciv_data* in the distribution) to
the server of your choice: just change the address in ``settings.STATIC_SOURCE`` to point to the new location. [#f6]_ 


Docker
======

Docker (https://www.docker.com/) is a highly popular, rapidly evolving [#f1]_ “containerization” system which will ultimately simplify the secure deployment
of software in a wide variety of different systems. Briefly, “containers” are a more efficient extension of the concept of 
`virtual machines <https://en.wikipedia.org/wiki/Virtual_machine>`_ —computers running programs which simulate the operation 
of other computers—by packaging all of the required software in an “image” file that is able to run on any system capable of 
running Docker. Because the operations within a container can be isolated from the host machine, and the contents of the
container can be inspected and verified, this should provide a more secure (and efficient) environment than situations where 
a variety of software 
needs to be installed in order for a system to run, and that software potentially has access to all of the resources of the system. [#f3]_
Hence the excitement.

To date, I have successfully gotten the Docker container described below to run CIVET in development mode as a container on my 
Macintosh; I attempted to get it running on the Google Cloud but was unsuccessful; I have not tried any other configurations.
As always, I will be happy to incorporate any additional suggestions into this documentation.

The guide I used for the deployment is http://michal.karzynski.pl/blog/2015/04/19/packaging-django-applications-as-docker-container-images/.
This was not the first one I tried, and as indicated above, Docker is still evolving
so you should make certain you are using a recent set of guides (and the instructions here may break sooner rather than 
later.)


Using Karzynski as a guide, here are the steps:

1. If you aren't already using Docker, get a Docker account—there is a free option—and install Docker: the instructions for
this will vary depending on your operating system; Karzynski's instructions are just for Linux.

2. Set-up a directory to hold the Docker project---I called this *Docker-CIVET*, which corresponds to Karzynski's local 
directory *dockyard*. I'll be using Karzynski's Docker image name DOCKYARD.

3. Copy the directory *djcivet_site* into *Docker-CIVET*.

4. In *Docker-CIVET*, create the *docker-entrypoint.sh* and *Dockerfile* files from the code given below. Your directory 
will now look like

    .. code::

        Docker-CIVET
        |-- docker-entrypoint.sh 
        |-- Dockerfile   
        |-- djcivet_site
        |   |-- db.sqlite3
        |   |-- djcivet_data
        |   |-- docs
        |   |-- djcivet_site
        |   |   |-- __init__.py
        |   |   |-- settings.py
        |   |   |-- urls.py
        |   |   |-- wsgi.py
        |   `-- manage.py
        `-- requirements.txt

5. Follow the remaining instructions to build and test the container with the ``user-name`` from your Docker account and the 
``image-name`` of your choice (e.g. ``docker-civet``).

Contents of *docker-entrypoint.sh*
-----------------------------------

.. code::

    #!/bin/bash
    python manage.py migrate                  # Apply database migrations
    python manage.py collectstatic --noinput  # Collect static files

    # Prepare log files and start outputting logs to stdout
    touch /srv/logs/gunicorn.log
    touch /srv/logs/access.log
    tail -n 0 -f /srv/logs/*.log &

    # Start Gunicorn processes
    echo Starting Gunicorn.
    exec gunicorn djcivet_site.wsgi:application \
        --name djcivet_site \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --log-level=info \
        --log-file=/srv/logs/gunicorn.log \
        --access-logfile=/srv/logs/access.log \
        "$@"
    
Contents of *Dockerfile*
--------------------------

..  code::

    ############################################################
    # Dockerfile to run a Django-based web application
    # Based on an Ubuntu Image
    ############################################################

    # Set the base image to use to Ubuntu
    FROM ubuntu:14.04

    # Set the file maintainer (your name - the file's author)
    MAINTAINER Parus Analytics

    # Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
    # Local directory with project source
    ENV DOCKYARD_SRC=djcivet_site
    # Directory in container for all project files
    ENV DOCKYARD_SRVHOME=/srv
    # Directory in container for project source files
    ENV DOCKYARD_SRVPROJ=/srv/djcivet_site

    # Update the default application repository sources list
    RUN apt-get update && apt-get -y upgrade
    RUN apt-get install -y python python-pip

    # Create application subdirectories
    WORKDIR $DOCKYARD_SRVHOME
    RUN mkdir media static logs
    VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

    # Copy application source code to SRCDIR
    COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

    # Install Python dependencies
    #RUN pip install -r $DOCKYARD_SRVPROJ/requirements.txt
    RUN pip install Django
    RUN pip install gunicorn
    # Port to expose
    EXPOSE 8000

    # Copy entrypoint script into the image
    WORKDIR $DOCKYARD_SRVPROJ
    COPY ./docker-entrypoint.sh /
    ENTRYPOINT ["/docker-entrypoint.sh"]


.. rubric:: Footnotes

.. [#f7]
    In particular, Heroku (https://www.heroku.com/) appears to be another 
    `Django-friendly <https://devcenter.heroku.com/articles/getting-started-with-django>`_ option, and also offers free accounts.
    Using Heroku requires a [free] GitHub account. 

.. [#f4]
    Which, ahem, cannot be said for my multiple attempts to get the system running on the comparable Google service, 
    though I'm sure it is possible to do this and would be happy to add instructions once someone has figured it
    out. 

.. [#f8]
    At some point I'll put a “turn-key” directory on GitHub that will have all of the appropriate files. But not yet.

.. [#f9]
    You can also leave ``PRODUCTION_MODE = False`` and set ``STATIC_SOURCE = "http://civet.parusanalytics.com/civet_static/"``:
    key here is that AWS needs to read static files from a remote server.

.. [#f10]
    The ‘.’ in front of the file name means these will probably be invisible in most standard views of the *AWS-CIVET*
    directory: this is a Unix feature, not a bug.

.. [#f5]
    Or simply took the approach that the Django system clearly prefers, depending on your perspective

.. [#f6]
    An apparently popular approach for handling this is to use an AWS S3 server instance for external storage of static files: 
    there are multiple descriptions on the Web describing how to do this. As it involves quite a few steps and I've
    got a perfectly good server already set up in the cloud, I went with that route instead.

.. [#f1]
    Which is to say, a whole lot of moving parts which don't quite always play well together and inconsistently documented: 
    see   http://blog.circleci.com/its-the-future/, 
    http://blog.circleci.com/it-really-is-the-future/, and https://valdhaus.co/writings/docker-misconceptions/ [#f2]_
    
.. [#f2]
    Thanks to John Beieler for the links.
    
.. [#f3]
    Or as the situation was recently explicated at our local software development meet-up, in reference 
    to a certain institution that does not have a campus but “Grounds”, and I am not referring to Starbucks, “So which 
    is it with your sysadmins? They want to make sure Docker is deployed securely? Well, there are plenty of ways to do 
    that. Or they just don't want to do any work? Then you've got a different set of problems.” 
    
