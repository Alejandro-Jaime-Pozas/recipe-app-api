# recipe-app-api
Recipe API project.

## Quickstart

### Overview

This is a Django rest_framework application to be used as a backend rest api framework for a frontend application by any developer.

Use the following link to view the API documentation:

http://ec2-100-27-216-147.compute-1.amazonaws.com/api/docs


### Using the API

To start using the API, you can take the following steps:

1. Under `user`, create a post request at /api/user/create/ to create your user.
2. Under `user`, create a post request at /api/user/token/ to generate a token.
3. Copy the generated token and click `Authorize` button at top of page.
4. Under `tokenAuth` Value field, input `Token` and a ' ' space character and paste your token to authenticate.
5. Under `user`, get your user object at /api/user/me to verify that you're newly created user is authenticated.
6. You are now ready to create recipes! Just make sure you turn the stove off/logout when you're done.
