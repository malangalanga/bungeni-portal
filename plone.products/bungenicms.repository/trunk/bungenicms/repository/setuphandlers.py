from Products.CMFPlone.utils import getToolByName

log = __import__("logging").getLogger("bungenicms.repository.setup")

"""OLD_PORTAL_TYPES = ("Document Repository", "Repository Community",
    "Repository Collection", "Repository Item"
)"""
OLD_PORTAL_TYPES = ("Digital Repository", "Repository Item")

def update_portal_types(context):
    site = context.getSite()
    catalog = getToolByName(site, "portal_catalog", None)
    if catalog is not None:
        for brain in catalog.searchResults(portal_type=OLD_PORTAL_TYPES):
            new_portal_type = brain.portal_type.replace(' ', '')
            obj = brain.getObject()
            obj.portal_type = new_portal_type
            obj.reindexObject()
            log.info("Setting portal type of %s from %s to %s",
                brain.getId, brain.portal_type, new_portal_type
            )
    else:
        log.error("Unable to acquire portal catalog. " 
            "Not renaming any repository types"
        )
