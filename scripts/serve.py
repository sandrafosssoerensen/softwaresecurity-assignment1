"""Start one local component. Use separate terminals for A, B, and C."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
service = sys.argv[1].upper()

if service not in ("A", "B", "C"):
    raise SystemExit("Use A, B, or C")

env = os.environ.copy()
env["SERVICE"] = service
env["PUBLIC_KEY_PATH"] = str(root / ".runtime/keys/public.pem")

if service == "A":
    env["PRIVATE_KEY_PATH"] = str(root / ".runtime/keys/private.pem")
port = {"A": 8000, "B": 8001, "C": 8002}[service]

subprocess.run([sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"],
               cwd=root, env=env, check=True)
