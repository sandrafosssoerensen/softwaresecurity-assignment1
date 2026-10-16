"""Minimal synchronous A/B/C request flow. Lab server only."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from time import monotonic
from uuid import UUID, uuid4
import jwt
import requests
from django.conf import settings
from django.core.exceptions import RequestDataTooBig
from django.http import JsonResponse
from alert_helper import select_alert, validate_result
from .security import issue, verify


class ApiError(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code


def endpoint(function):
    @wraps(function)
    def handle(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except ApiError as exc:
            return JsonResponse({"error": exc.code}, status=exc.status)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "INVALID_TOKEN"}, status=401)
        except PermissionError:
            return JsonResponse({"error": "FORBIDDEN"}, status=403)
        except RequestDataTooBig:
            return JsonResponse({"error": "INPUT_TOO_LARGE"}, status=413)
        except requests.Timeout:
            return JsonResponse({"error": "MODEL_OR_SERVICE_TIMEOUT"}, status=504)
        except requests.RequestException:
            return JsonResponse({"error": "SERVICE_UNAVAILABLE"}, status=503)
        except sqlite3.IntegrityError:
            return JsonResponse({"error": "DUPLICATE_ANALYSIS"}, status=409)
        except (ValueError, TypeError, KeyError):
            return JsonResponse({"error": "INVALID_INPUT"}, status=400)
    return handle


def body(request, fields):
    if request.content_type != "application/json":
        raise ApiError(400, "EXPECTED_JSON")
    data = json.loads(request.body)
    if not isinstance(data, dict) or set(data) != set(fields):
        raise ApiError(400, "INVALID_FIELDS")
    return data


def authority(request, audience, scope):
    value = request.headers.get("Authorization", "")
    if not value.startswith("Bearer "):
        raise ApiError(401, "MISSING_TOKEN")
    return verify(value[7:], audience, scope)


def relay(method, base, path, token, data=None):
    response = requests.request(method, base + path, json=data,
                                headers={"Authorization": "Bearer " + token}, timeout=(5, 310))
    if response.status_code == 204:
        return JsonResponse({}, status=204)
    return JsonResponse(response.json(), safe=isinstance(response.json(), dict), status=response.status_code)


@endpoint
def health(request):
    return JsonResponse({"service": settings.SERVICE, "status": "ok"})


@endpoint
def login(request):
    if request.method != "POST":
        raise ApiError(405, "METHOD_NOT_ALLOWED")
    data = body(request, {"username", "password"})
    if not all(isinstance(data[k], str) for k in data):
        raise ApiError(400, "INVALID_CREDENTIAL_FORMAT")
    from django.contrib.auth import authenticate
    user = authenticate(username=data["username"], password=data["password"])
    if user is None:
        raise ApiError(401, "INVALID_CREDENTIALS")
    return JsonResponse({"access_token": issue(user.pk, "A", "user", "admin" if user.is_staff else "user"),
                         "token_type": "Bearer", "expires_in": 900})


@endpoint
def public_analyses(request, analysis_id=None):
    user = authority(request, "A", "user")
    if request.method == "POST" and analysis_id is None:
        data = body(request, {"alert"})
        select_alert(data["alert"])
        analysis_id = str(uuid4())
        execute = issue(user["sub"], "B", "execute", analysis_id=analysis_id, lifetime=600)
        create = issue(user["sub"], "C", "create", analysis_id=analysis_id, lifetime=600)
        return relay("POST", os.environ.get("B_URL", "http://127.0.0.1:8001"), "/internal/analyze", execute,
                     {"alert": data["alert"], "storage_token": create})
    if request.method == "GET":
        scope = "read" if analysis_id else "list"
    elif request.method == "DELETE" and analysis_id:
        if user["role"] != "admin":
            raise ApiError(403, "ADMIN_REQUIRED")
        scope = "delete"
    else:
        raise ApiError(405, "METHOD_NOT_ALLOWED")
    token = issue(user["sub"], "C", scope, user["role"], analysis_id, lifetime=60)
    path = "/internal/analyses" + ("/" + analysis_id if analysis_id else "")
    return relay(request.method, os.environ.get("C_URL", "http://127.0.0.1:8002"), path, token)


@endpoint
def analyze(request):
    if request.method != "POST":
        raise ApiError(405, "METHOD_NOT_ALLOWED")
    claims = authority(request, "B", "execute")
    data = body(request, {"alert", "storage_token"})
    encoded = json.dumps(data["alert"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    # CWE-20 vulnerable experiment: temporarily comment out the active check.
    # if len(encoded) > 65536:
    #     raise ApiError(413, "INPUT_TOO_LARGE")
    if len(encoded) > 65536:
        raise ApiError(413, "INPUT_TOO_LARGE")
    selected = select_alert(data["alert"])
    target = verify(data["storage_token"], "C", "create")
    if (target["sub"], target.get("analysis_id")) != (claims["sub"], claims.get("analysis_id")):
        raise ApiError(403, "OWNER_OR_RESOURCE_MISMATCH")
    UUID(claims["analysis_id"])
    started = monotonic()
    # First milestone: deterministic stub. Real Ollama is a later integration step.
    result = {"observation": "The alert reports: " + selected["alert"]["signature"],
              "interpretation": "Development stub: no real model interpretation has been performed.",
              "uncertainty": "This alert alone does not establish attack success.",
              "recommended_actions": ["Have an analyst review the alert and supporting network evidence."],
              "evidence_fields": ["alert.signature"]}
    validate_result(result, selected)
    document = {"original_alert": data["alert"], "model_input": selected, "model": "development-stub",
                "prompt_version": "stub-v1", "settings": {}, "latency_seconds": monotonic()-started,
                "created_at": datetime.now(timezone.utc).isoformat(), "result": result}
    return relay("POST", os.environ.get("C_URL", "http://127.0.0.1:8002"), "/internal/analyses",
                 data["storage_token"], document)


@endpoint
def stored_analyses(request, analysis_id=None):
    from . import store
    scopes = {"GET": "read" if analysis_id else "list", "POST": "create", "DELETE": "delete"}
    if request.method not in scopes or (request.method == "POST" and analysis_id):
        raise ApiError(405, "METHOD_NOT_ALLOWED")
    claims = authority(request, "C", scopes[request.method])
    if analysis_id:
        UUID(analysis_id)
        if claims.get("analysis_id") != analysis_id:
            raise ApiError(403, "RESOURCE_MISMATCH")
    admin = claims["role"] == "admin"
    if request.method == "POST":
        document = body(request, {"original_alert", "model_input", "model", "prompt_version", "settings",
                                          "latency_seconds", "created_at", "result"})
        # CWE-807 vulnerable experiment: accept an untrusted owner_id field.
        # document = body(request, {"original_alert", "model_input", "model", "prompt_version", "settings",
        #                           "latency_seconds", "created_at", "result", "owner_id"})
        selected = select_alert(document["original_alert"])
        if document["model_input"] != selected:
            raise ApiError(400, "MODEL_INPUT_MISMATCH")
        validate_result(document["result"], selected)
        UUID(claims["analysis_id"])
        store.create(claims["analysis_id"], claims["sub"], document)
        # CWE-807 vulnerable experiment: trust owner_id instead of the token claim.
        # store.create(claims["analysis_id"], document["owner_id"], document)
        return JsonResponse({"id": claims["analysis_id"], "owner": claims["sub"], **document}, status=201)
    if request.method == "GET" and analysis_id is None:
        return JsonResponse({"analyses": store.listing(claims["sub"], admin)})
    if request.method == "DELETE":
        if not admin:
            raise ApiError(403, "ADMIN_REQUIRED")
        if not store.delete(analysis_id):
            raise ApiError(404, "NOT_FOUND")
        return JsonResponse({}, status=204)
    result = store.read(analysis_id, claims["sub"], admin)
    if result is None:
        raise ApiError(404, "NOT_FOUND")
    return JsonResponse(result)
