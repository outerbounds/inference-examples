from metaflow import S3
import os 
import argparse
from typing import Dict, Any, Optional

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_s3_path', type=str, required=True)
    parser.add_argument('--download_dir', type=str, required=True)
    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--cloud_provider', type=str, required=True)
    parser.add_argument('--s3_root', type=str, required=True)
    return parser.parse_args()

def _get_coreweave_client_params() -> Dict[str, Any]:
    """Fetch CoreWeave credentials from the environment, or error out."""
    try:
        access_key = os.environ['COREWEAVE_ACCESS_KEY']
        secret_key = os.environ['COREWEAVE_SECRET_KEY']
    except KeyError as e:
        raise ValueError(f"{e.args[0]} is not set") from None

    return {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "endpoint_url": "https://cwobject.com",
        "config": {"s3": {"addressing_style": "virtual"}},
    }

def download_model(
    model_s3_root: str,
    model_s3_path: str,
    download_dir: str,
    model_name: str,
    *,
    cloud_provider: str = 'aws'
) -> None:
    """
    Download all objects under `model_s3_path` from an S3-compatible endpoint.
    
    If `coreweave=True`, will pull credentials from
    COREWEAVE_ACCESS_KEY and COREWEAVE_SECRET_KEY and use the CoreWeave endpoint.
    """
    # Prepare client params
    client_params: Optional[Dict[str, Any]] = None
    if cloud_provider == 'coreweave':
        client_params = _get_coreweave_client_params()

    # Ensure base download dir exists
    os.makedirs(download_dir, exist_ok=True)

    # Open S3 and list/download objects
    with S3(s3root=model_s3_root, client_params=client_params) as s3:
        objs = s3.get_recursive([model_s3_path])
        for obj in objs:
            print(f"Downloading {obj.key}…")
            local_path = os.path.join(download_dir, model_name, obj.key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(obj.blob)

if __name__ == '__main__':
    args = parse_args()

    try:
        download_model(args.s3_root, args.model_s3_path, args.download_dir, args.model_name, cloud_provider=args.cloud_provider)
    except Exception as e:
        print(f"Error downloading model: {e}")
        exit(1)