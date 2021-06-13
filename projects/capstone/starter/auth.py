import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from dotenv import load_dotenv
import os


AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
ALGORITHMS = os.environ.get("ALGORITHMS")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
CLIENT_ID = os.environ.get("CLIENT_ID")
CALLBACK_URL = os.environ.get("CALLBACK_URL")
ASSISTANT_TOKEN = os.environ.get("ASSISTANT_TOKEN")
DIRECTOR_TOKEN = os.environ.get("DIRECTOR_TOKEN")
PRODUCER_TOKEN = os.environ.get("PRODUCER_TOKEN")

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
get_token_auth_header() method
    Attempts to get the header from the request
        raises an AuthError if no header is present
    Attempts to split bearer and the token
        raises an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    # Get auth from header, raise error if not found
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            "code": "auth_header_not_found",
            "description": "Authorization header is not found"
        }, 401)

    # Splitt header to get bearer prefix and token
    parts = auth.split()
    bearer_prefix = parts[0]

    # Interrogate bearer prefix
    if not bearer_prefix:
        raise AuthError({
            "code": "invalid_header",
            "description": "Bearer prefix is not found"
        }, 401)
    elif bearer_prefix and len(parts) == 1:
        raise AuthError({
            "code": "invalid_header",
            "description": "Token is not found"
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            "code": "invalid_header",
            "description": "Authorization header is mal-formed"
        }, 401)

    token = parts[1]

    return token


'''
check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:movie', 'post:actor')
        payload: decoded jwt payload

    Raises an AuthError if permissions are not included in the payload
        !!NOTE check RBAC settings in Auth0
    Raises an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    # Make sure permissions are in the payload
    if "permissions" not in payload:
        raise AuthError({
            "code": "bad_request",
            "description": "Permissions not included in token"
        }, 400)

    # Make sure the right permission exists
    if permission not in payload["permissions"]:
        raise AuthError({
            "code": "forbidden",
            "description": "Permission not found"
        }, 403)

    return True


'''
verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    Auth0 token with key id (kid)
    Verifies the token using Auth0 /.well-known/jwks.json
    Decodes the payload from the token
    Validates the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


'''
requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:movie', 'post:actor')

    uses the get_token_auth_header method to get the token
    uses the verify_decode_jwt method to decode the jwt
    uses the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except ValueError as e:
                print(f'Error: {str(e)}')
                abort(401)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
