import requests, requests_cache
from flask import Flask, jsonify, Response, request
from functools import wraps

def get_token(request):
	auth = request.authorization
	return auth.token

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.token:
            return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
        return f(*args, **kwargs)
    return wrapper

app = Flask(__name__)
requests_cache.install_cache('cache', backend='memory', expire_after=1800)

@app.route("/get_repository/<organization>/<repo_name>")
@authenticate
def get_repository(organization, repo_name):
	url = "https://api.travis-ci.org/repos/%s/%s" % (organization, repo_name)
	response = requests.get(url, auth=(get_token(request)))
	return response

app.run(host= '0.0.0.0')