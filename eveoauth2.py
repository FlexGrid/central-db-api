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
from eve import Eve
from oauth2 import BearerAuth
from flask_sentinel import ResourceOwnerPasswordCredentials, oauth
from eve_swagger import swagger, add_documentation
import redis
from flask import request

app = Eve(auth=BearerAuth)
ResourceOwnerPasswordCredentials(app)

@app.route('/authorization/')
def check_token():
    print(f"The app is {app.auth}")
    if app.auth.check_auth(
        request.args.get('token', default = None, type = str),
        [],
        request.args.get('resource', default = '/', type = str),
        request.args.get('method', default = 'get', type = str)):
      return "OK"
    else:
      return "Unauthorized"


@app.route('/endpoint')
@oauth.require_oauth()
def restricted_access():
    return "You made it through and accessed the protected resource!"

app.register_blueprint(swagger)
# required. See http://swagger.io/specification/#infoObject for details.
app.config['SWAGGER_INFO'] = {
    'title': 'Flexgrid DataBase API',
    'version': '1.0',
    'description': 'The central repository of the flexgrid project',
    'termsOfService': 'my terms of service',
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

app.config['SWAGGER_EXAMPLE_FIELD_REMOVE'] = True

# optional. Add/Update elements in the documentation at run-time without deleting subtrees.
add_documentation({
    'paths': {
        '/data_points_aggr': {
            'get': {
                'parameters': [{
                    'in': 'query',
                    'name': 'aggregate',
                    'required': True,
                    'description':
                    'JSON with the values like this: `{"$start": "2017-07-11T19:05:00","$end":"2017-07-11T22:00:01", "$prosumer_ids": ["5ee8e1fc00871cbb09d9fdf8", "5ee8e0fa00871cbb09d9fdc0"], "$interval": 3600}`',
                    'type': 'string'
                }]
            }
        }
    }
})

add_documentation({
    'securityDefinitions': {
        "MyTokenAuth": {
            'type': 'oauth2',
            'flow': 'password',
            'tokenUrl': 'https://db.flexgrid-project.eu/oauth/token',
        }
    }
})
# iterate over all resources and items and add security
for resource, rd in app.config['DOMAIN'].items():
    if (rd.get('disable_documentation') or resource.endswith('_versions')):
        continue

    methods = rd['resource_methods']
    url = '/%s' % rd['url']
    for method in methods:
        add_documentation({
            'paths': {
                url: {
                    method.lower(): {
                        "security": [{
                            "MyTokenAuth": []
                        }]
                    }
                }
            }
        })

    methods = rd['item_methods']
    item_id = '%sId' % rd['item_title'].lower()
    url = '/%s/{%s}' % (rd['url'], item_id)
    for method in methods:
        add_documentation({
            'paths': {
                url: {
                    method.lower(): {
                        "security": [{
                            "MyTokenAuth": []
                        }]
                    }
                }
            }
        })

if __name__ == '__main__':
    app.run()
