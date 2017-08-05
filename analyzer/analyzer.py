import datetime
import math
import requests
import requests_cache
from flask import Flask, jsonify, Response, request
from functools import wraps

from community_plugin import CommunityPlugin


def get_number_of_repos(organization, username, password):
    url = "http://github/get_number_of_repos/%s" % organization
    response = requests.get(url, auth=(username, password))
    return response.json()


def get_repos(organization, page, username, password):
    url = "http://github/get_repos/%s/%s" % (organization, page)
    response = requests.get(url, auth=(username, password))
    return response.json()


def get_releases(organization, repo_name, username, password):
    url = "http://github/get_releases/%s/%s" % (organization, repo_name)
    response = requests.get(url, auth=(username, password))
    return response.json()


def get_tag_created(x):
    mindate = datetime.datetime(datetime.MINYEAR, 1, 1)
    return x.tag_created or mindate


def get_datetime(timestamp):
    if not timestamp:
        return ""
    return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")


def get_download_count(releases):
    total_count = 0
    for release in releases:
        if "assets" in release:
            for asset in release['assets']:
                total_count += asset['download_count']
    return total_count


def get_travis_repository(organization, repo_name, token):
    url = "http://travis/get_repository/%s/%s" % (organization, repo_name)
    response = requests.get(url, auth=(token))
    return response.json()


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
        return f(*args, **kwargs)

    return wrapper


app = Flask(__name__)
requests_cache.install_cache('cache', backend='memory', expire_after=1800)


@app.route("/<organization>")
@authenticate
def list_repos(organization):
    auth = request.authorization
    username = auth.username
    password = auth.password
    number_of_repos = get_number_of_repos(organization, username, password)
    pages = int(math.ceil(number_of_repos / 30)) + 1
    plugins = []
    for i in range(1, pages):
        repos = get_repos(organization, i, username, password)
        for repo in repos:
            tag_name = get_latest_release(organization, repo["name"], username, password)
            tag_created = get_latest_release_date(organization, repo_name["name"], username, password)
            downloads = get_download_count(organization, repo_name["name"], username, password)
            plugins.append(CommunityPlugin(repo["name"], repo['html_url'], get_datetime(repo["created_at"]),
                                           get_datetime(repo["updated_at"]), tag_name, tag_created, downloads))


sorted_plugins = sorted(plugins, key=lambda x: get_tag_created(x), reverse=True)
return jsonify(sorted_plugins)

app.run(host='0.0.0.0')
