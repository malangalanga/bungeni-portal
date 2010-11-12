import logging
logger = logging.getLogger("plone")
from ubify.policy.config import contentroot_details

def setup_root_permissions(context):
    """ Deny Authenticated Users the 'Reader and Contributor' roles.
    Such permissions should be assigned explicitly on content objects.
    """
    portal = context.getSite()
    cr_obj = getattr(portal, contentroot_details['id'])
    cr_obj.portal_type
    cr_obj.manage_delLocalRoles(('AuthenticatedUsers',))
    logger.info("Delete roles assigned to AuthenticatedUsers' group \
    on the root folder.")
