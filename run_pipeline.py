import subprocess
import sys
from pathlib import Path

# Define the scripts to run in order
SCRIPTS_TO_RUN = [
    "modeling/01_prepare_data.py",
    "modeling/02_run_modeling.py",
    "modeling/03_tune_model.py",
    "modeling/04_finalize_evaluation.py",
]

def run_script(script_path):
    """Runs a Python script and checks for errors."""
    print(f"\n{'='*20} RUNNING: {script_path} {'='*20}\n")
    try:
        # Use sys.executable to ensure we're using the same Python interpreter from the uv venv
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False, # Set to True to capture and print output on error
            text=True
        )
        print(f"--- COMPLETED: {script_path} ---")
    except subprocess.CalledProcessError as e:
        print(f"--- FAILED: {script_path} ---", file=sys.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout, file=sys.stderr)
        if e.stderr:
            print("STDERR:", e.stderr, file=sys.stderr)
        sys.exit(1) # Exit the whole pipeline if one script fails

def main():
    """Main function to orchestrate the entire ML pipeline."""
    print("Starting the end-to-end World Bank GDP Shock prediction pipeline.")
    
    # Ensure the script is run from the project root
    project_root = Path(__file__).parent
    if Path.cwd() != project_root:
        print(f"Please run this script from the project root directory: {project_root}")
        sys.exit(1)

    for script in SCRIPTS_TO_RUN:
        if not Path(script).exists():
            print(f"Error: Script not found at {script}", file=sys.stderr)
            sys.exit(1)
        run_script(script)

    print(f"\n{'='*20} PIPELINE FINISHED SUCCESSFULLY {'='*20}")
    print("To view the results, run: mlflow ui")

if __name__ == '__main__':
    main()