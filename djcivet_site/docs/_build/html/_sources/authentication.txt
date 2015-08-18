**************
Authentication
**************

Django famously includes, "out of the box", a very robust system for handling user authentication and permissions. Except 
for a few minor modifications such as changing the web page headings and providing vaguely informative messages for log-in
failures, CIVET simply implements the default version of this, so you can be guided the instructions at 
https://docs.djangoproject.com/en/1.8/topics/auth/.

Authentication is controlled by the *civet_settings.py* global variable ``REQUIRE_LOGIN``. By default, this is set to 
``True`` when ``PRODUCTION_MODE = True`` and ``False`` otherwise. If you enter the name of the site without any additional
arguments, the program will go to a login page when ``civet_settings.REQUIRE_LOGIN = True``; otherwise it will go 
directly to the home page.
Attempting to access the home page when ``REQUIRE_LOGIN = True`` without a login will redirect to the login page.

Creating a superuser
====================

To keep things simple, CIVET handles the administration of users through the controls available to a “superuser”. 
To create a superuser, at the *djciv_site* level of the directory, use the terminal command [#f1]_

.. code::

    python manage.py createsuperuser
    
In development mode, start the system with the usual command

.. code::

    python manage.py runserver
    
and enter the URL

.. code::

    http://127.0.0.1:8000/admin/
    
You should see a page similar to this: [#f2]_

.. figure:: adminpage.png
   :alt: CIVET superuser administration page

The *Add* and *Change* buttons provide access to a rich set of options for adding users and editing information about them.
Clicking on “Users” will give a screen listing all of the users in the system, and clicking on a user name on that screen 
goes to a page with information about the user. You can delete one or more users from these screens; the “Groups” option
allows users to be organized into groups.   

Additional notes
================

1. Accessing the page without additional arguments automatically does a logout.

2. Django provides an extensive set of utilities for resetting passwords: for the sake of simplicity. as well as removing a 
possible venue for mischief, these have not been activated: it should be relatively simple to do this if you would like
to have that capability.

    At the present time, the AWS deployment does not show the pretty form, but all of the options are still there and 
    function: this will be corrected at some future date.

3. The GitHub version of the program is populated with at least the following:

    Superuser: civet-super  Password: je-kiffe-grenouilles [#f3]_
    
    User: ima-coder  Password: code-code-code!
    
    For the sake of security, you will probably want to delete these after you create your own environment, or at
    least change the passwords.


.. rubric:: Footnotes

.. [#f1]
    A description of the process can be found at https://docs.djangoproject.com/en/1.8/intro/tutorial02/

.. [#f2]
    The options seen in the tutorial version of this screen which allow the editing of the databases have been deactivated 
    since the database structure is tightly linked to various functions of the program, particularly the reading and
    writing of the workspace files. These could, of course, be modified, but this will need to be done in the program 
    itself, not simply by adding fields.

.. [#f3]
    You were expecting “password”, “CHANGEME” or “12345678”??

