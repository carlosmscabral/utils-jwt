from jwks_utils import generate_and_upload_jwks
from jwt_generator import generate_jwt
from utils.config import load_config
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate JWKS and/or JWT.")
    parser.add_argument(
        "--action",
        choices=["all", "jwt_only"],
        default="all",
        help="What to generate: 'all' (JWKS and JWT), 'jwt_only' (only JWT).",
    )

    args = parser.parse_args()
    config = load_config()

    # JWKS Upload (if requested)
    if args.action == "all":
        bucket_name = config.get("BUCKET_NAME")
        if bucket_name:
            jwks_local_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "config"
            )
            public_jwks_url = generate_and_upload_jwks(
                bucket_name, local_output_dir=jwks_local_dir
            )

            if public_jwks_url:
                print(f"Public JWKS URL: {public_jwks_url}")
        else:
            print("Skipping JWKS upload: BUCKET_NAME not configured.")

    # JWT Generation
    try:
        jwt_token = generate_jwt()
        print(f"Generated JWT: {jwt_token}")
    except Exception as e:
        print(f"Error generating JWT: {e}")