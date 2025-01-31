from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwk
import json

def load_rsa_private_key(private_key_path):
    """Loads an RSA private key from a PEM file.

    Args:
        private_key_path (str): Path to the private key file.

    Returns:
        cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey: The loaded private key.
    """
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def load_rsa_public_key(public_key_path):
    """Loads an RSA public key from a PEM file.

    Args:
        public_key_path (str): Path to the public key file.

    Returns:
        cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey: The loaded public key.
    """
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


def get_public_jwk(public_key, algorithm):
    """Creates a public JWK from an RSA public key.

    Args:
        public_key (rsa.RSAPublicKey): The RSA public key.
        algorithm (str): The algorithm used (e.g., "RS256").

    Returns:
        dict: The JWK representation of the public key.
    """
    return jwk.construct(public_key, algorithm=algorithm).to_dict()

def create_jwks(public_key, algorithm, key_id):
    """Creates a JWKS from an RSA public key.

    Args:
        public_key (rsa.RSAPublicKey): The RSA public key.
        algorithm (str): The algorithm used (e.g., "RS256").
        key_id (str): The key ID.

    Returns:
        dict: The JWKS representation.
    """
    public_jwk = get_public_jwk(public_key, algorithm)
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": key_id,  # Use the provided key_id
                "alg": algorithm,
                "use": "sig",
                "n": public_jwk['n'],
                "e": public_jwk['e'],
            }
        ]
    }