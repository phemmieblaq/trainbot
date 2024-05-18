import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
import re
import calendar
from word2number import w2n
import datetime as dt
from db import get_train_station_data  # Import function to get train station data

# Initialize SpaCy
nlp = spacy.load("en_core_web_sm")
phrase_matcher = PhraseMatcher(nlp.vocab)

# Define patterns for matching station names
station_names = get_train_station_data()

station_name_patterns = list(nlp.pipe(station_names[0]))

# Remove "Rail Station" and "\N" from each station namenew_station_names = [name.text.replace(" Rail Station", "").replace("\\N", "") for name in station_name_patterns]
new_station_names = [name.text for name in station_name_patterns if name.text]
#print(new_station_names)

station_code_patterns = list(nlp.pipe(station_names[1]))
#print(station_code_patterns)



#print(station_pattern)
phrase_matcher.add("stationName", None, *station_name_patterns, *station_code_patterns)

# Define custom SpaCy component to identify station names
@spacy.Language.component("identify_station_names")
def identify_station_names(doc):
    matches = phrase_matcher(doc)
    spans = [Span(doc, start, end, label="STATION") for match_id, start, end in matches]
    filtered_spans = []
    for span in spans:
        if not filtered_spans or span.start >= filtered_spans[-1].end:
            filtered_spans.append(span)
    doc.ents = filtered_spans
    return doc

# Add custom SpaCy component to SpaCy pipeline
nlp.add_pipe("identify_station_names", after="ner")

# Define patterns for matching other entities
yes_pattern = [{'LOWER': {'REGEX': '^(y|yes|yep|yeah|true|yh|ye)$'}}]
no_pattern = [{'LOWER': {'REGEX': '^(n|no|nah|nope|false)$'}}]
service_pattern = [{'LOWER': {'REGEX': '^(travel|travelling|book|booking|bookings|delay|delays)$'}}]
day_pattern = [{'LOWER': {'REGEX': '^(today|tomorrow)$'}}]
weekday_pattern = [{'LOWER': {'REGEX': '^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$'}}]
full_date_pattern = [{'LOWER': {'REGEX': '^((([0-2]\d|3[0-1])|\d)([stndrh]{2})?)$'}},
                    {'LOWER': {'REGEX': '^(january|february|march|april|may|june|july|august|september|'
                                        'october|november|december)$'}, 'OP': '?'},
                    {'POS': 'NUM', 'SHAPE': 'dddd', 'OP': '?'}]
before_time_pattern = [{'LOWER': 'before'},
                       {'TEXT': {'REGEX': '^(24:00|([01]?\d|2[0-3]):([0-5]\d))$'}}]

numerical_date_pattern = [{'TEXT': {'REGEX': '^(([0-2]\d|3[0-1]|\d)[\/]((0[1-9]|1[0-2])|[1-9])'
                                          '([\/](\d{4}|\d{2}))?)$'}}]
dashed_date_pattern = [{'TEXT': {'REGEX': '^(([0-2]\d|3[0-1]|\d))$'}},
                       {'DEP': 'punct'},
                       {'TEXT': {'REGEX': '^((0[1-9]|1[0-2])|[1-9])$'}},
                       {'DEP': 'punct', 'OP': '?'},
                       {'TEXT': {'REGEX': '^(\d{4}|\d{2})$'}, 'OP': '?'}]
military_time_pattern = [{'TEXT': {'REGEX': '^(24:00|([01]?\d|2[0-3]):([0-5]\d))$'}}]
casual_time_pattern = [{'LOWER': {'REGEX': '^(((1[0-2]|\d)|(1[0-2]|\d:[0-5]\d))([aApP][Mm]))$'}}]
casual_time_pattern2 = [{'LOWER': {'REGEX': '^(((1[0-2]|\d)|(1[0-2]|\d:[0-5]\d)))$'}},
                        {'LOWER': {'REGEX': '^([aApP][Mm])$'}}]
quarter_past_to_pattern = [{'LOWER': 'quarter'},
                           {'LOWER': {'REGEX': '^(past|to)$'}},
                           {'TEXT': {'REGEX': '^([1][0-2]|\d)$'}},
                           {'LOWER': 'in', 'OP': '?'},
                           {'LOWER': 'the', 'OP': '?'},
                           {'DEP': 'pobj', 'OP': '?'}]
half_past_pattern = [{'LOWER': 'half'},
                     {'LOWER': 'past'},
                     {'TEXT': {'REGEX': '^([1][0-2]|\d)$'}},
                     {'LOWER': 'in', 'OP': '?'},
                     {'LOWER': 'the', 'OP': '?'},
                     {'DEP': 'pobj', 'OP': '?'}]
midday_midnight_pattern = [{'LOWER': {'REGEX': '^(midday|midnight)$'}}]
midday_midnight_pattern2 = [{'LOWER': {'REGEX': '^(mid)$'}},
                             {'LOWER': {'REGEX': '^(day|night)$'}}]
outgoing_station_pattern = [{'LOWER': 'from'},
                             {'ENT_TYPE': 'STATION', 'OP': '+'}]
destination_station_pattern = [{'LOWER': 'to'},
                                {'ENT_TYPE': 'STATION', 'OP': '+'}]
station_name_pattern = [{'ENT_TYPE': 'STATION'}]
minute_pattern = [{'LOWER': {'REGEX': '^(\d+(minute[s]?|min[s]?))$'}}]
minute_pattern2 = [{'LOWER': {'REGEX': '^(\d+)$'}},
                   {'LOWER': {'REGEX': '^(minutes|minute|mins|min)$'}}]



