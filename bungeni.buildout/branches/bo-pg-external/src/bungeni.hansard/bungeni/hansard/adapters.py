from z3c.traverser.traverser import NameTraverserPlugin
from bungeni.alchemist import Session
from bungeni.hansard.models import domain
from zope.security.proxy import removeSecurityProxy
from zope import interface
from zope.location.interfaces import ILocation
class HansardTraverserPlugin(NameTraverserPlugin):
    traversalName = 'hansard'
    def _traverse(self, request, name):
        self.context = removeSecurityProxy(self.context)
        session = Session()
        context = session.merge(self.context)
        hansard = session.query(domain.Hansard) \
                                .filter(domain.Hansard.group_sitting_id 
                                                == context.group_sitting_id) \
                                .first()
        if not hansard:
            hansard = domain.Hansard()
            hansard.group_sitting_id = context.group_sitting_id
            session.add(hansard)
            session.flush()
            hansard.media_paths = domain.HansardMediaPaths()
        hansard.__name__ = 'hansard'
        hansard.__parent__ = self.context
        interface.alsoProvides(hansard, ILocation)
        return hansard
