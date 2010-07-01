# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt
"""Taggings of Workflow States

$Id: app.py 6682 2010-06-03 14:32:56Z mario.ruggier $
"""

# Declaration of active tags (it is an error to specify an undeclared tag)

ACTIVE_TAGS = [
    "private", 
    "public",
    "tobescheduled",
    "scheduled",
    "terminal",
    "succeed", # terminal
    "fail", # terminal
] 

# Tags for Workflow States, per Parliamentary Item

TAG_MAPPINGS = {}
TAG_MAPPINGS["bill"] = {
    "working_draft": ["private",],
    "gazetted": [],
    "first_reading_pending": ["tobescheduled",],
    "first_reading": ["scheduled",],
    "first_reading_postponed": ["tobescheduled",],
    "first_committee": [],
    "first_report_reading_pending": ["tobescheduled",],
    "first_report_reading": ["scheduled",],
    "first_report_reading_postponed": ["tobescheduled",],
    "second_reading_pending": ["tobescheduled",],
    "second_reading": ["scheduled",],
    "second_reading_postponed": ["tobescheduled",],
    "whole_house_pending": ["tobescheduled",],
    "whole_house": ["scheduled",],
    "whole_house_postponed": ["tobescheduled",],
    "second_committee": [],
    "third_reading_pending": ["tobescheduled",],
    "third_reading": ["scheduled",],
    "third_reading_postponed": ["tobescheduled",],
    "withdrawn_public": ["terminal", "fail",],
    "approved": ["terminal", "succeed",],
    "rejected": ["terminal", "fail",],
}




