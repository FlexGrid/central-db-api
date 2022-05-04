# -*- coding: utf-8 -*-
"""
    Eve Demo (Secured)
    ~~~~~~~~~~~~~~~~~~

    This is a fork of Eve Demo (https://github.com/pyeve/eve-demo)
    intended to demonstrate how a Eve API can be secured by means of
    Flask-Sentinel.

    For demonstration purposes, besides protecting a couple API endpoints
    with a BearerToken class instance, we are also adding a static html
    endpoint an protecting with via decorator.

    :copyright: (c) 2015 by Nicola Iarocci.
    :license: BSD, see LICENSE for more details.
"""
from bson.objectid import ObjectId
from eve import Eve
from oauth2 import BearerAuth
from flask_sentinel import ResourceOwnerPasswordCredentials, oauth
from eve_swagger import get_swagger_blueprint, add_documentation
import redis
from flask import request, send_from_directory, render_template
from eve.io.mongo.validation import Validator
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

# importing ObjectId from bson library

client1 = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=3)
client1.admin.command('ismaster')
client2 = MongoClient(os.getenv("SENTINEL_MONGO_URI"),
                      serverSelectionTimeoutMS=3)
client2.admin.command('ismaster')


class MyValidator(Validator):
    def _validate_is_iso_8601(self, constraint, field, value):
        """ Test that it is a valid ISO 8601 timestamp.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint is True:
            try:
                datetime.fromisoformat(value)
            except ValueError:
                try:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    print(value)
                    self._error(field, "Must be valid is 8601 string in UTC")

    def _validate_is_valid_offset(self, constraint, field, value):
        """ Test that it is a valid object.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint is True:
            obj_id = self.document.get('prosumer_id')
            obj_type = self.document.get('type')
            obj_name = self.document.get('obj_name')
            # id = "5fec2c0b348df9f22156cc07"
            objInstance = ObjectId(obj_id)

            obj = client1['flexgrid_main']['dr_prosumers'].find_one(
                objInstance)

            if obj is None:
                print(field)
                self._error('prosumer_id',
                            f"Prosumer with id {objInstance} not found")

            if obj[obj_type][value]["name"] != obj_name:

                self._error(
                    "field",
                    f"Prosumer with id {objInstance} doesn't have {obj_name} at index {value} of {obj_type}"
                )

    def _validate_is_valid_object(self, constraint, field, value):
        """ Test that it is a valid object.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint is True:

            obj_id = ObjectId(value)

            if field == "prosumer_id":
                collection = 'dr_prosumers'
            elif field == "flex_request_id":
                collection = 'flex_requests'
            elif field == "flex_offer_id":
                collection = 'flex_offers'

            obj = client1['flexgrid_main'][collection].find_one(obj_id)

            if obj is None:
                print(field)
                self._error(field, f"{collection} with id {obj_id} not found")

    def _validate_is_valid_direction(self, constraint, field, value):
        """ Test that it is a valid direction.

        Valid directions are 'Up' and 'Down'

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint is True:

            if value not in ['Up', 'Down']:
                self._error(field, "direction must be 'Up' or 'Down'")

    def _validate_description(self, description, field, value):
        """ {'type': 'string'} """
        # Accept description attribute, used for swagger doc generation
        pass

    def _validate_example(self, description, field, value):
        """ {'type': 'string'} """
        # Accept an example attribute, used for swagger doc generation
        pass


app = Eve(__name__, auth=BearerAuth, validator=MyValidator, static_url_path='')
ResourceOwnerPasswordCredentials(app)

print("Mongodb active")


@app.route('/swagger/')
def send_swagger():
    return render_template('index.html', host=f"{request.url_root}api-docs")


@app.route('/swagger/<path:path>')
def send_swagger_assets(path):
    print("the path is", path)
    return send_from_directory('swagger', path)


@app.route('/authorization/')
def check_token():
    print(f"The app is {app.auth}")
    if app.auth.check_auth(request.args.get('token', default=None, type=str),
                           [],
                           request.args.get('resource', default='/', type=str),
                           request.args.get('method', default='get',
                                            type=str)):
        return "OK"
    else:
        return "Unauthorized"


@app.route('/endpoint')
@oauth.require_oauth()
def restricted_access():
    return "You made it through and accessed the protected resource!"


swagger = get_swagger_blueprint()
app.register_blueprint(swagger)
# required. See http://swagger.io/specification/#infoObject for details.
app.config['SWAGGER_INFO'] = {
    'title': 'Flexgrid DataBase API',
    'version': '1.0',
    'description': 'The central repository of the flexgrid project',
    # 'termsOfService': 'my terms of service',
    'contact': {
        'name': 'Dimitros J. Vergados',
        'url': 'https://flexgrid-project.eu'
    },
    'license': {
        'name': 'BSD',
        'url': 'https://github.com/pyeve/eve-swagger/blob/master/LICENSE',
    },
    'schemes': ['https']
}

app.config['SWAGGER_HOST'] = os.getenv("SWAGGER_HOST")

# optional. Add/Update elements in the documentation at run-time without deleting subtrees.
add_documentation(
    swagger, {
        'paths': {
            '/data_points_aggr': {
                'get': {
                    'parameters': [{
                        'in': 'query',
                        'name': 'aggregate',
                        'required': True,
                        'description':
                        'JSON with the values like this: `{"$start": "2017-07-11T19:05:00","$end":"2017-07-11T22:00:01", "$prosumer_ids": ["5ee8e1fc00871cbb09d9fdf8", "5ee8e0fa00871cbb09d9fdc0"], "$interval": 3600}`',
                        'schema': {
                            'type': 'string',
                            'example': {
                                '$start':
                                "2017-07-11T19:05:00",
                                "$end":
                                "2017-07-11T22:00:01",
                                "$prosumer_ids": [
                                    "5ee8e1fc00871cbb09d9fdf8",
                                    "5ee8e0fa00871cbb09d9fdc0"
                                ],
                                "$interval":
                                3600
                            }
                        }
                    }]
                }
            }
        }
    })

if __name__ == '__main__':
    app.run()
