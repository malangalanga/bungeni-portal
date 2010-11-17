import logging

from zope.site.hooks import adapter_hook
from ore.alchemist.interfaces import IModelDescriptor
from ore.alchemist.model import Field

from bungeni.models import interfaces
from bungeni.ui import descriptor

####
# Functions to manage fields

def get_position(fields, name):
    # Return the position of field
    idx = [fields.index(f) for f in fields if f.name == name]

    if idx:
        # only the first in list if any
        return idx[0]

    return -1

def move(fields, name, position):
    # Take the fields and move the <name> field in the specified position
    idx  = get_position(fields, name)
    if idx == position:
        return None

    if position >= 0:
        field = fields.pop(idx)
        fields.insert(position, field)


####
# Descriptor Helper class
# note: if catalyst is loaded after this package m is None because the Model
# is still not instantiated.
# Retrieve of interface and descriptor is based on bungeni packages organization.

class DescriptorHelper(object):

    def __init__(self, name):
        self.package = 'bungeni.models.interfaces.I%s'%name
        self.interface = getattr(interfaces, 'I%s'%name)
        self.descriptor = getattr(descriptor, '%sDescriptor'%name)
        self.fields = self.descriptor.fields

    def position(self, field_name):
        pos = get_position(self.fields, field_name)
        if pos >= 0:
            return  pos
        else:
            logging.warning("position: Field %s not found.", field_name)

    def hide(self, field_name):
        # Hide the field
        found = False
        for f in self.fields:
            if f.name == field_name:
                f.modes = ""
                found = True
                break

        if not found:
            logging.warning("hide: Field %s not found.", field_name)


    def move(self, field_name, position):
        # Move (in-place) the field from actual position to the specified one
        found = [item for item in self.fields if item.name == field_name]
        if len(found) > 0:
            move(self.fields, field_name, position)
        else:
          logging.warning("move: Field %s not found.", field_name)

    def reload_fields(self):
        model = adapter_hook(
                    IModelDescriptor,
                    self.interface,
                    self.package)
        if model is not None:
            logging.info("Reload fields for %s", self.package)
            model.fields = [info for info in self.fields]
        else:
            logging.warning("Failing to reload fields for", self.package)
