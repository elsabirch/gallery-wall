
#Gallery Wall 

![gwlogo](/docs/gw_logo.png)

Gallery Wall is the project of Elsa Birch while a student at Hackbright Academy in San Francisco, Winter 2016. You can reach her via <elsa.birch@gmail.com> or see more about her interests and background on her [personal website](http://www.elsabirch.com).

## Overview & Features

It is trendy to hang a collected gallery of pictures together as a larger composition. Gallery Wall produces visually pleasing arrangements from a set of user provided pictures. Users can select from different styles, such as columnar or cloud-like. Continually varying layouts are produced dynamically for any gallery of pictures, regardless of sizes and numbers of pictures.  Users may save and compare wall layouts for a single gallery set and handy dimensions are provided for hanging.

Sample sets of pictures are also available for users to try the layout algorithms and heuristics designed specifically for this project. The Object Oriented design of the arrangement process itself also lends itself to refinement and extension!

*Quick note on terminology:  throughout this application, ‘gallery’ indicates an unordered collection of pictures, and ‘wall’ refers to such a collection once it has been arranged and carries physical placement information.*

### Tech Stack

**Server**: Python, Flask with Jinja templates

**Database**: SQL, using Postgres and SQLAlchemy

**Backend/Algorithms**: Python implementations of custom algorithms

**Frontend**: Javascript, JQuery, Bootstrap, ChartsJS, HTML5

**Static Resources**: User upload file storage Amazon Web Services S3 cloud storage via Boto3

**Testing**: Doctests and Unittest

### Screenshots

Navigation homepage for a logged in user.

![navhome](/docs/navigation-screenshot.png)

Gallery selection.

![arrange](/docs/galleries-screenshot.png)

Arrangement interface.

![arrange](/docs/arrange-screenshot.png)

Wall dimensions for hanging.

![dimensions](/docs/dimensions-screenshot.png)


### Component Files of Note

`server.py` contains the the routes accessible directly by the user, as well as those accessed asynchronously to provide data to the client.

`utilities.py` contains logic and functionality used by server.py for basic user interaction such as login, logout, upload, and viewing database stored content.

`model.py` provides the data model associated with user interaction and database storage: Pictures, Galleries, Walls, Users, etc.

`arrange.py` provides the functions of picture arrangement. It contains a Workspace class that provides state as a gallery is arranged into a wall.  Workspaces use members of a Pic class which contain a subset of the information about a Picture with some modification to facilitate arrangement. Arrangement is accomplished by controllers called Arrangers that act on the workspace. Each type of arranger is a subclasses of the abstract base class Arranger that provides some shared methods.

`wall.js` contains javascript methods needed to request from the server and then plot walls onto HTML5 canvas for display.  This includes the functionality to do so in the arrangement interface, in which new wall arrangements may be requested form the server before plotting. Note that the visual display of galleries is accomplished via a wall.

`time_track.py` and `timeplot-spark.js` exist for my own personal tracking of how I have spent my time on the project, and are not intended to be used by others (the text file with the data for these functions is not provided.)



### Try it Locally

Still very much a work in progress! But if you'd like to try running the app locally, these steps may help.  This is not meant to be a step-by-step guide, but just a quick to-do list for users already familiar with the required tasks.

1. Create virtualenv using requirements.txt and activate it

2. create a psql database called gallerywall

3. Run seed_database.py

4. Run server.py

5. Head to "http://localhost:5000/" in your browser!
