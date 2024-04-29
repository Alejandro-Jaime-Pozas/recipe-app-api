#!/bin/sh

# code above is used to mark our file as a shell script file for execution

# set -e: if any command within this file fails, then entire script fails
set -e

python manage.py wait_for_db  # need to wait for the db to be available or app will crash
python manage.py collectstatic --noinput  # collects all initial static files
python manage.py migrate  # run migrations that have been applied (updated) or created (first-time) so our db is up to date

# run uwsgi app/service on a tcp socket on port 9000 (nginx will connect to it); set app to run w/ 4 workers; --master sets this uwsgi app/service as the main app running on the nginx server; --enable-threads to allow multi-threading; --module to specify the module which is app > wsgi.py (not app.app.wsgi since this script will run within the main app dir)
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi