# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Bungeni Alchemist model - [
    ore.alchemist.model
]

$Id$
"""
log = __import__("logging").getLogger("bungeni.alchemist")

from zope import component, interface, schema
from zope.interface.interfaces import IInterface
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from bungeni.alchemist.interfaces import (
    IAlchemistContent,
    IModelAnnotation,
    IIModelInterface,
    IModelDescriptor
)

from bungeni.ui.utils import common 


# ore.alchemist.model


def queryModelInterface(cls):
    """We can passed in a class or an interface.
    """
    if not IInterface.providedBy(cls):
        candidates = list(interface.implementedBy(cls))
        ifaces = filter(IIModelInterface.providedBy, candidates)
        #import pdb; pdb.set_trace()
        if not ifaces:
            for i in candidates:
                if issubclass(i, IAlchemistContent):
                    ifaces.append(i)
        if not ifaces:
            raise SyntaxError("No Model Interface on Domain Object")
        if ifaces:
            assert len(ifaces)==1, "Multiple Model Interfaces on Domain Object"
        #import pdb; pdb.set_trace()
        cls = ifaces[0]
    else:
        assert IIModelInterface.providedBy(cls), "Invalid Interface"
    return cls


def queryModelDescriptor(ob):
    if not IInterface.providedBy(ob):
        ob = filter(IIModelInterface.providedBy, 
            list(interface.implementedBy(ob)))[0]    
    name = "%s.%s" % (ob.__module__, ob.__name__)
    return component.queryAdapter(ob, IModelDescriptor, name)

# Register queryModelDescriptor adaptor (to override their upstream ZCML reg)
# signature: factory, adapts:[iface], provides:iface, name, event=False
component.getGlobalSiteManager().registerAdapter(queryModelDescriptor, 
    [IAlchemistContent],
    IModelAnnotation
)


class IModelDescriptorField(interface.Interface):
    # name
    # label
    # description
    modes = schema.ASCIILine(
        title=u"View Usage Modes for Field",
        description=u"Pipe separated string of different modes.. "
            "view|edit|add|listing|search are all valid"
            # !+PIPE(mr, nov-2010) get rid of it, use whitespace instead?
    )
    # property
    listing_column = schema.Object(interface.Interface,
        title=u"A Custom Column Widget for Listing Views",
        required=False
    )
    # !+LISTING_WIDGET(mr, nov-2010) why inconsistently named "listing_column"?
    view_widget = schema.Object(interface.Interface,
        title=u"A Custom Widget Factory for Read Views",
        required=False
    )
    edit_widget = schema.Object(interface.Interface,
        title=u"A Custom Widget Factory for Write Views",
        required=False,
    )
    add_widget = schema.Object(interface.Interface,
        title=u"A Custom Widget Factory for Add Views",
        required=False
    )
    search_widget = schema.ASCIILine(
        title=u"A Custom Search Widget Factory",
        required=False
    )
    ''' !+FIELD_PERMISSIONS(mr, nov-2010) these params are deprecated -- when 
    applied to any field (that corresponds to an attribute of the domain's 
    class), the domain.zcml setting for that same class attribute will anyway 
    take precedence.

    view_permission = schema.ASCIILine(
        title=u"Read Permission",
        description=u"If the user does not have this permission this field "
            "will not appear in read views",
        required=False
    )
    edit_permission = schema.ASCIILine(
        title=u"Read Permission",
        description=u"If the user does not have this permission this field "
            "will not appear in write views",
        required=False
    )
    '''
    
class Field(object):
    interface.implements(IModelDescriptorField)
    
    # INIT Parameter (and Defaults)
    
    # CONVENTION: the default value for each init parameter is the value 
    # assigned to the corresponding class attribute - reasons for this are:
    # a) makes it easier to override init param default values by trivial 
    # subclassing.
    # b) no need to set an instance attribute for init parameters that are 
    # not set, simply let the lookup pick the (default) value off the class.
    
    name = None      # str : field name
    label = ""       # str: title for field
    description = "" # str : description for field
    
    modes = "view|edit|add" # str : see _valid_modes for allows values
    
    property = None # zope.schema.interfaces.IField
    
    listing_column = None   # zc.table.interfaces.IColumn
    
    view_widget = None      # zope.app.form.interaces.IDisplayWidget
    edit_widget = None      # zope.app.form.interfaces.IInputWidget
    add_widget = None       # zope.app.form.interfaces.IInputWidget
    search_widget = None    # zope.app.form.interfaces.IInputWidget
    
    view_permission = "zope.Public"         # str
    edit_permission = "zope.ManageContent"  # str
    # !+FIELD_PERMISSIONS(mr, nov-2010) these attributes are left here because 
    # alchemist.catalyst.domain.ApplySecurity accesses them directly (even if
    # resulting permission is what is anyway what is specified in domain.zcml).
    
    
    # OTHER Attributes (and Defaults)
    
    # required flag can only be used if the field is not required by database
    #required = False 
    # !+Field.required(mr, oct-2010) this is OBSOLETED as it has no affect on
    # generated forms -- whether a field, in the UI, is handled as required 
    # or not depends entirely on the value of Field.property.required and/or 
    # whether the corresponding column is nullable or not.

    #fieldset = "default"
    # !+FIELDSET(mr, oct-2010) not used - determine intention, remove.
    
    # for relations, we want to enable grouping them together based on
    # model, this attribute specifies a group. the relation name will be
    # used on a vocabulary. perhaps an example is cleaner, so say we
    # have a movie object with separate relations to directors and actors
    # if we specify both as group "People", we inform the view machinery
    # to create a single relation viewlet, that displays and edits
    # via a single provider with a vocabulary for the relation.
    #group = None
    # !+GROUP(mr, oct-2010) not used - determine intention, remove.
    
    
    _valid_modes = ("view", "edit", "add", "listing", "search")
    
    def __init__(self, 
        name=None, label=None, description=None, 
        modes=None, property=None, listing_column=None, 
        view_widget=None, edit_widget=None, add_widget=None, search_widget=None,
        #view_permission=None, edit_permission=None
        # !+FIELD_PERMISSIONS(mr, nov-2010) deprecated -- permission on any 
        # domain class attribute (and so, descriptor field) are declared in
        # domain.zcml. There is however still the possibility that these may 
        # be useful for when a descriptor field does not correspond directly 
        # to a domain class attribute (to be determined). 
    ):
        """The defaults of each init paremeter is set as a class attribute --
        if not explicitly specified, then an attribute on the instance is
        NOT set.
        
        CONVENTION: not specifying a parameter or specifying it as None
        are interpreted to be equivalent.
        """
        kw = vars()
        cls = self.__class__
        # parameter integrity
        assert name, "Field [%s] must specify valid name" % (name)
        assert not ((property or self.property) and 
                not (modes or self.modes)), \
            """Can't specify "property" and no "modes" for field: %s""" % (
                name)
        if modes: 
            assert not " " in modes, \
                """Field [%s] "modes" [%s] may not contain whitespace""" % (
                    name, modes)
        if listing_column:
            assert ((modes and "listing" in modes) or 
                    (self.modes and "listing" in self.modes)), \
                "Field [%s] sets listing_column but no listing mode" % (name)
        # set attribute values (for specified attributes only)
        for p in (
            "name", "label", "description", "modes", 
            "property", "listing_column", 
            "view_widget", "edit_widget", "add_widget", "search_widget", 
            #"view_permission", "edit_permission"
            # !+FIELD_PERMISSIONS(mr, nov-2010) deprecated
        ):
            v = kw[p]
            if v is not None:
                setattr(self, p, v)
        
        # Ensure that a field is included in a descriptor only when it is 
        # relevant to the UI i.e. it is displayed in at least one mode -- 
        # this obsoletes/replaces the previous concept of descripor "omit". 
        # Apparently there has been a security-related issue as motivation 
        # for the previous "omit" concept -- as per this discussion:
        # http://groups.google.com/group/bungeni-dev/browse_thread/thread/7f7831b32e798708
        # But, testing the UI with all such fields removed has uncovered no 
        # such security-related issues (see r19 commit log of bungeni-testing).
        assert self.modes, "A descriptor field must specify one or more modes."
    
    def get(self, k, default=None):
        return self.__dict__.get(k, default)
    
    def __getitem__(self, k):
        return self.__dict__[k]



