#!/usr/bin/env python

import app_config
import oauth
from flask import Flask, make_response, render_template
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from flask.ext.basicauth import BasicAuth
from werkzeug.debug import DebuggedApplication

from util.models import Story

app = Flask(__name__)
app.secret_key = app_config.SECRET_KEY
app.config['BASIC_AUTH_USERNAME'] = app_config.ADMIN_USER
app.config['BASIC_AUTH_PASSWORD'] = app_config.ADMIN_PASS
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

app.debug = app_config.DEBUG

admin = Admin(app, name='carebot', template_mode='bootstrap3')

# Set up model views
class StoryAdmin(ModelView):
    column_filters = ('name', )

admin.add_view(StoryAdmin(Story))

@app.route('/')
@oauth.oauth_required
def index():
    return make_response("You're good to go.")

app.register_blueprint(oauth.oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app


# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab app" instead!'
