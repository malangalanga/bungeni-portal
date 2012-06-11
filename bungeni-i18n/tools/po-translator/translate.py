#!/usr/bin/env/python
"""This script translates a po file into a target language.

We use the google translate api and the google python client library
"""
import sys
import os
import re
import polib
from apiclient.discovery import build

MESSAGE_SET_OPTIONS = ("untranslated", "fuzzy" , "all")
DEFAULT_MESSAGE_SET = "untranslated"
DEFAULT_BUNCH_SIZE = 50
DUMMY_OPTIONS = ["Y", "N", "YES", "NO"]
DUMMY_MAPPING = { "Y": True, "N": False, "YES": True, "NO": False }
UNTRANSLATABLE_STRINGS = "\$\w+|\${\w+\}|%\w+|%\(\w+\)\w"
PURGE_FLAGS = ("fuzzy",)

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

    def translate(self, bunch_size=DEFAULT_BUNCH_SIZE, 
        translate=DEFAULT_MESSAGE_SET, dummy=False
    ):
        service = build("translate", "v2", developerKey=self.api_key)
        keygen = KeyGenerator()
        src_file = polib.pofile(self.source_po)
        if translate == "all":
            messages = src_file
        elif translate == "untranslated":
            messages = src_file.untranslated_entries()
        elif translate == "fuzzy":
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
            src_file.save(self.dest_po)
def usage():
    options = ("<source-po-file> <source-language> <destination-po-file> " 
        "<destination-language> <api-key> <bunch-size> <what-messages> "
        "<dummy>"
    )
    print """USAGE:: python translate.py %s\n
    <bunch-size> options   : %s
    <what-messages> options: %s
    <dummy> options        : %s
    """ %(options, "a number e.g. 10", opts(MESSAGE_SET_OPTIONS), 
        opts(DUMMY_OPTIONS)
    )

def run_translator():
    #!+ARGS(mb, nov-2011) Should utilize optparse or similar approach here
    arguments = sys.argv[1:]
    if len(arguments) not in [5, 6, 7, 8]:
        usage()
        exit(1)
    len_arguments = len(arguments)
    if len_arguments==5:
        arguments.extend([DEFAULT_BUNCH_SIZE, DEFAULT_MESSAGE_SET, False])
    elif len_arguments==6:
        arguments.extend([DEFAULT_MESSAGE_SET, False])
    elif len_arguments==7:
        arguments.append(False)
    source_po, source_lang, dest_po, dest_lang, api_key, bunch_size, what_msgs, dummy = arguments
    
    try:
        assert os.path.exists(source_po)
        assert what_msgs in MESSAGE_SET_OPTIONS
        assert dummy in DUMMY_OPTIONS
        bunch_size = int(bunch_size)
        assert bunch_size > 0
    except (AssertionError, ValueError, TypeError):
        usage()
        exit(1)
    translator = CatalogTranslator(source_po, source_lang, dest_po, dest_lang,
        api_key
    )
    dummy_bool = DUMMY_MAPPING[dummy]
    translator.translate(bunch_size=bunch_size, translate=what_msgs, 
        dummy=dummy_bool
    )

if __name__ == "__main__":
    run_translator()
