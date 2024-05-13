# recipe-app-api
Recipe API project.

- requirements.dev.txt file is used for dependencies only required by development teams

proxy/default.conf.tpl file:
    - this file serves as a configuration block for the server (nginx) that will run our django app
    - listen...
        - set the port that the server will listen on (as a variable ie. ${<variable>})
        - location blocks are used to define url mappings as you want them configured
        - location /static: server will set contents in /vol/static from our docker build/container to /static url endpoint
        - location /: setting our uwsgi server to run on a host and port; include to include params from http requests in our uwsgi server; client max body size sets a limit to the size of the file that the server can accept from our users (10 megabytes for our user images)

proxy/uwsgi_params:
    - copy and paste reqs for uwsgi params from their website https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html
