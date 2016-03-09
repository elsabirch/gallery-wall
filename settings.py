"""File containing settings that a user may wish to modify for practical use.

Example: Contains easy toggle for online/offline resource locations.
"""

online = False

if online:
    jquery_path = "https://code.jquery.com/jquery.js"
    boostrap_css_path = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"
    boostrap_js_path = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"
    chartjs_path = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.js"
else:
    jquery_path = "/static/local_copies_untracked/jquery.js"
    boostrap_css_path = "/static/local_copies_untracked/bootstrap.css"
    boostrap_js_path = "/static/local_copies_untracked/bootstrap.js"
    chartjs_path = "/static/local_copies_untracked/chart.js"
