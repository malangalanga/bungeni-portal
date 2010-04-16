
from zope import interface, schema, lifecycleevent
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.app.container.interfaces import IContainer
from ore.alchemist.interfaces import IAlchemistContent
from ore.alchemist.interfaces import IAlchemistContainer
from ore.wsgiapp.interfaces import IApplication
from i18n import _



DEBUG = True
ENABLE_LOGGING = False
ENABLE_EVENT_LOGGING = False

if ENABLE_EVENT_LOGGING:
    import eventlog

class IBungeniApplication( IApplication ):
    """
    Bungeni Application
    """

class IBungeniAdmin( IContainer ):
    """
    Admin Container
    """

class IAdminUserContainer( interface.Interface ):
    """
    a container that returns object for the admin ui, marked with admin interface markers
    """

class IAdminGroupContainer( interface.Interface ):
    pass

class IUserAdmin( interface.Interface ):
    """
    marker interface attached to user objects viewed in the admin for admin views
    """
class IGroupAdmin( interface.Interface ):
    """
    marker interface attached to user objects viewed in the admin for admin views    
    """

class IBungeniUser( interface.Interface ):
    """
    a user in bungeni
    """     
    
class IBungeniGroup( interface.Interface ):
    """
    a group in bungeni
    """
class IParliament(IBungeniGroup):
    """ marker interface for group parliament """

class IGovernment(IBungeniGroup):
    """ marker interface for group Government """

class IMinistry(IBungeniGroup):
    """ marker interface for group ministry """            

class ICommittee(IBungeniGroup):
    """ marker interface for group ministry """ 
    
class IPoliticalParty(IBungeniGroup):
    """ marker interface for political party """   

class IOffice(IBungeniGroup):
    """ marker interface for a parliamentary office """   
    
class ICommittee(IBungeniGroup):
    pass

class IBungeniGroupMembership( interface.Interface ):
    """
    group membership in bungeni
    """

class IMemberOfParliament( IBungeniGroupMembership ):
    pass
    
class IPartyMember( IBungeniGroupMembership ):
    pass
    
class IMinister( IBungeniGroupMembership ):
    pass
    
class ICommitteeMember( IBungeniGroupMembership ):
    pass

class ICommitteeStaff( IBungeniGroupMembership ):
    pass
    
class IOfficeMember( IBungeniGroupMembership ):
    pass




class IBungeniContent( interface.Interface ):
    """
    parliamentary content
    """

class IBungeniContainer(IAlchemistContainer):
    """
    parliamentary container
    """

class IGroupSittingContainer( IBungeniContainer ):
    pass

class IBungeniGroupMembershipContainer( IBungeniContainer ):
    pass

class ICommitteeMemberContainer(IBungeniGroupMembershipContainer):
    pass
    
class ICommitteeStaffContainer(IBungeniGroupMembershipContainer):
    pass
       
class IVersionContainer(IBungeniContainer):
    pass


class IHeading( IBungeniContent ):
    pass

class IEventItem( IBungeniContent ):
    pass

class IQuestion( IBungeniContent ):
    """ Parliamentary Question
    """

class IQuestionVersion(IQuestion):
    pass

class IQuestionVersionContainer(IVersionContainer):
    pass


class IBill( IBungeniContent ):
    """ Parliamentary Bill
    """

class IBillVersion(IBill):
    pass

class IBillVersionContainer(IVersionContainer):
    pass

class IMotion( IBungeniContent ):
    """ Parliamentary Motion
    """

class IMotionVersion(IMotion):
    pass

class IMotionVersionContainer(IVersionContainer):
    pass
    


class IGroupSitting(interface.Interface):
    pass

class IGroupSittingAttendance(interface.Interface):
    pass


class IItemSchedule(interface.Interface):
    pass

class ISittingType(interface.Interface):
    pass


class IScheduledItemDiscussion(interface.Interface):
    pass

class ITabledDocument(IBungeniContent):
    """
    tabled document
    """
class ITabledDocumentVersion(ITabledDocument):
    pass

class ITabledDocumentVersionContainer(IVersionContainer):
    pass
    
class IAgendaItem(IBungeniContent):
    pass
    
class IAgendaItemVersion(IAgendaItem):
    pass

class IAgendaItemVersionContainer(IVersionContainer):
    pass
    
class IParliamentSession( interface.Interface ):
    pass

class IBungeniSetup( interface.Interface ):

    def setUp( app ):
        """
        setup the application on server start
        """

