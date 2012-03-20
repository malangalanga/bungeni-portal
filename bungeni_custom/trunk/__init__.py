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

# language ids, either as a space-separated string or as a list of strings
zope_i18n_allowed_languages = "ar en es fr it nl pt sw" 

# boolean: True, False
zope_i18n_compile_mo_files = True 

# string, language identifier, must be one of zope_i18n_allowed_languages
default_language = "en"

#language ids for languages written right to left, as a space-separated string
right_to_left_languages= "ar" 

# integer, minimum number of seconds to wait between checks for whether a 
# localization file needs reloading; 0 means never check (deployment)
check_auto_reload_localization = 5

#Default number of items in listings
default_number_of_listing_items = 100