class ModelDescriptor(object):
    """Model type descriptor for table/mapped objects. 
    
    The notion is that an annotation Field object corresponds to a column, 
    and Field attributes correspond to application specific column metadata.
    
    We use class attribute fields=[Field] directly i.e. Field instances on 
    the class itself, implying there is no instance.fields=[Field] attribute.
    
    Always retrieve the *same* descriptor *instance* for a model class via:
        queryModelDescriptor(model_interface)
    """
    interface.implements(IModelDescriptor)
    
    # editable table listing !+
    #edit_grid = True 
    
    # for subclasses to reset
    fields = () # [Field]
    properties = () # !+USED?
    schema_order = () # !+USED?
    schema_invariants = ()
    
    def __call__(self, iface):
        """Models are also adapters for the underlying objects
        """
        return self
    
    def __init__(self):
        self._fields_by_name = {}
        for f in self.__class__.fields:
            self.sanity_check_field(f)
        log.info("Initializing ModelDescriptor: %s" % self)
    
    def sanity_check_field(self, f):
        """Do necessary checks on supplied Field instances.
        """
        name = f["name"]
        assert name not in self._fields_by_name, \
            "[%s] Can't have two fields with same name [%s]" % (
                self.__class__.__name__, name)
        self._fields_by_name[name] = f
        # !+DESCRIPTOR_VALIDATION(mr, nov-2010) a descriptor may specify a 
        # field with a name that does not correspond to an attribute on the 
        # model -- this may be useful, but we do not use it, and any such
        # occurance is most likely an code error... should we check for such
        # situations?
    
    
    # we override the following methods as, thanks to self._fields_by_name, 
    # they may be redefined in a much simpler way (as well as being faster).
    
    def get(self, name, default=None):
        print '!+ModelDescriptor.get("%s")' % (name), self
        return self._fields_by_name.get(name, default)
    
    def keys(self):
        print "!+ModelDescriptor.keys", self
        return self._fields_by_name.keys()
    
    def values(self):
        print "!+ModelDescriptor.values", self
        return self._fields_by_name.values()
    
    def __getitem__(self, name):
        print "!+ModelDescriptor.__getitem__", self
        return self._fields_by_name[name]
    
    def __contains__(self, name):
        print "!+ModelDescriptor.__contains__", self
        return name in self._fields_by_name

    def _mode_columns(self, mode):
        self.test_context_roles(mode)
        return [ f for f in self.__class__.fields if mode in f.modes ]
    
    @property
    def listing_columns(self): # !+listing_column_NAMES(mr, nov-2010) !
        return [ f.name for f in self._mode_columns("listing") ]
    @property
    def search_columns(self): 
        return self._mode_columns("search")
    @property
    def edit_columns(self):
        return self._mode_columns("edit")
    @property
    def add_columns(self):
        return self._mode_columns("add")
    @property
    def view_columns(self):
        return self._mode_columns("view")
    
    
    def test_context_roles(self, mode):
        """EXPERIMENTAL sample code to get a user's roles and whether is_admin 
        or not -- this is the info needed (in addition to the field's modes) 
        to further filter whether a field is visible or not for a 
        given (user, mode).
        """
        request = common.get_request()
        if request is None:
            context = None
            principal = None
        else:
            context = common.get_traversed_context(request)
            principal = request.principal
        if IUnauthenticatedPrincipal.providedBy(principal):
            roles = None
        else: 
            roles = common.get_context_roles(context)
        print """!+ModelDescriptor TEST_CONTEXT_ROLES [%s]
        PRINCIPAL: %s
        CONTEXT: %s
        MODE: %s
        ROLES: %s
        IS ADMIN: %s""" % (self,
            principal, 
            context,
            mode,
            roles, 
            common.is_admin(context)
        )


