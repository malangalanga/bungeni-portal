# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Signatories validation machinery for parliamentary documents

$Id$
"""

import zope.component
import zope.interface
from zope.security.proxy import removeSecurityProxy
from zope.component import getGlobalSiteManager

from bungeni.models import interfaces
from bungeni.utils.capi import capi

log = __import__("logging").getLogger("bungeni.models.signatories")

CONFIGURABLE_PARAMS = ("max_signatories", "min_signatories",)

class SignatoryValidator(object):
    zope.interface.implements(interfaces.ISignatoryManager)
    
    max_signatories = 0
    min_signatories = 0
    
    def __init__(self, pi_instance):
        self.pi_instance = pi_instance
        self.object_type = pi_instance.type

    @property
    def signatories(self):
        #!+VERSIONS(mb, aug-2011) automatic transitions firing for versions?
        # as at r8488 - check whether the context actually has signatories
        #!+SECURITY(mb, aug-2011) remove proxy to allow access to 
        # signature status. View permission only checked on attribute access
        # from container `values` listing
        if hasattr(self.pi_instance, "signatories"):
            return removeSecurityProxy(
               self.pi_instance.signatories.values()
            )
            return self.pi_instance.signatories.values()
        else:
            log.warning("The object  %s has no signatories. Returning empty"
                " list of signatories.", 
                self.pi_instance.__str__()
            )
            return []

    @property
    def signatories_count(self):
        return len(list(self.signatories))

    @property
    def consented_signatories(self):
        return self.consentedSignatories()
    
    #!+PLEASE_USE_STANDARD_NAMING_CONVENTIONS(mr, apr-2012)
    
    def requireSignatures(self):
        return self.min_signatories > 0

    def validateSignatories(self):
        return self.signatories_count > 0

    def consentedSignatories(self, status=u"consented"):
        return len(filter(lambda cs:cs.status==u"consented", self.signatories))
    
    def validateConsentedSignatories(self):
        return (
            (self.consented_signatories >= self.min_signatories) and
            ((not self.max_signatories) or 
                (self.consented_signatories <= self.max_signatories)
            )
        )

    def allowSignature(self):
        return (not self.max_signatories or 
            (self.consented_signatories < self.max_signatories)
        ) and self.documentSubmitted()

    def expireSignatures(self):
        return unicode(self.pi_instance.status) == u"submitted"

    def documentSubmitted(self):
        return unicode(self.pi_instance.status) == u"submitted_signatories"

    def documentInDraft(self):
        """Check that a document is being redrafted
        """
        return unicode(self.pi_instance.status) == u"redraft"

def createManagerFactory(domain_class, **params):
    gsm = getGlobalSiteManager()
    manager_name = "%sSignatoryManager" % domain_class.__name__
    domain_iface = None
    iface_name = "I%s" % domain_class.__name__
    domain_iface = getattr(interfaces, iface_name, None)
    if domain_iface is None:
        log.error("No such interface %s class %s", iface_name, domain_class)
        log.error("Signatory Manager for class %s not created", domain_class)
        return
    if manager_name in globals().keys():
        log.errror("Signatory manager named %s already exists", manager_name)
        return
    globals()[manager_name] = type(manager_name, (SignatoryValidator,), {})
    manager = globals()[manager_name]
    for config_name, config_value in params.iteritems():
        assert (config_name in CONFIGURABLE_PARAMS), ("Check your signatory "
            "feature configuration for %s. Only these parameters may be "
            " configured %s" % (domain_class.__name__, CONFIGURABLE_PARAMS)
        )
        config_type = type(getattr(manager, config_name))
        setattr(manager, config_name, config_type(config_value))

    gsm.registerAdapter(manager, (domain_iface,), interfaces.ISignatoryManager)

