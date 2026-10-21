import os
from pathlib import Path
from time import time
from uuid import uuid4
import jwt

ISSUER = "assignment-api"


def issue(subject, audience, scope, role="user", analysis_id=None, lifetime=900):
    now = int(time())

    claims = {"iss": ISSUER, "aud": audience, "sub": str(subject), "iat": now,
              "exp": now + lifetime, "jti": str(uuid4()), "scope": scope, "role": role}
    
    if analysis_id is not None:
        claims["analysis_id"] = analysis_id

    return jwt.encode(claims, Path(os.environ["PRIVATE_KEY_PATH"]).read_bytes(), algorithm="RS256")


def verify(token, audience, scope):
    claims = jwt.decode(token, Path(os.environ["PUBLIC_KEY_PATH"]).read_bytes(),
                        algorithms=["RS256"], audience=audience, issuer=ISSUER,
                        options={"require": ["iss", "aud", "sub", "iat", "exp", "jti", "scope", "role"]})
    
    if claims["scope"] != scope or claims["role"] not in ("user", "admin"):
        raise PermissionError("Insufficient scope")
    
    return claims
