"""
Project-wide application configuration.

DO NOT STORE SECRETS, PASSWORDS, ETC. IN THIS FILE.
They will be exposed to users. Use environment variables instead.
See get_secrets() below for a fast way to access them.
"""

import os

from authomatic.providers import oauth2
from authomatic import Authomatic

"""
NAMES
"""
# Project name to be used in urls
# Use dashes, not underscores!
PROJECT_SLUG = 'carebot'

# Project name to be used in file paths
PROJECT_FILENAME = 'carebot'

# The name of the repository containing the source
REPOSITORY_NAME = 'carebot'
GITHUB_USERNAME = 'thecarebot'
REPOSITORY_URL = 'https://github.com/%s/%s.git' % (GITHUB_USERNAME, REPOSITORY_NAME)
REPOSITORY_ALT_URL = None # 'git@bitbucket.org:nprapps/%s.git' % REPOSITORY_NAME'

# Slack info
slack_key = os.environ.get('SLACKBOT_API_TOKEN')
LINGER_UPDATE_CHANNEL = '#matt-slackbot-spam'

# Dailygraphics archive
COPY_GOOGLE_DOC_KEY = '0Ak3IIavLYTovdGdpcXlFS1lBaVE5aEJqcG1nMUFTVWc'
COPY_PATH = 'data/copy.xlsx'

STORIES_GOOGLE_DOC_KEY = '1Gcumd0uOl3eSUvc0y5CWmmHVOKwX609-js5EnE8i3lI'
STORIES_PATH = 'data/stories.xlsx'


"""
Google analytics
"""
GA_ORGANIZATION_ID = '100688391'
GA_SAMPLING_LEVEL = 'HIGHER_PRECISION'
GA_RESULT_SIZE = 10000
GA_METRICS = ['sessions', 'pageviews']
GA_DIMENSIONS = ['pagePath', 'source', 'deviceCategory']

"""
OAUTH
"""

GOOGLE_OAUTH_CREDENTIALS_PATH = '~/.google_oauth_credentials'

authomatic_config = {
    'google': {
        'id': 1,
        'class_': oauth2.Google,
        'consumer_key': os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
        'consumer_secret': os.environ.get('GOOGLE_OAUTH_CONSUMER_SECRET'),
        'scope': ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/analytics.readonly'],
        'offline': True,
    },
}

authomatic = Authomatic(authomatic_config, os.environ.get('AUTHOMATIC_SALT'))

"""
DEPLOYMENT
"""
PRODUCTION_SERVERS = ['54.201.77.124']
STAGING_SERVERS = ['54.201.159.92']

# Should code be deployed to the web/cron servers?
DEPLOY_TO_SERVERS = False

SERVER_USER = 'ubuntu'
SERVER_PYTHON = 'python2.7'
SERVER_PROJECT_PATH = '/home/%s/apps/%s' % (SERVER_USER, PROJECT_FILENAME)
SERVER_REPOSITORY_PATH = '%s/repository' % SERVER_PROJECT_PATH
SERVER_VIRTUALENV_PATH = '%s/virtualenv' % SERVER_PROJECT_PATH

# Services are the server-side services we want to enable and configure.
# A three-tuple following this format:
# (service name, service deployment path, service config file extension)
SERVER_SERVICES = [
    ('bot', '/etc/init', 'conf')
    # ('uwsgi', '/etc/init', 'conf'),
    # ('nginx', '/etc/nginx/locations-enabled', 'conf'),
]

# These variables will be set at runtime. See configure_targets() below
SERVERS = []

"""
Utilities
"""
def get_secrets():
    """
    A method for accessing our secrets.
    """
    secrets_dict = {}

    for k,v in os.environ.items():
        if k.startswith(PROJECT_SLUG):
            k = k[len(PROJECT_SLUG) + 1:]
            secrets_dict[k] = v

    return secrets_dict

def configure_targets(deployment_target):
    """
    Configure deployment targets. Abstracted so this can be
    overriden for rendering before deployment.
    """
    global S3_BUCKET
    global S3_BASE_URL
    global S3_DEPLOY_URL
    global SERVERS
    global SERVER_BASE_URL
    global SERVER_LOG_PATH
    global DEBUG
    global DEPLOYMENT_TARGET
    global DISQUS_SHORTNAME
    global ASSETS_MAX_AGE

    if deployment_target == 'production':
        # S3_BUCKET = PRODUCTION_S3_BUCKET
        S3_BASE_URL = 'http://%s/%s' % (S3_BUCKET, PROJECT_SLUG)
        S3_DEPLOY_URL = 's3://%s/%s' % (S3_BUCKET, PROJECT_SLUG)
        SERVERS = PRODUCTION_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DISQUS_SHORTNAME = 'npr-news'
        DEBUG = False
        ASSETS_MAX_AGE = 86400
    elif deployment_target == 'staging':
        # S3_BUCKET = STAGING_S3_BUCKET
        S3_BASE_URL = 'http://%s/%s' % (S3_BUCKET, PROJECT_SLUG)
        S3_DEPLOY_URL = 's3://%s/%s' % (S3_BUCKET, PROJECT_SLUG)
        SERVERS = STAGING_SERVERS
        SERVER_BASE_URL = 'http://%s/%s' % (SERVERS[0], PROJECT_SLUG)
        SERVER_LOG_PATH = '/var/log/%s' % PROJECT_FILENAME
        DISQUS_SHORTNAME = 'nprviz-test'
        DEBUG = True
        ASSETS_MAX_AGE = 20
    else:
        S3_BUCKET = None
        S3_BASE_URL = 'http://127.0.0.1:8000'
        S3_DEPLOY_URL = None
        SERVERS = []
        SERVER_BASE_URL = 'http://127.0.0.1:8001/%s' % PROJECT_SLUG
        SERVER_LOG_PATH = '/tmp'
        DISQUS_SHORTNAME = 'nprviz-test'
        DEBUG = True
        ASSETS_MAX_AGE = 20

    DEPLOYMENT_TARGET = deployment_target

"""
Run automated configuration
"""
DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', None)

configure_targets(DEPLOYMENT_TARGET)
