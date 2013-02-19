#!/usr/bin/env/python
"""This script translates a PO file or XML catalog into a target language.

We use the google translate api and the google python client library
"""
import sys
import os
import re
import polib
from apiclient.discovery import build
from lxml import etree

XML_TYPE, PO_TYPE = CATALOG_TYPES = ("xml", "po")
UNTRANSLATED, ALL_MESSAGES, FUZZY = MESSAGE_SET_OPTIONS = ("untranslated", "all", "fuzzy")
DEFAULT_MESSAGE_SET = UNTRANSLATED
DEFAULT_BUNCH_SIZE = 50
DUMMY_OPTIONS = ["Y", "N", "YES", "NO"]
DUMMY_MAPPING = { "Y": True, "N": False, "YES": True, "NO": False }
UNTRANSLATABLE_STRINGS = "\$\w+|\${\w+\}|%\w+|%\(\w+\)\w"
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'
PURGE_FLAGS = (FUZZY,)

def bunch_list(source, size):
    return [ source[x:(x + size)] for x in xrange(0, len(source), size) ]

def opts(source_list, separator=", "):
    return separator.join([ str(item) for item in source_list ])

class KeyGenerator(object):
    current = 1

    @property
    def next(self):
        _current = self.current
        self.current = self.current + 1
        return _current


class POCatalogTranslator(object):
    
    names_map = {}
    
    def __init__(self, source_file, source_lang, output_file, dest_lang, api_key):
        self.source_file = source_file
        self.source_lang = source_lang
        self.output_file = output_file
        self.dest_lang = dest_lang
        self.api_key = api_key

    def restore_names(self, translation):
        name_keys = re.findall("DNT\d+", translation)
        if not name_keys:
            return translation
        restored_translation = translation
        for name_key in name_keys:
            restored_translation = restored_translation.replace(name_key, 
                self.names_map[name_key], 1
            )
        return restored_translation

    def translate(self, bunch_size=DEFAULT_BUNCH_SIZE, 
        translate=DEFAULT_MESSAGE_SET, dummy=False
    ):
        service = build("translate", "v2", developerKey=self.api_key)
        keygen = KeyGenerator()
        src_file = polib.pofile(self.source_file)
        if translate == ALL_MESSAGES:
            messages = src_file
        elif translate == UNTRANSLATED:
            messages = src_file.untranslated_entries()
        elif translate == FUZZY:
            messages = src_file.fuzzy_entries()
        if dummy:
            print "============ DUMMY MODE =============="
        print "Translating %d messages" % len(messages)
        bunched_messages = bunch_list(messages, bunch_size)
        bunch_length = len(bunched_messages)
        for bunch_no, bunch in enumerate(bunched_messages):
            print "Translating bunch %d/%d (%d messages)" %(
                bunch_no, bunch_length, len(bunch)
            )
            messages_to_translate = []
            for message in bunch:
                translate_text = message.msgid
                if message.comment:
                    parse_default = message.comment.lstrip().rstrip().replace(
                            "Default: ", ""
                    ).strip("\"")
                    if parse_default:
                        translate_text = parse_default
                replace_names = re.findall(UNTRANSLATABLE_STRINGS, translate_text)
                for name in replace_names:
                    name_key = "DNT%d" % keygen.next
                    self.names_map[name_key] = name
                    translate_text = translate_text.replace(name, name_key, 1)
                messages_to_translate.append(translate_text)
            #translate this bunch
            if dummy:
                continue
            result = service.translations().list(
                source = self.source_lang,
                target = self.dest_lang,
                q = messages_to_translate
            ).execute()
            for index, translation in enumerate(result.get("translations")):
                bunch[index].msgstr = self.restore_names(
                    translation.get("translatedText")
                )
                flags = bunch[index].flags
                for flag in PURGE_FLAGS:
                    if flag in flags:
                        bunch[index].flags.remove(flag)
        if not dummy:
            src_file.save(self.output_file)


