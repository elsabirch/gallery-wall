"""File containing settings that a user may wish to modify for practical use.

Example: Contains easy toggle for online/offline resource locations.
"""

online = False

if online:
    jquery_path = "https://code.jquery.com/jquery.js"
else:
    jquery_path = "/static/local_copies_untracked/jquery.js"
