
import json 
from pipeline.storage import write_json_atomic

def test_round_trip(tmp_path):
    file_path = tmp_path / "sub" / "data.json"
    payload = {"id": 101, "status": "active"}

    write_json_atomic(file_path, payload)

    with open(file_path, "r") as f:
        loaded_data = json.load(f)

    assert file_path.exists()
    assert loaded_data == payload
    assert loaded_data["status"] == "active"

def test_no_tmp_file_left(tmp_path):
    file_path = tmp_path / "sub" / "data.json"
    payload = {"id": 101, "status": "active"}

    write_json_atomic(file_path, payload)

    assert not (tmp_path / "sub" / "data.json.tmp").exists()

