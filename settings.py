import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(verbose=True)
from bson import ObjectId

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
            'address': {
                'type': 'string'
            },
            'city': {
                'type': 'string'
            }
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

dp_schema = {
    'time_stamp': {
        'type': 'ISODate',
    },
    '_id': {
        'type': 'string',
    },
    'prosumer_id': {
        'type': 'number',
    },
    'acpower_kw': {
        'type': 'number',
    },
    'acpower_w': {
        'type': 'number',
    },
    'acpower2_kw': {
        'type': 'number',
    },
    'acpower2_w': {
        'type': 'number',
    },
    'grid_feed_in_kw': {
        'type': 'number',
    },
    'grid_feed_in_w': {
        'type': 'number',
    },
    'grid_consumption_kw': {
        'type': 'number',
    },
    'grid_consumption_w': {
        'type': 'number',
    },
    'acvoltage_phase_l1_v': {
        'type': 'number',
    },
    'acvoltage_phase_l12_v': {
        'type': 'number',
    },
    'acvoltage_phase_l2_v': {
        'type': 'number',
    },
    'acvoltage_phase2_l2_v': {
        'type': 'number',
    },
    'acvoltage_phase_l22_v': {
        'type': 'number',
    },
    'acvoltage_phase_l32_v': {
        'type': 'number',
    },
    'acvoltage_phase_l3_v': {
        'type': 'number',
    },
    'acgrid_frequency_hz': {
        'type': 'number',
    },
    'acgrid_frequency2_hz': {
        'type': 'number',
    },
    'dcpower_input_a_kw': {
        'type': 'number',
    },
    'dcpower_input_a_w': {
        'type': 'number',
    },
    'dcpower_input_b_kw': {
        'type': 'number',
    },
    'dcpower_input_b_w': {
        'type': 'number',
    },
    'dcvoltage_input_a_v': {
        'type': 'number',
    },
    'dcvoltage_input_b_v': {
        'type': 'number',
    },
    'dccurrent_input_a_a': {
        'type': 'number',
    },
    'dccurrent_input_b_a': {
        'type': 'number',
    },
    'insulation_resistance': {
        'type': 'number',
    },
    'insulation_resistance2': {
        'type': 'number',
    },
    'battery_charge_kw': {
        'type': 'number',
    },
    'battery_charge_w': {
        'type': 'number',
    },
    'battery_discharge_kw': {
        'type': 'number',
    },
    'battery_discharge_w': {
        'type': 'number',
    },
    'accurrent_phase_l1_a': {
        'type': 'number',
    },
    'accurrent_phase_l2_a': {
        'type': 'number',
    },
    'accurrent_phase_l3_a': {
        'type': 'number',
    },
    'battery_charging_w': {
        'type': 'number',
    },
    'battery_discharging_w': {
        'type': 'number',
    },
    'soc': {
        'type': 'number',
    }
}

data_points = {
    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'schema': dp_schema,
    'aggregation': {
        'pipeline': [{
            "$match": {
                "_updated": {
                    "$gte": "$upd"
                }
            }
        }, {
            "$group": {
                "_id": '$Hashtag',
                "count": {
                    "$sum": 1
                }
            }
        }, {
            "$sort": {
                "count": -1
            }
        }, {
            "$limit": 10
        }]
    }
}

