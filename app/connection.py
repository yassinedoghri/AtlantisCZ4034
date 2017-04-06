# -*- coding: utf-8 -*-
from pymongo import MongoClient


class MongodbConnection():
    """Connect to a mongo database using a connection name and a database name."""

    def __init__(self, connection_name):
        self.connection_name = connection_name
        self.con = None

    def connect(self):
        try:
            mongodb_config = get_config_param('main', 'mongodb.' + self.connection_name)
            server = mongodb_config['server']
            port = mongodb_config['port']
            client = MongoClient(server, port)

            if mongodb_config['auth']:
                password = mongodb_config['password']
                user = mongodb_config['user']
                admin_db = mongodb_config['admin_db']
                client.the_database.authenticate(user, password, source=admin_db)
                # print(password, user, admin_db)
            self.con = client
        except Exception as e:
            print(e)

    def get_database(self, db_name):
        return self.con[get_config_param('main', 'mongodb.' + self.connection_name + '.' + db_name)]

    def close(self):
        self.con.close()
