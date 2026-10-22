"""Worker parent liveness; an abruptly closed server must not orphan work."""

import os
from pathlib import Path
import signal
import subprocess
import threading
import time


def process_alive(pid):
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        code = wintypes.DWORD()
        try:
            return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def watch_parent(pid, out):
    def monitor():
        while process_alive(pid):
            time.sleep(0.2)
        # Parent is gone, so it can no longer arbitrate publication. Preserve
        # interrupted status before ending this worker and its owned children.
        from .output import finish_run
        import json
        path = Path(out) / "manifest.json"
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            if manifest["status"] in ("queued", "running"):
                finish_run(Path(out), manifest, "interrupted", "Worker detected server process exit")
        except (OSError, ValueError, KeyError):
            pass
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(os.getpid()), "/T", "/F"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.killpg(os.getpid(), signal.SIGTERM)
        os._exit(3)
    threading.Thread(target=monitor, name="server-parent-watch", daemon=True).start()
