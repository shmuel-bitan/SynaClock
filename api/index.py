"""Vercel FastAPI entrypoint preserving the incoming public URL.

Vercel rewrites all routes to this one Python function. The matched path is
forwarded in a private query parameter so Starlette still sees /, /admin,
/static/... and /api/... instead of /api/index.py.
"""
from urllib.parse import parse_qsl, urlencode, unquote
from app.main import app as fastapi_app


async def app(scope, receive, send):
    if scope["type"] not in ("http", "websocket"):
        await fastapi_app(scope, receive, send)
        return

    params = parse_qsl(scope.get("query_string", b"").decode("utf-8"), keep_blank_values=True)
    path_items = [value for key, value in params if key == "__synaclock_path"]
    if path_items:
        public_path = unquote(path_items[-1])
        if not public_path.startswith("/") or public_path.startswith("//"):
            public_path = "/"
        scope = dict(scope)
        scope["path"] = public_path
        scope["raw_path"] = public_path.encode("utf-8")
        scope["query_string"] = urlencode([(key, value) for key, value in params if key != "__synaclock_path"]).encode("utf-8")
    await fastapi_app(scope, receive, send)
