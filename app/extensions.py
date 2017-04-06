# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app2 factory located in app2.py."""
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_elasticsearch import FlaskElasticsearch
from flask_wtf.csrf import CSRFProtect
from flask_pymongo import PyMongo

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
es = FlaskElasticsearch()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
mongodb = PyMongo(config_prefix='MONGODB')
