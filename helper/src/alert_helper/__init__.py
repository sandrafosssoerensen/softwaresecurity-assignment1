"""Small, separately installed alert-data dependency."""
from datetime import datetime
from ipaddress import ip_address


def text(value):
    return isinstance(value, str) and bool(value.strip())


def integer(value, low, high=None):
    return type(value) is int and value >= low and (high is None or value <= high)


def select_alert(event):
    if not isinstance(event, dict) or event.get("event_type") != "alert":
        raise ValueError("Expected an alert event")
    detail = event.get("alert")
    if not isinstance(detail, dict):
        raise ValueError("Missing alert object")
    if not text(detail.get("signature")) or not integer(detail.get("signature_id"), 1):
        raise ValueError("Invalid signature or signature_id")
    if not integer(detail.get("severity"), 1, 3) or not text(event.get("proto")):
        raise ValueError("Invalid severity or protocol")
    timestamp = event.get("timestamp")
    if not text(timestamp) or datetime.fromisoformat(timestamp.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("Expected timestamp with timezone")
    for field in ("src_ip", "dest_ip"):
        if not isinstance(event.get(field), str):
            raise ValueError("Expected IP address")
        ip_address(event[field])
    result = {k: event[k] for k in ("event_type", "timestamp", "src_ip", "dest_ip", "proto")}
    result["alert"] = {k: detail[k] for k in ("signature_id", "signature", "severity")}
    for field in ("src_port", "dest_port"):
        if field in event:
            if not integer(event[field], 0, 65535):
                raise ValueError("Invalid port")
            result[field] = event[field]
    return result


def validate_result(result, selected):
    names = {"observation", "interpretation", "uncertainty", "recommended_actions", "evidence_fields"}
    if not isinstance(result, dict) or set(result) != names:
        raise ValueError("Unexpected result fields")
    for field in ("observation", "interpretation", "uncertainty"):
        if not text(result[field]):
            raise ValueError("Invalid result text")
    for field in ("recommended_actions", "evidence_fields"):
        value = result[field]
        if not isinstance(value, list) or not value or not all(text(v) for v in value):
            raise ValueError("Invalid result list")
    allowed = set(selected) - {"alert"}
    allowed |= {"alert." + k for k in selected["alert"]}
    if not set(result["evidence_fields"]) <= allowed:
        raise ValueError("Unknown evidence field")
    return result
