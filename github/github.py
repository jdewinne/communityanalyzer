import requests, requests_cache
from flask import Flask, jsonify, Response, request
from functools import wraps

def get_username(request):
	auth = request.authorization
	return auth.username

def get_password(request):
	auth = request.authorization
	return auth.password

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

@app.route("/get_number_of_repos/<organization>")
@authenticate
def get_number_of_repos(organization):
	url = "https://api.github.com/orgs/%s" % organization
	response = requests.get(url, auth=(get_username(request), get_password(request)))
	org = response.json()
	return jsonify(number=org["public_repos"])

@app.route("/get_repos/<organization>/<int:page>")
@authenticate
def get_repos(organization, page):
	url = "https://api.github.com/orgs/%s/repos?page=%s" % (organization, page)
	response = requests.get(url, auth=(get_username(request), get_password(request)))
	return response

@app.route("/get_releases/<organization>/<repo_name>")
@authenticate
def get_releases(organization, repo_name):
	url = "https://api.github.com/repos/%s/%s/releases" % (organization, repo_name)
	response = requests.get(url, auth=(get_username(request), get_password(request)))
	return response

app.run(host= '0.0.0.0')