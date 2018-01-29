__author__ = 'Michael Messmore'
__email__ = 'mike@messmore.org'
__version__ = '0.2.0'

try:
    import urlparse
except:
    from urllib import parse as urlparse

import json

import yaml
from flask import jsonify, request, Blueprint, redirect
from flask_restless import APIManager
from flask_restless.helpers import *

sqlalchemy_swagger_mapping = {
    'INTEGER': {'format': 'int32', 'type': 'integer'},
    'SMALLINT': {'format': 'int32', 'type': 'integer'},
    'NUMERIC': {'format': 'float', 'type': 'number'},
    'DECIMAL': {'format': 'float', 'type': 'number'},
    'VARCHAR': {'format': 'string', 'type': 'string'},
    'TEXT': {'format': 'string', 'type': 'string'},
    'DATE': {'format': 'date', 'type': 'string'},
    'BOOLEAN': {'format': 'bool', 'type': 'boolean'},
    'TINYINT': {'format': 'bool', 'type': 'boolean'},
    'BLOB': {'format': 'binary', 'type': 'string'},
    'BYTEA': {'format': 'binary', 'type': 'string'},
    'BINARY': {'format': 'binary', 'type': 'string'},
    'VARBINARY': {'format': 'binary', 'type': 'string'},
    'FLOAT': {'format': 'float', 'type': 'number'},
    'REAL': {'format': 'double', 'type': 'number'},
    'DATETIME': {'format': 'date-time', 'type': 'string'},
    'BIGINT': {'format': 'int64', 'type': 'integer'},
    'ENUM': {'format': 'string', 'type': 'string'},
    'INTERVAL': {'format': 'date-time', 'type': 'string'},
}


class SwagAPIManager(object):
    swagger = {
        'swagger': '2.0',
        'info': {},
        'schemes': ['http', 'https'],
        'basePath': '/api',
        'consumes': ['application/json'],
        'produces': ['application/json'],
        'paths': {},
        'definitions': {},
        'tags': []
    }

    def __init__(self, app=None, **kwargs):
        self.app = None
        self.manager = None

        if app is not None:
            self.init_app(app, **kwargs)

    def to_json(self, **kwargs):
        return json.dumps(self.swagger, **kwargs)

    def to_yaml(self, **kwargs):
        return yaml.dump(self.swagger, **kwargs)

    def __str__(self):
        return self.to_json(indent=4)

    @property
    def version(self):
        if 'version' in self.swagger['info']:
            return self.swagger['info']['version']
        return None

    @version.setter
    def version(self, value):
        self.swagger['info']['version'] = value

    @property
    def title(self):
        if 'title' in self.swagger['info']:
            return self.swagger['info']['title']
        return None

    @title.setter
    def title(self, value):
        self.swagger['info']['title'] = value

    @property
    def description(self):
        if 'description' in self.swagger['info']:
            return self.swagger['info']['description']
        return None

    @description.setter
    def description(self, value):
        self.swagger['info']['description'] = value

    def add_path(self, model, **kwargs):
        name = model.__tablename__
        schema = model.__name__
        path = kwargs.get('url_prefix', "") + '/' + name
        id_path = "{0}/{{{1}Id}}".format(path, schema.lower())
        self.swagger['paths'][path] = {}
        self.swagger['tags'].append({'name': schema})
        for method in [m.lower() for m in kwargs.get('methods', ['GET'])]:
            if method == 'get':
                self.swagger['paths'][path][method] = {
                    'tags': [schema],
                    'parameters': [{
                        'name': 'q',
                        'in': 'query',
                        'description': 'searchjson',
                        'type': 'string'
                    }],
                    'responses': {
                        200: {
                            'description': 'List ' + name,
                            'schema': {
                                'title': name,
                                'type': 'array',
                                'items': {'$ref': '#/definitions/' + schema}
                            }
                        }

                    }
                }

                if model.__doc__:
                    self.swagger['paths'][path]['description'] = model.__doc__
                if id_path not in self.swagger['paths']:
                    self.swagger['paths'][id_path] = {}
                self.swagger['paths'][id_path][method] = {
                    'tags': [schema],
                    'parameters': [{
                        'name': schema.lower() + 'Id',
                        'in': 'path',
                        'description': 'ID of ' + schema,
                        'required': True,
                        'type': 'integer'
                    }],
                    'responses': {
                        200: {
                            'description': 'Success ' + name,
                            'schema': {
                                'title': name,
                                '$ref': '#/definitions/' + schema
                            }
                        }

                    }
                }
                if model.__doc__:
                    self.swagger['paths'][id_path]['description'] = model.__doc__
            elif method == 'delete':
                if id_path not in self.swagger['paths']:
                    self.swagger['paths'][id_path] = {}
                self.swagger['paths']["{0}/{{{1}Id}}".format(path, schema.lower())][method] = {
                    'tags': [schema],
                    'parameters': [{
                        'name': schema.lower() + 'Id',
                        'in': 'path',
                        'description': 'ID of ' + schema,
                        'required': True,
                        'type': 'integer'
                    }],
                    'responses': {
                        200: {
                            'description': 'Success'
                        }

                    }
                }
                if model.__doc__:
                    self.swagger['paths'][id_path]['description'] = model.__doc__
            else:
                self.swagger['paths'][path][method] = {
                    'tags': [schema],
                    'parameters': [{
                        'name': name,
                        'in': 'body',
                        'description': schema,
                        'required': True,
                        'schema': {"$ref": "#/definitions/" + schema}
                    }],
                    'responses': {
                        200: {
                            'description': 'Success'
                        }

                    }
                }
                if model.__doc__:
                    self.swagger['paths'][path]['description'] = model.__doc__

    def add_defn(self, model, **kwargs):
        name = model.__name__
        self.swagger['definitions'][name] = {
            'type': 'object',
            'properties': {}
        }
        columns = get_columns(model).keys()
        for column_name, column in get_columns(model).items():
            if column_name in kwargs.get('exclude_columns', []):
                continue
            try:
                column_type = str(column.type)
                if '(' in column_type:
                    column_type = column_type.split('(')[0]
                column_defn = sqlalchemy_swagger_mapping[column_type]
            except AttributeError:
                schema = get_related_model(model, column_name)
                if column_name + '_id' in columns:
                    column_defn = {'schema': {
                        '$ref': schema.__name__
                    }}
                else:
                    column_defn = {'schema': {
                        'type': 'array',
                        'items': {
                            '$ref': schema.__name__
                        }
                    }}

            if column.__doc__:
                column_defn['description'] = column.__doc__
            self.swagger['definitions'][name]['properties'][column_name] = column_defn

    def init_app(self, app, **kwargs):
        self.app = app
        self.manager = APIManager(self.app, **kwargs)

        swagger = Blueprint('swagger', __name__, static_folder='static',
                            static_url_path=self.app.static_url_path + '/swagger', )

        @swagger.route('/swagger')
        def swagger_ui():
            return redirect('/static/swagger/swagger-ui/index.html')

        @swagger.route('/swagger.json')
        def swagger_json():
            # I can only get this from a request context
            self.swagger['host'] = urlparse.urlparse(request.url_root).netloc
            return jsonify(self.swagger)

        app.register_blueprint(swagger)

    def create_api(self, model, **kwargs):
        self.manager.create_api(model, **kwargs)
        self.add_defn(model, **kwargs)
        self.add_path(model, **kwargs)

    def swagger_blueprint(self):

        return swagger
