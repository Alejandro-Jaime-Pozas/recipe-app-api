# run an nginx image. by default, nginxinc runs with the root user (not ideal for auth/permissions) which is why we use the unprivileged version which is more secure
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="https://portfolio-alejandro-jaime.web.app/"

# copy our files created in this proxy dir to ngnix location
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# define the env variables; listen port is where our nginx server is listening on; app port is where the app runs
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# switch to root user in order to run the following commands
USER root

# create the /vol/static dir to store our static files; chmod 755 to allow read permissions from those files; touch: used to set up a default.conf file (writes an empty file); chown nginx:nginx to allow our nginx user to be the owner of that new default.conf file (not the root user); chmod +x to allow docker container to run run.sh file
RUN mkdir -p /vol/static && \
chmod 755 /vol/static && \
touch /etc/nginx/conf.d/default.conf && \
chown nginx:nginx /etc/nginx/conf.d/default.conf && \
chmod +x /run.sh

# creating a default volume for our docker image
VOLUME /vol/static

# switch to nginx user for future command executions
USER nginx

# default script that will run when we create instances from this docker image
CMD [ "/run.sh" ]
