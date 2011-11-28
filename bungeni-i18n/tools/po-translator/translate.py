#!/usr/bin/env/python
"""This script translates a po file into a target language.

We use the google translate api and the google python client library
"""
import sys
import os
import re
import polib
from apiclient.discovery import build

UNTRANSLATABLE_STRINGS = "\$\w+|\${\w+\}|%\w+|%\(\w+\)\w"

class KeyGenerator(object):
    current = 1

    @property
    def next(self):
        _current = self.current
        self.current = self.current + 1
        return _current

class CatalogTranslator(object):
    
    names_map = {}
    
    def __init__(self, source_po, source_lang, dest_po, dest_lang, api_key):
        self.source_po = source_po
        self.source_lang = source_lang
        self.dest_po = dest_po
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

    def translate(self):
        service = build("translate", "v2", developerKey=self.api_key)
        keygen = KeyGenerator()
        src_file = polib.pofile(self.source_po)
        untranslated_messages = src_file.untranslated_entries()
        print "Translating %d messages" % len(untranslated_messages)
        for message in untranslated_messages:
            translate_text = message.msgstr or message.msgid
            if message.comment:
                parse_default = eval(
                    message.comment.lstrip().rstrip().replace(
                        "Default: ", ""
                    )
                )
                if parse_default:
                    translate_text = parse_default
            replace_names = re.findall(UNTRANSLATABLE_STRINGS, translate_text)
            for name in replace_names:
                name_key = "DNT%d" % keygen.next
                self.names_map[name_key] = name
                translate_text = translate_text.replace(name, name_key, 1)
            result = service.translations().list(
                source = self.source_lang,
                target = self.dest_lang,
                q = translate_text
            ).execute()
            translation = result.get("translations")[0].get("translatedText")
            message.msgstr = self.restore_names(translation)
        src_file.save(self.dest_po)
def usage():
    print ("USAGE:: python translate.py <source-po-file> <source-language> "
        "<destination-po-file> <destination-language> <api-key>"
    )

def run_translator():
    if len(sys.argv[1:]) != 5:
        usage()
        exit(1)
    source_po, source_lang, dest_po, dest_lang, api_key = sys.argv[1:]
    assert os.path.exists(source_po)
    translator = CatalogTranslator(source_po, source_lang, dest_po, dest_lang,
        api_key
    )
    translator.translate()

if __name__ == "__main__":
    run_translator()
