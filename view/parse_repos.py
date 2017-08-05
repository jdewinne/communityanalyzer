import requests, requests_cache
from flask import Flask, render_template, Response, request
from flask_misaka import Misaka
from functools import wraps

def get_analyzed_repos(organization, username, password):
	url = "http://analyzer/%s" % organization
	response = requests.get(url, auth=(username, password))
	return response.json()

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
        return f(*args, **kwargs)
    return wrapper

app = Flask(__name__, template_folder="views")
requests_cache.install_cache('cache', backend='memory', expire_after=1800)
Misaka(app, tables=True)

@app.route("/<organization>")
@authenticate
def analyze(organization):
	auth = request.authorization
	username = auth.username
	password = auth.password
	
	sorted_plugins = get_analyzed_repos(organization, username, password)
	result = "|name|created|lastupdated|latest_tag|tag_date|downloads|\n"
	result += "| --- | --- | --- | --- | --- | --- |\n"
	for plugin in sorted_plugins:
		result += "|[%s](%s)|%s|%s|%s|%s|%s|\n" % (plugin.repo_name, plugin.repo_url, plugin.created, plugin.last_updated, plugin.tag_name, plugin.tag_created, plugin.downloads)
	return render_template('index.html', text=result)


app.run(host= '0.0.0.0')