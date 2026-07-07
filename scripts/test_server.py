#!/usr/bin/env python3
"""
Test script for Mastodon MCP Server

Tests tool registration, parameter signatures, version consistency,
helper functions, and live connectivity to a Mastodon instance.

Author: Vítězslav Dvořák
License: MIT
"""

import asyncio
import html
import inspect
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PASS = "✓"
FAIL = "✗"
SKIP = "⚠"

_errors = 0


def ok(msg: str) -> None:
    print(f"  {PASS} {msg}")


def fail(msg: str) -> None:
    global _errors
    _errors += 1
    print(f"  {FAIL} {msg}", file=sys.stderr)


def skip(msg: str) -> None:
    print(f"  {SKIP} {msg}")


# ─── SECTION 1: module import ─────────────────────────────────────────────────

print("=" * 60)
print("1. Module import")
print("=" * 60)

try:
    from mastodon_mcp_server.server import mcp, get_client, fmt, is_read_only, validate_write
    ok("mastodon_mcp_server.server imported")
except Exception as e:
    fail(f"Import failed: {e}")
    sys.exit(1)

try:
    from mastodon_mcp_server._mcp import FastMCP
    ok("mastodon_mcp_server._mcp (stdlib FastMCP) imported")
except Exception as e:
    fail(f"_mcp import failed: {e}")

print()

# ─── SECTION 2: tool registration ─────────────────────────────────────────────

print("=" * 60)
print("2. Tool registration")
print("=" * 60)

EXPECTED_TOOLS = [
    "instance_info",
    "account_verify", "account_get", "account_search", "account_statuses",
    "account_followers", "account_following",
    "account_follow", "account_unfollow",
    "account_mute", "account_unmute",
    "account_block", "account_unblock",
    "account_relationships", "account_update",
    "timeline_home", "timeline_local", "timeline_public", "timeline_hashtag",
    "status_get", "status_context", "status_post", "status_delete",
    "status_favourite", "status_unfavourite",
    "status_reblog", "status_unreblog",
    "status_bookmark", "status_unbookmark",
    "status_favourited_by", "status_reblogged_by",
    "notifications_get", "notification_dismiss", "notifications_clear",
    "search",
    "trending_tags", "trending_statuses", "trending_links",
    "favourites", "bookmarks",
    "lists_get", "list_accounts", "list_create", "list_delete",
    "list_accounts_add", "list_accounts_delete",
    "poll_vote",
    "follow_requests", "follow_request_authorize", "follow_request_reject",
    "mutes", "blocks",
    "media_post",
    "directory",
    "status_update", "status_history", "status_source", "status_translate",
    "conversations", "scheduled_statuses", "scheduled_status_update",
    "scheduled_status_delete", "notifications_unread_count",
    "account_lookup", "status_pin", "status_unpin", "status_mute",
    "status_unmute", "tag_follow", "tag_unfollow",
]

# Support both bundled _mcp.FastMCP (has _tool_definitions) and fastmcp (has list_tools)
if hasattr(mcp, "list_tools"):
    tools = asyncio.run(mcp.list_tools())
    tool_names = {t.name for t in tools}
else:
    tool_names = {t["name"] for t in mcp._tool_definitions()}

for name in EXPECTED_TOOLS:
    if name in tool_names:
        ok(name)
    else:
        fail(f"Missing tool: {name}")

extra = tool_names - set(EXPECTED_TOOLS)
if extra:
    skip(f"Extra tools (not in expected list): {sorted(extra)}")

print(f"\n  Total: {len(tool_names)} tools registered, {len(EXPECTED_TOOLS)} expected")
print()

# ─── SECTION 3: helper functions ──────────────────────────────────────────────

print("=" * 60)
print("3. Helper functions")
print("=" * 60)

# fmt
result = fmt({"key": "value", "num": 42})
try:
    parsed = json.loads(result)
    assert parsed == {"key": "value", "num": 42}
    ok("fmt() produces valid JSON")
except Exception as e:
    fail(f"fmt() error: {e}")

result = fmt({"date": __import__("datetime").datetime(2026, 1, 1)})
try:
    json.loads(result)
    ok("fmt() handles non-serialisable types via default=str")
except Exception as e:
    fail(f"fmt() default=str error: {e}")

