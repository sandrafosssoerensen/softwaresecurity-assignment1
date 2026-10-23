#!/usr/bin/env bash
# Manual CWE-20 check through the public API: start A, B, C as normal servers,
# log in as bob, send an alert with 66,000 padding characters to Component A.
WT="$1"; LABEL="$2"; PY="$3"
cd "$WT"
W=$(cygpath -w "$WT")
echo "===== $LABEL ====="
"$PY" scripts/setup_lab.py >/dev/null
pids=()
for svc in C B A; do
  port=$([ $svc = A ] && echo 8000 || ([ $svc = B ] && echo 8001 || echo 8002))
  env SERVICE=$svc PUBLIC_KEY_PATH="$W\.runtime\keys\public.pem" \
      $([ $svc = A ] && echo PRIVATE_KEY_PATH="$W\.runtime\keys\private.pem") \
      "$PY" manage.py runserver 127.0.0.1:$port --noreload > ".runtime/$svc.log" 2>&1 &
  pids+=($!)
done
for port in 8000 8001 8002; do
  for i in $(seq 1 60); do curl -s -m 2 "http://127.0.0.1:$port/health" >/dev/null && break; sleep 0.5; done
  echo "health $port: $(curl -s http://127.0.0.1:$port/health)"
done
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/token -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"Lab-only-Password-123!"}' | "$PY" -c "import json,sys;print(json.load(sys.stdin)['access_token'])")
echo "logged in as bob (ordinary user): token length ${#TOKEN}"
"$PY" -c "import json;d=json.load(open('examples/request.json'));d['alert']['padding']='x'*66000;open('.runtime/padded.json','w').write(json.dumps(d))"
echo "request body size: $(wc -c < .runtime/padded.json) bytes (Django limit 131072, processing limit 65536)"
echo "> POST http://127.0.0.1:8000/analyses  (Authorization: Bearer <bob token>)"
RESP=$(curl -s -w '\nHTTP_STATUS=%{http_code}' -X POST http://127.0.0.1:8000/analyses \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" --data-binary @.runtime/padded.json)
echo "$RESP" | tail -1
echo "response body (first 120 chars): $(echo "$RESP" | head -1 | cut -c1-120)"
echo "Component B access log:"; grep "internal/analyze" .runtime/B.log
echo "Component C access log:"; grep "POST /internal/analyses" .runtime/C.log || echo "  (no store request reached C)"
kill "${pids[@]}" 2>/dev/null; wait 2>/dev/null
