=============================
flask-restless-swagger-2
=============================

Magically create Swagger_ documentation as you magically create your RESTful API with Flask-Restless_

This has lingered a while without the love it needs due to other more pressing projects.  Contributions are welcome and appreciated.


This is my fork of [flask-restless-swagger](https://github.com/mmessmore/flask-restless-swagger). It had several bugs and also lackluster doc.
To install:

    pip install flask-restless-swagger-2
    
To use import like so
    
    from flask_restless_swagger import SwagAPIManager as APIManager

Using this, you replace your current flask-restless APIManager usage with the swagg'd one


Run your flask app, and then go to [localhost:5000/swagger](localhost:5000/swagger)

You can see the generated swagger json in [localhost:5000/swagger.json](localhost:5000/swagger.json)


Features
--------

This strives to be a drop in replacement for Flask-Restless_' APIManager.  It wraps 
the APIManager calls to try to gather enough information to present a Swagger_ 2.0
file.  It also deploys the static content for the Swagger-UI configured to point
to said Swagger_ JSON file.

Status
------
Currently it "works-for-me".  There are a few terrible assumptions it makes.  It 
probably needs some more features to be usable for everyone.  Suggestions, and 
pull requests are welcome.

TODO
----

* Add Docstrings in Models as descriptions
* Cleanup Markup
* Make it suck less

.. _Flask-Restless: https://flask-restless.readthedocs.org/en/latest/
.. _Swagger: http://swagger.io

