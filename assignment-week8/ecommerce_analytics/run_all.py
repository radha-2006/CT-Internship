
import subprocess
import sys

# Use the exact same Python interpreter that's running this script
# (fixes "python3 not found" on Windows, where only python.exe exists)
PYTHON = sys.executable

STEPS = [
    ("Generating raw data", [PYTHON, "01_data_generation.py"]),
    ("Cleaning data", [PYTHON, "02_data_cleaning.py"]),
    ("Loading into SQLite", [PYTHON, "03_load_to_sqlite.py"]),
    ("Running SQL analysis", [PYTHON, "07_run_sql_report.py"]),
    ("Running edge-case tests", [PYTHON, "06_test_edge_cases.py"]),
]

for title, cmd in STEPS:
    print(f"\n{'='*70}\n{title}\n{'='*70}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\nStep failed: {title}")
        sys.exit(1)

print("\nAll steps completed successfully.")
print("Try the interactive report tool next:  python 05_report_cli.py")
