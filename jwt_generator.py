from jose import jwt
import datetime
from utils.config import load_config
from utils.key_management import load_rsa_private_key
from cryptography.hazmat.primitives import serialization

def generate_jwt(algorithm="RS256"):
    """Generates a JWT using the configuration."""

    config = load_config()
    private_key_path = config.get("PRIVATE_KEY_FILE")
    key_id = config.get("KEY_ID")

    if not private_key_path:
        raise ValueError("PRIVATE_KEY_FILE not found in the configuration.")

    if not key_id:
        raise ValueError("KEY_ID not found in the configuration.")

    private_key = load_rsa_private_key(private_key_path)

    # Convert private key to PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Prepare JWT claims
    now = datetime.datetime.utcnow()
    expiry_seconds = int(config.get("EXPIRY_SECONDS", 300))

    claims = {
        "iss": config.get("ISS"),
        "sub": config.get("SUB"),
        "aud": config.get("AUD"),
        "iat": now,
        "exp": now + datetime.timedelta(seconds=expiry_seconds)
    }

    # Add custom claims
    for key, value in config.items():
        if key.startswith("CUSTOM_CLAIM_"):
            claim_name = key.replace("CUSTOM_CLAIM_", "")
            claims[claim_name] = value

    # Sign and encode the JWT
    encoded_jwt = jwt.encode(
        claims,
        private_key_pem,  # Pass the PEM-formatted key
        algorithm=algorithm,
        headers={"kid": key_id}  # Include kid in the header
    )

    return encoded_jwt