import app_config
import copy
import datetime
from dateutil.parser import parse
from fabric.api import *
from fabric.state import env
from jinja2 import Template
from slacker import Slacker

import app_config
from oauth import get_document
from util.models import Story
from util.slack import SlackTools
from scrapers.analytics import GoogleAnalyticsScraper
from scrapers.nprapi import NPRAPIScraper
from scrapers.spreadsheet import SpreadsheetScraper

env.user = app_config.SERVER_USER
env.hosts = app_config.SERVERS
env.slug = app_config.PROJECT_SLUG

slackTools = SlackTools()

"""
Base configuration
"""
env.user = app_config.SERVER_USER
env.forward_agent = True

env.hosts = []
env.settings = None

slack = Slacker(app_config.slack_key)

SECONDS_BETWEEN_CHECKS = 1 * 60 * 60 # 1 hour
MAX_SECONDS_SINCE_POSTING = 3 * 24 * 60 * 60 # 2 days

"""
MINUTES_BETWEEN_CHECKS = 15
MINUTES_BETWEEN_REPORTS = [
    240,  # 4 hours
    480   # 8 hours
]
"""

"""
Configuration
"""
def _get_template_conf_path(service, extension):
    """
    Derive the path for a conf template file.
    """
    return 'confs/%s.%s' % (service, extension)

def _get_rendered_conf_path(service, extension):
    """
    Derive the rendered path for a conf file.
    """
    return 'confs/rendered/%s.%s.%s' % (app_config.PROJECT_FILENAME, service, extension)

def _get_installed_conf_path(service, remote_path, extension):
    """
    Derive the installed path for a conf file.
    """
    return '/etc/init/%s.%s.%s' % (app_config.PROJECT_FILENAME, service, extension)

def _get_installed_service_name(service):
    """
    Derive the init service name for an installed service.
    """
    return '%s.%s' % (app_config.PROJECT_FILENAME, service)


"""
Running the app
Probably only neded the first time, to set up oauth creds
"""
@task
def app(port='8000'):
    """
    Serve app.py.
    """
    if env.settings:
        local("DEPLOYMENT_TARGET=%s bash -c 'gunicorn -b 0.0.0.0:%s --timeout 3600 --debug --reload app:wsgi_app'" % (env.settings, port))
    else:
        local('gunicorn -b 0.0.0.0:%s --timeout 3600 --debug --reload app:wsgi_app' % port)

"""
Data tasks
"""
@task
def load_new_stories():
    get_document(app_config.STORIES_GOOGLE_DOC_KEY, app_config.STORIES_PATH)
    scraper = SpreadsheetScraper()
    stories = scraper.scrape_spreadsheet(app_config.STORIES_PATH)
    new_stories = scraper.write(stories)
    print new_stories

    for story in new_stories:
        slackTools.send_tracking_started_message(story)

@task
def get_linger_rate():
    scraper = GoogleAnalyticsScraper()
    stats = scraper.get_linger_rate('space-time-stepper-20160208')

def seconds_since(a):
    now = datetime.datetime.now()
    return (now - a).total_seconds()

def time_bucket(t):
    if not t:
        return False

    seconds = seconds_since(t)

    # 7th message, 2nd day midnight + 10 hours
    # 8th message, 2nd day midnight + 15 hours
    second_day_midnight_after_publishing = t + datetime.timedelta(days=2)
    second_day_midnight_after_publishing.replace(hour = 0, minute = 0, second=0, microsecond = 0)
    seconds_since_second_day = seconds_since(second_day_midnight_after_publishing)

    if seconds_since_second_day > 15 * 60 * 60: # 15 hours
        return 'day 2 hour 15'

    if seconds_since_second_day > 10 * 60 * 60: # 10 hours
        return 'day 2 hour 10'

    # 5th message, 1st day midnight + 10 hours
    # 6th message, 1st day midnight + 15 hours
    midnight_after_publishing = t + datetime.timedelta(days=1)
    midnight_after_publishing.replace(hour = 0, minute = 0, second=0, microsecond = 0)
    seconds_since_first_day = seconds_since(midnight_after_publishing)

    if seconds_since_second_day > 10 * 60 * 60: # 15 hours
        return 'day 1 hour 15'

    if seconds_since_second_day > 10 * 60 * 60: # 10 hours
        return 'day 1 hour 10'

    # 2nd message, tracking start + 4 hours
    # 3rd message, tracking start + 8 hours
    # 4th message, tracking start + 12 hours
    if seconds > 12 * 60 * 60: # 12 hours
        return 'hour 12'

    if seconds > 8 * 60 * 60: # 8 hours
        return 'hour 8'

    if seconds > 4 * 60 * 60: # 4 hours
        return 'hour 4'

    # Too soon.
    return False


