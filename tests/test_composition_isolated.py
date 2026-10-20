"""Focused CWE-807 comparison using the existing fresh HTTP environment."""
import json
import unittest
from uuid import uuid4

import requests

import test_flow


class CompositionIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flow = test_flow.FlowTests()
        cls.flow.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.flow.tearDownClass()

    def test_delegated_create_cannot_assign_another_owner(self):
        flow = self.flow
        original = flow.create()
        normal_path = flow.urls["A"] + "/analyses/" + original["id"]
        alice_normal = requests.get(normal_path, headers=flow.headers(), timeout=5)
        bob_normal = requests.get(normal_path, headers=flow.headers("bob"), timeout=5)

        # Establish that the normal read ownership check is still active.
        self.assertEqual(alice_normal.status_code, 200, alice_normal.text)
        self.assertEqual(bob_normal.status_code, 404, bob_normal.text)
        self.assertEqual(original["owner"], "1")

        analysis_id = str(uuid4())
        fields = ("original_alert", "model_input", "model", "prompt_version", "settings",
                  "latency_seconds", "created_at", "result")
        document = {field: original[field] for field in fields}
        document["owner_id"] = "2"

        # Simulate Component B holding a valid create permission for Alice.
        # Only the lab test harness uses the signing key to prepare this token.
        create_token = flow.service_token("C", "create", analysis_id, subject="1")
        delegated_headers = {"Authorization": "Bearer " + create_token}
        created = requests.post(flow.urls["C"] + "/internal/analyses",
                                headers=delegated_headers, json=document, timeout=5)

        # Read through Component A with the users' ordinary login tokens.
        path = flow.urls["A"] + "/analyses/" + analysis_id
        reads = {
            user: requests.get(path, headers=flow.headers(user), timeout=5)
            for user in ("alice", "bob", "admin")
        }
        anonymous = requests.get(path, timeout=5)
        denied_delete = requests.delete(
            flow.urls["C"] + "/internal/analyses/" + analysis_id,
            headers=delegated_headers, timeout=5,
        )

        observation = {
            "normal_alice_read": alice_normal.status_code,
            "normal_bob_read": bob_normal.status_code,
            "delegated_permission": {"aud": "C", "scope": "create", "sub": "1",
                                     "analysis_id": analysis_id},
            "body_owner_id": "2",
            "create_status": created.status_code,
            "created_owner": created.json().get("owner"),
            "created_error": created.json().get("error"),
            "alice_read": reads["alice"].status_code,
            "bob_read": reads["bob"].status_code,
            "admin_read": reads["admin"].status_code,
            "bob_observed_owner": reads["bob"].json().get("owner"),
            "anonymous_read": anonymous.status_code,
            "create_token_delete": denied_delete.status_code,
        }
        print("COMPOSITION_OBSERVATION " + json.dumps(observation, sort_keys=True), flush=True)

        self.assertEqual(anonymous.status_code, 401, anonymous.text)
        self.assertEqual(denied_delete.status_code, 403, denied_delete.text)
        if created.status_code == 201:
            # Verify the exact wrong-owner record before failing the security
            # expectation. Alice is denied because normal read checks remain.
            self.assertEqual(created.json()["id"], analysis_id)
            self.assertEqual(created.json()["owner"], "2")
            self.assertEqual(reads["alice"].status_code, 404, reads["alice"].text)
            for user in ("bob", "admin"):
                self.assertEqual(reads[user].status_code, 200, reads[user].text)
                self.assertEqual(reads[user].json()["id"], analysis_id)
                self.assertEqual(reads[user].json()["owner"], "2")

        # The same secure expectation is used in both branches.
        self.assertEqual(created.status_code, 400, json.dumps(observation, sort_keys=True))
        self.assertEqual(created.json(), {"error": "INVALID_FIELDS"})
        for user, response in reads.items():
            self.assertEqual(response.status_code, 404, user + ": " + response.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
