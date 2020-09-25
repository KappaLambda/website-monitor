import json

from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from six.moves.urllib import request

from website_monitor.settings.base import *  # noqa: F401,F403

if AUTH0_DOMAIN:  # noqa: F405
    jsonurl = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'  # noqa: F405
    response = request.urlopen(jsonurl)
    jwks = json.loads(response.read().decode('utf-8'))
    cert = (
        '-----BEGIN CERTIFICATE-----\n'
        f'{jwks["keys"][0]["x5c"][0]}'
        '\n-----END CERTIFICATE-----'
    )
    certificate = load_pem_x509_certificate(
        cert.encode('utf-8'),
        default_backend(),
    )
    PUBLIC_KEY = certificate.public_key()
    JWT_AUTH['JWT_PUBLIC_KEY'] = PUBLIC_KEY  # noqa: F405
