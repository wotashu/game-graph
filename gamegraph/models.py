from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid
from wtforms import StringField, Form
from wtforms.validators import DataRequired

# uncomment for local neo4j database
url = os.environ.get('NEO4J_URL', 'http://localhost:7474')

# for use with graphenedb
# url = os.environ.nhget('NEO4J_URL', 'http://localhost:7474')

username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

if username and password:
    authenticate(url.strip('http://'), username, password)

authenticate(url.strip('http://'), "neo4j", "u3Sm8kEVFzE81N6n")
graph = Graph(url + '/db/data/')


class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def set_password(self, password):
        self.password = bcrypt.encrypt(password)
        return self

    def register(self):
        if not self.find():
            user = Node("User", username=self.username, password=self.password)
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def add_node(self, node_type, node_title, node_notes):
        user = self.find()
        type = node_type
        title = node_title
        notes = node_notes
        new_node = Node(type,
                        title=title,
                        node_notes=notes,
                        id=str(uuid.uuid4()),
                        timestamp=timestamp(),
                        date=date())
        rel = Relationship(user, "ADDED", new_node,
            time=timestamp(), date=date())
        graph.create(rel)

    def add_relationship(self, node, attribute_field, attribute, relationship):
        user = self.find()
        node = node
        node = Node(
            node,
            str(uuid.uuid4()),
            title = attribute,
            date = date()
        )
        graph.create(node)

    def add_game(self, title, tags, genre, platform):
        user = self.find()
        game = Node(
            "Game",
            id=str(uuid.uuid4()),
            title=title,
            timestamp=timestamp(),
            date=date()
        )
        game = graph.merge_one("Game", "title", title)
        rel = Relationship(user, "CATALOGED", game, 
            time=timestamp(), date=date())
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(',')]
        for t in tags:
            tag = graph.merge_one("Tag", "name", t)
            rel = Relationship(tag, "TAGGED", game,
                time=timestamp(), date=date())
            graph.create(rel)

        genre = [x.strip() for x in genre.lower().split(',')]
        for g in genre:
            gen = graph.merge_one("Genre", "name", g)
            rel = Relationship(game, "HAS_GENRE", gen,
                               time=timestamp(), date=date())
            graph.create(rel)

        platform = [x.strip() for x in platform.lower().split(',')]
        for g in genre:
            gen = graph.merge_one("Platform", "name", g)
            rel = Relationship(game, "HAS_PLATFORM", gen,
                               time=timestamp(), date=date())
            graph.create(rel)

    def like_game(self, game_id):
        user = self.find()
        game = graph.find_one("Game", "id", game_id)
        graph.create_unique(Relationship(user, "LIKED", game))

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both tagged.
        query = """
        MATCH (you:User)-[:CATALOGED]->(:Game)<-[:TAGGED]-(tag:Tag),
              (they:User)-[:CATALOGED]->(:Game)<-[:TAGGED]-(tag)
        WHERE you.username = {username} AND you <> they
        WITH they,
             COLLECT(DISTINCT tag.name) AS tags,
             COUNT(DISTINCT tag) AS len
        ORDER BY len DESC LIMIT 3
        RETURN they.username AS similar_user, tags
        """

        similar = graph.cypher.execute(query, username=self.username)
        return similar

    def get_commonality_of_user(self, username):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:User {username:{they}}),
              (you:User {username:{you}})
        OPTIONAL MATCH (they)-[:LIKED]->(game:Game)<-[:CATALOGED]-(you)
        OPTIONAL MATCH (they)-[:CATALOGED]->(:Game)<-[:TAGGED]-(tag:Tag),
                       (you)-[:CATALOGED]->(:Game)<-[:TAGGED]-(tag)
        RETURN COUNT(DISTINCT game) AS likes,
               COLLECT(DISTINCT tag.name) AS tags
        """

        result = graph.cypher.execute(query,
                                      they=username,
                                      you=self.username)

        result = result[0]
        common = dict()
        common['likes'] = result.likes
        common['tags'] = result.tags if len(result.tags) > 0 else None
        return common


def get_users_recent_games(username):
    query = """
    MATCH (:User {username:{username}})-[:CATALOGED]->(game:Game),
          (tag:Tag)-[:TAGGED]->(game)
    RETURN game.id AS id,
           game.date AS date,
           game.timestamp AS timestamp,
           game.title AS title,
           COLLECT(tag.name) AS tags
    ORDER BY timestamp DESC
    LIMIT 5
    """

    games = graph.cypher.execute(query, username=username)
    return games


def get_todays_recent_games():
    query = """
    MATCH (game:Game {date: {today}}),
          (user:User)-[:CATALOGED]->(game),
          (tag:Tag)-[:TAGGED]->(game)
    RETURN user.username AS username,
           game.id AS id,
           game.date AS date,
           game.timestamp AS timestamp,
           game.title AS title,
           COLLECT(tag.name) AS tags
    ORDER BY timestamp DESC
    LIMIT 5
    """

    # games = graph.cypher.execute(query, today = date())
    games = graph.cypher.execute(query, today=date())
    return games


def get_all_games():
    query = """
    MATCH (game:Game)-[r]->(genre:Genre)
    RETURN game.id AS id,
        game.date AS date,
        game.timestamp AS timestamp,
        game.title AS title,
        genre.name AS genre
    ORDER BY title ASC
    """

    games = graph.cypher.execute(query)
    return games


def get_game(game_title):
    games = graph.find_one("Game", "title", game_title)
    return games


def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()


def date():
    return datetime.now().isoformat()


class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
