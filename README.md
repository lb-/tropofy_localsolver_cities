
# Overview

This is a demo app to show off some features of Tropofy.
Purpose is to generate a customised wish-list of cities, based on user's preference.

Built with https://tropofy.com/

This app showcases:
* Loading example data from csv

# Developing

1. Activate the Virtual Environment
  `$ source ../tropofy_env/bin/activate`

2. Launch the application from the root project directory
  `$ python run.py`

3. Open running app in your browser at http://localhost:8080/app/



# Getting Started

1. Install Tropofy and ensure you have your Virtual Environment set up.
  * https://docs.tropofy.com/index.html#getting-started

2. Add a local `keys.py` file with the following:
  ```
  tropofy_private = "<private key for tropofy>"
  tropofy_public = "<public key for tropofy>"
  ```

3. Configure app and install dependencies from the root project directory
  `$ python setup.py develop`


# Helpful Links

* sqlalchemy docs (version 0.8 in use, but 0.9 docs only available)
  * http://docs.sqlalchemy.org/en/rel_0_9/
* Mako - templating language
  * http://www.makotemplates.org/
