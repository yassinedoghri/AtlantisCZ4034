# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask import request
from flask.helpers import get_debug_flag
from werkzeug import url_encode
import datetime
from dateutil import parser

from app.app import create_app
from app.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)


@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))


@app.template_filter('datestring_fmt')
def _jinja2_filter_datetime(datestring, fmt='%b %d, %Y'):
    date = parser.parse(datestring)
    if fmt == 2:
        fmt = '%I:%M %p, %d %b %Y'
    return date.strftime(fmt)


if __name__ == "__main__":
    app.run()
