# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""UI Vocabulary handling.

$Id$
"""
log = __import__("logging").getLogger("bungeni.ui.vocabulary")

import os
import re
import hashlib
from lxml import etree

from zope import interface, component
from zope.schema.interfaces import (
    IContextSourceBinder,
    IBaseVocabulary,  # IBaseVocabulary(ISource)
    IVocabulary,  # IVocabulary(IIterableVocabulary, IBaseVocabulary)
    IVocabularyFactory)
from zope.schema import vocabulary
from zope.security.proxy import removeSecurityProxy
from zope.app.container.interfaces import IContainer
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.securitypolicy.interfaces import IRole
from i18n import _

import sqlalchemy.sql.expression as sql

from bungeni.capi import capi
from bungeni.alchemist import Session
from bungeni.alchemist.container import valueKey
from bungeni.alchemist.interfaces import (
    IAlchemistContainer,
    IAlchemistContent
)

from bungeni.models import schema, domain, utils, delegation
from bungeni.models.interfaces import (
    ISubRoleAnnotations,
    IGroup,
    IGroupMember,
    IGroupAssignment,
    IGroupAssignmentContainer,
    IDoc,
    ITranslatable,
    ISignatory,
    ISignatoryContainer,
    IVersion,
    IDocVersion,
    IScheduleText,
    IScheduleContent,
    ISerializable
)
from bungeni.core.interfaces import IWorkspaceContainer

from bungeni.core.translation import translate_obj
from bungeni.core.language import get_default_language
from bungeni.core.dc import IDCDescriptiveProperties

from bungeni.utils import common
from bungeni.ui.interfaces import ITreeVocabulary
from bungeni.ui.reporting.generators import BUNGENI_REPORTS_NS
from bungeni.utils import misc, naming

try:
    import json
except ImportError:
    import simplejson as json
import imsvdex.vdex

# valid vdex filenames 
# !+VDEX_FILE_REGEX what about digits? so, if a number is used in a vdex 
# filename, the vocab is just not loaded?! Should just use the "symbol" regex.
VDEX_FILE_REGEX = re.compile("^[a-z]+[a-z|_]+\.vdex$")

# !+combined_name?
def get_translated_group_label(group):
    """Get a translated display text to refer to the group.
    """
    g = translate_obj(group)
    return "%s - %s" % (g.short_name, g.full_name)


class BaseVocabularyFactory(object):
    
    interface.implements(
        # IContextSourceBinder is needed for when this vocabulary factory 
        # instance is used as an ISource e.g. as the value of "source" or
        # "vocabulary" for a IChoice field property; causes the instance to be 
        # called with the context on each use.
        IContextSourceBinder, # __call__(context) -> IVocabulary
        
        # IBaseVocabulary (inherits from ISource) is gained "automagically" 
        # when registering instance as a utility via ZCML
        IBaseVocabulary, # getTerm(value) -> ITerm, (ISource) __contains__(value)
        
        # can create vocabularies !+ same as IContextSourceBinder?!
        IVocabularyFactory, # __call__(context) -> IVocabulary
    )


# vdex 
VDEX_BOOL_PROFILE_TYPE = "booleanTerms"
class VDEXManager(imsvdex.vdex.VDEXManager):
    default_language = capi.default_language
    fallback_to_default_language = True

    def isBoolean(self):
        """
        returns true if the VDEX profile type denotes a bool type vocabulary
        """ 
        vdex = self.tree._root
        return vdex.get('profileType') == VDEX_BOOL_PROFILE_TYPE

class VDEXVocabularyMixin(object):
    interface.implements(IBaseVocabulary)
    
    def __init__(self, manager):
        assert isinstance(manager, VDEXManager)
        self.vdex = manager
    
    # zope.schema.interfaces.ISource(Interface)

    # zope.schema.interfaces.IIterableVocabulary
    def __iter__(self):
        """Return an iterator which provides the 
        (zope.schema.vocabulary.SimpleTerm) terms from the vocabulary.
        zope.schema.interfaces.IIterableVocabulary
        """
        for term_value in self.vdex.term_dict:
            yield self.getTerm(term_value)

    def __len__(self):
        """Return the number of valid terms, or sys.maxint.
        zope.schema.interfaces.IIterableVocabulary
        """
        return len(self.vdex.term_dict)
    
    def __contains__(self, value):
        """Is the value available in this source? 
        (zope.schema.interfaces.ISource)
        """
        return self.vdex.getTermById(value) is not None
    
    # zope.schema.interfaces.IBaseVocabulary(ISource)
    def getTerm(self, value):
        """Return the zope.schema.vocabulary.SimpleTerm instance for value.
        (zope.schema.interfaces.IBaseVocabulary)
        """
        # !+NONE_LOOKUPERROR(mr, jul-0212) making vdex try to seem like a 
        # "schema vocab" with this method gives problems when value is None, 
        # and vdex does not define a term for None.
        term = self.getTermById(value)
        title = self.vdex.getTermCaption(term, lang=get_default_language())
        value_cast = self.__class__.value_cast
        return vocabulary.SimpleTerm(value_cast(value), value, title)
    
    # imsvdex.vdex.VDEXManager
    
    def getTermById(self, value):
        """Return the caption(s) for a given term identifier.
        As per imsvdex.vdex.VDEXManager (well, almost... None is LookupError).
        """
        term = self.vdex.getTermById(value)
        # !+NONE_LOOKUPERROR(mr, jul-2012) how should one handle a None value?
        if term is None:
            raise LookupError("This VDEX has no such ID :: %s", value)
        return term
    
    def getTermCaptionById(self, value, lang=get_default_language()):
        """Returns the str caption(s) for a given term identifier, in lang.
        As per imsvdex.vdex.VDEXManager.
        """
        return self.vdex.getTermCaptionById(value, lang)


    value_cast = unicode
    # zope.schema.interfaces.IVocabularyFactory
    def __call__(self, context=None):
        """Return a context-bound instance that implements ISource.
        zope.schema.interfaces.IVocabularyFactory
        """
        return vocabulary.SimpleVocabulary([term for term in self])

# !+NEED_NOT_BE_A_FACTORY, can register on IVocabulary
class TreeVDEXVocabulary(VDEXVocabularyMixin):
    """Class to generate hierarchical vdex vocabularies
    
    vocabulary = TreeVDEXVocabulary(file_name)
    """
    # !+ should inherit from IVocabulary (so also Iterable?) ?
    interface.implements(ITreeVocabulary)
    
    def generateJSON(self, selected = []):
        vdict = self.vdex.getVocabularyDict(lang=get_default_language())
        dynatree_dict = dict_to_dynatree(vdict, selected)
        return json.dumps(dynatree_dict)

    def validateTerms(self, value_list):
        for value in value_list:
            if self.getTermById(value) is None:
                raise LookupError

# !+NEED_NOT_BE_A_FACTORY, can register on IVocabulary
class FlatVDEXVocabularyFactory(VDEXVocabularyMixin, BaseVocabularyFactory):
    """    
    !+ instances are called in zope.formlib.form.setUpEditWidgets() and a new
    vocabulary.SimpleVocabulary() for the *current* language is created each
    time (could be cached).
    
    !+ to use POT-based translations instead... could make this inherit from
    vocabulary.SimpleVocabulary() and then only specify a single 
    default/reference language in the vdex file.
    """
    interface.implements(IVocabulary) # IVocabulary(IIterableVocabulary, IBaseVocabulary)
    # !+BaseVocabularyFactory should probably simply include this, instead of IBaseVocabulary?

class BoolFlatVDEXVocabularyFactory(FlatVDEXVocabularyFactory):
    value_cast = staticmethod(misc.as_bool)

    def getTermById(self, value):
        """Look up vdex term using unicode of boolean value"""
        value = unicode(value)
        return super(BoolFlatVDEXVocabularyFactory, self).getTermById(value)

# /vdex

class GroupRoleFactory(BaseVocabularyFactory):
    def __call__(self, context=None):
        app = common.get_application()
        terms = []
        roles = getUtilitiesFor(IRole, app)
        for name, role in roles:
            # Roles that must not be assigned to users in an office
            # !+ROLE_QUALIFIER need better role qualifiers, to make this dynamic from conf
            if name in ["bungeni.Anonymous",
                        "bungeni.Authenticated",
                        "bungeni.Drafter",
                        "bungeni.Owner",
                        "bungeni.Signatory",
                        "zope.Manager",
                        "bungeni.Admin",
                ]:
                continue
            if not ISubRoleAnnotations(role).is_sub_role:
                terms.append(vocabulary.SimpleTerm(name, name, role.title))
        return vocabulary.SimpleVocabulary(sorted(terms, key=lambda a: a.title))
group_role_factory = GroupRoleFactory()
component.provideUtility(GroupRoleFactory(), IVocabularyFactory, "group_role")


class GroupSubRoleFactory(BaseVocabularyFactory):
    def __call__(self, context):
        terms = []
        while not IGroup.providedBy(context):
            context = (getattr(context, "group", None) or 
                getattr(context, "__parent__", None))
            if not context:
                raise NotImplementedError("Context does not implement IGroup")
        group = removeSecurityProxy(context)
        assert interfaces.IGroup.providedBy(group), group
        role = getUtility(IRole, group.group_role)
        for sub_role in ISubRoleAnnotations(role).sub_roles:
            terms.append(vocabulary.SimpleTerm(sub_role, sub_role, sub_role))
        return vocabulary.SimpleVocabulary(terms)
group_sub_role_factory = GroupSubRoleFactory()
component.provideUtility(group_sub_role_factory, IVocabularyFactory, "group_sub_role")


# database sources

class DatabaseSource(BaseVocabularyFactory):
    """A simple implementation of vocabularies on top of a domain model, 
    ideally should only be used with small skinny tables, 
    actual value stored is the id.
    """
    
    # !+SOURCE_PARAMS(mr, aug-2012) make order of equivalent params consistent
    # across DatabaseSource and SpecializedSource to (token, title, value)
    # !+SOURCE_FACTORY(mr, aug-2012) merge DatabaseSource and SpecializedSource 
    # down to only one source factory class.
    def __init__(self, domain_model, token_field, value_field, 
            title_field=None, 
            title_getter=None, 
            order_by=None
        ):
        self.domain_model = domain_model
        self.token_field = token_field
        self.value_field = value_field
        assert title_field is None or title_getter is None, \
            "DatabaseSource [%s]: EITHER title_field [%s] OR title_getter [%s]" % (
                title_field, title_getter)
        self.title_field = title_field
        self.title_getter = title_getter
        self.order_by = order_by
    
    def construct_query(self, context):
        query = Session().query(self.domain_model)
        if self.order_by:
            query = query.order_by(self.order_by)
        return query
    
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        terms = []
        title_field = self.title_field or self.token_field
        title_getter = self.title_getter or (lambda ob: getattr(ob, title_field))
        for ob in results:
            if ITranslatable.providedBy(ob):
                ob = translate_obj(ob)
            terms.append(vocabulary.SimpleTerm(
                    value = getattr(ob, self.value_field), 
                    token = getattr(ob, self.token_field),
                    title = title_getter(ob),
            ))
        return vocabulary.SimpleVocabulary(terms)


chamber_factory = DatabaseSource(
    domain.Chamber, "short_name", "group_id",
    title_getter=lambda ob: "%s (%s-%s)" % (
        ob.full_name,
        ob.start_date and ob.start_date.strftime("%Y/%m/%d") or "?",
        ob.end_date and ob.end_date.strftime("%Y/%m/%d") or "?"))
component.provideUtility(chamber_factory, IVocabularyFactory, "chamber")

committee_factory = DatabaseSource(
    domain.Committee, "short_name", "group_id",
    title_getter=lambda ob: get_translated_group_label(ob)
)
component.provideUtility(committee_factory, IVocabularyFactory, "committee")


country_factory = DatabaseSource(
    domain.Country, "country_id", "country_id",
    title_field="country_name",
)
component.provideUtility(country_factory, IVocabularyFactory, "country")

report_factory = DatabaseSource(
    domain.Report, "doc_id", "doc_id",
    title_getter=lambda ob: IDCDescriptiveProperties(ob).title
)
component.provideUtility(report_factory, IVocabularyFactory, "report")

sitting_factory = DatabaseSource(
    domain.Sitting, "sitting_id", "sitting_id",
    title_getter=lambda ob: IDCDescriptiveProperties(ob).title
)
component.provideUtility(sitting_factory, IVocabularyFactory, "sitting")


class SpecializedSource(BaseVocabularyFactory):
    
    # !+SOURCE_PARAMS(mr, aug-2012) make order of equivalent params consistent
    # across DatabaseSource and SpecializedSource to (token, title, value)
    def __init__(self, token_field, title_field, value_field):
        self.token_field = token_field
        self.title_field = title_field
        self.value_field = value_field
    
    def construct_query(self, context):
        raise NotImplementedError("Must be implemented by subclass.")
    
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        terms = []
        title_field = self.title_field or self.token_field
        for ob in results:
            obj = translate_obj(ob)
            terms.append(vocabulary.SimpleTerm(
                    value = getattr(obj, self.value_field), 
                    token = getattr(obj, self.token_field),
                    title = getattr(obj, title_field),
            ))
        return vocabulary.SimpleVocabulary(terms)


class VenueFactory(BaseVocabularyFactory):
    def __call__(self, context):
        chamber = utils.get_chamber_for_context(context)
        results =[ venue for venue in chamber.venues.values() ]
        terms = []
        for ob in results:
            terms.append(
                vocabulary.SimpleTerm(
                    value=ob.venue_id, 
                    token=ob.venue_id,
                    title=IDCDescriptiveProperties(ob).title
                ))
        return vocabulary.SimpleVocabulary(terms)
venue_factory = VenueFactory()
component.provideUtility(venue_factory, IVocabularyFactory, "venue")

class SessionFactory(BaseVocabularyFactory):
    def __call__(self, context):
        chamber = utils.get_chamber_for_context(context)
        results =[ sess for sess in chamber.sessions.values() ]
        terms = []
        for ob in results:
            terms.append(
                vocabulary.SimpleTerm(
                    value=ob.session_id, 
                    token=ob.session_id,
                    title=IDCDescriptiveProperties(ob).title
                ))
        return vocabulary.SimpleVocabulary(terms)
session_factory = SessionFactory()
component.provideUtility(session_factory, IVocabularyFactory, "session")


class GroupTitleTypesFactory(SpecializedSource):
    def __init__(self):
        pass
    
    def construct_query(self, context):
        session= Session()
        return session.query(domain.TitleType) \
                .filter(schema.title_type.c.group_id == context.group_id)
    
    def __call__(self, context=None):
        while not IGroup.providedBy(context):
            context = context.__parent__
            if not context:
                raise NotImplementedError("Context does not implement IGroup")
        query = self.construct_query(context)
        results = query.all()
        terms = []
        for ob in results:
            obj = translate_obj(ob)
            terms.append(vocabulary.SimpleTerm(
                    value = obj.title_type_id, 
                    token = obj.title_type_id,
                    title = obj.title_name,
                ))
        return vocabulary.SimpleVocabulary(terms)
component.provideUtility(GroupTitleTypesFactory(), IVocabularyFactory, "group_title_types")


class WorkflowStatesVocabularyFactory(BaseVocabularyFactory):
    def __call__(self, context):
        if IVersion.providedBy(context):
            # also provides IAlchemistContent (check must precede)
            discriminator = removeSecurityProxy(context).head
        elif IAlchemistContent.providedBy(context):
            discriminator = context
        elif IAlchemistContainer.providedBy(context):
            discriminator = context.domain_model
        wf = capi.get_type_info(discriminator).workflow
        terms = [ 
            vocabulary.SimpleTerm(status, status, _(wf.get_state(status).title))
            for status in wf.states.keys() 
        ]
        return vocabulary.SimpleVocabulary(terms)
workflow_states = WorkflowStatesVocabularyFactory()
component.provideUtility(workflow_states, IVocabularyFactory, "workflow_states")


# Chamber Member vocabularies

class SpecializedMemberSource(BaseVocabularyFactory):
    """Base class for Member vocabularies for various scenarios.
    """
    chamber = None # set in self.construct_query
    context_user = None # set in self.construct_query
    
    # !+ why context optional?
    def __call__(self, context=None):
        query = self.construct_query(removeSecurityProxy(context))
        results = query.all() # either([Member], [User])
        terms = [
            vocabulary.SimpleTerm(
                value=ob.user_id,
                token=ob.user_id,
                title="%s %s" % (ob.first_name, ob.last_name))
            for ob in sorted(results)
        ]
        
        # only for Doc/Member/User contexts
        if not IAlchemistContainer.providedBy(context):
            user = self.context_user
            
            # consider only if not yet included in terms
            if user.user_id not in [ t.value for t in terms ]:
                
                # !+DECLARATIVE_ROOT_CONTAINER conditional on GroupMember.root_container ?
                # i.e. a user must be a member of root_container to be eligible...
                # !+ self.chamber.active_membership(user.user_id) ?
                if user not in [ m.user for m in self.chamber.group_members ]:
                    log.warn("Adding chamber [%s] non-member user [%s] to "
                        "vocabulary [%s] terms for context [%s]",
                            self.chamber.group_id, user.user_id, self, context)
                    #raise ValueError("%s: context user %r not a member of chamber %r" % (
                    #    self, user.login, self.chamber.principal_name))
                    
                    # !+ check if context user is NOT a member of this chamber -- should never happen?
                    # !+ still true? must add user, to avoid exception from view form
                    terms.append(vocabulary.SimpleTerm(
                            value=user.user_id,
                            token=user.user_id,
                            title="(%s %s)" % (user.first_name, user.last_name)))
        
        return vocabulary.SimpleVocabulary(terms)
    
    def construct_query(self, ctx):
        raise NotImplementedError("Must be implemented by subclass.")


class MemberSource(SpecializedMemberSource):
    """The list of Users (Group Container context) or Members (Member context).
    
    ASSUMPTION:
    "chamber_member" vocabulary, for "user_id" of Committee, PoliticalGroup, ...
    So, context here is EITHER a MemberContainer OR a Member.
    """
    
    def construct_query(self, ctx):
        session = Session()
        if IAlchemistContainer.providedBy(ctx):
            # MemberContainer - "add" member (Committee, PoliticalGroup)
            assert IGroupMember.implementedBy(ctx.domain_model), ctx
            # the group is the context's __parent__
            assert IGroup.providedBy(ctx.__parent__), ctx
            self.chamber = utils.get_chamber_for_group(ctx.__parent__)
            # potentials to become Members are all Users who ARE already members of the Chamber
            # !+ this logic is for groups within a chamber... 
            member_user_ids = [ m.user_id for m in self.chamber.group_members ]
            query = session.query(domain.User
                ).filter(
                    #sql.not_( !+negation with ColumnOperators.in_(), method notin_ in v0.8
                    domain.Member.user_id.in_(member_user_ids))
        else:
            # Member - "view" member
            assert IGroupMember.providedBy(ctx), ctx
            assert IGroup.providedBy(ctx.group), ctx
            self.chamber = utils.get_chamber_for_group(ctx.group)   
            chamber_id = self.chamber.group_id
            self.context_user = ctx.user
            user_id = ctx.user_id
            # all active Members of this Chamber
            query = session.query(domain.Member
                ).filter(
                    sql.or_(
                        sql.and_(
                            domain.Member.user_id == user_id,
                            domain.Member.group_id == chamber_id),
                        sql.and_(
                            domain.Member.group_id == chamber_id,
                            domain.Member.active_p == True)))
        return query
component.provideUtility(
    MemberSource(), IVocabularyFactory, "chamber_member")


class MemberDelegationSource(MemberSource):
    """MemberSource filtered down to either:
    
    a) EITHER only include only those Members who have delegated to current 
        logged in user if any (and, current user, if an MP, must also be 
        included as one of the delegators)
    b) OR, if no-one has delegated to current logged in user (a typical example
        would be when current logged in user is admin) then include all MPs!
    
    A logged in User will only be able to choose himself if he is a member
    of chamber or those Persons who gave him rights to act on his behalf.
    
    ASSUMPTION:
    "chamber_member_delegation" vocabulary, for "owner_id" of Bill, Question, ...
    So, context here is EITHER a {Doc}Container OR a {Doc}.
    
    !+DELEGATION_TO_NON_MP consequence of above logic is that if an MP delegates 
    to the Clerk (or Admin), the Clerk (or Admin) "loses" the full list of MPs!
    """
    
    def construct_query(self, ctx):
        
        if IAlchemistContainer.providedBy(ctx):
            if IWorkspaceContainer.providedBy(ctx):
                self.chamber = utils.get_login_user_chamber()
            else:
                # {Doc}Container - "add" doc
                assert IDoc.implementedBy(ctx.domain_model), ctx
                # chamber is a __parent__ ancestor
                # !+ in admin, the chamber is the context's __parent__
                assert IGroup.providedBy(ctx.__parent__), ctx
                self.chamber = utils.get_chamber_for_group(ctx.__parent__)
        else:
            # !+VERSION descriptor for DocVersion also uses this vocabulary for the 
            # "owner_id" field, but the source data we want here is tied to the 
            # version's head doc...
            if IDocVersion.providedBy(ctx):
                # proceed as if context is the version's head doc
                ctx = ctx.head
            # {Doc} - "view" a doc
            assert IDoc.providedBy(ctx), ctx
            # chamber is a doc.chamber
            assert IGroup.providedBy(ctx.chamber), ctx
            self.chamber = ctx.chamber
            self.context_user = ctx.owner
        
        # all active Members of this Chamber
        chamber_id = self.chamber.group_id
        all_mp_query = Session().query(domain.Member
            ).filter(
                sql.and_(
                    domain.Member.group_id == chamber_id,
                    domain.Member.active_p == True)
            )
        
        # user delegations
        user = utils.get_login_user()
        user_ids = [ ud.user_id 
            for ud in delegation.get_user_delegations(user) ]
        # current user must also be considered as (a potential MP) delegator
        if user.user_id not in user_ids:
            user_ids.append(user.user_id)
        
        delegated_mp_query = all_mp_query.filter(
                domain.Member.user_id.in_(user_ids))
        
        # if no-one has delegated to current logged in user (e.g. admin),
        # then include all MPs. !+DELEGATION_TO_NON_MP
        if len(delegated_mp_query.all()) == 0:
            return all_mp_query
        else:
            return delegated_mp_query
component.provideUtility(
    MemberDelegationSource(), IVocabularyFactory, "chamber_member_delegation")


class MemberSignatorySource(MemberSource):
    """Vocabulary for selection of signatories - other MPs excluding 
    any pre-selected signatories and the doc owner.
    
    ASSUMPTION:
    "signatory" vocabulary, for "user_id" of Signatory
    So, context here is EITHER a SignatoryContainer OR a Signatory
    """
    
    def construct_query(self, ctx):
        if IAlchemistContainer.providedBy(ctx):
            # SignatoryContainer - "add" signatory
            assert ISignatoryContainer.providedBy(ctx), ctx
            signatory_container = ctx
            # __parent__ is the doc
            assert IDoc.providedBy(ctx.__parent__), ctx
            head_doc = ctx.__parent__
            # chamber is a doc.chamber
            assert IGroup.providedBy(ctx.__parent__.chamber), ctx
            self.chamber = ctx.__parent__.chamber
        else:
            # Signatory - "view" a signatory
            assert ISignatory.providedBy(ctx), ctx
            # __parent__ is the signatory container
            assert ISignatoryContainer.providedBy(ctx.__parent__), ctx
            signatory_container = ctx.__parent__
            head_doc = ctx.head
            # chamber is a head.chamber
            self.chamber = ctx.head.chamber
            self.context_user = ctx.user
        
        # all active Members of this Chamber
        chamber_id = self.chamber.group_id
        all_mp_query = Session().query(domain.Member
            ).filter(
                sql.and_(
                    domain.Member.group_id == chamber_id,
                    domain.Member.active_p == True)
            )
        # exclude head doc owner and current signatories
        exclude_ids = set(
            [ sgn.user_id for sgn in signatory_container.values() ])
        exclude_ids.add(head_doc.owner_id)
        return all_mp_query.filter(sql.not_(
                domain.Member.user_id.in_(list(exclude_ids))))
component.provideUtility(MemberSignatorySource(), IVocabularyFactory, "signatory")


class UserNotMPSource(SpecializedMemberSource):
    """All active Users who are NOT Members.
    
    ASSUMPTION:
    "user_not_mp" vocabulary, for "user_id" of Committee Staff, Office Member
    So, context here is EITHER a MemberContainer OR a Member.
    """
    def construct_query(self, ctx):
        if IAlchemistContainer.providedBy(ctx):
            # MemberContainer - "add" member (Committee, Office)
            assert IGroupMember.implementedBy(ctx.domain_model), ctx
            # the group is the context's __parent__
            assert IGroup.providedBy(ctx.__parent__), ctx
            self.chamber = utils.get_chamber_for_group(ctx.__parent__)
        else:
            # Member - "view" member
            assert IGroupMember.providedBy(ctx), ctx
            assert IGroup.providedBy(ctx.group), ctx
            self.chamber = utils.get_chamber_for_group(ctx.group)   
            self.context_user = ctx.user
        
        mp_user_ids = sql.select(
            [schema.member.c.user_id], 
            schema.member.c.group_id == self.chamber.group_id)
        query = Session().query(domain.User).filter(
            sql.and_(
                sql.not_(domain.User.user_id.in_(mp_user_ids)),
                domain.User.active_p == "A"))
        return query
component.provideUtility(UserNotMPSource(), IVocabularyFactory, "user_not_mp")



class MinistrySource(SpecializedSource):
    """Ministries in the current chamber.
    """
    
    def __init__(self, value_field):
        self.value_field = value_field
    
    def construct_query(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        ministry_id = getattr(trusted, self.value_field, None)
        chamber = utils.get_chamber_for_context(trusted)
        if chamber:
            governments = session.query(domain.Government).filter(
                sql.and_(
                    domain.Government.parent_group_id == chamber.group_id,
                    domain.Government.status == u"active"
                ))
            government = governments.all()
            if len(government) > 0:
                gov_ids = [gov.group_id for gov in government]
                if ministry_id:
                    query = session.query(domain.Ministry).filter(
                        sql.or_(
                            domain.Ministry.group_id == ministry_id,
                            sql.and_(
                                domain.Ministry.parent_group_id.in_(gov_ids),
                                domain.Ministry.status == u"active"
                            ))
                    )
                else:
                    query = session.query(domain.Ministry).filter(
                            sql.and_(
                                domain.Ministry.parent_group_id.in_(gov_ids),
                                domain.Ministry.status == u"active"
                            ))
            else:
                if ministry_id:
                    query = session.query(domain.Ministry).filter(
                            domain.Ministry.group_id == ministry_id)
                else:
                    query = session.query(domain.Ministry)
        else:
            query = session.query(domain.Ministry)
        return query
               
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        terms = []
        trusted = removeSecurityProxy(context)
        ministry_id = getattr(trusted, self.value_field, None)
        for ob in results:
            terms.append(
                vocabulary.SimpleTerm(
                    value = getattr(ob, "group_id"), 
                    token = getattr(ob, "group_id"),
                    title = get_translated_group_label(ob)
                ))
        # !+MINISTRY_ID(mr, jul-2012) logic below must be faulty... (a) if this 
        # is ever executed, it will fail as "obj" is undefined (since long time), 
        # and (b) it seems to not have failed for a long time, so what is the 
        # code below trying to do anyway?
        if ministry_id:
            if query.filter(domain.Group.group_id == ministry_id).count() == 0:
                session = Session()
                ob = session.query(domain.Group).get(ministry_id)
                terms.append(
                    vocabulary.SimpleTerm(
                        value = getattr(ob, "group_id"), 
                        token = getattr(ob, "group_id"),
                        title = get_translated_group_label(ob)
                ))
        return vocabulary.SimpleVocabulary(terms)
ministry = MinistrySource("group_id")
component.provideUtility(ministry, IVocabularyFactory, "ministry")


'''
class MemberTitleSource(SpecializedSource):
    """ get titles (i.e. roles/functions) in the current context """
    
    def __init__(self, value_field):
        self.value_field = value_field 
    
    def _get_user_type(self, context):
        user_type = getattr(context, "member_type", None)
        if not user_type:
            user_type = self._get_user_type(context.__parent__)
        return user_type
    
    def construct_query(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        user_type = self._get_user_type(trusted)
        titles = session.query(domain.MemberTitle).filter(
            domain.MemberTitle.user_type == user_type).order_by(
                domain.MemberTitle.sort_order)
        return titles
    
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        terms = []
        for ob in results:
            obj = translate_obj(ob)
            terms.append(
                vocabulary.SimpleTerm(
                    value = getattr(obj, 'user_role_type_id'), 
                    token = getattr(obj, 'user_role_type_id'),
                    title = getattr(obj, 'user_role_name'),
                   ))
        return vocabulary.SimpleVocabulary(terms)
'''


class OwnerOrLoggedInUserSource(SpecializedSource):
    """The context owner OR the current logged in user (a list of 1 item).
    """
    def __call__(self, context):
        try:
            user = removeSecurityProxy(context).owner
            assert user is not None
        except (AttributeError, AssertionError):
            user = utils.get_login_user()
        title_field = self.title_field or self.token_field
        obj = translate_obj(user)
        terms = [
            vocabulary.SimpleTerm(
                value=getattr(obj, self.value_field), 
                token=getattr(obj, self.token_field),
                title=getattr(obj, title_field)),
        ]
        return vocabulary.SimpleVocabulary(terms)
owner_or_login = OwnerOrLoggedInUserSource(
    token_field="user_id",
    title_field="combined_name",
    value_field="user_id"
)
component.provideUtility(owner_or_login, IVocabularyFactory, "owner_or_login")


class UserSource(SpecializedSource):
    """All active users.
    """
    def construct_query(self, context):
        session = Session()
        users = session.query(domain.User).filter(domain.User.active_p == "A")
        return users
user = UserSource(
    token_field="user_id", 
    title_field="combined_name", 
    value_field="user_id"
)
component.provideUtility(user, IVocabularyFactory, "user")


class GroupSource(SpecializedSource):
    """All active groups.
    """

    def construct_query(self, context):
        # !+GROUP_FILTERS, refine, check for active, ...
        groups = Session().query(domain.Group).order_by(
            domain.Group.short_name, domain.Group.full_name)
        return groups

    def __call__(self, context=None):
        results = self.construct_query(context).all()
        terms = []
        for ob in results:
            terms.append(
                vocabulary.SimpleTerm(
                    value = getattr(ob, "group_id"), 
                    token = getattr(ob, "group_id"),
                    title = get_translated_group_label(ob)
                ))
        return vocabulary.SimpleVocabulary(terms)

group = GroupSource(
    token_field="group_id",
    title_field="short_name",
    value_field="group_id",
)
component.provideUtility(group, IVocabularyFactory, "group")

class GroupAssignmentSource(GroupSource):
    """Vocabulary for groups that may have a document assigned to them
    """
    def construct_query(self, context):
        principal_ids = []
        trusted = removeSecurityProxy(context)
        if IGroupAssignmentContainer.providedBy(trusted):
            for assignment in trusted.__parent__.sa_group_assignments:
                principal_ids.append(assignment.principal.principal_id)
        else:
            assert IGroupAssignment.providedBy(trusted)
            for assignment in trusted.doc.sa_group_assignments:
                principal_ids.append(assignment.principal.principal_id)
            principal_ids.remove(trusted.principal.principal_id)
        groups = Session().query(domain.Group).order_by(
            domain.Group.short_name, domain.Group.full_name).filter(
            sql.not_(domain.Group.principal_id.in_(principal_ids)))
        return groups

group_assignment = GroupAssignmentSource(
    token_field="principal_id",
    title_field="short_name",
    value_field="principal_id",
)
component.provideUtility(group_assignment, IVocabularyFactory,
    "group_assignment")

class MembershipUserSource(UserSource):
    """Filter out users already added to a membership container
    """
    def construct_query(self, context):
        users = super(MembershipUserSource, self).construct_query(context)
        trusted = removeSecurityProxy(context)
        exclude_ids = set()
        if IContainer.providedBy(trusted):
            for member in trusted.values():
                exclude_ids.add(member.user_id)
            users = users.filter(
                sql.not_(domain.User.user_id.in_(list(exclude_ids)))
            )
        return users
member = MembershipUserSource(
    token_field="user_id",
    title_field="combined_name",
    value_field="user_id",
)
component.provideUtility(member, IVocabularyFactory, "member")

                

class SittingAttendanceSource(SpecializedSource):
    """All members of this group who do not have an attendance record yet.
    """
    def construct_query(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        user_id = getattr(trusted, self.value_field, None)
        if user_id:
            query = session.query(domain.User).filter(domain.User.user_id == user_id)
            return query
        else:
            sitting = trusted.__parent__
            group_id = sitting.group_id
            sitting_id = sitting.sitting_id
            all_member_ids = sql.select([schema.member.c.user_id], 
                    sql.and_(
                        schema.member.c.group_id == group_id,
                        schema.member.c.active_p == True))
            attended_ids = sql.select([schema.sitting_attendance.c.member_id],
                     schema.sitting_attendance.c.sitting_id == sitting_id)
            query = session.query(domain.User).filter(
                sql.and_(domain.User.user_id.in_(all_member_ids),
                    ~ domain.User.user_id.in_(attended_ids)))
            return query
                 
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        terms = []
        for ob in results:
            terms.append(
                vocabulary.SimpleTerm(
                    value = getattr(ob, "user_id"), 
                    token = getattr(ob, "user_id"),
                    title = "%s %s" % (getattr(ob, "first_name"),
                            getattr(ob, "last_name"))
                   ))
        user_id = getattr(context, self.value_field, None) 
        if user_id:
            if len(query.filter(schema.user.c.user_id == user_id).all()) == 0:
                session = Session()
                ob = session.query(domain.User).get(user_id)
                terms.append(
                vocabulary.SimpleTerm(
                    value = getattr(ob, "user_id"), 
                    token = getattr(ob, "user_id"),
                    title = "(%s %s)" % (getattr(ob, "first_name"),
                            getattr(ob, "last_name"))
                   ))
        return vocabulary.SimpleVocabulary(terms)
sitting_attendance = SittingAttendanceSource(
    token_field="user_id",
    title_field="combined_name",
    value_field="member_id"
)
component.provideUtility(sitting_attendance, IVocabularyFactory, "sitting_attendance")




class SubstitutionSource(SpecializedSource):
    """Active user of the same group.
    """
    def _get_group_id(self, context):
        trusted = removeSecurityProxy(context)
        group_id = getattr(trusted, "group_id", None)
        if not group_id:
            group_id = getattr(trusted.__parent__, "group_id", None)
        return group_id
    
    def _get_user_id(self, context):
        trusted = removeSecurityProxy(context)
        user_id = getattr(trusted, "user_id", None)
        if not user_id:
            user_id = getattr(trusted.__parent__, "user_id", None)
        return user_id
    
    def construct_query(self, context):
        session= Session()
        query = session.query(domain.GroupMember
            #!+PRINCIPAL ).order_by("last_name", "first_name"
            ).filter(domain.GroupMember.active_p == True)
        user_id = self._get_user_id(context)
        if user_id:
            query = query.filter(
                domain.GroupMember.user_id != user_id)
        group_id = self._get_group_id(context)
        if group_id:
            query = query.filter(
                domain.GroupMember.group_id == group_id)
        return query
    
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        tdict = {}
        for ob in results:
            tdict[getattr(ob.user, "user_id")] = "%s %s" % (
                    getattr(ob.user, "first_name"),
                    getattr(ob.user, "last_name"))
        user_id = getattr(context, "replaced_id", None) 
        if user_id:
            if len(query.filter(domain.GroupMember.replaced_id == user_id).all()) == 0:
                session = Session()
                ob = session.query(domain.User).get(user_id)
                tdict[getattr(ob, "user_id")] = "%s %s" % (
                            getattr(ob, "first_name"),
                            getattr(ob, "last_name"))
        terms = []
        for t in tdict.keys():
            terms.append(
                vocabulary.SimpleTerm(value=t, token=t, title=tdict[t]))
        return vocabulary.SimpleVocabulary(terms)
substitution = SubstitutionSource(
    token_field="user_id",
    title_field="combined_name",
    value_field="user_id"
)
component.provideUtility(substitution, IVocabularyFactory, "substitution")


''' !+ORPHANED(mr, jun-2012) some time prior to r9435
class PIAssignmentSource(SpecializedSource):
    
    # !+STATES_TAGS_ASSUMPTIONS(mr, jun-2012) this aggregates all states of all 
    # workflows, assumes that a same named state has the same meaning acorss 
    # workflows, plus assumes that state tag names have special meaning, plus
    # assumes that all workflow/states are tagged with these tags.
    assignable_state_ids = set(sid
        for (key, ti) in capi.iter_type_info()
        for sid in ti.workflow.get_state_ids(
            not_tagged=["private", "fail", "terminal"], restrict=False)
    )
    
    def construct_query(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        parliament_id = common.getattr_ancestry(context, "parliament_id")
        item_id = getattr(context, self.value_field, None)
        trusted = removeSecurityProxy(context)
        existing_item_ids = [assn.item_id for assn in trusted.values()]
        if item_id:
            query = session.query(domain.Doc).filter(
                domain.Doc.doc_id == item_id)
        else:
            query = session.query(domain.Doc).filter(
                    sql.and_(
                        sql.not_(domain.Doc.status.in_(self.assignable_state_ids)),
                        sql.not_(domain.Doc.doc_id.in_(existing_item_ids)),
                        domain.Doc.parliament_id == parliament_id
                    )
                )
        return query
'''

''' !+UNUSED
class CommitteeSource(SpecializedSource):

    def construct_query(self, context):
        session= Session()
        parliament_id = common.getattr_ancestry(context, "parliament_id")
        query = session.query(domain.Committee).filter(
            sql.and_(
            domain.Committee.status == "active",
            domain.Committee.parent_group_id == parliament_id))
        return query
'''

''' !+UNUSED
class MotionPoliticalGroupSource(SpecializedSource):

    def construct_query(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        user_id = getattr(trusted, "owner_id", None)
        if user_id is None:
            user_id = utils.get_login_user().user_id
        parliament_id = common.getattr_ancestry(trusted, "parliament_id")
        
        if user_id: 
            query = session.query(domain.PoliticalGroupMember
               ).filter(
                    sql.and_(domain.PoliticalGroupMember.active_p == True,
                        domain.PoliticalGroupMember.user_id == user_id,
                        domain.PoliticalGroupMember.parent_group_id == parliament_id)
                       )
        else:
            query = session.query(domain.PoliticalGroup).filter(
                        domain.PoliticalGroup.parent_group_id == parliament_id)
        return query
'''

class QuerySource(object):
    """ call a query with an additonal filter and ordering
    note that the domain_model *must* not have a where and order_by clause 
    (otherwise the parameters passed to this query will be ignored),
    the order_by and filter_field fields *must* be public attributes"""
    interface.implements(IContextSourceBinder)
    
    def getValueKey(self, context):
        """iterate through the parents until you get a valueKey """
        if context.__parent__ is None:
            return None
        else:
            try:
                value_key = valueKey(context.__parent__.__name__)[0]
            except:
                value_key = self.getValueKey(context.__parent__)
        return value_key

    def __init__(self,
            domain_model, 
            token_field, 
            title_field, 
            value_field, 
            filter_field, 
            filter_value=None, 
            order_by_field=None
        ):
        self.domain_model = domain_model
        self.token_field = token_field
        self.value_field = value_field
        self.title_field = title_field
        self.filter_field = filter_field
        self.order_by_field = order_by_field
        self.filter_value = filter_value
    
    def construct_query(self, context):
        session = Session()
        trusted=removeSecurityProxy(context)
        if self.filter_value:
            query = session.query(self.domain_model).filter(
                self.domain_model.c[self.filter_field] == 
                    trusted.__dict__[self.filter_value])
        else:
            pfk = self.getValueKey(context)
            query = session.query(self.domain_model)
            query = query.filter(self.domain_model.c[self.filter_field] == pfk)
        
        query = query.distinct()
        if self.order_by_field:
            query = query.order_by(self.domain_model.c[self.order_by_field])
        
        return query
        
    def __call__(self, context=None):
        query = self.construct_query(context)
        results = query.all()
        terms = []
        title_field = self.title_field or self.token_field
        for ob in results:
            terms.append(
                vocabulary.SimpleTerm(
                    value = getattr(ob, self.value_field), 
                    token = getattr(ob, self.token_field),
                    title = getattr(ob, title_field),
            ))
        return vocabulary.SimpleVocabulary(terms)


def child_selected(children, selected):
    return (
        bool(set([ _["key"] for _ in children]).intersection(selected)) or
        bool([ _ for _ in children
            if _["children"] and child_selected(_["children"], selected) ])
    )

def dict_to_dynatree(input_dict, selected):
    """
    Adapted from collective.dynatree
    """
    if not input_dict:
        return []
    retval = []
    for key in input_dict:
        title, children = input_dict[key]
        children = dict_to_dynatree(children, selected)
        retval.append({
            "title": title,
            "key": key,
            "children": children,
            "select": key in selected,
            "isFolder": bool(children),
            "expand": bool(selected) and child_selected(children, selected)
        })
    return retval



#
# Vocabularies for XML configuration based report generation
#

# !+please use conformant method naming

class ReportXHTMLTemplateFactory(BaseVocabularyFactory):
    """XHTML templates for generation of reports in scheduling.
    
    Templates can be customized/added in:
    `bungeni_custom/reporting/templates/scheduling/`
    """
    terms = []
    template_folder = "scheduling"
    
    def __init__(self):
        self.terms = self.buildTerms()
    
    def getTitle(self, path):
        title = None
        doctree = etree.fromstring(open(path).read())
        node = doctree.find("{%s}config/title" % BUNGENI_REPORTS_NS)
        if node is not None:
            title = node.text
        return title
    
    def buildTerms(self):
        vocabulary_terms = []
        template_folder = capi.get_path_for("reporting", "templates", 
            self.template_folder
        )
        if not os.path.exists(template_folder):
            log.error("Directory for XHTML templates does not exist: %s",
                template_folder
            )
            return
        file_list = filter(lambda fname: fname.endswith(".html"),
            os.listdir(template_folder)
        )
        for file_name in file_list:
            file_path = "/".join([template_folder, file_name])
            vocabulary_terms.append(
                vocabulary.SimpleTerm(file_path,
                    token=hashlib.md5(file_name).hexdigest(),
                    title=self.getTitle(file_path)
                )
            )
        return vocabulary_terms

    def getTermByFileName(self, file_name):
        """Get the vocabulary term with the file_name.
        """
        for term in self.terms:
            if os.path.basename(term.value).startswith(file_name):
                return term
        return None
    
    def __call__(self, context=None):
        return vocabulary.SimpleVocabulary(self.terms)

report_xhtml_template_factory = ReportXHTMLTemplateFactory()

def update_term_doctype(term):
    template_file = open(term.value)
    doctree = etree.fromstring(template_file.read())
    node = doctree.find("{%s}config/doctypes" % BUNGENI_REPORTS_NS)
    if node is None:
        term.doctypes = []
    else:
        term.doctypes = [ dtype.strip() for dtype in node.text.split() ]
    template_file.close()
    return term

class DocumentXHTMLTemplateFactory(ReportXHTMLTemplateFactory):
    """XHTML templates for publication of documents in other formats.
    
    Templates can be customized or added in:
    `bungeni_custom/reporting/templates/documents`
    """
    template_folder = "documents"
    
    def __init__(self):
        super(DocumentXHTMLTemplateFactory, self).__init__()
        self.updateTermDocTypes()
    
    def updateTermDocTypes(self):
        """Read configuration options and update terms with doctype property.
        """
        self.terms = map(update_term_doctype, self.terms)

document_xhtml_template_factory = DocumentXHTMLTemplateFactory()

_i18n_message_factory = _
class WorkflowedTypeVocabulary(BaseVocabularyFactory):
    """A vocabulary of workflowed types
    """
    def __call__(self, context=None):
        terms = [vocabulary.SimpleTerm(value="*", token="*",
                title=_("* All types *")
        )]
        for (type_key, info) in capi.iter_type_info():
            if not ISerializable.implementedBy(info.domain_model):
                continue
            terms.append(
                vocabulary.SimpleTerm(
                    value=type_key, 
                    token=type_key,
                    #!+I18N(mb, Nov-2012) some display names aren't i18n msgids
                    # wrap them here so formlib translates from bungeni catalog
                    title=_i18n_message_factory(
                        (info.descriptor_model.display_name if 
                            info.descriptor_model else naming.plural(type_key))
                    )
                ))
        return vocabulary.SimpleVocabulary(terms)
serializable_type_factory = WorkflowedTypeVocabulary()
component.provideUtility(serializable_type_factory, IVocabularyFactory, "serializable_type")

class TextRecordTypesVocabulary(BaseVocabularyFactory):
    """This is a vocabulary of text records types used in scheduling.
    """
    def __call__(self, context=None):
        terms = []
        for (type_key, info) in capi.iter_type_info():
            if (IScheduleText.implementedBy(info.domain_model) 
                and IScheduleContent.implementedBy(info.domain_model)):
                    terms.append(
                        vocabulary.SimpleTerm(
                            value=type_key,
                            token=type_key,
                            title=_i18n_message_factory(
                                info.descriptor.display_name)
                        )
                    )
text_record_types_factory = TextRecordTypesVocabulary()
component.provideUtility(text_record_types_factory, IVocabularyFactory, "text_record_type")


def register_vocabulary_utility(vocabulary_name, vocabulary):
    globals()[vocabulary_name] = vocabulary
    component.provideUtility(vocabulary, IVocabularyFactory, vocabulary_name)

def register_vdex_vocabularies():
    """Register all VDEX vocabularies.
    """
    vocab_dir = capi.get_path_for("vocabularies")
    os.chdir(vocab_dir)
    for file_name in os.listdir(vocab_dir):
        if re.match(VDEX_FILE_REGEX, file_name) is not None:
            try:
                vdex = VDEXManager(open(file_name))
            except imsvdex.vdex.VDEXError:
                log.error("Exception while loading VDEX file %s", file_name)
                continue
            if vdex.isBoolean():
                vocab_class = BoolFlatVDEXVocabularyFactory
            elif vdex.isFlat():
                vocab_class = FlatVDEXVocabularyFactory
            else:
                vocab_class = TreeVDEXVocabulary
            vocabulary_name = file_name[:-len(".vdex")]
            register_vocabulary_utility(vocabulary_name, vocab_class(vdex))
        else:
            log.warning("Will not process VDEX file named %s. File name is "
                "not valid. File name must start with a lower case letter, "
                "may contain underscores and must have a 'vdex' extension",
                file_name)
#!+REGISTRATION(mb, feb-2013) - can't use ZCML to register
# descriptors seem to be imported before vocabularies are set up
register_vdex_vocabularies()

# !+VERSION_CLASS_PER_TYPE doc_version_type, an aggregated vdex vocab, of 
# current defined "{doc}_type" vocabs, that is needed for the "doc_type" field 
# of doc_version; only needed until a dedicated version classes per version.
def _doc_version_tmp_aggregated_type():
    import copy
    vdex = copy.deepcopy(doc_type.vdex)
    vdex.term_dict.update(event_type.vdex.term_dict)
    vdex.term_dict.update(question_type.vdex.term_dict)
    vdex.term_dict.update(bill_type.vdex.term_dict)
    vdex.term_dict.update(doc_type.vdex.term_dict)
    register_vocabulary_utility(
        "doc_version_tmp_aggregated_type", FlatVDEXVocabularyFactory(vdex))
_doc_version_tmp_aggregated_type()

