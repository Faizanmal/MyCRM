"""
One-Command Stack Launcher for MyCRM
-----------------------------------
Starts a healthy MyCRM stack from a clean checkout.
Supports both Local (ASGI Daphne/Uvicorn) and Containerized (Docker Compose) modes.
"""

import os
import sys
import subprocess
import time
import argparse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def ensure_env_file():
    """Ensure backend/.env exists, creating from example if necessary."""
    env_file = BACKEND_DIR / ".env"
    example_file = BACKEND_DIR / ".env.example"
    if not env_file.exists():
        print("[INFO] backend/.env not found. Creating from .env.example...")
        import secrets
        if example_file.exists():
            content = example_file.read_text(encoding="utf-8")
            content = content.replace("your-secret-key-here", secrets.token_urlsafe(50))
            # Enable SQLite for seamless out-of-the-box local development
            content = content.replace("DATABASE_URL=postgresql://postgres:password@localhost:5432/mycrm_db", "# DATABASE_URL=postgresql://postgres:password@localhost:5432/mycrm_db\nUSE_SQLITE=True")
            env_file.write_text(content, encoding="utf-8")
            print("[INFO] Created backend/.env with generated SECRET_KEY and SQLite default.")
        else:
            default_env = (
                f"SECRET_KEY={secrets.token_urlsafe(50)}\n"
                "DEBUG=True\n"
                "USE_SQLITE=True\n"
                "ENVIRONMENT=local\n"
                "ALLOWED_HOSTS=localhost,127.0.0.1,testserver\n"
            )
            env_file.write_text(default_env, encoding="utf-8")
            print("[INFO] Created default backend/.env.")


def run_migrations():
    """Run database migrations."""
    print("[INFO] Running database migrations...")
    env = os.environ.copy()
    env.setdefault("DEBUG", "True")
    env.setdefault("USE_SQLITE", "True")
    env.setdefault("ENVIRONMENT", "local")
    result = subprocess.run(
        [sys.executable, "backend/manage.py", "migrate", "--noinput"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] Migrations failed:\n{result.stderr}")
        return False
    print("[INFO] Migrations applied successfully.")
    return True


def check_system():
    """Run Django system check."""
    print("[INFO] Running system check...")
    env = os.environ.copy()
    env.setdefault("DEBUG", "True")
    env.setdefault("USE_SQLITE", "True")
    result = subprocess.run(
        [sys.executable, "backend/manage.py", "check"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[ERROR] System check failed:\n{result.stderr}")
        return False
    print("[INFO] System check passed (0 issues).")
    return True


def verify_health_endpoint(url="http://localhost:8000/api/health/", max_retries=10, delay=1):
    """Poll health check endpoint until healthy or timed out."""
    print(f"[INFO] Verifying health endpoint: {url}")
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MyCRM-HealthCheck/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    print(f"[SUCCESS] Stack is healthy! HTTP {resp.status} received from {url}")
                    return True
        except Exception as e:
            time.sleep(delay)
    print(f"[WARNING] Health check probe timed out after {max_retries} attempts.")
    return False


def start_docker(compose_file="docker-compose.yml"):
    """Start stack via Docker Compose."""
    print(f"[INFO] Starting stack via Docker Compose ({compose_file})...")
    result = subprocess.run(
        ["docker", "compose", "-f", compose_file, "up", "-d"],
        cwd=PROJECT_ROOT
    )
    if result.returncode == 0:
        verify_health_endpoint()
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="MyCRM One-Command Stack Launcher")
    parser.add_argument("--docker", action="store_true", help="Launch using Docker Compose")
    parser.add_argument("--prod", action="store_true", help="Use production configuration")
    parser.add_argument("--check-only", action="store_true", help="Only run checks and migrations without starting server")
    args = parser.parse_args()

    print("=" * 60)
    print("MyCRM Stack Launcher")
    print("=" * 60)

    ensure_env_file()

    if not run_migrations():
        sys.exit(1)

    if not check_system():
        sys.exit(1)

    if args.check_only:
        print("[SUCCESS] Stack configuration and database are healthy.")
        sys.exit(0)

    if args.docker:
        compose_file = "docker-compose.production.yml" if args.prod else "docker-compose.yml"
        success = start_docker(compose_file)
        sys.exit(0 if success else 1)
    else:
        print("[INFO] Local stack is configured and ready.")
        print("[INFO] Start backend ASGI server: python -m daphne -b 0.0.0.0 -p 8000 backend.asgi:application")
        print("[INFO] Start frontend Next.js:     npm run dev --prefix frontend")


if __name__ == "__main__":
    main()
