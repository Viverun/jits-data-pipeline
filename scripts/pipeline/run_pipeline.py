import os
import subprocess
import sys
import argparse

def run_step(script_path):
    print(f"\n🚀 Running: {script_path}...")
    try:
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {script_path}:")
        print(e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="JITS Data Pipeline Runner")
    parser.add_argument("--start", type=int, default=1, help="Step to start from (1-7)")
    args = parser.parse_args()

    # Define the sequence of scripts
    pipeline_steps = [
        "scripts/pipeline/step01_ingest.py",
        "scripts/pipeline/step02_extract_metadata.py",
        "scripts/pipeline/step03_classify.py",
        "scripts/pipeline/step04_transitions.py",
        "scripts/pipeline/step05_issues.py",
        "scripts/pipeline/step06_citations.py",
        "scripts/pipeline/step07_similarity_signals.py",
        "scripts/pipeline/step07b_similarity_clusters.py"
    ]

    print("🏗️ Starting JITS Pipeline Execution")
    
    for i in range(args.start - 1, len(pipeline_steps)):
        step_script = pipeline_steps[i]
        if not os.path.exists(step_script):
            print(f"⚠️ Script not found: {step_script}")
            continue
            
        success = run_step(step_script)
        if not success:
            print(f"\n🛑 Pipeline halted at step {i+1}")
            sys.exit(1)

    print("\n✅ JITS Pipeline completed successfully!")

if __name__ == "__main__":
    main()
