"""File containing settings that a user may wish to modify for practical use.

Example: Contains easy toggle for online/offline resource locations.
"""


class ResourcePaths(object):
    """Provides paths to resources, default via cdn set online false for local."""

    def __init__(self, online=True):
        self.online = online

    @property
    def jquery_path(self):
        if self.online:
            return "https://code.jquery.com/jquery.js"
        else:
            return "/static/local_copies_untracked/jquery.js"

    @property
    def boostrap_css_path(self):
        if self.online:
            return "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"
        else:
            return "/static/local_copies_untracked/bootstrap.css"

    @property
    def boostrap_js_path(self):
        if self.online:
            return "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"
        else:
            return "/static/local_copies_untracked/bootstrap.js"

    @property
    def chartjs_path(self):
        if self.online:
            return "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.js"
        else:
            return "/static/local_copies_untracked/chart.js"
