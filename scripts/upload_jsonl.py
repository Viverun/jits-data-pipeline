
import os
import sys

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError

REPO_ID = os.environ.get("HF_DATASET_REPO_ID", "Viverun/jits-legal-dataset")
FILE_PATH = "train.jsonl"
PATH_IN_REPO = "train.jsonl"  # Root of the dataset
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

def upload():
    api = get_api()
    print(f"Uploading {FILE_PATH} to {REPO_ID}...")
    try:
        api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)
        api.upload_file(
            path_or_fileobj=FILE_PATH,
            path_in_repo=PATH_IN_REPO,
            repo_id=REPO_ID,
            repo_type="dataset",
            commit_message=(
                "v1.4: Fix classification, transition temporal guardrails, and similarity signals\n\n"
                "- domain distribution corrected (criminal: 356, service: 191, mixed: 179, civil: 119)\n"
                "- 0 spurious BNS mappings on pre-July-2024 judgments\n"
                "- 307/307 IPC-bearing cases now have section signals in similarity graph\n"
                "- 90,924 similarity edges, 25 refined clusters\n"
                "- breaking: 397 judgment_ids changed due to domain correction"
            )
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
