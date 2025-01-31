from google.cloud import storage
from google.auth import default as google_auth_default
import json
import uuid
import os
from utils.config import load_config
from utils.key_management import load_rsa_private_key, load_rsa_public_key, create_jwks

def generate_and_upload_jwks(bucket_name, jwks_file_name="jwks.json",
                             service_account_key_path=None, algorithm="RS256", local_output_dir="."):
    """
    Generates a JWKS from an RSA key pair, uploads it to a GCS bucket, and saves it locally.

    Args:
        bucket_name (str): Name of the GCS bucket.
        jwks_file_name (str): Name of the file in the bucket (default: "jwks.json").
        service_account_key_path (str, optional): Path to the service account JSON key file.
        algorithm (str): The signing algorithm (e.g., "RS256").
        local_output_dir (str): Local directory to save the jwks.json file.

    Returns:
        str: The public URL of the uploaded JWKS file, or None if an error occurred.
    """
    config = load_config()
    private_key_path = config.get("PRIVATE_KEY_FILE")

    if not private_key_path:
        raise ValueError("PRIVATE_KEY_FILE not found in the configuration.")

    # Generate a key ID
    key_id = config.get("KEY_ID")

    if not key_id:
        raise ValueError("KEY_ID not found in the configuration.")

    # Load keys
    private_key = load_rsa_private_key(private_key_path)
    public_key_path = private_key_path.replace("private", "public")
    public_key = load_rsa_public_key(public_key_path)

    # Create JWKS
    jwks = create_jwks(public_key, algorithm, key_id)
    jwks_json = json.dumps(jwks, indent=2)

    # Save JWKS locally
    local_jwks_path = os.path.join(local_output_dir, jwks_file_name)
    try:
        with open(local_jwks_path, "w") as f:
            f.write(jwks_json)
        print(f"JWKS saved locally to: {local_jwks_path}")
    except Exception as e:
        print(f"Error saving JWKS locally: {e}")

    # Try to use ADC first for GCS upload
    try:
        credentials, project = google_auth_default()
        storage_client = storage.Client(credentials=credentials, project=project)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(jwks_file_name)

        blob.upload_from_string(jwks_json, content_type="application/json")

        # Construct the public URL directly
        public_url = f"https://storage.googleapis.com/{bucket_name}/{jwks_file_name}"

        print(f"JWKS uploaded to: {public_url} (using ADC)")
        return public_url

    except Exception as e:
        print(f"Error uploading to GCS using ADC: {e}")

        # Fallback to service account key if provided
        if service_account_key_path is None:
            service_account_key_path = config.get("SERVICE_ACCOUNT_KEY_FILE")

        if service_account_key_path:
            try:
                storage_client = storage.Client.from_service_account_json(service_account_key_path)
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(jwks_file_name)

                blob.upload_from_string(jwks_json, content_type="application/json")

                # Construct the public URL directly
                public_url = f"https://storage.googleapis.com/{bucket_name}/{jwks_file_name}"

                print(f"JWKS uploaded to: {public_url} (using service account)")
                return public_url

            except Exception as e:
                print(f"Error uploading to GCS using service account: {e}")
                return None
        else:
            print("No service account key provided and ADC failed.")
            return None