# Add patterns to the Matcher
matcher = Matcher(nlp.vocab)
matcher.add("true", [yes_pattern])
matcher.add("false", [no_pattern])
matcher.add("service", [service_pattern])

# Create a pattern that matches a date in the format '20th July'
#date_pattern = [{'IS_DIGIT': True}, {'LOWER': {'IN': ['st', 'nd', 'rd', 'th']}}, {'IS_ALPHA': True}]

# Create a pattern that matches a time in the format '11am'
time_pattern = [{'TEXT': {'REGEX': '^(0[0-9]|1[0-9]|2[0-3]|[0-9])$'}},
                {'TEXT': {'IN': [':']}, 'OP': '?'},
                {'TEXT': {'REGEX': '^([0-5][0-9]|[0-9])$'}, 'OP': '?'},
                {'LOWER': {'IN': ['am', 'pm']}, 'OP': '?'}]


# Create a pattern that matches 'before' or 'after' followed by a time
#time_modifier_pattern = [{'LOWER': {'IN': ['before', 'after']}}, {'IS_DIGIT': True}, {'LOWER': {'IN': ['am', 'pm']}}]

# Add the patterns to the matcher





matcher.add("time", [time_pattern, military_time_pattern,casual_time_pattern, casual_time_pattern2])
#matcher.add("timeModifier", [time_modifier_pattern])
matcher.add("day", [day_pattern])
matcher.add("weekday", [weekday_pattern])
matcher.add("fullDate", [full_date_pattern, dashed_date_pattern])
matcher.add("numericalDate", [numerical_date_pattern])
# matcher.add("militaryTime", [military_time_pattern])
#matcher.add("casualTime", [casual_time_pattern, casual_time_pattern2])
matcher.add("quarterHalfTime", [quarter_past_to_pattern, half_past_pattern])
matcher.add("middayMidnightTime", [midday_midnight_pattern, midday_midnight_pattern2])
# matcher.add("fromStation", [outgoing_station_pattern])
# matcher.add("toStation", [destination_station_pattern])
# matcher.add("stationName", [station_name_pattern])
matcher.add("minute", [minute_pattern, minute_pattern2])
from_station_patterns = [[{'LOWER': 'from'}, {'LOWER': name.lower()}] for name in new_station_names]

# Add each pattern to the matcher
for pattern in from_station_patterns:
    matcher.add("fromCity", [pattern])

to_station_patterns = [[{'LOWER': 'to'}, {'LOWER': name.lower()}] for name in new_station_names]

# Add each pattern to the matcher
for pattern in to_station_patterns:
    matcher.add("toCity", [pattern])

days_later_pattern = [{'LIKE_NUM': True}, {'LOWER': 'days'}, {'LOWER': 'later'}]

# Add the pattern to the matcher
matcher.add("daysLater", [days_later_pattern])


import dateparser
def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[((n//10%10!=1)*(n%10<4)*n%10)::4])

import re
from dateutil.parser import parse

from datetime import datetime

def get_entities(json):
    message = json['message']  # Input text
    messages = re.split('come back|and return| go back| head back|make a return|travel back|get back|bounce back|move back|journey back|and backtrack|and revert|and retreat', message)
    departing_message = messages[0]
    arriving_message = messages[1] if len(messages) > 1 else ''

    departing_doc = nlp(departing_message)
    arriving_doc = nlp(arriving_message)

    departing_matches = matcher(departing_doc)
    arriving_matches = matcher(arriving_doc)

    departing_results = {}
    arriving_results = {}

    for match_id, start, end in departing_matches:
        match_id_string = nlp.vocab.strings[match_id]
        match = departing_doc[start:end].text
        if match_id_string == 'fromCity':
            departing_results[match_id_string] = match
        elif match_id_string == 'toCity':
            departing_results[match_id_string] = match
        elif match_id_string == 'fullDate':
            if 'am' in match or 'pm' in match:
                departing_results[match_id_string] = None
            else:
                try:
                    date = parse(match, fuzzy=True)
                    departing_results[match_id_string] = date.strftime('%dth %B')
                except ValueError:
                    departing_results[match_id_string] = None
        elif match_id_string == 'time':
            if 'am' in match or 'pm' in match:
                time = parse(match, fuzzy=True)
                departing_results[match_id_string] = time.strftime('%H:%M')
            else:
                departing_results[match_id_string] = None
        else:
            departing_results[match_id_string] = match

    for match_id, start, end in arriving_matches:
        match_id_string = nlp.vocab.strings[match_id]
        match = arriving_doc[start:end].text
        if match_id_string == 'fromCity':
            arriving_results[match_id_string] = match
        elif match_id_string == 'fullDate':
            if 'am' in match or 'pm' in match:
                arriving_results[match_id_string] = None
            else:
                try:
                    date = parse(match, fuzzy=True)
                    arriving_results[match_id_string] = date.strftime('%dth %B')
                except ValueError:
                    arriving_results[match_id_string] = None
        elif match_id_string == 'time':
            if 'am' in match or 'pm' in match:
                time = parse(match, fuzzy=True)
                arriving_results[match_id_string] = time.strftime('%H:%M')
            else:
                arriving_results[match_id_string] = None
        else:
            arriving_results[match_id_string] = match

    return {'singleJourney': departing_results, 'returnJourney': arriving_results}