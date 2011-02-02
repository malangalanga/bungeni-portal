# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Bungeni Custom

Package to include deployment-specific customizations -- this package should 
be replicated and modified as necessary. 

To specify a deployment's customizations package simply configure the 
python path appropriately; a way to do this is to add a ".pth" file in 
the deployment's python site-packages folder, containing a single line 
with the path to the parent folder of the "bungeni_custom" package.

For example, create the file at:
/home/{USER}/cinst/python25/lib/python2.5/site-packages/bungeni_custom.pth

Containing the one line:
/home/{USER}/cinst/bungeni/src


$Id$
"""

zope_i18n_allowed_languages = "en fr pt sw en-ke it"
zope_i18n_compile_mo_files = "1" # True

