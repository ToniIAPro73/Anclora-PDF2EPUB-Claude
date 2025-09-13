import os
import time
import shutil
import subprocess
from pathlib import Path

import pytest
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_PORT = os.environ.get("BACKEND_PORT", "5175")


@pytest.fixture(scope="session")
def api_url():
    """Spin up backend, worker, redis and db using docker-compose."""
    if shutil.which("docker") is None:
        pytest.skip("Docker not available")
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            cwd=ROOT_DIR,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception:
        pytest.skip("Docker Compose not available")

    env = os.environ.copy()
    # Use separate database file for tests when running with sqlite fallback
    env.setdefault("CONVERSION_DB", str(ROOT_DIR / "backend" / "test_conversions.db"))

    subprocess.run(
        ["docker", "compose", "up", "-d", "backend", "worker", "db", "redis"],
        cwd=ROOT_DIR,
        env=env,
        check=True,
    )

    base_url = f"http://localhost:{BACKEND_PORT}"
    # Wait for backend to be ready
    for _ in range(60):
        try:
            requests.get(base_url + "/api/history", timeout=1)
            break
        except requests.RequestException:
            time.sleep(1)
    else:
        subprocess.run(["docker", "compose", "logs"], cwd=ROOT_DIR, env=env)
        pytest.fail("Backend service did not start in time")

    yield base_url

    subprocess.run(["docker", "compose", "down", "-v"], cwd=ROOT_DIR, env=env)


def test_pdf_conversion(api_url):
    base_url = api_url
    token = requests.post(base_url + "/api/auth/register", json={"email": "a@a.com", "password": "pw"}).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    pdf_path = Path(__file__).parent / "sample.pdf"
    with pdf_path.open("rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        resp = requests.post(base_url + "/api/convert", files=files, headers=headers)
    assert resp.status_code == 202
    task_id = resp.json()["task_id"]

    # Poll for completion
    for _ in range(120):
        status = requests.get(base_url + f"/api/status/{task_id}", headers=headers).json()
        if status.get("status") == "SUCCESS":
            output_path = status["result"].get("output_path")
            break
        time.sleep(1)
    else:
        pytest.fail("Conversion task did not finish")

    assert output_path, "No output path returned"

    # Verify EPUB exists inside backend container
    subprocess.run(
        ["docker", "compose", "exec", "-T", "backend", "test", "-f", output_path],
        cwd=ROOT_DIR,
        check=True,
    )

    history = requests.get(base_url + "/api/history", headers=headers).json()
    assert any(entry.get("task_id") == task_id for entry in history)