@task
def get_story_stats():
    analytics = GoogleAnalyticsScraper()

    for story in Story.select():
        story_time_bucket = time_bucket(story.article_posted)
        last_bucket = time_bucket(story.last_checked)

        # Check when the story was last reported on
        if last_bucket:

            # Skip stories that have been checked recently
            # And stories that are too old.
            if (last_bucket == story_time_bucket):
                print "Checked recently. Bucket: " + story_time_bucket
                continue

        if not story_time_bucket:
            print "This story is too new. Not checking yet."
            continue

        # Some stories have multiple slugs
        story_slugs = story.slug.split(',')
        story_slugs = [slug.strip() for slug in story_slugs]

        # Get the linger rate for each
        for slug in story_slugs:
            stats = analytics.get_linger_rate(slug)
            if stats:
                print(story.name, slug, stats)
                # TODO:
                # Handle stories with multiple slugs better
                slackTools.send_linger_time_update(story, stats, story_time_bucket)
            else:
                print "No stats"

        # Mark the story as checked
        story.last_checked = datetime.datetime.now()
        # story.save() # TODO

@task
def send_message():
    # Send a message to #general channel
    slack.chat.post_message('#broadway-carebot', 'Hi @livlab!', as_user=True)

"""
Deploy tasks
"""

@task
def production():
    """
    Run as though on production.
    """
    env.settings = 'production'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def staging():
    """
    Run as though on staging.
    """
    env.settings = 'staging'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def create_directories():
    """
    Create server directories.
    """
    require('settings', provided_by=['production', 'staging'])

    run('mkdir -p %(SERVER_PROJECT_PATH)s' % app_config.__dict__)
    run('git clone %(REPOSITORY_URL)s %(SERVER_PROJECT_PATH)s' % app_config.__dict__)

@task
def setup_logs():
    """
    Create log directories.
    """
    require('settings', provided_by=['production', 'staging'])

    sudo('mkdir %(SERVER_LOG_PATH)s' % app_config.__dict__)
    sudo('chown ubuntu:ubuntu %(SERVER_LOG_PATH)s' % app_config.__dict__)

@task
def create_virtualenv():
    """
    Setup a server virtualenv.
    """
    require('settings', provided_by=['production', 'staging'])

    run('virtualenv -p %(SERVER_PYTHON)s %(SERVER_VIRTUALENV_PATH)s' % app_config.__dict__)
    run('source %(SERVER_VIRTUALENV_PATH)s/bin/activate' % app_config.__dict__)


@task
def clone_repo():
    """
    Clone the source repository.
    """
    require('settings', provided_by=['production', 'staging'])

    run('git clone %(REPOSITORY_URL)s %(SERVER_REPOSITORY_PATH)s' % app_config.__dict__)

    if app_config.REPOSITORY_ALT_URL:
        run('git remote add bitbucket %(REPOSITORY_ALT_URL)s' % app_config.__dict__)


@task
def checkout_latest():
    """
    Get the updated code
    """
    run('cd %s; git pull origin master' % (app_config.SERVER_PROJECT_PATH))


@task
def install_requirements():
    """
    Install the latest requirements.
    """
    require('settings', provided_by=['production', 'staging'])

    run('%(SERVER_VIRTUALENV_PATH)s/bin/pip install -U -r %(SERVER_PROJECT_PATH)s/requirements.txt' % app_config.__dict__)
    # run('cd %(SERVER_REPOSITORY_PATH)s; npm install' % app_config.__dict__)


