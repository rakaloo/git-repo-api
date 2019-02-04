**Git Repo API*
An API for aggregating information across Git repository hosting services - GitHub and BitBucket

*Project setup*
Python version: 3.6.8

In order to run this project, you will need a Github Auth token which can be obtained via:
https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/
This token should be set as an environment variable called `GITHUB_AUTH_TOKEN`

Install project requirements
`pip install -r requirements.txt`

Run application within project directory
`flask run`

In the event that this command gives an FLASK_APP environment variable not set error
`export $FLASK_APP=app.py`

Once the application is running, hit the following endpoint via curl or Postman, etc
`http://127.0.0.1:5000/user/<username>`