data_points_aggr = {
    'datasource': {
        'source': 'data_points',
        'query_objectid_as_string': True,
        'aggregation': {
            'pipeline': [
                {
                    "$match": {
                        "$expr": {
                            "$and": [{
                                "$gte": [
                                    {
                                        "$toLong": "$time_stamp"
                                    },
                                    {
                                        "$subtract": [
                                            {
                                                "$toLong": "$start",
                                            },
                                            {
                                                "$mod": [
                                                    {
                                                        "$subtract": [
                                                            {
                                                                "$toLong":
                                                                "$start",
                                                            },
                                                            1,
                                                        ],
                                                    },
                                                    {
                                                        "$multiply":
                                                        [1000, "$interval"]
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                ]
                            }, {
                                "$lte": [
                                    {
                                        "$toLong": "$time_stamp"
                                    },
                                    {
                                        "$subtract": [
                                            {
                                                "$toLong": "$end",
                                            },
                                            {
                                                "$mod": [
                                                    {
                                                        "$add": [
                                                            {
                                                                "$toLong":
                                                                "$end",
                                                            },
                                                            0,
                                                        ],
                                                    },
                                                    {
                                                        "$multiply":
                                                        [1000, "$interval"]
                                                    },
                                                ],
                                            },
                                        ],
                                    },
                                ]
                            }],
                        },
                        "prosumer_id": {
                            "$in": "$prosumer"
                        }
                    },
                },
                {
                    "$group": {
                        "_id": {
                            "prosumer_id": "$prosumer_id",
                            "date": {
                                "$toDate": {
                                    "$add": [{
                                        "$subtract": [
                                            {
                                                "$toLong": "$time_stamp"
                                            },
                                            {
                                                "$mod": [
                                                    {
                                                        "$subtract": [{
                                                            "$toLong":
                                                            "$time_stamp"
                                                        }, 1]
                                                    },
                                                    {
                                                        "$multiply":
                                                        [1000, "$interval"]
                                                    },
                                                ],
                                            },
                                        ],
                                    }, {
                                        "$subtract": [{
                                            "$multiply": [1000, "$interval"]
                                        }, 1]
                                    }],
                                },
                            },
                        },
                        "consumption": {
                            "$avg": "$grid_consumption_w"
                        },
                    },
                },
                {
                    "$sort": {
                        "_id.date": 1
                    }
                },
            ]
        }
    },
}

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

DOMAIN = {'data_points': data_points, 'data_points_aggr': data_points_aggr}

# Let's just use the local mongod instance. Edit as needed.

# Please note that MONGO_HOST and MONGO_PORT could very well be left
# out as they already default to a bare bones local 'mongod' instance.
# SENTINEL_MONGO_HOST = 'db.flexgrid-project.eu'
# MONGO_HOST = 'db.flexgrid-project.eu'
# SENTINEL_MONGO_PORT = 27017
# MONGO_PORT = 27017

# Skip this block if your db has no auth. But it really should.
# SENTINEL_MONGO_USERNAME = os.getenv("SENTINEL_MONGO_USERNAME")
# MONGO_USERNAME = os.getenv("MONGO_USERNAME")
# SENTINEL_MONGO_PASSWORD = os.getenv("SENTINEL_MONGO_PASSWORD")
# MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
# Name of the database on which the user can be authenticated,
# needed if --auth mode is enabled.
# SENTINEL_MONGO_AUTH_SOURCE = 'admin'
# MONGO_AUTH_SOURCE = 'flexgrid_main'

# SENTINEL_MONGO_DBNAME = 'apiusers'
# MONGO_DBNAME = 'flexgrid_main'

# MONGO_URI = f'mongodb://{os.getenv("MONGO_USERNAME")}:{os.getenv("MONGO_PASSWORD")}@db.flexgrid-project.eu/flexgrid_main?ssl=true&ssl_cert_reqs=CERT_NONE&authSource=flexgrid_main'
# SENTINEL_MONGO_URI = f'mongodb://{os.getenv("SENTINEL_MONGO_USERNAME")}:{os.getenv("SENTINEL_MONGO_PASSWORD")}@db.flexgrid-project.eu/apiusers?ssl=true&ssl_cert_reqs=CERT_NONE&authSource=admin'

MONGO_URI = f'mongodb://{os.getenv("MONGO_USERNAME")}:{os.getenv("MONGO_PASSWORD")}@db.flexgrid-project.eu/flexgrid_main?ssl=true&authSource=flexgrid_main'
SENTINEL_MONGO_URI = f'mongodb://{os.getenv("SENTINEL_MONGO_USERNAME")}:{os.getenv("SENTINEL_MONGO_PASSWORD")}@db.flexgrid-project.eu/apiusers?ssl=true&authSource=admin'

MONGODB_CONNECT = False
SENTINEL_MONGODB_CONNECT = False

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
