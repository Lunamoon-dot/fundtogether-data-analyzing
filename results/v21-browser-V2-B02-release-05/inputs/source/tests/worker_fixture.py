"""Handshake/barrier worker for lifecycle integration; not a browser operation."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ceav_m1.__main__ import execute


if __name__ == "__main__":
    staged, out, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    if len(sys.argv) > 4:
        from ceav_m1.runtime import watch_parent
        watch_parent(int(sys.argv[4]), out)
    request = json.loads((staged / "request.json").read_text(encoding="utf-8"))
    execute("analyze", request["config"], request["profile"], request["mechanism"], out, defer_publication=True)
    child = None
    if mode == "child":
        kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], **kwargs)
    (staged / "started.json").write_text(json.dumps({"pid": os.getpid(), "child_pid": child.pid if child else None}), encoding="utf-8")
    print(json.dumps({"progress": {"phase": "test_only_barrier", "completed": 1, "total": 2}}), flush=True)
    while not (staged / "release").exists():
        time.sleep(0.02)
    if child:
        child.terminate()
        child.wait(timeout=5)
    raise SystemExit(7 if mode == "crash" else 0)
