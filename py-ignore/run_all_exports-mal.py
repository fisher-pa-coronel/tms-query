import os
import subprocess
from pathlib import Path

# ======================
# Configuration Settings
# ======================
SCRIPT_FOLDER = "exports"           # Folder containing scripts (can be "." for same dir)
TARGET_PATTERN = "-mal"             # Change this to "-dev", "-test", etc.
CASE_SENSITIVE = False              # Set to False for case-insensitive matching

# Optional: directories and files to ignore
ignore_dirs = {"__pycache__", "ignore", ".git"}
ignore_files = {"temp.py", "debug.py"}

# ======================
# Determine folder path
# ======================
script_dir = Path(__file__).parent
folder_path = script_dir / SCRIPT_FOLDER

# Convert to absolute path for clarity
folder_path = folder_path.resolve()

if not folder_path.exists():
    print(f"❌ Folder '{folder_path}' does not exist.")
else:
    print(f"🔍 Looking for Python scripts in: {folder_path}")
    print(f"🎯 Matching pattern: '{TARGET_PATTERN}'")
    if not CASE_SENSITIVE:
        print("📝 Case-insensitive mode")

    matched_any = False

    for root, dirs, files in os.walk(folder_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in files:
            # Skip ignored files
            if filename in ignore_files:
                continue

            # Check file extension
            if not filename.endswith(".py"):
                continue

            # Apply pattern matching (case-sensitive or not)
            search_name = filename if CASE_SENSITIVE else filename.lower()
            target_str = TARGET_PATTERN if CASE_SENSITIVE else TARGET_PATTERN.lower()

            if target_str in search_name:
                matched_any = True
                file_path = Path(root) / filename
                print(f"\n✅ Found: {filename}")
                print(f"🚀 Running: {file_path}")
                try:
                    result = subprocess.run(
                        ["python", str(file_path)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        print(result.stdout)
                    else:
                        print("❌ Script output (error):")
                        print(result.stderr)
                except subprocess.TimeoutExpired:
                    print("⏰ Error: Script timed out!")
                except Exception as e:
                    print(f"❌ Failed to run {file_path}: {e}")

    if not matched_any:
        print(f"\n📭 No Python files found containing '{TARGET_PATTERN}' in their name.")