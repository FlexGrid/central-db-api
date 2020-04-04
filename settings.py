import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

schema = {
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'firstname': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 10,
    },
    'lastname': {
        'type': 'string',
        'minlength': 1,
        'maxlength': 15,
        'required': True,
        # talk about hard constraints! For the purpose of the demo
        # 'lastname' is an API entry-point, so we need it to be unique.
        'unique': True,
    },
    # 'role' is a list, and can only contain values from 'allowed'.
    'role': {
        'type': 'list',
        'allowed': ["author", "contributor", "copy"],
    },
    # An embedded 'strongly-typed' dictionary.
    'location': {
        'type': 'dict',
        'schema': {
            'address': {'type': 'string'},
            'city': {'type': 'string'}
        },
    },
    'born': {
        'type': 'datetime',
    },
}

people = {
    # 'title' tag used in item links. Defaults to the resource title minus
    # the final, plural 's' (works fine in most cases but not for 'people')
    'item_title': 'person',

    # by default the standard item entry point is defined as
    # '/people/<ObjectId>'. We leave it untouched, and we also enable an
    # additional read-only entry point. This way consumers can also perform
    # GET requests at '/people/<lastname>'.
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'lastname'
    },

    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    # most global settings can be overridden at resource level
    'resource_methods': ['GET', 'POST'],

    'schema': schema
}

DOMAIN = {'people': people}

# Let's just use the local mongod instance. Edit as needed.

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
SENTINEL_MONGO_HOST = 'localhost'
MONGO_HOST = 'localhost'
SENTINEL_MONGO_PORT = 27017
MONGO_PORT = 27017

# Skip this block if your db has no auth. But it really should.
SENTINEL_MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
SENTINEL_MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# Name of the database on which the user can be authenticated,
# needed if --auth mode is enabled.
SENTINEL_MONGO_AUTH_SOURCE = 'admin'
MONGO_AUTH_SOURCE = 'admin'

SENTINEL_MONGO_DBNAME = 'apiusers'
MONGO_DBNAME = 'apitest'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']


# Default prefix for OAuth endpoints. Defaults to /oauth. Prepends both token and management urls.
#SENTINEL_ROUTE_PREFIX = '/oauth'

# Url for token creation endpoint. Set to False to disable this feature. Defaults to /token, so the complete url is /oauth/token.
#SENTINEL_TOKEN_URL = '/token'

# Url for management endpoint. Set to False to disable this feature. Defaults to /management, so the complete url is /oauth/management.
#SENTINEL_MANAGEMENT_URL = '/management'

# Url for the redis server. Defaults to redis://localhost:6379/0.
SENTINEL_REDIS_URL = os.getenv("REDIS_URL")

# Mongo database name. Defaults to oauth.
#SENTINEL_MONGO_DBNAME = 'oauth'

# Username needed to access the management page.
SENTINEL_MANAGEMENT_USERNAME = os.getenv("SENTINEL_MANAGEMENT_USERNAME")

# Password needed to access the management page.
SENTINEL_MANAGEMENT_PASSWORD = os.getenv("SENTINEL_MANAGEMENT_PASSWORD")

# The error page when there is an error, default value is /oauth/errors.
#OAUTH2_PROVIDER_ERROR_URI = '/oauth/errors'

# Default Bearer token expires time, default is 3600.
#OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 3600

# You can also configure the error page uri with an endpoint name.
#OAUTH2_PROVIDER_ERROR_ENDPOINT =
