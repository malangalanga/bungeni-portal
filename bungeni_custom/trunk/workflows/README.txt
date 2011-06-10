Custom Definitions of the Workflows of Parliamentary Documents
==============================================================

This file reference information and guidelines about how to define/localize the 
workflow instances of parliamentary documents, for a given Bungeni deployment.

!+DEVELOPER_ORIENTED(mr, jun-2011) this README is tyo be reworked, as
currently oriented more towards the Bungeni developer than to the site 
administartor of a Bungeni deployment.


Workflow XML Source Style Guide
===============================

States
------

- the state ID should be a lowercase *adverb* (more or less) that describes 
the _condition_ an object is in, given the transition trail of the object.

- state multiple-word IDs are `_` (underscore) separated -:- in particular 
the `-` (hyphen) should *not* be used as separator as this character, 
besides being invalid as part of a python name, is reserved by 
`bungeni.core.workflow` for use as a separator character.

- a bungeni _role_ name should *never* be part of a state name or title.

- states within a same workflow should never have a same id -:- because in 
an XML document all element IDs should be unique, and Bungeni defines each 
workflow as a single XML document.

- permissions are organized by target type, with each set of assignments
  for a target type being indicated within a comment to marke the start 
  of each such section.

- the order of attributes should respect:
    id 
    title
    version=False
    like_state
    note
    obsolete=False

- within each target-section, the order of appearance of permission actions 
  (for appropriate actions) is:
    View
    Edit
    Add
    Delete

- for each single permission, the order of assigment to each appropriate 
  role follows the following order:
    <role id="bungeni.Clerk" title="Clerks Office" />
    <role id="bungeni.Speaker" title="Speaker Office" />
    <role id="bungeni.Owner" title="Owner" />
    <role id="bungeni.MP" title="Member of parliament" />
    <role id="bungeni.Minister" title="Minister" />
    <role id="bungeni.Authenticated" title="All authenticated users" />
    <role id="bungeni.Anonymous" title="Bungeni Visitor" />

- for a motion, the MP is also the Owner.

- denying zope.View on a Role seems to deny every other permission !+??

- the root element id should not contain "-" (use "_" as separator).

NOTE: to easily see the the evaluated result of all permission assigments 
for each workflow state definition (that uses like_state) set the 
logging level to DEBUG.

!+ <state ... manual_date="true">
    transition to a "politicocratic" destination states need to allow 
    freedom to manually set the transition date_active, but transition 
    to a "bureaucratic" destination states should not.


Transitions
-----------

- the transition title should be a lowercase *verb*.

- a bungeni _role_ name should *never* be part of a transition title.

- each individual workflow transition (*except* for _initial_ category of 
transitions) have an automatically generated *dedicated* permission, that 
is named as follows: `bungeni.{object}.wf.{transition}`
The _initial_ class of transitions is an exception to this rule because 
such transitions have an _automatic_ trigger resulting from the act of 
creating the object, that presumably is already access-controlled with a 
`bungeni.{object}.Add` type permission. Because of this, all _initial_ 
transitions must have *no permission specified*.

- the order of attributes should respect:
    title
    source
    destination
    condition=None
    trigger=MANUAL
    roles=bungeni.Clerk
    permission=CheckerPublic !+ bungeni.{module}.wf.{transition_id}
    order=0
    require_confirmation=False
    note


