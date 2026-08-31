"""Minimal FastMCP-compatible MCP server using Python stdlib only."""

import inspect
import json
import logging
import re
import sys
import typing
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, List, Optional, get_type_hints

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = "2024-11-05"


def _type_to_schema(annotation) -> dict:
    if annotation is inspect.Parameter.empty:
        return {"type": "string"}

    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())

    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        return _type_to_schema(non_none[0]) if len(non_none) == 1 else {"type": "string"}

    if origin is list:
        return {"type": "array", "items": _type_to_schema(args[0] if args else str)}

    return {"type": {str: "string", int: "integer", float: "number", bool: "boolean"}.get(annotation, "string")}


def _parse_docstring(doc: str) -> tuple:
    """Return (short_description, {param_name: description})."""
    if not doc:
        return "", {}
    lines = doc.strip().split("\n")
    short = next((l.strip() for l in lines if l.strip()), "")
    params: Dict[str, str] = {}
    in_args = False
    for line in lines:
        stripped = line.strip()
        if stripped == "Args:":
            in_args = True
            continue
        if in_args:
            if stripped and stripped.rstrip(":") in ("Returns", "Raises", "Example", "Examples", "Note", "Notes"):
                break
            m = re.match(r"^(\w+):\s*(.+)", stripped)
            if m:
                params[m.group(1)] = m.group(2)
    return short, params


class FastMCP:
    def __init__(self, name: str):
        self.name = name
        self._tools: Dict[str, Callable] = {}
        self._annotations: Dict[str, Dict[str, bool]] = {}

    def tool(
        self,
        *,
        read_only_hint: bool,
        destructive_hint: bool,
        idempotent_hint: bool,
        open_world_hint: bool,
    ):
        annotations = {
            "readOnlyHint": read_only_hint,
            "destructiveHint": destructive_hint,
            "idempotentHint": idempotent_hint,
            "openWorldHint": open_world_hint,
        }

        def decorator(func: Callable) -> Callable:
            self._tools[func.__name__] = func
            self._annotations[func.__name__] = annotations
            return func
        return decorator

    def _tool_definitions(self) -> list:
        result = []
        for name, func in self._tools.items():
            short_desc, param_descs = _parse_docstring(func.__doc__ or "")
            try:
                hints = get_type_hints(func)
            except Exception:
                hints = {}
            sig = inspect.signature(func)
            properties: Dict[str, Any] = {}
            required: List[str] = []
            for pname, param in sig.parameters.items():
                if pname == "self":
                    continue
                schema = _type_to_schema(hints.get(pname, str))
                if pname in param_descs:
                    schema = dict(schema, description=param_descs[pname])
                properties[pname] = schema
                if param.default is inspect.Parameter.empty:
                    required.append(pname)
            input_schema: Dict[str, Any] = {"type": "object", "properties": properties}
            if required:
                input_schema["required"] = required
            result.append({
                "name": name,
                "description": short_desc,
                "inputSchema": input_schema,
                "annotations": self._annotations[name],
            })
        return result

    def _handle(self, request: dict) -> Optional[dict]:
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params") or {}

        if method == "initialize":
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": self.name, "version": "1.0.0"},
                },
            }

        if method in ("notifications/initialized", "notifications/cancelled", "ping"):
            return None if method != "ping" else {"jsonrpc": "2.0", "id": req_id, "result": {}}

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self._tool_definitions()}}

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments") or {}
            if tool_name not in self._tools:
                return {"jsonrpc": "2.0", "id": req_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
            try:
                result = self._tools[tool_name](**arguments)
                return {"jsonrpc": "2.0", "id": req_id,
                        "result": {"content": [{"type": "text", "text": str(result)}]}}
            except Exception as exc:
                logger.exception("Tool %s raised an error", tool_name)
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}}

        if req_id is not None:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}}
        return None

    def _run_stdio(self) -> None:
        for raw in sys.stdin:
            raw = raw.strip()
            if not raw:
                continue
            try:
                request = json.loads(raw)
            except json.JSONDecodeError as exc:
                logger.warning("Invalid JSON input: %s", exc)
                continue
            response = self._handle(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

    def _run_http(self, host: str, port: int) -> None:
        mcp = self

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt: str, *args: Any) -> None:
                logger.debug(fmt, *args)

            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                try:
                    request = json.loads(body)
                except json.JSONDecodeError:
                    self.send_error(400, "Bad JSON")
                    return

                response = mcp._handle(request)

                if response is None:
                    self.send_response(202)
                    self.end_headers()
                    return

                payload = json.dumps(response).encode()
                want_sse = "text/event-stream" in self.headers.get("Accept", "")

                if want_sse:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    self.wfile.write(b"data: " + payload + b"\n\n")
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)

        server = HTTPServer((host, port), _Handler)
        logger.info("MCP HTTP server listening on %s:%d", host, port)
        server.serve_forever()

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000,
            stateless: bool = False) -> None:
        if transport == "streamable-http":
            self._run_http(host, port)
        else:
            self._run_stdio()
