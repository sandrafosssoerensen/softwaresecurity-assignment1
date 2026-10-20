"""HTTP integration tests against three fresh Django processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.parse import quote
from uuid import uuid4
import jwt
import requests

ROOT = Path(__file__).resolve().parents[1]


class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Windows can briefly keep a subprocess log handle open after the
        # server process has terminated. Do not turn that cleanup race into a
        # failed test run; the temporary directory is only test data.
        cls.temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=(os.name == "nt"))
        cls.runtime = Path(cls.temp.name)
        cls.logs = []
        cls.processes = []

        cls.urls = {}

        try:
            seed_env = os.environ.copy()
            seed_env.update(SERVICE="A", DATA_DIR=str(cls.runtime / "A"), LAB_RUNTIME_DIR=str(cls.runtime))
            subprocess.run([sys.executable, "scripts/setup_lab.py"], cwd=ROOT, env=seed_env,
                           check=True, stdout=subprocess.DEVNULL)

            # Start downstream services first. Each binds port 0 and publishes
            # its actual OS-allocated port, so branch jobs cannot share ports.
            for service in "CBA":
                env = os.environ.copy()
                for key in ("PRIVATE_KEY_PATH", "B_URL", "C_URL"):
                    env.pop(key, None)
                env.update(SERVICE=service, DATA_DIR=str(cls.runtime / service),
                           PUBLIC_KEY_PATH=str(cls.runtime / "keys/public.pem"))
                env.update({name + "_URL": url for name, url in cls.urls.items()})
                
                if service == "A":
                    env["PRIVATE_KEY_PATH"] = str(cls.runtime / "keys/private.pem")
                log = (cls.runtime / (service + ".log")).open("w")
                cls.logs.append(log)
                ready = cls.runtime / (service + "-ready.json")
                process = subprocess.Popen([sys.executable, "scripts/serve_test.py", str(ready)],
                                           cwd=ROOT, env=env, stdout=log, stderr=log)
                cls.processes.append(process)
                deadline = time.monotonic() + 30
                while not ready.exists():
                    if process.poll() is not None or time.monotonic() > deadline:
                        details = (cls.runtime / (service + ".log")).read_text(errors="replace")
                        raise RuntimeError(f"Component {service} startup failed: {details[-2000:]}")
                    time.sleep(0.1)
                address = json.loads(ready.read_text(encoding="utf-8"))
                if address["service"] != service:
                    raise RuntimeError(f"Unexpected readiness identity for component {service}")
                url = "http://127.0.0.1:" + str(address["port"])
                cls.urls[service] = url
                while True:
                    if process.poll() is not None:
                        raise RuntimeError(f"Component {service} exited before its health check")
                    try:
                        response = requests.get(url + "/health", timeout=1)
                        if response.status_code == 200 and response.json().get("service") == service:
                            break
                    except requests.RequestException:
                        pass
                    if time.monotonic() > deadline:
                        raise RuntimeError(f"Component {service} health check failed")
                    time.sleep(0.1)

            cls.tokens = {}

            for username in ("alice", "bob", "admin"):
                response = requests.post(cls.urls["A"]+"/auth/token", json={"username": username,
                    "password": "Lab-only-Password-123!"}, timeout=5)
                response.raise_for_status()
                cls.tokens[username] = response.json()["access_token"]

        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        for process in cls.processes:
            if process.poll() is None:
                process.terminate()

        for process in cls.processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        for log in cls.logs:
            log.close()
            
        cls.temp.cleanup()

    def headers(self, user="alice"):
        return {"Authorization": "Bearer "+self.tokens[user]}

    def create(self, user="alice"):
        response = requests.post(self.urls["A"]+"/analyses", headers=self.headers(user),
                                 json=json.loads((ROOT/"examples/request.json").read_text()), timeout=5)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def service_token(self, audience, scope, analysis_id, subject="1", role="user", expired=False):
        now = int(time.time())
        return jwt.encode({"iss":"assignment-api", "aud":audience, "sub":subject,
            "iat":now-1000 if expired else now, "exp":now-1 if expired else now+60,
            "jti":str(uuid4()), "scope":scope, "role":role, "analysis_id":analysis_id},
            (self.runtime/"keys/private.pem").read_bytes(), algorithm="RS256")

    def test_create_read_cross_user_and_admin(self):
        doc = self.create()
        path = self.urls["A"]+"/analyses/"+doc["id"]
        self.assertEqual(requests.get(path, headers=self.headers(), timeout=5).status_code, 200)
        self.assertEqual(requests.get(path, headers=self.headers("bob"), timeout=5).status_code, 404)
        self.assertEqual(requests.get(path, headers=self.headers("admin"), timeout=5).status_code, 200)
        self.assertEqual(doc["model"], "development-stub")

    def test_list_only_owned(self):
        alice = self.create(); bob = self.create("bob")
        rows = requests.get(self.urls["A"]+"/analyses", headers=self.headers(), timeout=5).json()["analyses"]
        ids = {row["id"] for row in rows}
        self.assertIn(alice["id"], ids)
        self.assertNotIn(bob["id"], ids)

    def test_delete_role_and_positive_control(self):
        doc = self.create(); path = self.urls["A"]+"/analyses/"+doc["id"]
        self.assertEqual(requests.delete(path, headers=self.headers(), timeout=5).status_code, 403)
        self.assertEqual(requests.get(path, headers=self.headers(), timeout=5).status_code, 200)
        self.assertEqual(requests.delete(path, headers=self.headers("admin"), timeout=5).status_code, 204)
        self.assertEqual(requests.get(path, headers=self.headers(), timeout=5).status_code, 404)

    def test_b_authority_cannot_delete(self):
        doc=self.create(); token=self.service_token("C", "create", doc["id"])
        response=requests.delete(self.urls["C"]+"/internal/analyses/"+doc["id"],
                                 headers={"Authorization":"Bearer "+token}, timeout=5)
        self.assertEqual(response.status_code,403)
        self.assertEqual(requests.get(self.urls["A"]+"/analyses/"+doc["id"],headers=self.headers(),timeout=5).status_code,200)

    def test_expired_and_wrong_audience(self):
        doc=self.create(); path=self.urls["C"]+"/internal/analyses/"+doc["id"]
        for token in (self.service_token("C","delete",doc["id"],role="admin",expired=True), self.tokens["admin"]):
            self.assertEqual(requests.delete(path,headers={"Authorization":"Bearer "+token},timeout=5).status_code,401)
        self.assertEqual(requests.get(self.urls["A"]+"/analyses/"+doc["id"],headers=self.headers(),timeout=5).status_code,200)

    def test_invalid_signature_and_unknown_owner(self):
        data=json.loads((ROOT/"examples/request.json").read_text())
        data["alert"]["alert"]["signature"]=" "
        self.assertEqual(requests.post(self.urls["A"]+"/analyses",headers=self.headers(),json=data,timeout=5).status_code,400)
        data=json.loads((ROOT/"examples/request.json").read_text());data["owner_id"]="2"
        self.assertEqual(requests.post(self.urls["A"]+"/analyses",headers=self.headers(),json=data,timeout=5).status_code,400)

    def test_untrusted_owner_field_cannot_change_owner(self):
        original = self.create()
        analysis_id = str(uuid4())
        fields = ("original_alert", "model_input", "model", "prompt_version", "settings",
                  "latency_seconds", "created_at", "result")
        document = {field: original[field] for field in fields}
        document["owner_id"] = "2"

        create_token = self.service_token("C", "create", analysis_id, subject="1")
        create_response = requests.post(
            self.urls["C"] + "/internal/analyses",
            headers={"Authorization": "Bearer " + create_token},
            json=document,
            timeout=5,
        )

        bob_token = self.service_token("C", "read", analysis_id, subject="2")
        bob_response = requests.get(
            self.urls["C"] + "/internal/analyses/" + analysis_id,
            headers={"Authorization": "Bearer " + bob_token},
            timeout=5,
        )

        self.assertEqual(
            (create_response.status_code, bob_response.status_code),
            (400, 404),
            f"create={create_response.text}; bob_read={bob_response.text}",
        )

    def test_size_limit_direct_b(self):
        data=json.loads((ROOT/"examples/request.json").read_text())
        data["alert"]["padding"]="x"*66000
        identifier=str(uuid4())
        data["storage_token"]=self.service_token("C","create",identifier)
        response=requests.post(self.urls["B"]+"/internal/analyze",headers={"Authorization":"Bearer "+self.service_token("B","execute",identifier)},json=data,timeout=5)
        self.assertEqual(response.status_code,413)

    def test_sql_injection_via_api_does_not_return_a_record(self):
        # Use Alice's ordinary login token, not a test-signed service token.
        # Target her own record so this does not rely on the CWE-862 flaw.
        document = self.create()
        missing_id = str(uuid4())
        base = self.urls["A"] + "/analyses/"
        normal = requests.get(base + document["id"], headers=self.headers(), timeout=5)
        self.assertEqual(normal.status_code, 200, normal.text)
        missing = requests.get(base + missing_id, headers=self.headers(), timeout=5)
        self.assertEqual(missing.status_code, 404, missing.text)

        injected_id = f"{missing_id}' OR id='{document['id']}' -- "
        url = base + quote(injected_id, safe="")
        unauthenticated = requests.get(url, timeout=5)
        self.assertEqual(unauthenticated.status_code, 401, unauthenticated.text)
        response = requests.get(url, headers=self.headers(), timeout=5)

        # If injection succeeds, verify it selected this exact test record.
        if response.status_code == 200:
            self.assertEqual(response.json()["id"], document["id"])
            self.assertEqual(response.json()["owner"], document["owner"])
        self.assertEqual(
            response.status_code, 400,
            f"requested_id={injected_id!r}; response={response.text}",
        )
        self.assertNotIn("id", response.json())

    def test_forged_token(self):
        parts=self.tokens["alice"].split(".")
        parts[2]="A"*len(parts[2])
        self.assertEqual(requests.get(self.urls["A"]+"/analyses",headers={"Authorization":"Bearer "+".".join(parts)},timeout=5).status_code,401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
