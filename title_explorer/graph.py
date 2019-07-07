from .logger import log


def check_exists(tx, label, id_field='name', id_value=''):
    """
    Check if there is a node with label=`label` and `id_field`=`id_value`
    """
    log.debug(f'Checking if there is a {label} with {id_field}="{id_value}"')
    stmt = f'MATCH(node:{label} {{{id_field}: \'{id_value}\'}}) RETURN (node)'
    res = tx.run(stmt)
    num = 0
    for _ in res:
        num += 1
    return num > 0


def create_person_node(tx, name: str):
    exists = check_exists(tx, 'Person', 'name', name)
    if exists:
        log.debug(f'Not creating Person with name="{name}". Already exists')
        return
    log.debug(f'Creating Person="{name}"')
    stmt = f'CREATE (person:Person {{name: $name}})'
    tx.run(stmt, name=name)


def create_title_node(tx, title_object):
    title = title_object['title']
    rating = title_object['rating']
    runtime = title_object['runtime']
    runtime_mins = title_object['runtime_mins']
    genres = title_object['genres']
    release_date = title_object['release_date']
    if isinstance(release_date, dict):
        if 'start_year' in release_date.keys():
            release_date = f'{release_date["start_year"]} - {release_date["end_year"]}'
        else:
            release_date = release_date['release_date']
    story_line = title_object['story_line']

    log.debug(f'Creating Title="{title}"')

    tx.run('CREATE (title:Title{'
           'title: $title, '
           'rating: $rating, '
           'runtime: $runtime, '
           'runtime_mins: $runtime_mins, '
           'genres: $genres, '
           'release_date: $release_date, '
           'story_line: $story_line })',
           title=title, rating=rating, runtime=runtime,
           runtime_mins=runtime_mins, genres=genres, release_date=release_date,
           story_line=story_line)


def connect_title_to_person(tx, title, person, rel_type):
    """
    Create an edge from `title` to person `person` of type `person_type` with a `rel_type relationship
    """
    log.debug(
        f'Creating edge from Title="{title}" to Person="{person}" with rel_type="{rel_type}"')
    stmt = (f'MATCH (title:Title),(person:Person)\n'
            f'WHERE title.title = \'{title}\' AND person.name = \'{person}\'\n'
            f'CREATE (title)-[r:{rel_type}]->(person)'
            )
    tx.run(stmt)


def connect_person_to_title(tx, title, person, rel_type):
    """
    Create an edge from Person `person` to Title `title` with a `rel_type` relationship
    """
    log.debug(
        f'Creating edge from Person="{person}" to Title="{title}" with rel_type="{rel_type}"')
    stmt = (f'MATCH (title:Title),(person:Person)\n'
            f'WHERE title.title = \'{title}\' AND person.name = \'{person}\'\n'
            f'CREATE (person)-[r:{rel_type}]->(title)'
            )
    tx.run(stmt)


def connect_nodes(tx, out_label, out_id_field, out_id_value, in_label, in_id_field, in_id_value, rel_type):
    """
    Create an edge between 2 nodes
    n1 ->stars_in-> n2
    n1 is called the "outgoing node"
    n2 is called the "incoming node"
    :param tx:
    :param out_label: The label of the outgoing node. e.g.: "Title" or "Person"
    :param out_id_field: The field of the outgoing node, that identifies it. e.g.: "name" for Nodes with label="Person"
    :param out_id_value: The value of the outgoing node, that identifies it.
    e.g.: "Mark Hammil" for a node with label="Person"
    :param in_label: The label of the incoming node. e.g.: "Title" or "Person"
    :param in_id_field:The field of the incoming node, that identifies it. e.g.: "name" for Nodes with label="Person"
    :param in_id_value:The value of the incoming node, that identifies it.
    e.g.: "Mark Hammil" for a node with label="Person"
    :param rel_type:
    :return:
    """
    log.debug(
        f'Creating edge from node with (out_label="{out_label}" | {out_id_field}="{out_id_value}") to '
        f'(in_label="{in_label}" | {in_id_field}="{in_id_value}")')
    stmt = (f'MATCH (n1:{out_label}),(n2:{in_label})\n'
            f'WHERE n1.{out_id_field} = \'{out_id_value}\' AND n2.{in_id_field} = \'{in_id_value}\'\n'
            f'CREATE (n1)-[r:{rel_type}]->(n2)'
            )
    tx.run(stmt)


def make_connections(sess, result, field,  rel_type):
    """
    For every person in result[`field`], create a Person node if it doesn't exist,
    and create an edge from result['title'] to `person` with a `rel_type` relationship
    """
    title = result['title']
    for person in result[field]:
        sess.write_transaction(create_person_node, person)
        sess.write_transaction(connect_person_to_title, title, person, rel_type)


async def insert_to_db(app, result):
    driver = app['neo4j_driver']

    with driver.session() as sess:
        # Create a node for the title
        title = result['title']

        exists = sess.read_transaction(check_exists, 'Title', 'title', title)
        if exists:
            log.debug(
                f'Title Node with title={title} already exists. Not Creating it.')
            return

        sess.write_transaction(create_title_node, result)

        make_connections(sess, result, 'creators', 'created')
        make_connections(sess, result, 'directors',  'directed')
        make_connections(sess, result, 'writers', 'wrote')
        make_connections(sess, result, 'stars', 'starred_in')
