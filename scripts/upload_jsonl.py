import argparse
import os
import sys

from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi
from huggingface_hub.errors import HfHubHTTPError
from normalize_dataset import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_FILE, export_jsonl, validate_release_quality

REPO_ID = os.environ.get("HF_DATASET_REPO_ID", "Viverun/jits-legal-dataset")
RELEASE_ASSETS = [
    ("train.jsonl", "train.jsonl"),
    ("DATASET_CARD.md", "README.md"),
    ("jits-legal-dataset.py", "jits-legal-dataset.py"),
    ("scripts/validate_hf_schema.py", "validate_hf_schema.py"),
]
PLACEHOLDER_TOKENS = {"your_token_here", "hf_your_token_here"}
COMMIT_MESSAGE = (
    "v1.14.1: HF-safe uniform structs - fix parquet DatasetGenerationError\n\n"
    "- statutory_transitions and extractions.transitions.details now emit a\n"
    "  canonical 10-field struct from all producers (fixes Couldn't cast\n"
    "  struct<...,requires_judicial_confirmation,context_snippet> error)\n"
    "- metadata.bench always list[str]; citations/landmarks details uniform structs\n"
    "- train.jsonl: 14037 rows re-exported from 14678-judgment corpus, validated\n"
    "  with scripts/validate_hf_schema.py\n"
    "- add jits-legal-dataset.py explicit HF Features script so parquet\n"
    "  conversion no longer depends on first-chunk type inference"
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


def prepare_release_assets(include_unknown_cases: bool, exclude_unknown_domain: bool):
    output_file = DEFAULT_OUTPUT_FILE
    count, skipped = export_jsonl(
        input_dir=Path(DEFAULT_INPUT_DIR),
        output_file=Path(output_file),
        exclude_unknown_cases=not include_unknown_cases,
        exclude_unknown_domain=exclude_unknown_domain,
    )
    print(f"Prepared {output_file} with {count} records.")
    if skipped:
        summary = ", ".join(f"{reason}={count}" for reason, count in sorted(skipped.items()))
        print(f"Skipped records: {summary}")
    validate_release_quality(output_file)
    print("Release gate passed: no unknown-year (0000) IDs found.")


def upload(include_unknown_cases: bool = False, exclude_unknown_domain: bool = False, skip_export: bool = False):
    if not skip_export:
        prepare_release_assets(include_unknown_cases, exclude_unknown_domain)
    else:
        validate_release_quality(DEFAULT_OUTPUT_FILE)
        print("Release gate passed on existing train.jsonl: no unknown-year (0000) IDs found.")

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


def main():
    parser = argparse.ArgumentParser(description="Upload the public dataset release to Hugging Face.")
    parser.add_argument(
        "--include-unknown-cases",
        action="store_true",
        help="Include UNKNOWN-court / IN-UNKNOWN-UNK records in the uploaded train.jsonl.",
    )
    parser.add_argument(
        "--exclude-unknown-domain",
        action="store_true",
        help="Exclude records whose classified domain is UNKNOWN from the uploaded train.jsonl.",
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Upload the existing train.jsonl as-is without regenerating it first.",
    )
    args = parser.parse_args()

    upload(
        include_unknown_cases=args.include_unknown_cases,
        exclude_unknown_domain=args.exclude_unknown_domain,
        skip_export=args.skip_export,
    )


if __name__ == "__main__":
    main()
