# Using the API:

First create a client and a user using the GUI by visiting http://localhost:5000/oauth/management

Then use the client\_id, the username and password, to connect to the server
using the credentials you created, by replacing placeholders `CLIENT_ID`,
`USERNAME` and `PASSWORD`.

```bash
# Generating a Bearer Token using credentials
curl 'http://localhost:5000/oauth/token' \
     --form 'client_id=CLIENT_ID' \
     --form 'grant_type=password' \
     --form 'username=USERNAME' \
     --form 'password=PASSWORD'

# Generating a bearer token Using a retrieved refresh token
curl 'http://localhost:5000/oauth/token' \
     --form 'client_id=CLIENT_ID' \
     --form 'grant_type=refresh_token' \
     --form 'refresh_token=MLMMegAY29kxDydSq2NEGYQHqQPGyE'

# Accessing a protected resource using retrieved bearer token
curl 'http://localhost:5000/people?pretty' \
     --header 'Authorization: Bearer Q6ivNZLQ67cj3Z8VgAzUZ8y8YhqDiX'
```

# Eve-OAuth2

A [Eve-Demo][1] fork intended to demonstrate how you can protect API endpoints
by extending your [Eve][3] application with [Flask-Sentinel][3].

Flask-Sentinel extends the main Eve application by providing a token creation
endpoint at `/oauth/token` and a users and clients management endpoint at
`/oauth/management`.

In order to be granted access to regular API endpoints (`/people/` and
`/works/`) a client must first obtain a valid token by hitting the token
creation endpoint with valid client id, username and password. The returned
token will then be used for subsequent requests until it eventually times out.
For details on how to perform token and endpoint requests see
[Flask-Sentinel][3].

## Distributed Services
Besides extending your Eve instance with Flask-Sentinel you might also opt to
provide your auth service as a different, isolated application. This would be
a good choice if you are concerned about scalability and availability of your
services. Redis would then serve as a bridge between the applications, and
could itself reside on a different server, allowing for a totally distributed
and isolated network of (micro?) services.

## License
Eve-OAuth2 is a [Nicola Iarocci][5] and [Gestionali Amica][6] open source
project distributed under the [BSD license][7].

[1]: https://github.com/pyeve/eve-demo
[2]: http://python-eve.org
[3]: https://github.com/pyeve/flask-sentinel
[5]: http://nicolaiarocci.com
[6]: http://gestionaleamica.com
[7]: https://github.com/pyeve/eve-oauth2/blob/master/LICENSE
