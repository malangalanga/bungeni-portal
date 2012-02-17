Marginalia
==========

This Plone product integrates the 'marginalia' javascript application
for annotating documents. 'marginalia' is used more or less as-is. The
Plone product both implements the backend (storing and serving
annotations) and hosts the front-end (marginalia runs on documents
served by Plone).

marginalia
----------

Connections to Plone from marginalia correspond to four operations:

- listAnnotations
- createAnnotation
- updateAnnotation
- deleteAnnotation

Install
=======

In the skins folder link the javascript files from the marginalia Zope3
migration branch.

$ cd Marginalia/skins/
$ svn co https://bungeni-portal.googlecode.com/svn/Marginalia/branches/comat-marginalia/branches/marginalia/browser/js marginalia 
