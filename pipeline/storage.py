from pathlib import Path
import json
import os

def write_json_atomic(path, data):
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_suffix(path.suffix + ".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        os.replace(temp_path, path)

    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

def append_manifest_rows(rows, filename):
    # Open the file in append mode ('a') so it writes to the bottom of the file
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "a", encoding="utf-8") as file:
        for item in rows:
            # Convert the dict to a compact JSON string and add a newline character
            file.write(json.dumps(item, ensure_ascii=False) + "\n")

