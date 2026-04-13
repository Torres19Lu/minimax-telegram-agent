import os
import subprocess
import shutil
from typing import Optional

SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox"))


def _validate_path(filepath: str) -> str:
    """Ensure the filepath stays inside the sandbox directory."""
    abs_path = os.path.abspath(os.path.join(SANDBOX_DIR, filepath))
    if not abs_path.startswith(SANDBOX_DIR + os.sep) and abs_path != SANDBOX_DIR:
        raise ValueError(f"Path escapes sandbox: {filepath}")
    return abs_path


def write_file(filename: str, content: str) -> str:
    """Write a file inside the sandbox."""
    path = _validate_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written: {filename}"


def read_file(filename: str) -> str:
    """Read a file inside the sandbox."""
    path = _validate_path(filename)
    if not os.path.exists(path):
        return f"File not found: {filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_files(subdir: str = "") -> str:
    """List files inside the sandbox."""
    path = _validate_path(subdir)
    if not os.path.exists(path):
        return f"Directory not found: {subdir}"
    lines = []
    for root, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, SANDBOX_DIR)
        if rel_root == ".":
            rel_root = ""
        for f in files:
            lines.append(os.path.join(rel_root, f))
    return "\n".join(lines) if lines else "(empty)"


def execute_python(script_content: str) -> str:
    """Execute a Python script inside the sandbox."""
    try:
        result = subprocess.run(
            ["python", "-c", script_content],
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Execution timed out after 30 seconds."
    except Exception as e:
        return f"Execution failed: {e}"


def execute_shell(command: str) -> str:
    """Execute a shell command inside the sandbox.

    WARNING: This is restricted to safe commands only.
    """
    # Block dangerous commands
    blocked = ["rm -rf /", "rm -rf /*", ":(){ :|: & };:", "> /dev/sda", "mkfs"]
    for b in blocked:
        if b in command:
            return f"Blocked dangerous command: {command}"

    try:
        result = subprocess.run(
            command,
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Execution timed out after 30 seconds."
    except Exception as e:
        return f"Execution failed: {e}"
