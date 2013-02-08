Introduction
============

    Scope of this package is to allow to customize the user interface of
    Bungeni parliament portal.

Description
===========

    The ui interface is based on the descriptors declared in bungeni.ui.descriptor
    module. In the start-up phase the app loads (through the catalyst.zcml conf)
    the models. The fields are instances of Field class defined in
    bungeni.alchemist (before was ore.alchemist and descriptor's fields was
    dictionaries).

    This package provides two way to customize the UI: a declarative way and
    a xml based loader.

    To use this package to create a customization portal you need to add the
    name in the 'eggs' of the buildout.cfg (and the path in the 'develop'),
    In site.zcml add these lines after the bungeni.ui:

        <include package="bungeni.ui" />
        ...
        <include package="bungenicustom.parliament.customizer" />

    Then you must create a minimal package, for example:

       bungenicustom.parliament.kenya

    that can be minimal, it means must have:

        configure.zcml:

          <?xml version="1.0"?>
          <configure xmlns="http://namespaces.zope.org/zope" />

        __init__.py files:

      See tests.py and below for the code.

      In buildout add the package in eggs and develop and in the site.zcml
      you have to add:

        <include package="bungenicustom.parliament.kenya" />

      after the 'customizer'.

      Note: you can try some customization activating the tests module
        removing the comment in the __init__.py file.

    DescriptorHelper
    ----------------

      To manage a descriptor you need to create an instace of DescriptorHelper:

        from bungenicustom.parliament.customizer import helper
        dh = helper.DescriptorHelper('Bill')

      Hide a field

        dh.hide(field_name)

          This method setup the 'mode' attribute of the field.

      Move a field

        dh.move(field_name, position)

          Move the field in specified position.
          The correct way to use this function is with 'position' method:

              dh.position(name)

          this returns the position of 'name' in the fields list.
          So to move fields:

              dh.move('a_field', dh.position('another_field'))

          it moves 'a_field' before 'another_field' and

              move(descr1, 'a_field', position('another_field')+1)

          it moves 'a_field' after 'another_field'.

      Load the changes

        To make the changes done with the previous methods effective you have
        to call:

            dh.reload_fields()

        The method can be called at run-time (but after catalyst setup).

    XML configurator
    ----------------

        This is a sample of a xml configuration:

          <configurator>
              <descriptor name="Bill">
                  <hide field="submission_date"/>
                  <after name="submission_date" dst="short_name" />
                  <before ...>
              </descriptor>
          </configurator>

        Tag description

          descriptor

            Declare one of the ModelDescriptor in bungeni.ui.descriptor on which
            will be applied the following operations.
            The classes are in the form <name>Descriptor, we use the <name>
            that is usually the string used in the user interface (see
            'display_name' attribute).

          hide

              Take the name of the field to hide.

          after

              Move the specified 'name' field after the 'dst' field

          before

              Move the specified 'name' field before the 'dst' field

        How to parse an xml file

          The code looks like:

            from bungenicustom.parliament.customizer import xmlparser
            xmlparser.load(file('a_conf.xml').read())

    In the 'test.py' file there are examples of the two methods to customize
    the interface.
