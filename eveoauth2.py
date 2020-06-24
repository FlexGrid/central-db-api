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

app = Eve(auth=BearerAuth)
ResourceOwnerPasswordCredentials(app)

@app.route('/endpoint')
@oauth.require_oauth()
def restricted_access():
    return "You made it through and accessed the protected resource!"

app.register_blueprint(swagger)
# required. See http://swagger.io/specification/#infoObject for details.
app.config['SWAGGER_INFO'] = {
    'title': 'My Supercool API',
    'version': '1.0',
    'description': 'an API description',
    'termsOfService': 'my terms of service',
    'contact': {
        'name': 'nicola',
        'url': 'http://nicolaiarocci.com'
    },
    'license': {
        'name': 'BSD',
        'url': 'https://github.com/pyeve/eve-swagger/blob/master/LICENSE',
    },
    'schemes': ['http', 'https'],
}


# optional. Add/Update elements in the documentation at run-time without deleting subtrees.
add_documentation({'paths': {'/status': {'get': {'parameters': [
    {
        'in': 'query',
        'name': 'foobar',
        'required': False,
        'description': 'special query parameter',
        'type': 'string'
    }]
}}}})

if __name__ == '__main__':
    app.run()
