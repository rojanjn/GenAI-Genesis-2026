import subprocess
import sys
from pathlib import Path

# Get project root
root = Path(__file__).parent

backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.api.main:app", "--reload"],
    cwd=root
)

frontend = subprocess.Popen(
    ["npm", "start"],
    cwd=root / "frontend"
)

try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    print("\nShutting down...")
    backend.terminate()
    frontend.terminate()
