"""Run browser acceptance through installed Playwright CLI (not an app dependency)."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ceav_m1 import V1_MODEL_VERSION, V2_MODEL_VERSION, V3_MODEL_VERSION, V33_MODEL_VERSION
from ceav_m1.output import finish_run, new_run, sha256, write_json
from ceav_m1.runtime import process_alive


def get_json(url):
    with urlopen(url, timeout=10) as response:
        return json.load(response)


def until(predicate, timeout=15):
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            value = predicate()
        except (URLError, TimeoutError, ConnectionError) as error:
            # Observation failure says nothing about worker termination. Keep
            # polling this same handle until an actual terminal state arrives.
            last_error = str(error)
            value = None
        if value:
            return value
        time.sleep(0.1)
    raise ValueError("Timed out waiting for verified browser/server state: " + str(last_error))


def run(scenario, out, base):
    out = Path(out).resolve()
    if scenario.startswith("IPW-"):
        model_version = V33_MODEL_VERSION
    elif scenario.startswith(("V3-", "ROB-")):
        model_version = V3_MODEL_VERSION
    elif scenario.startswith(("V2-", "CAL-", "INC-")):
        model_version = V2_MODEL_VERSION
    else:
        model_version = V1_MODEL_VERSION
    manifest = new_run(out, "browser_acceptance", request={"scenario": scenario, "base_url": base}, model_version=model_version)
    servers, streams = [], []
    try:
        cli = shutil.which("playwright-cli.cmd") or shutil.which("playwright-cli")
        node = shutil.which("node")
        entry = Path(cli).parent / "node_modules/@playwright/cli/playwright-cli.js"
        if not cli or not node or not entry.is_file():
            raise ValueError("Installed playwright-cli runtime unavailable")
        def open_browser():
            last = None
            for _ in range(10):
                opened = subprocess.run([node, str(entry), "-s=ceav-m1", "open", base, "--browser=msedge"], cwd=ROOT, capture_output=True, text=True)
                if not opened.returncode:
                    return
                last = opened.stdout + opened.stderr
                time.sleep(0.5)
            raise ValueError("Cannot open Edge browser session: " + str(last))
        def start_server(port, suffix):
            stream = (out / f"server-{suffix}.txt").open("x", encoding="utf-8")
            streams.append(stream)
            kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
            child = subprocess.Popen([sys.executable, "-B", "-m", "ceav_m1", "serve", "--port", str(port)], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, **kwargs)
            servers.append(child)
            def ready():
                content = (out / f"server-{suffix}.txt").read_text(encoding="utf-8")
                if child.poll() is not None:
                    raise ValueError("Isolated browser server failed: " + content)
                match = re.search(r"http://127\.0\.0\.1:\d+", content)
                return match.group(0) if match else None
            return child, until(ready)
        if scenario == "B07":
            initial_server, base = start_server(0, "before-restart")
        subprocess.run([node, str(entry), "-s=ceav-m1", "close"], cwd=ROOT, capture_output=True, text=True)
        open_browser()
        def browser_call(script_path, log_name):
            command = [node, str(entry), "-s=ceav-m1", "run-code", "--filename=" + str(script_path)]
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
            log = process.stdout + process.stderr
            (out / log_name).write_text(log, encoding="utf-8", newline="\n")
            if process.returncode or "### Result\n" not in log:
                raise ValueError("Browser flow failed; see " + log_name)
            return json.loads(log.split("### Result\n", 1)[1].split("\n###", 1)[0])
        flow_name = "browser_flows_ipw.js" if scenario.startswith("IPW-") else "browser_flows_robustness.js" if scenario.startswith("ROB-") else "browser_flows_v3.js" if scenario.startswith("V3-") else "browser_flows_incentives.js" if scenario.startswith("INC-") else "browser_flows_calibration.js" if scenario.startswith("CAL-") else "browser_flows_v2.js" if scenario.startswith("V2-") else "browser_flows.js"
        script = (ROOT / "verification" / flow_name).read_text(encoding="utf-8")
        script = script.replace('"__SCENARIO__"', json.dumps(scenario)).replace('"__OUTPUT_DIR__"', json.dumps(out.as_posix())).replace('"__BASE_URL__"', json.dumps(base))
        (out / "flow.js").write_text(script, encoding="utf-8", newline="\n")
        result = browser_call(out / "flow.js", "browser_log.txt")
        if result["status"] == "pending_all":
            deadline = time.monotonic() + 600
            while True:
                job = get_json(base + "/api/jobs/" + result["all_job"])
                if job["status"] not in ("queued", "running"):
                    break
                if time.monotonic() >= deadline:
                    raise ValueError("Timed out waiting for full suite")
                heartbeat = subprocess.run([node, str(entry), "-s=ceav-m1", "tab-list"], cwd=ROOT, capture_output=True, text=True)
                if heartbeat.returncode:
                    raise ValueError("Browser session closed during full suite: " + heartbeat.stdout + heartbeat.stderr)
                time.sleep(10)
            code = 'async page => { const id = ' + json.dumps(result["all_run"]) + '; await page.waitForFunction(id => document.querySelector("#tests-result").dataset.runId===id, id, {timeout:30000}); await page.locator("#tests-result").scrollIntoViewIfNeeded(); await page.screenshot({path:' + json.dumps((out / "all-suite-results.png").as_posix()) + '}); return {text: await page.locator("#tests-result").innerText()}; }'
            (out / "finish.js").write_text(code, encoding="utf-8")
            ui = browser_call(out / "finish.js", "browser_finish_log.txt")
            tests = get_json(base + "/api/runs/" + result["all_run"] + "/artifacts/test_results.json")
            result["steps"].append({"step": "Complete all-suite result rendered by UI", "status": "pass" if tests["status"] == "passed" and job["status"] == "succeeded" else "fail", "observed": {"counts": tests["counts"], "job_status": job["status"], "ui": ui}})
            result["status"] = "passed" if tests["status"] == "passed" and job["status"] == "succeeded" else "failed"
        if result["status"] == "pending_restart":
            worker_pid = result["worker_pid"]
            if not worker_pid or not process_alive(worker_pid):
                raise ValueError("Restart scenario requires a confirmed live worker")
            initial_server.kill()
            initial_server.wait(timeout=5)
            until(lambda: not process_alive(worker_pid))
            _, restarted_base = start_server(urlsplit(base).port, "after-restart")
            restarted = get_json(restarted_base + "/api/runs/" + result["restart_run"])
            code = 'async page => { await page.reload(); await page.locator("#connection").filter({hasText:"Engine sẵn sàng"}).waitFor(); await page.locator(\'[data-view="history"]\').click(); await page.locator(' + json.dumps('[data-open-run="' + result["restart_run"] + '"]') + ').click(); await page.waitForFunction(id=>document.querySelector("#run-metadata").textContent.includes(id),' + json.dumps(result["restart_run"]) + '); await page.screenshot({path:' + json.dumps((out / "interrupted-after-restart.png").as_posix()) + '}); return {metadata: await page.locator("#run-metadata").innerText()}; }'
            (out / "finish.js").write_text(code, encoding="utf-8")
            ui = browser_call(out / "finish.js", "browser_restart_log.txt")
            passed = restarted["status"] == "interrupted" and not process_alive(worker_pid)
            result["steps"].append({"step": "Abrupt server restart stops worker and reopens interrupted history", "status": "pass" if passed else "fail", "observed": {"worker_pid": worker_pid, "worker_alive": process_alive(worker_pid), "manifest_status": restarted["status"], "ui": ui}})
            result["status"] = "passed" if passed else "failed"
        if scenario == "B03" and result["status"] == "passed":
            golden = next(step["observed"] for step in result["steps"] if step["step"] == "Golden run identities")
            parity = []
            for record in golden:
                original = ROOT / "results" / record["run_id"]
                destination = out / ("cli-" + record["golden"])
                command = [sys.executable, "-B", "-m", "ceav_m1", "analyze", "--config", str(original / "config.json"), "--profile", str(original / "profile.json"), "--out", str(destination)]
                cli_result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                (out / (record["golden"] + "-cli-log.txt")).write_text(cli_result.stdout + cli_result.stderr, encoding="utf-8")
                equal = cli_result.returncode == 0 and all((original / name).read_bytes() == (destination / name).read_bytes() for name in ("summary.json", "states.csv", "best_responses.json"))
                parity.append({"golden": record["golden"], "api_run": record["run_id"], "cli_exit_code": cli_result.returncode, "numeric_artifacts_byte_equal": equal})
            write_json(out / "cli_parity.json", parity)
            result["steps"].append({"step": "Actual CLI/API numeric artifacts match byte-for-byte G1-G4", "status": "pass" if all(r["numeric_artifacts_byte_equal"] for r in parity) else "fail", "observed": parity})
            if not all(r["numeric_artifacts_byte_equal"] for r in parity):
                result["status"] = "failed"
        if scenario == "B08" and result["status"] == "passed":
            source = next(step["observed"] for step in result["steps"] if step["step"] == "Downloaded artifact source")
            checks = []
            for name in ("config.json", "profile.json", "summary.json", "best_responses.json", "states.csv", "report.md"):
                expected = next(item["sha256"] for item in source["manifest"]["artifacts"] if item["name"] == name)
                checks.append({"artifact": name, "download_hash_matches": sha256((out / ("download-" + name)).read_bytes()) == expected})
            result["steps"].append({"step": "Downloaded bytes match run manifest hashes", "status": "pass" if all(c["download_hash_matches"] for c in checks) else "fail", "observed": checks})
            if not all(c["download_hash_matches"] for c in checks):
                result["status"] = "failed"
        write_json(out / "browser_results.json", result)
        (out / "report.md").write_text(f"# CEAV-M1 — Browser {scenario}\n\nStatus: {result['status']}. Browser: {result['browser']}; viewport: {result['viewport']}.\n\nSteps and observed values are in browser_results.json; screenshots and raw CLI output are pinned in this run.\n", encoding="utf-8", newline="\n")
        finish_run(out, manifest, "succeeded" if result["status"] == "passed" else "failed")
        print(json.dumps({"scenario": scenario, "status": result["status"], "steps": len(result["steps"]), "error": result.get("error"), "evidence": str(out)}, ensure_ascii=True))
        return result["status"] == "passed"
    except BaseException as error:
        (out / "report.md").write_text(f"# Browser acceptance failed\n\n{error}\n", encoding="utf-8")
        finish_run(out, manifest, "failed", error)
        raise
    finally:
        if 'node' in locals() and 'entry' in locals():
            subprocess.run([node, str(entry), "-s=ceav-m1", "close"], cwd=ROOT, capture_output=True, text=True)
        for server in servers:
            if server.poll() is None:
                server.terminate()
                server.wait(timeout=10)
        for stream in streams:
            stream.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=[f"B{i:02}" for i in range(1, 10)] + [f"V2-B{i:02}" for i in range(1, 7)] + ["CAL-B01", "INC-B01", "V3-B01", "ROB-B01", "IPW-B01"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--base", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.scenario, args.out, args.base) else 1)
