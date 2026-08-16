"""Publish DATASET_CARD.md to the Hugging Face dataset as its README.

Card-only upload. Use this when the documentation changed but the corpus did
not; `upload_jsonl.py` is the one that republishes `train.jsonl` alongside it.
"""

import argparse
import os
import sys

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError

# Same default as upload_jsonl.py. This previously pointed at
# `Viverun/jits-data-pipeline`, which is the GitHub repo name, not the dataset
# published on the Hub - the upload either 404'd or created a stray repo.
REPO_ID = os.environ.get("HF_DATASET_REPO_ID", "Viverun/jits-legal-dataset")
FILE_PATH = "DATASET_CARD.md"
PATH_IN_REPO = "README.md"
PLACEHOLDER_TOKENS = {"your_token_here", "hf_your_token_here"}


def get_api():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not token:
        print("Upload failed: HF_TOKEN or HUGGINGFACE_HUB_TOKEN is not set.")
        print("Set a real Hugging Face write token before running this script.")
        sys.exit(1)

    if token.strip() in PLACEHOLDER_TOKENS:
        print("Upload failed: HF_TOKEN is still set to a placeholder value.")
        print("Replace `your_token_here` with a real Hugging Face write token.")
        sys.exit(1)

    return HfApi(token=token)


def upload_card(commit_message: str):
    api = get_api()
    print(f"Uploading {FILE_PATH} to {REPO_ID} as {PATH_IN_REPO}...")
    try:
        api.upload_file(
            path_or_fileobj=FILE_PATH,
            path_in_repo=PATH_IN_REPO,
            repo_id=REPO_ID,
            repo_type="dataset",
            commit_message=commit_message,
        )
        print("Upload successful!")
    except HfHubHTTPError as e:
        status_code = getattr(e.response, "status_code", None)
        if status_code == 401:
            print("Upload failed: authentication was rejected by Hugging Face (401).")
            print("Use a real write-scoped token, not a placeholder or expired token.")
        elif status_code == 403:
            print("Upload failed: token is valid but cannot write to this dataset (403).")
        elif status_code == 404:
            print(f"Upload failed: dataset repo `{REPO_ID}` was not found.")
        else:
            print(f"Upload failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Upload failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-m",
        "--message",
        default="Docs: sync dataset card with pipeline repository",
        help="Commit message for the Hugging Face commit.",
    )
    args = parser.parse_args()
    upload_card(args.message)


if __name__ == "__main__":
    main()
