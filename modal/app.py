import os
import re
import subprocess
import tempfile
from pathlib import Path

import modal

LOCAL_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
RUNTIME_PYPROJECT = Path("/root/pyproject.toml")

def _read_project_dependency(name: str) -> str:
    pyproject = None
    for pyproject_path in (LOCAL_PYPROJECT, RUNTIME_PYPROJECT):
        if pyproject_path.exists():
            pyproject = pyproject_path.read_text()
            break
    if pyproject is None:
        raise RuntimeError("Could not find pyproject.toml for dependency resolution")

    in_dependencies = False
    for line in pyproject.splitlines():
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_dependencies = True
            continue
        if in_dependencies and stripped == "]":
            break
        if in_dependencies:
            match = re.match(r'"([^"]+)"\s*,?$', stripped)
            if match:
                dep = match.group(1)
                if dep.startswith(f"{name}"):
                    return dep
    raise RuntimeError(f"Could not find dependency for {name!r} in pyproject.toml")


MOJO_DEP = _read_project_dependency("mojo")
MAX_DEP = _read_project_dependency("max")

app = modal.App("76")
img = (
  modal.Image.from_registry("nvidia/cuda:12.4.0-base-ubuntu22.04")
  .apt_install("python-is-python3", "python3-pip")
  .pip_install(
      MOJO_DEP,
      MAX_DEP,
      index_url="https://whl.modular.com/nightly/simple/",
      extra_options="--pre --extra-index-url https://pypi.org/simple",
  )
  # The runtime container imports this module again, so keep pyproject.toml available.
  .add_local_file(LOCAL_PYPROJECT, remote_path="/root/pyproject.toml")
)

@app.function(image=img, gpu="A10")
def main(mojo_code: str):
    # Get real GPU info
    gpu_result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True
    )
    gpu_info = gpu_result.stdout.strip()
    yield {"status": "gpu_info", "gpu": gpu_info}

    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mojo', delete=False) as f:
        f.write(mojo_code)
        temp_path = f.name
    
    yield {"status": "compiling"}

    try:
        result = subprocess.run(
            ["mojo", "run", temp_path],
            capture_output=True,
            text=True
        )
        
        # Filter out noisy socket errors
        stderr_lines = [
            line for line in result.stderr.splitlines()
            if "socket.cc" not in line
        ]
        
        yield {
            "status": "complete",
            "stdout": result.stdout,
            "stderr": "\n".join(stderr_lines).strip(),
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }
    finally:
        os.unlink(temp_path)