@task
def render_confs():
    """
    Renders server configurations.
    """
    require('settings', provided_by=['production', 'staging'])

    with settings(warn_only=True):
        local('rm -rf confs/rendered')
        local('mkdir confs/rendered')

    # Copy the app_config so that when we load the secrets they don't
    # get exposed to other management commands
    context = copy.copy(app_config.__dict__)
    context.update(app_config.get_secrets())

    for service, remote_path, extension in app_config.SERVER_SERVICES:
        template_path = _get_template_conf_path(service, extension)
        rendered_path = _get_rendered_conf_path(service, extension)

        with open(template_path,  'r') as read_template:

            with open(rendered_path, 'wb') as write_template:
                payload = Template(read_template.read())
                write_template.write(payload.render(**context))

@task
def deploy_confs():
    """
    Deploys rendered server configurations to the specified server.
    This will reload nginx and the appropriate uwsgi config.
    """
    require('settings', provided_by=['production', 'staging'])

    put('%s.env' % env.settings, '%(SERVER_PROJECT_PATH)s/.env' % app_config.__dict__)
    # TODO -- we might want to run `source .env`?

    render_confs()

    with settings(warn_only=True):
        for service, remote_path, extension in app_config.SERVER_SERVICES:
            rendered_path = _get_rendered_conf_path(service, extension)
            installed_path = _get_installed_conf_path(service, remote_path, extension)

            print 'Updating %s' % installed_path
            put(rendered_path, installed_path, use_sudo=True)

            sudo('initctl reload-configuration')

            if service == 'nginx':
                sudo('service nginx reload')
            else:
                service_name = _get_installed_service_name(service)
                sudo('service %s restart' % service_name)


@task
def deploy_analytics_conf():
    # put('client_secrets.json', '%(SERVER_PROJECT_PATH)s/client_secrets.json' % app_config.__dict__)
    put('analytics.dat', '%(SERVER_PROJECT_PATH)s/analytics.dat' % app_config.__dict__)

    # Move google ouath credentials
    local('cp ~/.google_oauth_credentials ./.google_oauth_credentials')
    put('.google_oauth_credentials', '~/.google_oauth_credentials')

    # run('mkdir -p %(SERVER_PROJECT_PATH)s' % app_config.__dict__)

@task
def install_crontab():
    """
    Install cron jobs script into cron.d.
    """
    require('settings', provided_by=['production', 'staging'])

    sudo('cp %(SERVER_PROJECT_PATH)s/crontab /etc/cron.d/%(PROJECT_FILENAME)s' % app_config.__dict__)

@task
def setup_database():
    """
    Manually create an empty sqlite DB.
    Otherwise it gets created by root on first run, and regular
    users can't write to it.
    """
    sudo('sqlite3 %(SERVER_PROJECT_PATH)s/%(PROJECT_FILENAME)s.db ".databases"' % app_config.__dict__)
    sudo('chown ubuntu:ubuntu %(SERVER_PROJECT_PATH)s/%(PROJECT_FILENAME)s.db' % app_config.__dict__)

@task
def start_service(service):
    """
    Start a service on the server.
    """
    service_name = _get_installed_service_name(service)
    sudo('service %s start' % service_name)

@task
def stop_service(service):
    """
    Stop a service on the server
    """
    service_name = _get_installed_service_name(service)
    sudo('service %s stop' % service_name)

@task
def setup():
    require('settings', provided_by=['production', 'staging'])

    setup_logs()
    create_directories()
    create_virtualenv()
    clone_repo()
    checkout_latest()
    setup_database()
    install_requirements()
    deploy_analytics_conf()
    deploy_confs()
    install_crontab()

@task
def reboot():
    """
    Restart the server
    TKTK
    """
    None

@task
def deploy():
    require('settings', provided_by=['production', 'staging'])

    with settings(warn_only=True):
        stop_service('bot')

    checkout_latest()
    install_requirements()
    deploy_analytics_conf()
    render_confs()
    deploy_confs()
    install_crontab()

"""
Deaths, destroyers of worlds
"""
@task
def shiva_the_destroyer():
    """
    Remove all directories, databases, etc. associated with the application.
    """
    with settings(warn_only=True):
        run('rm -Rf %(SERVER_PROJECT_PATH)s' % app_config.__dict__)
        run('rm -Rf %(SERVER_VIRTUALENV_PATH)s' % app_config.__dict__)
        run('rm -Rf %(SERVER_LOG_PATH)s' % app_config.__dict__)

        # Remove any installed services
        stop_service('bot')
        installed_service_path = _get_installed_conf_path(service, remote_path, extension)
        sudo('rm -f %s' % installed_service_path)

