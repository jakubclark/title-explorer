# JSONSchema validator

import json

import jsonschema

with open('schema.json') as f:
    schema = json.load(f)

TITLE_OBJECT_SCHEMA = schema['definitions']['title-object']


def validate_title_object(json_data):
    jsonschema.validate(json_data, TITLE_OBJECT_SCHEMA)
