import json
import pathlib
import subprocess


def run(command: str) -> dict:
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


repo_dir = pathlib.Path("/workspace/parameter-golf")
result = {
    "cwd": str(pathlib.Path.cwd()),
    "repo_exists": repo_dir.exists(),
    "checks": [
        run("pwd"),
        run("ls -la /workspace"),
        run("python3 --version"),
        run("torchrun --version"),
        run("nvidia-smi -L"),
    ],
}

if repo_dir.exists():
    result["verify_pod_env"] = run("cd /workspace/parameter-golf && bash scripts/runpod/verify_pod_env.sh")

print(json.dumps(result, indent=2))
