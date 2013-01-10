# -*- coding: utf-8 -*-
# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Report documentation generator

Generates HTML documentation of names that may be used in report templates.

See sample templates in:
 `{BUNGENI_HOME}/src/bungeni_custom/reporting/templates/scheduling` or
 `{BUNGENI_HOME}/src/bungeni_custom/reporting/templates/documents`

$Id$
"""
import logging
logging.basicConfig(level=logging.INFO)

import sys
from lxml import etree
from sqlalchemy.orm import class_mapper, Mapper

from zope.dublincore.interfaces import IDCDescriptiveProperties

from bungeni.models import domain, orm
from bungeni.ui import descriptor
from bungeni.capi import capi

SIMPLE_LIST = "<ul/>"
TARGET_DIRECTORY = sys.argv[1]
JS_SOURCE = """function toggleBullet(c){var a="none";var b=c.nextSibling;while(b!=null){if(b.tagName.toLowerCase()=="ul"){if(b.style.display=="none"){a="block"}break}b=b.nextSibling}while(b!=null){if(b.tagName.toLowerCase()=="ul"){b.style.display=a}b=b.nextSibling}}function collapseAll(){var a=document.getElementsByTagName("ul");for(var b=0;b<a.length;b++){a[b].style.display="none"}a=document.getElementsByTagName("ul");for(var b=0;b<a.length;b++){a[b].style.display="none"}var c=document.getElementById("root");c.style.display="block"}function expandAll(){var a=document.getElementsByTagName("ul");for(var b=0;b<a.length;b++){a[b].style.display="block"}var c=document.getElementById("root");c.style.display="block"};"""
CSS_SOURCE = """
ul{
    list-style-type:none;
    font-size:14px;
}
li.item{
    padding: 0.2em;
    border-bottom:1px solid #eef;
    font-size:13px;
}
li.item:nth-child(even){
    background-color:#DCD6CE;
}
span.sec_title{
    display:block;
    border: 1px dotted #669900;
    font-weight:bold;
    cursor:pointer;
}
p.report_doc{
    border:1px solid #A8A8A8;
    padding: 10px;
    margin-bottom:10px;
    display:block;
    background-color:#FFFDDD;
    color:#383838;
    font-size:90%;
}
"""
REPORTING_DOCS = """
This is a hierarchy of the list of names available for use in HTML report templates.
You see sample usage in the templates in <strong>src/bungeni_custom/reporting/templates</strong>

Using a combination of these properties it is possible to design custom report 
templates for use in generating reports from sittings and/or document reports.

These names listed below are exposed to the template during report generation.<br/>

For the case of document reports, the names applicable to that document are
exposed at the root e.g. A document such as a Bill would expose its particular
properties e.g. <strong>title</strong> at the root of the hierarchy.<br/><br/>

*dc: prefixed properties refer to dublin core metadata for the current item
"""

def add_sub_element(parent, tag, text=None, **kw):
    if (kw.has_key("css_class")):
        kw["class"] = kw.get("css_class")
        del kw["css_class"]
    _element = etree.SubElement(parent, tag, **kw)
    if text: 
        _element.text = str(text)
    return _element

SITTING_EXTRAS = []

class ExtendedProperty(object):
    def __init__(self, key, class_):
        self.key = key
        self.mapper = class_
        self.uselist = True

for type_key, type_info in capi.iter_type_info():
    if type_info.workflow and type_info.workflow.has_feature("schedule"):
        SITTING_EXTRAS.append(
            ExtendedProperty("%ss" % type_key, type_info.domain_model)
        )

PROCESSED_PROPS = {}

def generate_doc_for(domain_class, title=None, expand=True):
    doc = etree.fromstring(SIMPLE_LIST)
    dc_adapter = None
    if title:
        add_sub_element(doc, "li", title)
    if not isinstance(domain_class, Mapper):
        dc_adapter = IDCDescriptiveProperties(domain_class(), None)
        mapped = class_mapper(domain_class)
    else:
        mapped = domain_class
        try:
            dc_adapter = IDCDescriptiveProperties(mapped.class_(), None)
        except:
            logging.error("Unable to get dc adapter for %s", mapped.class_)
    if dc_adapter:
        dc_keys = {}
        dc_keys.update(dc_adapter.__class__.__dict__)
        for (key, value) in dc_keys.iteritems():
            if (not key.startswith("_")) and (not hasattr(value, "__call__")):
                elx = add_sub_element(doc, "li")
                elx.text = "dc:%s" % key
                elx.set("class", "item dcitem")

    props = [ prop for prop in mapped.iterate_properties ]
    if domain_class == domain.Sitting:
        props.extend(SITTING_EXTRAS)
    for prop in sorted(props, key=lambda p:str(int(hasattr(p, "mapper")))+p.key):
        sub_el = add_sub_element(doc, "li")
        if hasattr(prop, "mapper") and expand:
            if prop.key in PROCESSED_PROPS.get(mapped.class_.__name__, []):
                continue
            else:
                try:
                    PROCESSED_PROPS[mapped.class_.__name__].add(prop.key)
                except KeyError:
                    PROCESSED_PROPS[mapped.class_.__name__] = set([prop.key])
            sub_el = add_sub_element(doc, "li")
            if prop.uselist:
                sub_title = "+ %s (list)" % (prop.key)
            else:
                sub_title = "+ %s" % prop.key
            add_sub_element(sub_el, "span", sub_title, css_class="sec_title",
                onclick="toggleBullet(this)"
            )
            sub_el.append(generate_doc_for(prop.mapper, title, prop.uselist))
        else:
            sub_el.text = prop.key
            sub_el.set("class", "item")
            
    return doc

def generate_documentation():
    document = etree.fromstring(SIMPLE_LIST)
    document.set("id", "root")
    st_tr = add_sub_element(document, "li")
    st_tr.attrib["style"] = "border-left:1px solid #ddd;"
    add_sub_element(st_tr, "span", "+ sittings (list)", 
        css_class="sec_title",
        onclick="toggleBullet(this)"
    ) 
    st_tr.append(generate_doc_for(domain.Sitting, 0))
    return etree.tostring(document)

if __name__ == "__main__":
    logging.info("Starting generation of reporting documentation...")
    doc_file_name = "/".join([TARGET_DIRECTORY, "index.html"])
    doc_file = open(doc_file_name, "w")
    doc_args = dict(
        js_source = JS_SOURCE,
        css_source = CSS_SOURCE,
        doc_text = generate_documentation(),
        reporting_docs = REPORTING_DOCS
    )
    doc_file.write("""
        <html>
            <head>
                <title>Bungeni: Reporting Documentation</title>
                <script type="text/javascript">%(js_source)s</script>
                <style>%(css_source)s</style>
            </head>
            <body onload="collapseAll()">
                <h1>Reporting Documentation</h1>
                <p class="report_doc">%(reporting_docs)s</p>
                <p>Click on each section to see properties.
                    <a href="javascript:collapseAll()">Collapse All</a>
                    <a href="javascript:expandAll()">Expand All</a>
                </p>
                <div>%(doc_text)s</div>
            </body>
        </html
        """ % doc_args
    )
    logging.info("Reporting documentation was generated and written to %s", 
        doc_file_name
    )
