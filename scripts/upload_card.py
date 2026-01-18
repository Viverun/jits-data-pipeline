
import os
from huggingface_hub import HfApi

REPO_ID = "Viverun/jits-data-pipeline"
FILE_PATH = "DATASET_CARD.md"
PATH_IN_REPO = "README.md"

def upload_card():
    api = HfApi()
    print(f"Uploading {FILE_PATH} to {REPO_ID} as README.md...")
    try:
        api.upload_file(
            path_or_fileobj=FILE_PATH,
            path_in_repo=PATH_IN_REPO,
            repo_id=REPO_ID,
            repo_type="dataset",
            commit_message="Docs: Add community feedback note"
        )
        print("Upload successful!")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    upload_card()
