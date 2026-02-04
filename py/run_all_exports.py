import os
import subprocess
from pathlib import Path

# ======================
# Configuration Settings
# ======================
SCRIPT_FOLDER = "exports"           # Folder containing scripts
TARGET_PATTERN = "-qav"             # Priority pattern (runs first)
CASE_SENSITIVE = False              # Case-insensitive matching

# Optional: directories and files to ignore
ignore_dirs = {"__pycache__", "ignore", ".git"}
ignore_files = {"temp.py", "debug.py"}

# ======================
# Determine folder path
# ======================
script_dir = Path(__file__).parent
folder_path = script_dir / SCRIPT_FOLDER
folder_path = folder_path.resolve()

# Lists to store scripts
priority_scripts = []   # Those with TARGET_PATTERN
regular_scripts = []    # Others

if not folder_path.exists():
    print(f"❌ Folder '{folder_path}' does not exist.")
    exit()

print(f"🔍 Scanning for Python scripts in: {folder_path}")
print(f"🎯 Priority pattern: '{TARGET_PATTERN}' (case-sensitive: {CASE_SENSITIVE})")

# Phase 1: Scan and classify scripts
for root, dirs, files in os.walk(folder_path):
    # Skip ignored directories
    dirs[:] = [d for d in dirs if d not in ignore_dirs]

    for filename in files:
        if filename in ignore_files:
            continue
        if not filename.endswith(".py"):
            continue

        file_path = Path(root) / filename

        # Check for priority pattern
        search_name = filename if CASE_SENSITIVE else filename.lower()
        target_str = TARGET_PATTERN if CASE_SENSITIVE else TARGET_PATTERN.lower()

        if target_str in search_name:
            priority_scripts.append(file_path)
        else:
            regular_scripts.append(file_path)

# Sort both lists for consistent order
priority_scripts.sort()
regular_scripts.sort()

# Phase 2: Run priority scripts first
print(f"\n⚡ Running {len(priority_scripts)} priority script(s) (matching '{TARGET_PATTERN}')...\n")
for file_path in priority_scripts:
    print(f"✅ Priority: {file_path.name}")
    print(f"🚀 Running: {file_path}")
    try:
        result = subprocess.run(
            ["python", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Script failed:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⏰ Error: Script timed out!")
    except Exception as e:
        print(f"❌ Failed to run {file_path}: {e}")

# Phase 3: Run remaining scripts
if regular_scripts:
    print(f"\n➡️ Running {len(regular_scripts)} remaining script(s)...\n")
    for file_path in regular_scripts:
        print(f"📎 Regular: {file_path.name}")
        print(f"🚀 Running: {file_path}")
        try:
            result = subprocess.run(
                ["python", str(file_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("❌ Script failed:")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("⏰ Error: Script timed out!")
        except Exception as e:
            print(f"❌ Failed to run {file_path}: {e}")
else:
    print("\n📄 No non-priority scripts found.")

# Final summary
print(f"\n✅ Execution complete.")
print(f"📊 Total scripts run: {len(priority_scripts) + len(regular_scripts)}")
print(f"⭐ Priority (-qav): {len(priority_scripts)}")
print(f"📁 Regular: {len(regular_scripts)}")