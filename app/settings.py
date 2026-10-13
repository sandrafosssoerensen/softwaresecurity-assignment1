import os
import secrets
from pathlib import Path

SERVICE = os.environ.get("SERVICE", "A")
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or secrets.token_hex(32)
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "a", "b", "c", "testserver"]
ROOT_URLCONF = "app.urls"
MIDDLEWARE = []
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes"] if SERVICE == "A" else []
DATA_DIR = Path(os.environ.get("DATA_DIR", ".runtime/data/" + SERVICE))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DATA_DIR / "auth.sqlite"}} if SERVICE == "A" else {}
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATA_UPLOAD_MAX_MEMORY_SIZE = 131072
