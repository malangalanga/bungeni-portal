import elementtree.ElementTree as ET
from helper import DescriptorHelper

####
# Parse xml and reload descriptors

def load(xml):
    tree = ET.fromstring(xml)

    for descriptor_tag in tree.findall("descriptor"):
        descriptor_name = descriptor_tag.get('name')
        dh = DescriptorHelper(descriptor_name)

        for item in descriptor_tag.findall('hide'):
            name = item.get('name')
            if name:
                dh.hide(name)

        for item in descriptor_tag.findall('before'):
            name = item.get('name')
            dst = item.get('dst')
            if name and dst:
                dh.move(
                    name,
                    dh.position(dst)-1)

        for item in descriptor_tag.findall('after'):
            name = item.get('name')
            dst = item.get('dst')
            if name and dst:
                dh.move(
                    name,
                    dh.position(dst)+1)

        dh.reload_fields()