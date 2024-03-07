# FROM below indicates we're using python version 3.9; python is the name of the docker image, the rest after the : colon is the docker tag
# alpine is a very basic version of linux, has bare minimum reqs and is efficient
FROM python:3.9-alpine3.13 
# LABEL maintainer is used so that other developers know who is the person in charge of app
# USER root # if you want to specify user when building image

LABEL maintainer="londonappdeveloper.com" 

# recommended when running py in docker container, means you don't want to buffer the output
ENV PYTHONBUFFERED 1

# COPY commands indicate to docker that the first input "./etc" should go in the appropiate path in docker (second input part of the COPY stmt)
# WORKDIR indicates which will be the base directory used to run app and commands in the docker image
# EXPOSE means expose the port 8000 from our container to our local computer
COPY ./requirements.txt /tmp/requirements.txt 
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app 
EXPOSE 8000

# the && \ is syntax to split code into lines for readability
# run is one long run cmd for our alpine (linux) system that runs all cmds. installs virtual env, upgrades pip, installs project reqs, removes tmp folders used for docker build so the image is as lightweight as possible for deployment
# adduser cmd then adds a specific user to our image; its best practice to specify a user that is not root/superadmin user for security. user w/no pwd, name the user
# ARG here is set and then overwritten in docker compose yml file, so that when app runs through docker compose, DEV is set to true, not false
# if, then, fi stmt is an if stmt in docker shell cmd, we're checking if DEV is set to true and if so installing the dev reqs from txt file
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    # REMOVING THIS BELOW SINCE DID NOT ALLOW ME TO PROCEED
    adduser \
        --disabled-password \
        --no-create-home \
        django-user 

# ENV PATH variable specifies an environ key which will help reduce code needed when running commands later
# ORIGINAL CODE FROM VIDEO WAS WRONG, GUIDING ME TO WRONG PATH SO HAD TO CHANGE PATH TO MAKE WORK
ENV PATH="/py/bin:$PATH"
# ENV PATH="/py/bin:/py/lib/python3.9/site-packages:$PATH"

# USER is last line of docker file; specifies user to switch to after root user has created Dockerfile; this new user will persist for all future docker commands
USER django-user 

# check current user in docker linux kernel shell
# current_user=$(whoami)
# grep "^$current_user:" /etc/passwd | cut -d: -f1