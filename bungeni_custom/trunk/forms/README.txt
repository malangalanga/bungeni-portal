Localization of Form UI Views
=============================

To localize the visibility of fields for each Bungeni Object Type -- to state 
in what modes and to what roles should an object field be displayed in the UI.

----
Generate the default localization file

Executing the following command:

    $ {cinst}/bin/python {cinst}/src/bungeni.main/bungeni/ui/descriptor/localization.py

will regenerate and *overwrite* the file:

    {bungeni_custom}/forms/ui.xml

The {bungeni_custom} folder is the current active one. The generated file 
corresponds exactly to all Form UI View settings in stock bungeni. 

----
Customize the localization file: forms/ui.xml

Modify the fields order of each descriptor and/or the visibility modifiers on 
each field as needed. For further explanation see the "Localization API" 
section in the document:

    Localization of Bungeni Forms
    http://code.google.com/p/bungeni-portal/wiki/DevFormLocalization#Localization_API


