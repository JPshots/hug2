import os
import json
import sys

print("==== DEBUG INFORMATION ====")
print(f"Current working directory: {os.getcwd()}")
print("\nDirectory structure:")
for root, dirs, files in os.walk('.', topdown=True):
    print(f"Directory: {root}")
    for d in dirs:
        print(f"  - {d}/")
    for f in files:
        if f.endswith('.json'):
            print(f"  - {f} [JSON]")
        else:
            print(f"  - {f}")

print("\nLooking for JSON files...")
json_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.json'):
            full_path = os.path.join(root, file)
            json_files.append(full_path)
            print(f"Found JSON file: {full_path}")

print(f"\nTotal JSON files found: {len(json_files)}")

print("\nCreating framework directory if it doesn't exist...")
os.makedirs('framework', exist_ok=True)

print("\nCopying JSON files to framework directory...")
import shutil
for file_path in json_files:
    filename = os.path.basename(file_path)
    dest_path = os.path.join('framework', filename)
    try:
        shutil.copy2(file_path, dest_path)
        print(f"Copied {file_path} to {dest_path}")
    except Exception as e:
        print(f"Error copying {file_path}: {str(e)}")

print("\nContents of framework directory:")
try:
    for file in os.listdir('framework'):
        print(f"  - {file}")
except Exception as e:
    print(f"Error listing framework directory: {str(e)}")

print("\nTrying to load JSON files from framework directory...")
for file in os.listdir('framework'):
    if file.endswith('.json'):
        try:
            with open(os.path.join('framework', file), 'r') as f:
                data = json.load(f)
                print(f"Successfully loaded {file}, contains {len(json.dumps(data))} characters")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

print("\n==== DEBUG COMPLETE ====")