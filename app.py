import os
import json
from collections import defaultdict

import requests
from flask import Flask, jsonify
from github import Github


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def get_github_user(username):
        github_client = Github(os.environ['GITHUB_AUTH_TOKEN'])
        user = github_client.get_user(username)
        repos = user.get_repos()
        
        data = {
            'public_repos': {
                'total': user.public_repos,
                'original': 0,
                'forked': 0
            },
            'followers': user.followers,
            'stars_given': user.get_starred().totalCount,
            'stars_received': 0,
            'open_issues': 0,
            'commits': 0,
            'account_size': 0,
            'languages': defaultdict(int),
            'topics': defaultdict(int)
        }

        for repo in repos:
            data['stars_received'] += repo.stargazers_count
            data['open_issues'] += repo.open_issues_count
            data['account_size'] += repo.size
            
            if repo.fork:
                data['public_repos']['forked'] += 1
            else:
                data['public_repos']['original'] += 1
                data['commits'] += repo.get_commits().totalCount

            if repo.language:
                data['languages'][repo.language] += 1

            topics = repo.get_topics()
            for topic in topics:
                data['topics'][topic] += 1

        return data

    def check_response_status(status_code):
        if status_code != 200:
            raise Exception(f'Error connecting to Bitbucket API. Status code: {response.status_code}')

    def get_paginated_count(url):
        count = 0
        while url:
            response = requests.get(url, headers=headers)
            check_response_status(response.status_code)

            response_data = json.loads(response.text)
            values = response_data['values']
            count += len(values)
            url = response_data.next if response_data.next else None                
        return count

    def get_bitbucket_user(username):
        BITBUCKET_BASE_URL = 'https://api.bitbucket.org/2.0'
        headers = {'Content-Type': 'application/json'}

        repo_url = BITBUCKET_BASE_URL + f'/users/{username}/repositories'
        response = requests.get(repo_url, headers=headers)
        check_response_status(response.status_code)

        repo_data = json.loads(response.text)
        data = {
            'public_repos': {
                'total': repo_data['size'],
                'original': 0,
                'forked': 0
            },
            'followers': 0,
            'open_issues': 0,
            'commits': 0,
            'account_size': 0,
            'languages': defaultdict(int),
        }

        for repo in repo_data['values']:
            data['account_size'] += repo['size']

            if repo.parent:
                data['public_repos']['forked'] += 1
            else:
                data['public_repos']['original'] += 1
                data['commits'] += get_paginated_count(repo['links']['commits'])

            if repo.has_issues:
                data['open_issues'] += get_paginated_count(repo['links']['issues'])

            if repo.language:
                    data['languages'][repo['language'] += 1

        return data

    @app.route('/user/<username>')
    def get_user(username):
        data = get_bitbucket_user(username)
        return jsonify(data)

    return app