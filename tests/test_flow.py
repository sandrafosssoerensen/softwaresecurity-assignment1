"""HTTP integration tests against three fresh Django processes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from uuid import uuid4
import jwt
import requests

ROOT = Path(__file__).resolve().parents[1]


class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.runtime = Path(cls.temp.name)
        cls.logs = []
        cls.processes = []
        seed_env = os.environ.copy()
        seed_env.update(SERVICE="A", DATA_DIR=str(cls.runtime / "A"), LAB_RUNTIME_DIR=str(cls.runtime))
        subprocess.run([sys.executable, "scripts/setup_lab.py"], cwd=ROOT, env=seed_env,
                       check=True, stdout=subprocess.DEVNULL)
        cls.urls = {s: "http://127.0.0.1:" + str(18000+i) for i, s in enumerate("ABC")}
        try:
            for i, service in enumerate("ABC"):
                env = os.environ.copy()
                env.update(SERVICE=service, DATA_DIR=str(cls.runtime / service),
                           PUBLIC_KEY_PATH=str(cls.runtime / "keys/public.pem"),
                           B_URL=cls.urls["B"], C_URL=cls.urls["C"])
                if service == "A":
                    env["PRIVATE_KEY_PATH"] = str(cls.runtime / "keys/private.pem")
                log = (cls.runtime / (service + ".log")).open("w")
                cls.logs.append(log)
                cls.processes.append(subprocess.Popen([sys.executable, "manage.py", "runserver",
                    "127.0.0.1:"+str(18000+i), "--noreload"], cwd=ROOT, env=env,
                    stdout=log, stderr=log))
            deadline = time.monotonic()+20
            for url in cls.urls.values():
                while True:
                    try:
                        if requests.get(url+"/health", timeout=1).status_code == 200:
                            break
                    except requests.RequestException:
                        pass
                    if time.monotonic() > deadline:
                        raise RuntimeError("Server startup failed")
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

    def test_size_limit_direct_b(self):
        data=json.loads((ROOT/"examples/request.json").read_text())
        data["alert"]["padding"]="x"*66000
        identifier=str(uuid4())
        data["storage_token"]=self.service_token("C","create",identifier)
        response=requests.post(self.urls["B"]+"/internal/analyze",headers={"Authorization":"Bearer "+self.service_token("B","execute",identifier)},json=data,timeout=5)
        self.assertEqual(response.status_code,413)

    def test_forged_token(self):
        parts=self.tokens["alice"].split(".")
        parts[2]="A"*len(parts[2])
        self.assertEqual(requests.get(self.urls["A"]+"/analyses",headers={"Authorization":"Bearer "+".".join(parts)},timeout=5).status_code,401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
