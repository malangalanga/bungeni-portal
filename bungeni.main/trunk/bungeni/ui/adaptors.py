from zope.component import getMultiAdapter

class BillAnnotationAdaptor(object):
    """Annotation Adaptor for Bills."""

    def __init__(self, context):
        self.context = context

    def getBodyText(self):
        """Returns the annotable text"""
        return self.context.body_text

    def getTitle(self):
        """Returns the annotable text"""
        return self.context.short_name

    def isAnnotatable(self):
        """Returns a boolean True"""
        return True

    def getAnnotatedUrl(self, request=None):
        """Returns the annotated url """
        view = getMultiAdapter((self.context, request), name=u'absolute_url')
        return view()


class RSSValues(object):
    """ Adapter for getting
        values to form rss feed
    """

    def __init__(self, context):
        self.context = context

    @property
    def values(self):
        return self.context.values()


class TimelineRSSValues(RSSValues):
    """ Adapter for getting values
        to form rss feed out of object's
        changes
    """

    @property
    def values(self):
        return self.context.changes
