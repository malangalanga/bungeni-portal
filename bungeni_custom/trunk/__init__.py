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
/opt/bungeni/bungeni_apps/python27/lib/python2.7/site-packages/bungeni_custom.pth

Containing the path to parent folder of the "bungeni_custom" package e.g.:
/opt/bungeni/bungeni_apps/bungeni/src


$Id$
"""

# language ids, either as a space-separated string or as a list of strings
zope_i18n_allowed_languages = "ar en fr pt sw" 

# boolean: True, False
zope_i18n_compile_mo_files = True 

# string, language identifier, must be one of zope_i18n_allowed_languages
default_language = "en"

# pivot languages - zero or more of zope_i18n_allowed_languages
pivot_languages = "en"

# language ids for languages written right to left, as a space-separated string
right_to_left_languages = "ar" 

# integer, minimum number of seconds to wait between checks for whether a 
# localization file needs reloading; 0 means never check (deployment)
check_auto_reload_localization = 5

# default number of items in listings
default_number_of_listing_items = 50

# when listing text columns, only display first so many characters
long_text_column_listings_truncate_at = 57

# duration in seconds before an access token expires
oauth_access_token_expiry_time = 3600

# duration in seconds before an authorisarion token expires
oauth_authorization_token_expiry_time = 600

# used to secure information during the OAuth flow
oauth_hmac_key = "wNo1CvEW5eN4BbzisBdb7Af2Asx6XXoke0GZtIMN3h3HCdA3"


