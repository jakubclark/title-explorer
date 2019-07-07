from .logger import log


def check_exists(tx, label, id_field='name', id_value=''):
    """
    Check if there is a node with label=`label` and `id_field`=`id_value`
    """
    log.debug(f'Checking if there is a Node:{label} | {id_field}={id_value}')
    stmt = f'MATCH(node:{label} {{{id_field}: \'{id_value}\'}}) RETURN (node)'
    res = tx.run(stmt)
    num = 0
    for _ in res:
        num += 1
    return num > 0


def create_person_node(tx, name: str):
    exists = check_exists(tx, 'Person', 'name', name)
    if exists:
        log.debug(f'Not creating Node:Person with name={name}. Already exists')
        return
    log.debug(f'Creating Node:Person with name={name}')
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

    log.debug(f'Creating {title} title')

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


def connect_title_to_person(tx, title, person, person_type, rel_type):
    """
    Create an edge from `title` to person `person` of type `person_type` with a `rel_type relationship
    """
    log.debug(
        f'Creating edge from title={title} to person={person} with rel_type={rel_type}')
    stmt = (f'MATCH (title:Title),(person:{person_type})\n'
            f'WHERE title.title = \'{title}\' AND person.name = \'{person}\'\n'
            f'CREATE (title)-[r:{rel_type}]->(person)'
            )
    tx.run(stmt)


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

        # Create a node for each creator/director/writer/star/
        for creator in result['creators']:
            sess.write_transaction(create_person_node, creator)
            # Connect the creator node to the title node
            sess.write_transaction(
                connect_title_to_person, title, creator, 'Person', 'created_by')

        for dir in result['directors']:
            sess.write_transaction(create_person_node, dir)
            # Connect the director node to the title node
            sess.write_transaction(
                connect_title_to_person, title, dir, 'Person', 'directed_by')

        for writer in result['writers']:
            sess.write_transaction(create_person_node, writer)
            # Connect the writer node to the title node
            sess.write_transaction(
                connect_title_to_person, title, writer, 'Person', 'written_by')

        for star in result['stars']:
            sess.write_transaction(create_person_node, star)
            # Connect the star node to the title node
            sess.write_transaction(
                connect_title_to_person, title, star, 'Person', 'starred_by')
