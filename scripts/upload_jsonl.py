
import os
import sys

from huggingface_hub import CommitOperationAdd, HfApi
from huggingface_hub.errors import HfHubHTTPError

REPO_ID = os.environ.get("HF_DATASET_REPO_ID", "Viverun/jits-legal-dataset")
RELEASE_ASSETS = [
    ("train.jsonl", "train.jsonl"),
    ("DATASET_CARD.md", "README.md"),
]
PLACEHOLDER_TOKENS = {"your_token_here", "hf_your_token_here"}
COMMIT_MESSAGE = (
    "v1.5: Court codes corrected, tribunal IDs added, metadata extraction tightened\n\n"
    "- 744 judgment IDs changed versus v1.4 (court codes and tribunal classification)\n"
    "- HIG/BLE/SUP legacy codes eliminated - all IDs now use canonical court codes\n"
    "- Tribunal records now correctly typed: IN-TR-CAT-* instead of IN-HC-BLE-*\n"
    "- Tighter line-based header parsing eliminates overmatched court strings\n"
    "- Court distribution: SC: 134, ALL: 116, DEL: 87, CAT: 9\n"
    "- Level distribution: HC: 685, SC: 134, TR: 11, UNKNOWN: 16\n"
    "- 23 refined clusters (was 25), 90,924 similarity edges\n"
    "- breaking: 744 judgment_ids changed from v1.4"
)


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

def upload():
    api = get_api()
    print(f"Uploading release assets to {REPO_ID}...")
    try:
        api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)
        operations = [
            CommitOperationAdd(path_in_repo=dest, path_or_fileobj=src)
            for src, dest in RELEASE_ASSETS
        ]
        api.create_commit(
            repo_id=REPO_ID,
            repo_type="dataset",
            operations=operations,
            commit_message=COMMIT_MESSAGE,
        )
        print("Upload successful!")
    except HfHubHTTPError as e:
        status_code = getattr(e.response, "status_code", None)
        if status_code == 401:
            print("Upload failed: authentication was rejected by Hugging Face (401).")
            print("Use a real write-scoped token, not a placeholder or expired token.")
        elif status_code == 403:
            print("Upload failed: token is valid but does not have permission to write to this dataset (403).")
        elif status_code == 404:
            print("Upload failed: dataset repo was not found and could not be created.")
            print(f"Check that you own or can create `{REPO_ID}`.")
        else:
            print(f"Upload failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Upload failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload()
