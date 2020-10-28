# /server.py

from datetime import datetime
import time
import json
from six.moves.urllib.request import urlopen
from functools import wraps

from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin, CORS
from jose import jwt
import redis

AUTH0_DOMAIN = 'dev-0gh3h3gj.eu.auth0.com'
MY_DOMAIN = 'localhost:5000'
API_AUDIENCE = "https://dev-0gh3h3gj.eu.auth0.com/userinfo"
ALGORITHMS = ["RS256"]

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

r = redis.Redis(host='localhost', port=6379, db=0)


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


# /server.py

# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with"
                             " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """
    Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://" + AUTH0_DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                print("assa")
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                     "incorrect claims,"
                                     "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                     "Unable to parse authentication"
                                     " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)

    return decorated

# def requires_scope(required_scope):
#     """Determines if the required scope is present in the Access Token
#     Args:
#         required_scope (str): The scope required to access the resource
#     """
#     token = get_token_auth_header()
#     unverified_claims = jwt.get_unverified_claims(token)
#     if unverified_claims.get("scope"):
#         token_scopes = unverified_claims["scope"].split()
#         for token_scope in token_scopes:
#             if token_scope == required_scope:
#                 return True
#     return False


def get_context():
    ctx = _request_ctx_stack.top
    if ctx is not None:
        return ctx


@app.route("/api/redis-data")
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def redis_data():
    usr = get_context().current_user
    # getting timestamp of last visit
    if r.exists(usr["sub"]):
        last_visit_timestamp = float((r.get(usr['sub'])).decode("utf-8"))

        response = jsonify(
            f"Your user sub: {usr['sub']}, "
            f"previous visit was at: {datetime.fromtimestamp(last_visit_timestamp)}"
        )
    else:
        response = jsonify(f"It is your first visit")

    r.set(usr["sub"], datetime.now().timestamp())

    # to check how waiting the data process works
    time.sleep(1)
    return response


if __name__ == '__main__':
    app.run()
