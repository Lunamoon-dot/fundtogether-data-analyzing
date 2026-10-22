"""Isolated server process for the abrupt-parent-exit integration test."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ceav_m1.server import create_server
from tests.test_server import BarrierLab


if __name__ == "__main__":
    folder = Path(sys.argv[1])
    lab = BarrierLab(folder / "results")
    lab.mode = "child"
    server = create_server(0, laboratory=lab)
    (folder / "server.json").write_text(json.dumps({"port": server.server_address[1], "token": lab.token}), encoding="utf-8")
    server.serve_forever()
