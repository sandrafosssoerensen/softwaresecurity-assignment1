"""Start a loopback-only test server on a port allocated by the OS."""
import json
import os
from pathlib import Path
import sys
from wsgiref.simple_server import make_server

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

from django.core.wsgi import get_wsgi_application


if __name__ == "__main__":
    ready = Path(sys.argv[1])
    with make_server("127.0.0.1", 0, get_wsgi_application()) as server:
        # Publish only after bind succeeds. Atomic replacement avoids partial JSON.
        temporary = ready.with_suffix(".tmp")
        temporary.write_text(json.dumps({"service": os.environ["SERVICE"],
                                         "port": server.server_port}), encoding="utf-8")
        temporary.replace(ready)
        server.serve_forever()
