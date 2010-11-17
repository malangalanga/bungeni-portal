from helper import DescriptorHelper

## test helper
dh = DescriptorHelper('Bill')
dh.hide('submission_date')
dh.hide('status')
dh.hide('bill_type_id')
dh.move(
    'publication_date',
    dh.position('short_name')+1)

# field not exists
dh.position('submission_xxx')
dh.hide('submission_xxx')
dh.move('submission_xxx', 1)

dh.reload_fields()


## test xml loader
from xmlparser import load

xml_conf = """
    <configurator>
        <descriptor name="Motion">
            <hide name="status"/>
            <before name="language" dst="owner_id" />
            <after name="owner_id" dst="status_date"/>
        </descriptor>
        <descriptor name="Question">
            <hide name="submission_date"/>
            <before name="question_type" dst="ministry_id" />
        </descriptor>
    </configurator>
    """
load(xml_conf)
