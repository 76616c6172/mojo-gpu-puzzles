import os
import subprocess
import tempfile
from pathlib import Path

import modal

import tomli as tomllib

def _read_project_dependency(name: str) -> str:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    for dep in pyproject["project"]["dependencies"]:
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
