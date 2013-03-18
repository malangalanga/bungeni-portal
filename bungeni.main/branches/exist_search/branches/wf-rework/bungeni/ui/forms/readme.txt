Setup
-----
Setting up Database Connection and Utilities:

   >>> from bungeni import models as model
   >>> import datetime
   >>> import bungeni.models.testing
   >>> db = bungeni.models.testing.setup_db()
   >>> from bungeni.alchemist import Session
   >>> session = Session()
   >>> from bungeni.ui.forms.test_dates import today, yesterday, tomorrow, dayat

   
Note that we only test the overlap of 'peers' here.
refer to test_dates.py to test  that contained objects are inside
their parents dates
   
Parliaments
-----------
   
   >>> parliament = model.Parliament( short_name=u"p_1", start_date=today, election_date=yesterday, end_date=tomorrow)
   >>> parliament.language = "en"
   >>> session.add( parliament)
   >>> session.flush()
   
   >>> parliament.parliament_id 
   1L
   
   >>> from bungeni.ui.forms import validations

   
Before you can add a new parliament all others must be closed
   
   
Add a new (open ended) parliament
   >>> parliament2 = model.Parliament( short_name=u"p_2", start_date=tomorrow, election_date=today, end_date=None)
   >>> parliament2.language = "en"
   >>> session.add( parliament2)
   >>> session.flush()
   
Note that the date yesterday is well ouside our p_2 so it does not matter.

give the 2nd parliament an end date and save
   >>> parliament2.end_date = dayat
   >>> session.flush() 
   
No open parliaments  anymore 

   
Now check for overlapping dates but not for the current (edited) parliament
   

   
Add a governmemt:

   >>> gov = model.Government(short_name=u"gov_1", start_date=today, end_date=tomorrow )
   >>> gov.parent_group_id = parliament.parliament_id
   >>> gov.language = "en"
   >>> session.add( gov )
   >>> session.flush() 
 
   
      
Add a second government

   >>> gov2 = model.Government(short_name=u"gov_2", start_date=tomorrow, end_date=dayat )
   >>> gov2.parent_group_id = parliament.parliament_id
   >>> gov2.language = "en"
   >>> session.add( gov2 )
   >>> session.flush()


Sessions
-----------
A parliamentary Session

   >>> sess = model.ParliamentSession()
   >>> sess.parliament_id = parliament.parliament_id
   >>> sess.short_name = u"First Session"
   >>> sess.full_name = u"First Session"
   >>> sess.start_date = yesterday
   >>> sess.end_date = today
   >>> sess.language = "en"
   >>> session.add(sess)
   >>> session.flush() 
 
   >>> sess.session_id
   1L
 

 
A second session
 
   >>> sess2 = model.ParliamentSession()
   >>> sess2.parliament_id = parliament.parliament_id
   >>> sess2.short_name = u"2nd Session"
   >>> sess2.full_name = u"2nd Session"
   >>> sess2.start_date = tomorrow
   >>> sess2.end_date = dayat
   >>> sess2.language = "en"
   >>> session.add(sess2)
   >>> session.flush()
 

 
Sittings
---------
 
    >>> ssit = model.GroupSitting()
    >>> ssit.group_id = parliament.parliament_id
    >>> ssit.start_date = today
    >>> ssit.end_date = tomorrow
    >>> ssit.language = "en"
    >>> session.add(ssit)
    >>> session.flush()

Just check if we get something back because the return value depends on the times


   
   
For Edit we need to be sure we do not check for the current data itself.
   
    >>> ssit2 = model.GroupSitting()
    >>> ssit2.group_id = parliament.parliament_id
    >>> ssit2.start_date = yesterday
    >>> ssit2.end_date = today
    >>> ssit2.language = "en"
    >>> session.add(ssit2)
    >>> session.flush()
   
Just a quick check that the above validation for yesterday now fails

and the real check
            


