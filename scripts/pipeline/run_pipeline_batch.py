import os
import subprocess
import sys
import argparse
import shutil
from pathlib import Path
from multiprocessing import cpu_count

def run_step(script_path, extra_args=None):
    print(f"  🚀 Running: {script_path}...")
    cmd = [sys.executable, script_path]
    if extra_args:
        cmd.extend(extra_args)
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error in {script_path}:")
        print(e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="JITS Batch Pipeline Runner")
    parser.add_argument("--batch-size", type=int, default=50, help="Number of cases to process in one batch")
    parser.add_argument("--workers", type=int, default=max(1, cpu_count() - 1), help="Number of parallel workers")
    args = parser.parse_args()

    RAW_DIR = "raw/judgments/unclassified"
    BATCH_DIR = "raw/judgments/current_batch"
    
    # Pipeline steps
    pipeline_steps = [
        ("scripts/pipeline/step01_ingest_parallel.py", ["--input-dir", BATCH_DIR, "--workers", str(args.workers)]),
        ("scripts/pipeline/step02_extract_metadata.py", []),
        ("scripts/pipeline/step03_classify.py", []),
        ("scripts/pipeline/step04_transitions.py", []),
        ("scripts/pipeline/step05_issues.py", []),
        ("scripts/pipeline/step06_citations_enhanced.py", []),
        ("scripts/pipeline/step08_consolidate.py", []),
        ("scripts/pipeline/step07_similarity_signals_optimized.py", ["--workers", str(args.workers)]),
        ("scripts/pipeline/step07b_similarity_clusters.py", [])
    ]

    if not os.path.exists(RAW_DIR):
        print(f"❌ RAW_DIR not found: {RAW_DIR}")
        return

    all_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]
    if not all_files:
        print("✅ No pending files in raw/judgments/unclassified")
        return

    print(f"📦 Total pending files: {len(all_files)}")
    print(f"⚙️ Batch size: {args.batch_size}, Workers: {args.workers}")
    
    for i in range(0, len(all_files), args.batch_size):
        batch = all_files[i:i + args.batch_size]
        print(f"\n--- 🔄 Processing Batch {i//args.batch_size + 1} ({len(batch)} files) ---")
        
        if os.path.exists(BATCH_DIR):
            shutil.rmtree(BATCH_DIR)
        os.makedirs(BATCH_DIR)
        
        for f in batch:
            shutil.copy(os.path.join(RAW_DIR, f), os.path.join(BATCH_DIR, f))
            
        success = True
        for step_script, extra_args in pipeline_steps:
            if not run_step(step_script, extra_args):
                success = False
                break
        
        if success:
            print(f"✅ Batch {i//args.batch_size + 1} completed.")
            # Optional: Move processed files to a 'processed_raw' folder instead of deleting
            # for f in batch: os.remove(os.path.join(RAW_DIR, f))
        else:
            print(f"🛑 Batch {i//args.batch_size + 1} failed. Stopping.")
            break

    print("\n🏁 All batches processed.")

if __name__ == "__main__":
    main()