class XMLCatalogTranslator(POCatalogTranslator):
    def translate(self, bunch_size=DEFAULT_BUNCH_SIZE, 
        translate=DEFAULT_MESSAGE_SET, dummy=False
    ):
        service = build("translate", "v2", developerKey=self.api_key)
        keygen = KeyGenerator()
        xml_file = open(self.source_file)
        src_doc = etree.fromstring(xml_file.read())
        if translate == ALL_MESSAGES:
            messages = [ msg for msg in src_doc ]
        elif translate == UNTRANSLATED:
            messages = [ msg for msg in src_doc if msg.text ]
        if dummy:
            print "============ DUMMY MODE =============="
        print "Translating %d messages" % len(messages)
        bunched_messages = bunch_list(messages, bunch_size)
        bunch_length = len(bunched_messages)
        for bunch_no, bunch in enumerate(bunched_messages):
            print "Translating bunch %d/%d (%d messages)" %(
                bunch_no, bunch_length, len(bunch)
            )
            messages_to_translate = []
            for message in bunch:
                translate_text = message.text
                replace_names = re.findall(UNTRANSLATABLE_STRINGS, translate_text)
                for name in replace_names:
                    name_key = "DNT%d" % keygen.next
                    self.names_map[name_key] = name
                    translate_text = translate_text.replace(name, name_key, 1)
                messages_to_translate.append(translate_text)
            #translate this bunch
            if dummy:
                continue
            result = service.translations().list(
                source = self.source_lang,
                target = self.dest_lang,
                q = messages_to_translate
            ).execute()
            for index, translation in enumerate(result.get("translations")):
                bunch[index].text = self.restore_names(
                    translation.get("translatedText")
                )
        if not dummy:
            target_file = open(self.output_file, "w")
            target_file.write("%s\n%s" % 
                (XML_HEADER, etree.tostring(src_doc, pretty_print=True, encoding='UTF-8')))


TRANSLATORS = dict([
    (XML_TYPE, XMLCatalogTranslator), (PO_TYPE, POCatalogTranslator)
])

def usage():
    options = ("<catalog-type> <source-file> <source-language> <destination-file> " 
        "<destination-language> <api-key> <bunch-size> <what-messages> "
        "<dummy>"
    )
    print """USAGE:: python translate.py %s\n
    <catalog-type> options : %s
    <bunch-size> options   : %s
    <what-messages> options: %s
    <dummy> options        : %s
    """ %(options, opts(CATALOG_TYPES) , "a number e.g. 10", opts(MESSAGE_SET_OPTIONS), 
        opts(DUMMY_OPTIONS)
    )

def run_translator():
    #!+ARGS(mb, nov-2011) Should utilize optparse or similar approach here
    arguments = sys.argv[1:]
    if len(arguments) not in [6, 7, 8, 9]:
        usage()
        exit(1)
    len_arguments = len(arguments)
    if len_arguments==6:
        arguments.extend([DEFAULT_BUNCH_SIZE, DEFAULT_MESSAGE_SET, False])
    elif len_arguments==7:
        arguments.extend([DEFAULT_MESSAGE_SET, "NO"])
    elif len_arguments==8:
        arguments.append("NO")
    file_type, source_file, source_lang, output_file, dest_lang, api_key, bunch_size, what_msgs, dummy = arguments
    
    try:
        assert os.path.exists(source_file)
        assert file_type in CATALOG_TYPES
        assert what_msgs in MESSAGE_SET_OPTIONS
        assert dummy in DUMMY_OPTIONS
        bunch_size = int(bunch_size)
        assert bunch_size > 0
    except (AssertionError, ValueError, TypeError):
        usage()
        exit(1)
    translator = TRANSLATORS.get(file_type)
    translator = translator(source_file, source_lang, output_file, dest_lang,
        api_key
    )
    dummy_bool = DUMMY_MAPPING[dummy]
    translator.translate(bunch_size=bunch_size, translate=what_msgs, 
        dummy=dummy_bool
    )

if __name__ == "__main__":
    run_translator()