# is_read_only
old_val = os.environ.get("READ_ONLY")
try:
    os.environ["READ_ONLY"] = "true"
    if is_read_only() is not True:
        fail("READ_ONLY=true should return True")
    os.environ["READ_ONLY"] = "false"
    if is_read_only() is not False:
        fail("READ_ONLY=false should return False")
    os.environ["READ_ONLY"] = "1"
    if is_read_only() is not True:
        fail("READ_ONLY=1 should return True")
finally:
    if old_val is None:
        if "READ_ONLY" in os.environ:
            del os.environ["READ_ONLY"]
    else:
        os.environ["READ_ONLY"] = old_val
ok("is_read_only() handles true/false/1")

# validate_write blocks in read-only mode
os.environ["READ_ONLY"] = "true"
try:
    validate_write()
    fail("validate_write() should raise in read-only mode")
except ValueError:
    ok("validate_write() raises ValueError in read-only mode")
finally:
    os.environ["READ_ONLY"] = "false"

print()

# ─── SECTION 4: version consistency ───────────────────────────────────────────

print("=" * 60)
print("4. Version consistency")
print("=" * 60)

try:
    import tomllib
except ImportError:
    import tomllib  # Python 3.11+

try:
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    pyproject_version = pyproject["project"]["version"]
    ok(f"pyproject.toml version: {pyproject_version}")
except Exception as e:
    fail(f"Could not read pyproject.toml: {e}")
    pyproject_version = None

try:
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "mastodon_mcp_server.server", "--version"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        fail(f"CLI --version failed: {(result.stderr or result.stdout).strip()}")
    else:
        cli_version = result.stdout.strip().split()[-1]
        ok(f"CLI --version: {cli_version}")
        if pyproject_version and cli_version != pyproject_version:
            fail(f"Version mismatch: pyproject={pyproject_version} cli={cli_version}")
        elif pyproject_version:
            ok("Versions match")
except Exception as e:
    skip(f"CLI version check skipped: {e}")

print()

# ─── SECTION 5: live connection ───────────────────────────────────────────────

print("=" * 60)
print("5. Live Mastodon connection")
print("=" * 60)

instance = os.getenv("MASTODON_INSTANCE")
token = os.getenv("MASTODON_ACCESS_TOKEN")

if not instance or not token:
    skip("MASTODON_INSTANCE / MASTODON_ACCESS_TOKEN not set — skipping live tests")
    print()
else:
    try:
        client = get_client()
        ok(f"Connected to {instance}")
    except Exception as e:
        fail(f"Connection failed: {e}")
        print()
        sys.exit(_errors)

    # 5a. account_verify
    try:
        me = client.account_verify_credentials()
        ok(f"account_verify_credentials(): @{me['username']}")
    except Exception as e:
        fail(f"account_verify_credentials(): {e}")
        me = None

    # 5b. instance info
    try:
        info = client.instance()
        title = info.get("title") or info.get("info", {}).get("title", "?")
        ok(f"instance(): {title}")
    except Exception as e:
        fail(f"instance(): {e}")

    # 5c. home timeline (read-only, limit=1)
    try:
        timeline = client.timeline_home(limit=1)
        ok(f"timeline_home(): {len(timeline)} status(es) returned")
    except Exception as e:
        fail(f"timeline_home(): {e}")

    # 5d. search
    try:
        results = client.search(q="mastodon")
        n = len(results.get("accounts", []))
        ok(f"search('mastodon'): {n} account(s)")
    except Exception as e:
        fail(f"search(): {e}")

    # 5e. trending tags
    try:
        tags = client.trending_tags(limit=3)
        ok(f"trending_tags(): {len(tags)} tag(s) — first: #{tags[0]['name'] if tags else '?'}")
    except Exception as e:
        fail(f"trending_tags(): {e}")

    # 5f. own statuses
    if me:
        try:
            statuses = client.account_statuses(me["id"], limit=1)
            if statuses:
                s = statuses[0]
                text = html.unescape(re.sub("<[^>]+>", "", s.get("content") or "")).strip()
                ok(f"account_statuses(): latest post — {text[:60] or '(reblog)'}")
            else:
                ok("account_statuses(): no posts found")
        except Exception as e:
            fail(f"account_statuses(): {e}")

    print()

# ─── SUMMARY ──────────────────────────────────────────────────────────────────

print("=" * 60)
if _errors == 0:
    print(f"{PASS} All tests passed")
else:
    print(f"{FAIL} {_errors} test(s) failed")
print("=" * 60)

sys.exit(_errors)
