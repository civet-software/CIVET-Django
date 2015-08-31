****************************
Projected Features
****************************

CIVET is part of a projected system designed for managing
tens-of-thousands, or even millions, of small text files. The transition
in the past three decades from paper-based to electronic sources has
dramatically increased the amount of information that can potentially be
coded, but results in a “drinking from a fire hose” problem where a huge
number of false positives must be managed because typically only a very
small percentage of the texts obtained for a project actually contain
unique codeable events: yields of 1% to 3% are not uncommon. There is
very little existing software designed to deal with this situation,
since the texts are too large to be treated as nominal variables in a
statistical package and too numerous to be treated as documents in a
word processor. Consequently large projects typically write customized
systems in a language such as perl or Python, but these require
programming skills which are not always easily available in the social
science community.

We are planning to extend the CIVET workspace format to become the basis
of an integrated series of well-documented and user-friendly utilities
for dealing with this situation. All of the software will be open-source
under the MIT license, and made available to the community on GitHub.
These utilities will provide at least the following capabilities:

-  Near-duplicate detection which will collect articles which appear to
   be dealing with the same incident

-  Extraction programs for converting common formats such as
   Lexis-Nexis, Factiva and GigaWord to the CIVET document format.

-  Filtering and classification of texts based on one or more of the
   following methods

   Pattern-based:
       These will include regular expressions and boolean phrases with
       proximity measures

   Semi-supervised learning:
       The system will construct one or more machine-learning models
       (for example support vector machines) to determine whether an
       article is relevant based on a set of positive and negative
       examples provided by the user

   Action-based:
       These will use either the open source TABARI or PETRARCH
       political event coders to determine the type of activity being
       described

   Actor-based:
       These will use a set of standard lists maintained on a common
       server of political actors such as nation-states, international
       organizations and militarized non-state actors

   Geographical:
       These will use systems such as the open-source Mordecai location
       resolution system developed by Caerus Analytics.

-  Workflow management software for allocating and tracking the coding
   of incidents in large coding teams; these will use web-based tools so
   that coders can work from any location and across institutions. We
   will also provide scripts for interfacing to mySQL installations,
   GitHub and Dataverse as remote servers.

-  Extension of CIVET to allow the various classification tools
   (actions, actors, and location) to automatically be used in coding
   forms.

-  Semi-automatic conversion of the resulting coded data to the
   Dataverse format, and more generally integrate the CIVET tools with
   the Dataverse metadata, APIs and other tools as well as providing an
   access and authorization protocol modeled on the categories used in
   Dataverse.

-  Development of training materials, both text and video, for the
   system

