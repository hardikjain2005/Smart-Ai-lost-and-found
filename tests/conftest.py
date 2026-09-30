import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "ml"))

# Test configuration (in-memory SQLite, throw-away secrets) must be set before the app is imported.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "test-secret-not-for-production"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["SEED_ADMIN_PASSWORD"] = "AdminPass-test1"
os.environ["SEED_DEMO_PASSWORD"] = "DemoPass-test1"
import tempfile  # noqa: E402

os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="campusfind-uploads-")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
