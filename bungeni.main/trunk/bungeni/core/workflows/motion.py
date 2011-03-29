
# setup in adapters.py
wf = None
states = None

#

from bungeni.core.workflows.notification import Notification, notifier
from bungeni.core import globalsettings as prefs
from bungeni.core.i18n import _


@notifier("Motion", "received")
class SendNotificationToMemberUponReceipt(Notification):
    body = _('notification_email_to_member_upon_receipt_of_motion',
             default="Motion received")
    
    @property
    def subject(self):
        return u'Motion received: %s' % self.context.short_name

    @property
    def condition(self):
        return self.context.receive_notification

    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()


@notifier("Motion", "submitted")
class SendNotificationToClerkUponSubmit(Notification):
    """Send notification to Clerk's office upon submit.

    We need to settings from a global registry to determine whether to
    send this notification and where to send it to.
    """
    body = _('notification_email_to_clerk_upon_submit_of_motion',
             default="Motion submitted")

    @property
    def subject(self):
        return u'Motion submitted: %s' % self.context.short_name

    @property
    def condition(self):
        return prefs.getClerksOfficeReceiveNotification()
    
    @property
    def recipient_address(self):
        return prefs.getClerksOfficeEmail()


@notifier("Motion", "inadmissible")
@notifier("Motion", "rejected")
class SendNotificationToMemberUponReject(Notification):
    """Issued when a motion was rejected by the speakers office.
    Sends a notice that the Motion was rejected"""
    body = _('notification_email_to_member_upon_rejection_of_motion',
             default="Motion rejected")

    @property
    def subject(self):
        return u'Motion rejected: %s' % self.context.short_name

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getSpeakersOfficeEmail()


@notifier("Motion", "clarification_required")
class SendNotificationToMemberUponNeedsClarification(Notification):
    """Issued when a motion needs clarification by the MP
    sends a notice that the motion needs clarification
    """
    body = _('notification_email_to_member_upon_need_clarification_of_motion',
             default="Your motion needs to be clarified")

    @property
    def subject(self):
        return u'Motion needs clarification: %s' % self.context.short_name

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()


@notifier("Motion", "deferred")
class SendNotificationToMemberUponDeferred(Notification):
    """Issued when a motion was deferred by Clerk's office.
    """
    body = _('notification_email_to_member_upon_defer_of_motion',
             default="Motion deferred")

    @property
    def subject(self):
        return u'Motion deferred: %s' % self.context.short_name

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getSpeakersOfficeEmail()


@notifier("Motion", "scheduled")
class SendNotificationToMemberUponSchedule(Notification):
    """Issued when a motion was scheduled by Speakers office.
    Sends a Notice that the motion is scheduled for ... 
    """
    body = _('notification_email_to_member_upon_schedule_of_motion',
             default="Motion scheduled")

    @property
    def subject(self):
        return u'Motion scheduled: %s' % self.context.short_name

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()

''' !+ remove, grep for: SendNotificationToMemberUponPostponed IMotionPostponedEvent
class SendNotificationToMemberUponPostponed(Notification):
    """Issued when a motion was postponed by the speakers office.
    sends a notice that the motion could not be debated and was postponed"""

    component.adapts(interfaces.IMotionPostponedEvent)

    body = _('notification_email_to_member_upon_postpone_of_motion',
             default="Motion postponed")

    @property
    def subject(self):
        return u'Motion postponed: %s' % self.context.short_name

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()
'''

