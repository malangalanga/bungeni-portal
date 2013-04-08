Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using 
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

Because add-on themes or products may remove or hide the login portlet, this test will use the login form that comes with plone.  

    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.  We then ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True

Finally, let's return to the front page of our site before continuing

    >>> browser.open(portal_url)

-*- extra stuff goes here -*-
The Repository Community content type
===============================

In this section we are tesing the Repository Community content type by performing
basic operations like adding, updadating and deleting Repository Community content
items.

Adding a new Repository Community content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Repository Community' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Community').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Community' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Community Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Repository Community' content item to the portal.

Updating an existing Repository Community content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Repository Community Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Repository Community Sample' in browser.contents
    True

Removing a/an Repository Community content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Repository Community
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Repository Community Sample' in browser.contents
    True

Now we are going to delete the 'New Repository Community Sample' object. First we
go to the contents tab and select the 'New Repository Community Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Repository Community Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Repository Community
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Repository Community Sample' in browser.contents
    False

Adding a new Repository Community content item as contributor
------------------------------------------------

Not only site managers are allowed to add Repository Community content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Repository Community' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Community').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Community' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Community Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Repository Community content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Document Repository content type
===============================

In this section we are tesing the Document Repository content type by performing
basic operations like adding, updadating and deleting Document Repository content
items.

Adding a new Document Repository content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Document Repository' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Document Repository').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Document Repository' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Document Repository Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Document Repository' content item to the portal.

Updating an existing Document Repository content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Document Repository Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Document Repository Sample' in browser.contents
    True

Removing a/an Document Repository content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Document Repository
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Document Repository Sample' in browser.contents
    True

Now we are going to delete the 'New Document Repository Sample' object. First we
go to the contents tab and select the 'New Document Repository Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Document Repository Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Document Repository
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Document Repository Sample' in browser.contents
    False

Adding a new Document Repository content item as contributor
------------------------------------------------

Not only site managers are allowed to add Document Repository content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Document Repository' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Document Repository').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Document Repository' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Document Repository Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Document Repository content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Repository Item content type
===============================

In this section we are tesing the Repository Item content type by performing
basic operations like adding, updadating and deleting Repository Item content
items.

Adding a new Repository Item content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Repository Item' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Item').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Item' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Item Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Repository Item' content item to the portal.

Updating an existing Repository Item content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Repository Item Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Repository Item Sample' in browser.contents
    True

Removing a/an Repository Item content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Repository Item
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Repository Item Sample' in browser.contents
    True

Now we are going to delete the 'New Repository Item Sample' object. First we
go to the contents tab and select the 'New Repository Item Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Repository Item Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Repository Item
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Repository Item Sample' in browser.contents
    False

Adding a new Repository Item content item as contributor
------------------------------------------------

Not only site managers are allowed to add Repository Item content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Repository Item' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Item').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Item' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Item Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Repository Item content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Repository Collection content type
===============================

In this section we are tesing the Repository Collection content type by performing
basic operations like adding, updadating and deleting Repository Collection content
items.

Adding a new Repository Collection content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Repository Collection' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Collection').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Collection' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Collection Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Repository Collection' content item to the portal.

Updating an existing Repository Collection content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Repository Collection Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Repository Collection Sample' in browser.contents
    True

Removing a/an Repository Collection content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Repository Collection
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Repository Collection Sample' in browser.contents
    True

Now we are going to delete the 'New Repository Collection Sample' object. First we
go to the contents tab and select the 'New Repository Collection Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Repository Collection Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Repository Collection
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Repository Collection Sample' in browser.contents
    False

Adding a new Repository Collection content item as contributor
------------------------------------------------

Not only site managers are allowed to add Repository Collection content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Repository Collection' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Collection').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Collection' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Collection Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Repository Collection content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Community content type
===============================

In this section we are tesing the Community content type by performing
basic operations like adding, updadating and deleting Community content
items.

Adding a new Community content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Community' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Community').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Community' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Community Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Community' content item to the portal.

Updating an existing Community content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Community Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Community Sample' in browser.contents
    True

Removing a/an Community content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Community
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Community Sample' in browser.contents
    True

Now we are going to delete the 'New Community Sample' object. First we
go to the contents tab and select the 'New Community Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Community Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Community
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Community Sample' in browser.contents
    False

Adding a new Community content item as contributor
------------------------------------------------

Not only site managers are allowed to add Community content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Community' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Community').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Community' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Community Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Community content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Repository Collection content type
===============================

In this section we are tesing the Repository Collection content type by performing
basic operations like adding, updadating and deleting Repository Collection content
items.

Adding a new Repository Collection content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Repository Collection' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Collection').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Collection' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Collection Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Repository Collection' content item to the portal.

Updating an existing Repository Collection content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Repository Collection Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Repository Collection Sample' in browser.contents
    True

Removing a/an Repository Collection content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Repository Collection
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Repository Collection Sample' in browser.contents
    True

Now we are going to delete the 'New Repository Collection Sample' object. First we
go to the contents tab and select the 'New Repository Collection Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Repository Collection Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Repository Collection
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Repository Collection Sample' in browser.contents
    False

Adding a new Repository Collection content item as contributor
------------------------------------------------

Not only site managers are allowed to add Repository Collection content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Repository Collection' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Repository Collection').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Repository Collection' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Repository Collection Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Repository Collection content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)



