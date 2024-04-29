#!/bin/sh

set -e  # to make sure entire script fails if any of the subscripts fail

envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf  # env substitute to insert our default.conf.tpl nginx file into our docker image environment, and substitute its dynamic variables ${} with the env variable that matches its name
nginx -g 'daemon off;'  # starts nginx with the config above, but instead of running in background of the image, runs in the foreground so that all the logs can be output for the nginx server in our CLI