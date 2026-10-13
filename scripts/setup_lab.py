"""Generate local keys, migrate A's database, and seed known lab accounts."""
import os
from pathlib import Path
import subprocess
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

root = Path(__file__).resolve().parents[1]
os.chdir(root)
keydir = Path(os.environ.get("LAB_RUNTIME_DIR", str(root / ".runtime"))) / "keys"
keydir.mkdir(parents=True, exist_ok=True)
private = keydir / "private.pem"
public = keydir / "public.pem"
if not private.exists():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                          serialization.NoEncryption()))
    private.chmod(0o600)
    public.write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,
                                                     serialization.PublicFormat.SubjectPublicKeyInfo))
os.environ["SERVICE"] = "A"
subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], check=True)
sys.path.insert(0, str(root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django
django.setup()
from django.contrib.auth.models import User
for name in ("alice", "bob", "admin"):
    user, _ = User.objects.get_or_create(username=name)
    user.set_password("Lab-only-Password-123!")
    user.is_staff = name == "admin"
    user.save()
print("Seeded alice, bob, admin. Lab password is documented in README.")
