import datetime, math, requests
from community_plugin import CommunityPlugin
from flask import Flask, render_template, Response, request
from flask_misaka import Misaka
from functools import wraps

def get_number_of_repos(organization, username, password):
	url = "https://api.github.com/orgs/%s" % organization
	response = requests.get(url, auth=(username, password))
	org = response.json()
	return org["public_repos"]

def get_repos(organization, page, username, password):
	url = "https://api.github.com/orgs/%s/repos?page=%s" % (organization, page)
	response = requests.get(url, auth=(username, password))
	return response.json()

def get_releases(organization, repo_name, username, password):
	url = "https://api.github.com/repos/%s/%s/releases" % (organization, repo_name)
	response = requests.get(url, auth=(username, password))
	return response.json()

def get_tag_created(x):
	mindate = datetime.datetime(datetime.MINYEAR, 1, 1)
	return x.tag_created or mindate

def get_datetime(timestamp):
	if not timestamp:
		return ""
	return datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ")

def get_download_count(releases):
	total_count = 0
	for release in releases:
		if "assets" in release:
			for asset in release['assets']:
				total_count += asset['download_count']
	return total_count


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return Response('Login!', 401, {'WWW-Authenticate': 'Basic realm="Login!"'})
        return f(*args, **kwargs)
    return wrapper

app = Flask(__name__, template_folder="views")
Misaka(app, tables=True)

@app.route("/")
@authenticate
def list_latest_releases():
	organization = request.args.get('organization')
	auth = request.authorization
	username = auth.username
	password = auth.password
	number_of_repos = get_number_of_repos(organization, username, password)
	pages = int(math.ceil(number_of_repos/30))+1
	plugins = []
	for i in range(1,pages):
		repos = get_repos(organization,i, username, password)
		for repo in repos:
			releases = get_releases(organization, repo["name"], username, password)
			if len(releases) > 0:
				plugins.append(CommunityPlugin(repo["name"], repo['html_url'], get_datetime(repo["created_at"]), get_datetime(repo["updated_at"]), releases[0]["tag_name"], get_datetime(releases[0]["published_at"]), get_download_count(releases)))
			else:
				plugins.append(CommunityPlugin(repo["name"], repo['html_url'], get_datetime(repo["created_at"]), get_datetime(repo["updated_at"])))

	sorted_plugins = sorted(plugins, key=lambda x: get_tag_created(x), reverse=True)
	result = "|name|created|lastupdated|latest_tag|tag_date|downloads|\n"
	result += "| --- | --- | --- | --- | --- | --- |\n"
	for plugin in sorted_plugins:
		result += "|[%s](%s)|%s|%s|%s|%s|%s|\n" % (plugin.repo_name, plugin.repo_url, plugin.created, plugin.last_updated, plugin.tag_name, plugin.tag_created, plugin.downloads)
	return render_template('index.html', text=result)


app.run(host= '0.0.0.0')