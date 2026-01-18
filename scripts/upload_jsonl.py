
import os
from huggingface_hub import HfApi

REPO_ID = "Viverun/jits-data-pipeline"
FILE_PATH = "train.jsonl"
PATH_IN_REPO = "train.jsonl" # Root of the dataset

def upload():
    api = HfApi()
    print(f"Uploading {FILE_PATH} to {REPO_ID}...")
    try:
        api.upload_file(
            path_or_fileobj=FILE_PATH,
            path_in_repo=PATH_IN_REPO,
            repo_id=REPO_ID,
            repo_type="dataset",
            commit_message="Fix: Upload normalized train.jsonl for HF Viewer support"
        )
        print("Upload successful!")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    upload()
