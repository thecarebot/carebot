#!/usr/bin/env python

import app_config
import oauth
from flask import Flask, make_response, render_template
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.debug = app_config.DEBUG

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
