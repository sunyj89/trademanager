import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def test_editable_install_with_dev_dependencies(tmp_path):
    venv_dir = tmp_path / "editable-install-venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, cwd=PROJECT_ROOT)

    python_exe = _venv_python(venv_dir)

    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--disable-pip-version-check", "-e", ".[dev]"],
        check=True,
        cwd=PROJECT_ROOT,
    )

    probe = subprocess.run(
        [str(python_exe), "-c", "import app.main; print(app.main.app.title)"],
        check=True,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert "TradeManager CRM MVP" in probe.stdout
