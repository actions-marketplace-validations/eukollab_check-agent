# Copyright © 2026 EuKreate, Inc.
# SPDX-License-Identifier: Apache-2.0
"""The Action's checks: the network's checks of agent.json with a CI token, and, given the server's
address, whether agent.json still matches what the server declares. It writes nothing but its report."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["ekl", *args], capture_output=True, text=True, check=False)


def main() -> int:
    file, mcp, platform = os.environ["FILE"], os.environ.get("MCP", ""), os.environ["PLATFORM"]
    lines = [f"### EuKollab check of `{file}`", ""]
    failed = False
    if os.environ.get("EKL_TOKEN"):
        login = run("login", "--platform", platform)
        if login.returncode != 0:
            lines += ["**Could not sign in with `EKL_TOKEN`:**", "", f"```\n{login.stderr.strip()}\n```"]
            failed = True
        else:
            checked = run("--json", "agent", "check", file)
            try:
                problems = json.loads(checked.stdout).get("problems", [])
            except json.JSONDecodeError:
                problems = [{"level": "error", "field": "-", "message": checked.stderr.strip() or "no answer"}]
            errors = [p for p in problems if p.get("level") == "error"]
            failed |= bool(errors)
            lines.append("**The network's checks:** " + ("problems found" if errors else "passed"))
            lines += [f"- {p['level']}: `{p.get('field') or '-'}` {p['message']}" for p in problems]
    else:
        # GitHub gives no secrets to a pull request from a fork.
        lines.append("**The network's checks were skipped:** no `EKL_TOKEN` (for example, a pull request from a fork).")
    if mcp:
        synced = run("agent", "sync", file, "--mcp", mcp, "--check")
        same = synced.returncode == 0
        failed |= not same
        lines += ["", "**Against the server's declarations:** " + ("the same" if same else "different")]
        if not same:
            lines += ["", f"```\n{(synced.stdout + synced.stderr).strip()}\n```"]
    report = "\n".join(lines) + "\n"
    print(report)
    for target in (os.environ.get("GITHUB_STEP_SUMMARY"), str(Path(os.environ["RUNNER_TEMP"]) / "eukollab-check.md")):
        if target:
            with Path(target).open("a") as out:
                out.write(report)
    shutil.rmtree(os.environ["EKL_CONFIG_DIR"], ignore_errors=True)  # the signed-in token goes with the job
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