class IBungeniSettings( interface.Interface ):
    speakers_office_email = schema.TextLine(title=_(u"Speaker's Office Email"), 
                                            default=u"speakers.office@parliament.go.tld")
    speakers_office_notification = schema.Bool( title=_(u"Speaker's Office Notification"),
                                                description=_(
                                                    u"true if the Speakers office wants to be alerted by mail" \
                                                    u"whenever a bill, motion, question is submitted" ),
                                                default=True
                                                )
    clerks_office_notification = schema.Bool( title=_("Clerk's Office Notification"),
                                              description=_(
                                                  u"true if the clerks office wants to be alerted by mail"
                                                  u"whenever a bill, motion, question is submitted"),
                                              default=True
                                              )
    clerks_office_email   = schema.TextLine(title=_(u"Clerks's Office Email"),
                                            default=u"clerks.office@parliament.go.tld" )
    
    administrators_email  = schema.TextLine(title=_(u"Administrator's Email") )
    question_submission_allowed = schema.Bool( title=_(u"Allow Question Submission"), default=True )    
    days_to_defer_question = schema.Int(title=_(u"Days to Defer Question"),
                                        description=_(u"Time after which admissible questions are automatically deferred"),
                                        default=10 )
    days_to_notify_ministry_unanswered = schema.Int(title=_(u"Days to Notify Ministry of Pending Response"),
                                                    description=_(u"Timeframe after which the clerksoffice and the ministry is alerted that" \
                                                                  u"questions that are pending response are not yet answered"
                                                                  )
                                                    )
    days_before_question_schedule = schema.Int( title=_(u"Days before question scheduled"), default=3 )
    days_before_bill_schedule = schema.Int( title=_(u"Days before bill scheduled"), default=3 )    
    max_questions_sitting = schema.Int( title=_(u"Max Questions Per Sitting"), default=15  )
    max_mp_questions_sitting = schema.Int( title=_(u"Max Questions Per Sitting Per MP"), default=1  )

class IBungeniUserSettings( interface.Interface ):

    # examples
    email_delivery = schema.Bool( title=_(u"Email Notifications Enabled?"), default=True  )
    
class IAssignment( IAlchemistContent ):

    content = schema.Object( IAlchemistContent )
    context = schema.Object( IAlchemistContent )
    title = schema.TextLine(title=_(u"Name of the Assignment"))
    start_date = schema.Date(title=_(u"Start Date of the Assignment"))
    end_date = schema.Date(title=_(u"End Date of the Assignment"))    
    type = schema.TextLine(title=_(u"Assignment Type"), readonly=True)
    status = schema.TextLine(title=_(u"Status"), readonly=True)
    notes  = schema.Text( title=_(u"Notes"), description=_(u"Notes"))
    
class IContentAssignments( interface.Interface ):
    """ assignments of this content to different contexts""" 

    def __iter__(  ):
        """ iterate over assignments for this context """

class IContextAssignments( interface.Interface ):
    """ content assignments for the given context/group """
    
    def __iter__(  ):
        """ iterate over assignments for this context """

class IAssignmentFactory( interface.Interface ):
    """ assignment factory """
    
    def new( **kw ):
        """
        create a new assignment
        """
        
class IAttachedFile( interface.Interface ):     
    pass   
        
       
class IAttachedFileVersionContainer(IVersionContainer):
    pass
        
class IConsignatory( interface.Interface ):
    """ consignatories for bills, motions,.."""
    
class IConstituency( interface.Interface ):
    """ Constituencies """

class IConstituencyDetail( interface.Interface ):
    pass

class IItemScheduleCategory( interface.Interface ):
    pass

    
class IDirectoryLocation( interface.Interface ):

    repo_path = schema.ASCIILine()
    object_id = schema.Int()
    object_type = schema.ASCIILine()

class IProxiedDirectory( interface.Interface ):
    """ an interface for a contained directory we can attach menu links
        to that point back to our parent
    """
    
class IVersion( interface.Interface ):
    """
    a version of an object is identical in attributes to the actual object, based
    on that object's domain schema
    """

class IAttachedFileVersion( IVersion ):     
    pass   


class IDateRangeFilter(interface.Interface):
    """Adapts a model container instance and a SQLAlchemy query
    object, applies a date range filter and returns a query.

    Parameters: ``start_date``, ``end_date``.

    These must be bound before the query is executed.
    """
    
    
class IChange(interface.Interface):
    """ Marker for Change (log table) """
        
class IMemberRoleTitle(interface.Interface):
    pass        
        
    
class IUserAddress(interface.Interface):
    """ marker interface addresses of a user """

class IGroupItemAssignment(interface.Interface):
    pass

class IGroupGroupItemAssignment(IGroupItemAssignment):
    pass

class IItemGroupItemAssignment(IGroupItemAssignment):
    pass            
    
class IReport(interface.Interface):
    pass        
            
class IUserDelegation(interface.Interface):
    pass

class IProvince(interface.Interface):
    pass
    
class IRegion(interface.Interface):
    pass    

class ITranslatable(interface.Interface):
    """ Marker Interface if an object is translatable """
    language = interface.Attribute(
        """The language of the values of the translatable attributes of 
        the instance""")

                
