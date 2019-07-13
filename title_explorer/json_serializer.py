import json
from datetime import date
from typing import List

from neo4j import Node

from .validator import validate_title_object


def json_serializer(o):
    if isinstance(o, date):
        return o.__str__()


def dumps(obj):
    res = json.dumps(obj, indent=2, default=json_serializer)
    return res


def title_to_json(search_results: List[Node]):
    result_json = {
        "genres": [],
        "creators": [],
        "directors": [],
        "writers": [],
        "stars": [],

    }

    fields_to_copy = ['id', 'title', 'rating', 'runtime', 'runtime_mins',
                      'genres', 'story_line', 'production_company',
                      'type', 'image']

    populated_title = False

    for record in search_results:
        if not populated_title:
            title_node = record[0]
            for field in fields_to_copy:
                result_json[field] = title_node[field]
            result_json['release_date'] = str(title_node['release_date'])
            populated_title = True

        if len(record) == 3:
            relationship = record[1]
            person_node = record[2]

            if relationship.type == 'starred_in':
                star = person_node['name']
                result_json['stars'].append(star)
            elif relationship.type == 'directed':
                director = person_node['name']
                result_json['directors'].append(director)
            elif relationship.type == 'wrote':
                writer = person_node['name']
                result_json['directors'].append(writer)
            elif relationship.type == 'created':
                creator = person_node['name']
                result_json['directors'].append(creator)

    validate_title_object(result_json)

    return result_json