Parliament members
Regions and provinces get their primary key with a db sequence:
 
 >>> region = model.Region()
 >>> region.region = u"Nairobi"
 >>> region.language = "en"
 >>> session.add(region)
 >>> session.flush() 

 >>> province = model.Province()
 >>> province.province= u"Central"
 >>> province.language = "en"
 >>> session.add(province)
 >>> session.flush()

 >>> constituency = model.Constituency()
 >>> constituency.name = u"Nairobi/Westlands"
 >>> constituency.region_id = 1
 >>> constituency.province_id = 1
 >>> constituency.start_date = today
 >>> constituency.language = "en"
 >>> session.add(constituency)
 >>> session.flush()

add some users:
    >>> mp_1 = model.User(u"mp_1", 
    ...        first_name=u"a", 
    ...        last_name=u'ab', 
    ...        email=u"mp1@example.com", 
    ...        date_of_birth=today,
    ...        language="en",
    ...        gender='M')
    >>> mp_2 = model.User(u"mp_2", 
    ...        first_name=u"b", 
    ...        last_name=u"bc", 
    ...        date_of_birth=today,
    ...        email=u"mp2@example.com",
    ...        language="en",
    ...        gender='M')
    >>> session.add(mp_1)
    >>> session.add(mp_2)
    >>> session.flush()
    
    >>> mp1 = model.MemberOfParliament()
    >>> mp1.group_id = parliament.group_id
    >>> mp1.user_id = mp_1.user_id
    >>> mp1.start_date = today
    >>> mp1.constituency_id = 1
    >>> mp1.elected_nominated = "E"
    >>> mp1.language = "en"
    >>> session.add(mp1)
    >>> session.flush()
    
    >>> mp2 = model.MemberOfParliament()
    >>> mp2.group_id = parliament.group_id
    >>> mp2.user_id = mp_2.user_id
    >>> mp2.start_date = today
    >>> mp2.constituency_id = 1
    >>> mp2.elected_nominated = "N"
    >>> mp2.language = "en"
    >>> session.add(mp2)
    >>> session.flush()

titles
--------------

    >>> mrt1 = model.MemberTitle()
    >>> mrt1.user_type = 'memberofparliament'
    >>> mrt1.user_role_name = u"President"
    >>> mrt1.user_unique = True
    >>> mrt1.sort_order = 10
    >>> mrt1.language = "en"
    >>> session.add(mrt1)
    >>> session.flush()
    
    >>> mrt2 = model.MemberTitle()
    >>> mrt2.user_type = 'memberofparliament'
    >>> mrt2.user_role_name = u"Member"
    >>> mrt2.user_unique = False
    >>> mrt2.sort_order = 20
    >>> mrt2.language = "en"
    >>> session.add(mrt2)
    >>> session.flush()
    
    
    
    >>> mt1 = model.MemberRoleTitle()
    >>> mt1.membership_id = mp1.membership_id
    >>> mt1.title_name_id = mrt1.user_role_type_id
    >>> mt1.start_date = today
    >>> mt1.title_name_id = mrt1.user_role_type_id
    >>> session.add(mt1)
    >>> session.flush()

A (group) member can only hold the same title once at a time
-------------------------------------------------------------

 
    >>> mt1.end_date = tomorrow
    >>> session.flush()

  
exclude data with role_title_id when editing the record

  

Some titles must be unique inside a group
-----------------------------------------
    
    >>> mt2 = model.MemberRoleTitle()
    >>> mt2.membership_id = mp1.membership_id
    >>> mt2.title_name_id = mrt2.user_role_type_id
    >>> mt2.start_date = today
    >>> session.add(mt2)
    >>> session.flush()
   
second check for same title at a time

A president is already there
  

Members do not have to be unique


And the day after tomorrow there is no more president


when editing exclude self

    
    


Membership in a political group
---------------------------


      
      
clean up - commit open transactions
---------------------------------

   >>> session.flush()
   >>> session.close() 
         
         
   
