# FROM below indicates we're using python version 3.9; python is the name of the docker image, the rest after the : colon is the docker tag
# alpine is a very basic version of linux, has bare minimum reqs and is efficient
FROM python:3.9-alpine3.13
# LABEL maintainer is used so that other developers know who is the person in charge of app
# USER root # if you want to specify user when building image

LABEL maintainer="londonappdeveloper.com"

# recommended when running py in docker container, means you don't want to buffer the output
ENV PYTHONBUFFERED 1

# COPY commands indicate to docker that the first input "./etc" should go in the appropiate path in docker created system (linux) (second input part of the COPY stmt)
# WORKDIR indicates which will be the base directory used to run app and commands in the docker container
# EXPOSE means expose the port 8000 from our container to our local computer
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
# DEPLOYMENT /scripts will be helper scripts run by our docker app
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

# the && \ is syntax to split code into lines for readability
# run is one long run cmd for our alpine (linux) system that runs all cmds. installs virtual env, upgrades pip, installs project reqs, removes tmp folders used for docker build so the image is as lightweight as possible for deployment
# adduser cmd then adds a specific user to our image; its best practice to specify a user that is not root/superadmin user for security. user w/no pwd, name the user
# ARG here is set and then overwritten in docker compose yml file, so that when app runs through docker compose, DEV is set to true, not false
# if, then, fi stmt is an if stmt in docker shell cmd, we're checking if DEV is set to true and if so installing the dev reqs from txt file
# apk add lines: first line indicates dependencies to install and persist after image creation; second line --virtual adds temp when building image but then removes dependencies for efficiency
# apk lines: client for postgres so that it can run during prod. jpeg-dev is req (needs to be installed) to run Pillow package for image mgmt. --virtual line sets a virtual dependancy package, that can later be removed. packages below that are the ones needed to install so that psycopg2 is installed correctly
# linux-headers package is required for our uWSGI server installation; uWSGI server connects our app to a web server; only temporarily needed
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    # DEPLOYMENT: add linux-headers
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # REMOVING THIS BELOW SINCE DID NOT ALLOW ME TO PROCEED
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    # need to create static and media file directories with django-user permissions, not root user else run into issues
    # '-p' used to indicate all subdirectories to be made in path specified after /vol...
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    # chown to change owner;
    # -R for recursive; <owner>:<group> used to indicate owner and group of /vol
    chown -R django-user:django-user /vol && \
    # change mode (755) to change permissions in /vol directory, so owner and group can make any changes
    chmod -R 755 /vol && \
    # +x /scripts ensures that scripts dir is executable
    chmod -R +x /scripts

# DEPLOYMENT: ENV PATH variable specifies an environ key which will help reduce code needed when running commands later
ENV PATH="/scripts:/py/bin:$PATH"
# # Dev: OLD ENV PATH for dev build testing variable specifies an environ key which will help reduce code needed when running commands later
# ENV PATH="/py/bin:$PATH"
# ENV PATH="/py/bin:/py/lib/python3.9/site-packages:$PATH"  # was testing with this code since python was NOt executing

# USER is last line of docker file; specifies user to switch to after root user has created Dockerfile; this new user will persist for all future docker commands
USER django-user

# DEPLOYMENT: command run.sh is the CLI script that is going to run our entire application on a web server; this is the default command; we can overwrite in docker compose
CMD ["run.sh"]


# check current user in docker linux kernel shell
# current_user=$(whoami)
# grep "^$current_user:" /etc/passwd | cut -d: -f1
