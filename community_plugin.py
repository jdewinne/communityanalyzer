

class CommunityPlugin(object):
    def __init__(self, repo_name, repo_url, created, last_updated, tag_name=None, tag_created=None, downloads = 0):
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.created = created
        self.last_updated = last_updated
        self.tag_name = tag_name
        self.tag_created = tag_created
        self.downloads = downloads