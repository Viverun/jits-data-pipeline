import os
import json
import logging
import re
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

class BaseStep:
    def __init__(self, input_dir, output_dir, remove_processed=False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.remove_processed = remove_processed
        os.makedirs(self.output_dir, exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def run(self):
        if not self.input_dir.exists():
            self.logger.error(f"Input directory not found: {self.input_dir}")
            print(f"[ERROR] Input directory not found: {self.input_dir}")
            return

        files = list(self.input_dir.glob("*.json"))
        if not files:
            self.logger.warning(f"No .json files found in {self.input_dir}")
            print(f"[WARNING] No .json files found in {self.input_dir}")
            return

        print(f"Processing {len(files)} files from {self.input_dir} to {self.output_dir}...")

        failed_files = []
        successful = 0
        renamed_count = 0
        processed_files = []  # Track files to delete

        for file in tqdm(files):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                processed_data = self.process_item(data)

                if processed_data:
                    # ✅ Check if judgment_id changed (file renaming needed)
                    old_id = file.stem  # Filename without extension
                    new_id = processed_data.get("judgment_id", old_id)

                    if old_id != new_id:
                        # ID was regenerated - rename file to match
                        out_path = self._build_out_path(new_id, file.name)
                        if out_path.stem != new_id:
                            self.logger.info(f"Path sanitized: {new_id} → {out_path.relative_to(self.output_dir)}")
                        self.logger.info(f"Renaming: {old_id} → {new_id}")
                        renamed_count += 1
                    else:
                        # ID unchanged - keep same filename
                        out_path = self._build_out_path(file.stem, file.name)

                    # Create parent directories if they don't exist (for hierarchical IDs)
                    out_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(out_path, "w", encoding="utf-8") as out:
                        json.dump(processed_data, out, indent=2, ensure_ascii=False)
                    successful += 1
                    processed_files.append(file)  # Track for deletion
                else:
                    failed_files.append((file.name, "process_item returned None"))
                    self.logger.warning(f"Skipped {file.name}: process_item returned None")
            except Exception as e:
                failed_files.append((file.name, str(e)))
                self.logger.error(f"Error processing {file.name}: {str(e)}", exc_info=True)
                print(f"[ERROR] Error processing {file.name}: {str(e)}")

        # Remove processed files if requested
        if self.remove_processed and processed_files:
            self._remove_files(processed_files)

        # Report summary
        print(f"\n[OK] Successfully processed: {successful}/{len(files)}")
        if renamed_count > 0:
            print(f"[RENAMED] Files renamed (ID regenerated): {renamed_count}")
        if failed_files:
            print(f"[FAILED] Failed: {len(failed_files)}/{len(files)}")
            self._write_error_log(failed_files)

    def _write_error_log(self, failed_files):
        """Write error log to output directory."""
        error_log_path = self.output_dir / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "step": self.__class__.__name__,
            "total_failures": len(failed_files),
            "failures": [
                {"file": filename, "error": error}
                for filename, error in failed_files
            ]
        }
        with open(error_log_path, "w", encoding="utf-8") as f:
            json.dump(error_data, f, indent=2, ensure_ascii=False)
        print(f"📝 Error log written to: {error_log_path}")

    def _remove_files(self, files):
        """Remove processed files from the input directory."""
        removed_count = 0
        failed_removals = []

        for file in files:
            try:
                file.unlink()
                removed_count += 1
                self.logger.debug(f"Removed: {file.name}")
            except Exception as e:
                failed_removals.append((file.name, str(e)))
                self.logger.error(f"Failed to remove {file.name}: {str(e)}")

        print(f"🗑️  Removed {removed_count}/{len(files)} processed files from input directory")
        if failed_removals:
            print(f"⚠️  Failed to remove {len(failed_removals)} file(s)")
            for filename, error in failed_removals:
                print(f"   - {filename}: {error}")

    def process_item(self, data):
        raise NotImplementedError("Subclasses must implement process_item")

    def _build_out_path(self, judgment_id: str, original_filename: str) -> Path:
        """Return a filesystem-safe path for a judgment ID while keeping directory semantics."""
        parts = [self._sanitize_segment(p) for p in re.split(r"[\\/]+", judgment_id) if p]
        if not parts:
            parts = [self._sanitize_segment(Path(original_filename).stem)]

        # Last part becomes the filename; preceding parts become directories
        filename = f"{parts[-1]}.json"
        subdirs = parts[:-1]
        return self.output_dir.joinpath(*subdirs, filename)

    def _sanitize_segment(self, segment: str) -> str:
        """Strip unsafe characters and normalize whitespace for safe filesystem usage."""
        cleaned = segment.strip()
        cleaned = re.sub(r'[<>:"|?*]', "_", cleaned)
        cleaned = re.sub(r"\s+", "-", cleaned)
        return cleaned or "unnamed"

