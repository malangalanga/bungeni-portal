$Id$

This folder contains the static resources (such as any image, CSS or 
Javascript files) used by the HTML reporting templates in conjunction 
with elements of br:type="src".


Adding an image
---------------

First, prepare the image file and place it in this folder.
E.g. if the image file is "favicon.ico", place it at:

    bungeni_custom/reporting/static/favicon.ico

Then, in an HTML template, you can liberally use this file as the @src for 
appropriate HTML tags, such as <img> tags, specifiying it as a *relative* 
URL path, as shown here:

    <img br:type="src" br:src="favicon.ico" />

If additional tags are desired, just enter them directly e.g.

    <img br:type="src" br:src="favicon.ico" alt="fav!" width="100" height="75" />

For <img> tag details see: http://www.w3schools.com/tags/tag_img.asp


Other bungeni resource folders
------------------------------

Absolute paths to other image resources under bungeni may be specified as
paths starting with "/@@" as per zope convention for accessing resources. 
For example, to access images under the bungeni resource folder:

    bungeni.main/bungeni/portal/static/html/resources

you would use:

    <img br:type="src" br:src="/@@/images/favicon.ico" />


External images
---------------

External paths will be output as is (not resolved to this folder) e.g.:

    <img br:type="src" br:src="http://www.google.com/favicon.ico" />

But note that for above, it would be anyway be simpler to just specify 
boilerplate html in the first place e.g. 

    <img src="http://www.google.com/favicon.ico" />


