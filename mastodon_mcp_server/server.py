#!/usr/bin/env python3
"""
Mastodon MCP Server - Integration with Mastodon API using Mastodon.py

This server provides access to Mastodon social network functionality through
the Model Context Protocol (MCP), enabling AI assistants and other tools to
interact with Mastodon instances.

Author: Vítězslav Dvořák
License: MIT
"""

import argparse
import os
import json
import logging
from typing import Any, Dict, List, Optional
from mastodon_mcp_server._mcp import FastMCP
from mastodon import Mastodon, MastodonError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Mastodon MCP Server")

_client: Optional[Mastodon] = None


def get_client() -> Mastodon:
    global _client

    if _client is None:
        instance = os.getenv("MASTODON_INSTANCE")
        access_token = os.getenv("MASTODON_ACCESS_TOKEN")

        if not instance:
            raise ValueError("MASTODON_INSTANCE environment variable is required")
        if not access_token:
            raise ValueError("MASTODON_ACCESS_TOKEN environment variable is required")

        logger.info(f"Connecting to Mastodon instance: {instance}")
        _client = Mastodon(
            access_token=access_token,
            api_base_url=instance,
        )
        logger.info("Mastodon client initialized")

    return _client


def is_read_only() -> bool:
    return os.getenv("READ_ONLY", "false").lower() in ("true", "1", "yes")


def validate_write() -> None:
    if is_read_only():
        raise ValueError("Server is in read-only mode - write operations are not allowed")


def fmt(data: Any) -> str:
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


# ─── INSTANCE ────────────────────────────────────────────────────────────────

@mcp.tool()
def instance_info() -> str:
    """Get information about the connected Mastodon instance.

    Returns:
        str: JSON with instance name, description, version, rules, etc.
    """
    client = get_client()
    return fmt(client.instance())


# ─── ACCOUNT ─────────────────────────────────────────────────────────────────

@mcp.tool()
def account_verify() -> str:
    """Get the authenticated account's own profile.

    Returns:
        str: JSON with account id, username, display_name, followers_count, etc.
    """
    client = get_client()
    return fmt(client.account_verify_credentials())


@mcp.tool()
def account_get(account_id: str) -> str:
    """Get a Mastodon account by its numeric ID.

    Args:
        account_id: Numeric account ID.

    Returns:
        str: JSON with account details.
    """
    client = get_client()
    return fmt(client.account(account_id))


@mcp.tool()
def account_search(query: str, limit: int = 10, resolve: bool = False) -> str:
    """Search for accounts by username or display name.

    Args:
        query: Search string (username or display name).
        limit: Maximum number of results (default 10, max 80).
        resolve: Whether to resolve non-local accounts (default False).

    Returns:
        str: JSON list of matching accounts.
    """
    client = get_client()
    return fmt(client.account_search(query, limit=limit, resolve=resolve))


@mcp.tool()
def account_statuses(
    account_id: str,
    limit: int = 20,
    only_media: bool = False,
    exclude_replies: bool = False,
    exclude_reblogs: bool = False,
) -> str:
    """Get statuses posted by a specific account.

    Args:
        account_id: Numeric account ID.
        limit: Maximum number of results (default 20, max 40).
        only_media: Only return statuses with media (default False).
        exclude_replies: Exclude replies (default False).
        exclude_reblogs: Exclude reblogs (default False).

    Returns:
        str: JSON list of statuses.
    """
    client = get_client()
    return fmt(client.account_statuses(
        account_id,
        limit=limit,
        only_media=only_media,
        exclude_replies=exclude_replies,
        exclude_reblogs=exclude_reblogs,
    ))


@mcp.tool()
def account_followers(account_id: str, limit: int = 40) -> str:
    """Get followers of an account.

    Args:
        account_id: Numeric account ID.
        limit: Maximum number of results (default 40, max 80).

    Returns:
        str: JSON list of follower accounts.
    """
    client = get_client()
    return fmt(client.account_followers(account_id, limit=limit))


@mcp.tool()
def account_following(account_id: str, limit: int = 40) -> str:
    """Get accounts that a given account follows.

    Args:
        account_id: Numeric account ID.
        limit: Maximum number of results (default 40, max 80).

    Returns:
        str: JSON list of followed accounts.
    """
    client = get_client()
    return fmt(client.account_following(account_id, limit=limit))


@mcp.tool()
def account_follow(account_id: str) -> str:
    """Follow an account.

    Args:
        account_id: Numeric account ID to follow.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.account_follow(account_id))


@mcp.tool()
def account_unfollow(account_id: str) -> str:
    """Unfollow an account.

    Args:
        account_id: Numeric account ID to unfollow.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.account_unfollow(account_id))


@mcp.tool()
def account_mute(account_id: str) -> str:
    """Mute an account.

    Args:
        account_id: Numeric account ID to mute.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.account_mute(account_id))


@mcp.tool()
def account_unmute(account_id: str) -> str:
    """Unmute an account.

    Args:
        account_id: Numeric account ID to unmute.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.account_unmute(account_id))


@mcp.tool()
def account_block(account_id: str) -> str:
    """Block an account.

    Args:
        account_id: Numeric account ID to block.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.account_block(account_id))


@mcp.tool()
def account_unblock(account_id: str) -> str:
    """Unblock an account.

    Args:
        account_id: Numeric account ID to unblock.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.account_unblock(account_id))


@mcp.tool()
def account_relationships(account_ids: List[str]) -> str:
    """Get the authenticated user's relationship to one or more accounts.

    Args:
        account_ids: List of numeric account IDs.

    Returns:
        str: JSON list of relationship objects.
    """
    client = get_client()
    return fmt(client.account_relationships(account_ids))


@mcp.tool()
def account_update(
    display_name: Optional[str] = None,
    note: Optional[str] = None,
    bot: Optional[bool] = None,
    locked: Optional[bool] = None,
) -> str:
    """Update the authenticated account's profile.

    Args:
        display_name: New display name.
        note: New bio/note (profile description).
        bot: Mark account as a bot (True/False).
        locked: Require approval for follow requests (True/False).

    Returns:
        str: JSON with updated account details.
    """
    validate_write()
    client = get_client()
    kwargs: Dict[str, Any] = {}
    if display_name is not None:
        kwargs["display_name"] = display_name
    if note is not None:
        kwargs["note"] = note
    if bot is not None:
        kwargs["bot"] = bot
    if locked is not None:
        kwargs["locked"] = locked
    return fmt(client.account_update_credentials(**kwargs))


# ─── TIMELINE ─────────────────────────────────────────────────────────────────

@mcp.tool()
def timeline_home(limit: int = 20) -> str:
    """Get the authenticated user's home timeline.

    Args:
        limit: Maximum number of statuses (default 20, max 40).

    Returns:
        str: JSON list of statuses from followed accounts.
    """
    client = get_client()
    return fmt(client.timeline_home(limit=limit))


@mcp.tool()
def timeline_local(limit: int = 20) -> str:
    """Get the local (instance) public timeline.

    Args:
        limit: Maximum number of statuses (default 20, max 40).

    Returns:
        str: JSON list of public statuses from the local instance.
    """
    client = get_client()
    return fmt(client.timeline_local(limit=limit))


@mcp.tool()
def timeline_public(limit: int = 20, remote: bool = False) -> str:
    """Get the federated public timeline.

    Args:
        limit: Maximum number of statuses (default 20, max 40).
        remote: Only show remote statuses (default False).

    Returns:
        str: JSON list of public federated statuses.
    """
    client = get_client()
    return fmt(client.timeline_public(limit=limit, remote=remote))


@mcp.tool()
def timeline_hashtag(hashtag: str, limit: int = 20, local: bool = False) -> str:
    """Get statuses with a specific hashtag.

    Args:
        hashtag: Hashtag to search (without the # prefix).
        limit: Maximum number of statuses (default 20, max 40).
        local: Only show statuses from the local instance (default False).

    Returns:
        str: JSON list of statuses with the hashtag.
    """
    client = get_client()
    return fmt(client.timeline_hashtag(hashtag, limit=limit, local=local))


# ─── STATUSES ────────────────────────────────────────────────────────────────

@mcp.tool()
def status_get(status_id: str) -> str:
    """Get a single status by ID.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with status details.
    """
    client = get_client()
    return fmt(client.status(status_id))


@mcp.tool()
def status_context(status_id: str) -> str:
    """Get ancestors and descendants of a status (thread context).

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with 'ancestors' and 'descendants' lists.
    """
    client = get_client()
    return fmt(client.status_context(status_id))


@mcp.tool()
def status_post(
    status: Optional[str] = None,
    content: Optional[str] = None,
    visibility: str = "public",
    spoiler_text: Optional[str] = None,
    in_reply_to_id: Optional[str] = None,
    sensitive: bool = False,
    language: Optional[str] = None,
    media_ids: Optional[List[str]] = None,
) -> str:
    """Post a new status (toot).

    Args:
        status: Text content of the status (preferred argument name).
        content: Backward-compatible alias for status text.
        visibility: 'public', 'unlisted', 'private', or 'direct' (default 'public').
        spoiler_text: Content warning / spoiler text shown before the status.
        in_reply_to_id: Numeric ID of the status to reply to.
        sensitive: Mark media as sensitive (default False).
        language: ISO 639-1 language code (e.g. 'en', 'cs').
        media_ids: List of media attachment IDs to attach.

    Returns:
        str: JSON with the newly created status.
    """
    validate_write()
    text = status if status is not None else content
    if not text:
        raise ValueError("Either 'status' or 'content' must be provided")

    client = get_client()
    return fmt(client.status_post(
        text,
        visibility=visibility,
        spoiler_text=spoiler_text,
        in_reply_to_id=in_reply_to_id,
        sensitive=sensitive,
        language=language,
        media_ids=media_ids,
    ))


@mcp.tool()
def status_delete(status_id: str) -> str:
    """Delete a status posted by the authenticated account.

    Args:
        status_id: Numeric ID of the status to delete.

    Returns:
        str: JSON with the deleted status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_delete(status_id))


@mcp.tool()
def status_favourite(status_id: str) -> str:
    """Favourite (like) a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the favourited status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_favourite(status_id))


@mcp.tool()
def status_unfavourite(status_id: str) -> str:
    """Remove a favourite from a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_unfavourite(status_id))


@mcp.tool()
def status_reblog(status_id: str, visibility: str = "public") -> str:
    """Reblog (boost) a status.

    Args:
        status_id: Numeric status ID.
        visibility: Visibility of the reblog: 'public', 'unlisted', or 'private'.

    Returns:
        str: JSON with the reblog status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_reblog(status_id, visibility=visibility))


@mcp.tool()
def status_unreblog(status_id: str) -> str:
    """Remove a reblog (unboost) of a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the original status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_unreblog(status_id))


@mcp.tool()
def status_bookmark(status_id: str) -> str:
    """Bookmark a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the bookmarked status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_bookmark(status_id))


@mcp.tool()
def status_unbookmark(status_id: str) -> str:
    """Remove a bookmark from a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_unbookmark(status_id))


@mcp.tool()
def status_favourited_by(status_id: str) -> str:
    """Get accounts that favourited a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON list of accounts.
    """
    client = get_client()
    return fmt(client.status_favourited_by(status_id))


@mcp.tool()
def status_reblogged_by(status_id: str) -> str:
    """Get accounts that reblogged a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON list of accounts.
    """
    client = get_client()
    return fmt(client.status_reblogged_by(status_id))


# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

@mcp.tool()
def notifications_get(
    limit: int = 20,
    exclude_types: Optional[List[str]] = None,
) -> str:
    """Get notifications for the authenticated account.

    Args:
        limit: Maximum number of notifications (default 20, max 30).
        exclude_types: Types to exclude: 'follow', 'favourite', 'reblog',
                       'mention', 'poll', 'follow_request', 'update', 'status'.

    Returns:
        str: JSON list of notification objects.
    """
    client = get_client()
    kwargs: Dict[str, Any] = {"limit": limit}
    if exclude_types:
        kwargs["exclude_types"] = exclude_types
    return fmt(client.notifications(**kwargs))


@mcp.tool()
def notification_dismiss(notification_id: str) -> str:
    """Dismiss (clear) a single notification.

    Args:
        notification_id: Numeric notification ID.

    Returns:
        str: JSON confirmation.
    """
    validate_write()
    client = get_client()
    client.notifications_dismiss(notification_id)
    return fmt({"success": True, "notification_id": notification_id})


@mcp.tool()
def notifications_clear() -> str:
    """Dismiss all notifications for the authenticated account.

    Returns:
        str: JSON confirmation.
    """
    validate_write()
    client = get_client()
    client.notifications_clear()
    return fmt({"success": True})


# ─── SEARCH ──────────────────────────────────────────────────────────────────

@mcp.tool()
def search(
    query: str,
    resolve: bool = False,
    limit: int = 20,
    search_type: Optional[str] = None,
) -> str:
    """Search Mastodon for accounts, statuses, and hashtags.

    Args:
        query: Search string.
        resolve: Resolve non-local accounts/statuses (default False).
        limit: Maximum results per category (default 20).
        search_type: Restrict to 'accounts', 'statuses', or 'hashtags'.
                     None returns all types.

    Returns:
        str: JSON with 'accounts', 'statuses', and 'hashtags' lists.
    """
    client = get_client()
    kwargs: Dict[str, Any] = {"q": query, "resolve": resolve}
    if search_type:
        kwargs["result_type"] = search_type
    # Mastodon.py's search()/search_v2() has no `limit` parameter, even
    # though the underlying /api/v2/search endpoint accepts one, so results
    # are truncated client-side instead of being forwarded to the library.
    results = client.search(**kwargs)
    for category in ("accounts", "statuses", "hashtags"):
        if category in results:
            results[category] = results[category][:limit]
    return fmt(results)


# ─── TRENDING ─────────────────────────────────────────────────────────────────

@mcp.tool()
def trending_tags(limit: int = 10) -> str:
    """Get trending hashtags on the instance.

    Args:
        limit: Maximum number of tags (default 10).

    Returns:
        str: JSON list of trending tag objects with name and history.
    """
    client = get_client()
    return fmt(client.trending_tags(limit=limit))


@mcp.tool()
def trending_statuses(limit: int = 20) -> str:
    """Get trending statuses on the instance.

    Args:
        limit: Maximum number of statuses (default 20).

    Returns:
        str: JSON list of trending statuses.
    """
    client = get_client()
    return fmt(client.trending_statuses(limit=limit))


@mcp.tool()
def trending_links(limit: int = 10) -> str:
    """Get trending links (articles) on the instance.

    Args:
        limit: Maximum number of links (default 10).

    Returns:
        str: JSON list of trending link card objects.
    """
    client = get_client()
    return fmt(client.trending_links(limit=limit))


# ─── FAVOURITES & BOOKMARKS ──────────────────────────────────────────────────

@mcp.tool()
def favourites(limit: int = 20) -> str:
    """Get statuses favourited by the authenticated account.

    Args:
        limit: Maximum number of results (default 20, max 40).

    Returns:
        str: JSON list of statuses.
    """
    client = get_client()
    return fmt(client.favourites(limit=limit))


@mcp.tool()
def bookmarks(limit: int = 20) -> str:
    """Get statuses bookmarked by the authenticated account.

    Args:
        limit: Maximum number of results (default 20, max 40).

    Returns:
        str: JSON list of statuses.
    """
    client = get_client()
    return fmt(client.bookmarks(limit=limit))


# ─── LISTS ───────────────────────────────────────────────────────────────────

@mcp.tool()
def lists_get() -> str:
    """Get all lists created by the authenticated account.

    Returns:
        str: JSON list of list objects with id and title.
    """
    client = get_client()
    return fmt(client.lists())


@mcp.tool()
def list_accounts(list_id: str, limit: int = 40) -> str:
    """Get accounts in a specific list.

    Args:
        list_id: Numeric list ID.
        limit: Maximum number of accounts (default 40).

    Returns:
        str: JSON list of account objects.
    """
    client = get_client()
    return fmt(client.list_accounts(list_id, limit=limit))


@mcp.tool()
def list_create(title: str, replies_policy: str = "list") -> str:
    """Create a new list.

    Args:
        title: Title of the list.
        replies_policy: 'followed', 'list', or 'none' (default 'list').

    Returns:
        str: JSON with the newly created list.
    """
    validate_write()
    client = get_client()
    return fmt(client.list_create(title, replies_policy=replies_policy))


@mcp.tool()
def list_delete(list_id: str) -> str:
    """Delete a list.

    Args:
        list_id: Numeric list ID.

    Returns:
        str: JSON confirmation.
    """
    validate_write()
    client = get_client()
    client.list_delete(list_id)
    return fmt({"success": True, "list_id": list_id})


@mcp.tool()
def list_accounts_add(list_id: str, account_ids: List[str]) -> str:
    """Add accounts to a list.

    Args:
        list_id: Numeric list ID.
        account_ids: List of numeric account IDs to add.

    Returns:
        str: JSON confirmation.
    """
    validate_write()
    client = get_client()
    client.list_accounts_add(list_id, account_ids)
    return fmt({"success": True, "list_id": list_id, "added": account_ids})


@mcp.tool()
def list_accounts_delete(list_id: str, account_ids: List[str]) -> str:
    """Remove accounts from a list.

    Args:
        list_id: Numeric list ID.
        account_ids: List of numeric account IDs to remove.

    Returns:
        str: JSON confirmation.
    """
    validate_write()
    client = get_client()
    client.list_accounts_delete(list_id, account_ids)
    return fmt({"success": True, "list_id": list_id, "removed": account_ids})


# ─── POLLS ───────────────────────────────────────────────────────────────────

@mcp.tool()
def poll_vote(poll_id: str, choices: List[int]) -> str:
    """Vote in a poll.

    Args:
        poll_id: Numeric poll ID.
        choices: List of choice indices (0-based) to vote for.

    Returns:
        str: JSON with updated poll.
    """
    validate_write()
    client = get_client()
    return fmt(client.poll_vote(poll_id, choices))


# ─── FOLLOW REQUESTS ─────────────────────────────────────────────────────────

@mcp.tool()
def follow_requests(limit: int = 40) -> str:
    """Get pending follow requests for the authenticated account.

    Args:
        limit: Maximum number of results (default 40).

    Returns:
        str: JSON list of accounts that sent follow requests.
    """
    client = get_client()
    return fmt(client.follow_requests(limit=limit))


@mcp.tool()
def follow_request_authorize(account_id: str) -> str:
    """Approve a follow request.

    Args:
        account_id: Numeric account ID of the requester.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.follow_request_authorize(account_id))


@mcp.tool()
def follow_request_reject(account_id: str) -> str:
    """Reject a follow request.

    Args:
        account_id: Numeric account ID of the requester.

    Returns:
        str: JSON with the resulting relationship.
    """
    validate_write()
    client = get_client()
    return fmt(client.follow_request_reject(account_id))


# ─── MUTES & BLOCKS ──────────────────────────────────────────────────────────

@mcp.tool()
def mutes(limit: int = 40) -> str:
    """Get accounts muted by the authenticated account.

    Args:
        limit: Maximum number of results (default 40).

    Returns:
        str: JSON list of muted accounts.
    """
    client = get_client()
    return fmt(client.mutes(limit=limit))


@mcp.tool()
def blocks(limit: int = 40) -> str:
    """Get accounts blocked by the authenticated account.

    Args:
        limit: Maximum number of results (default 40).

    Returns:
        str: JSON list of blocked accounts.
    """
    client = get_client()
    return fmt(client.blocks(limit=limit))


# ─── MEDIA ───────────────────────────────────────────────────────────────────

@mcp.tool()
def media_post(file_path: str, description: Optional[str] = None) -> str:
    """Upload a media file (image, video, audio) to Mastodon.

    Args:
        file_path: Absolute path to the media file to upload.
        description: Alt text / accessibility description for the media.

    Returns:
        str: JSON with the media attachment object including its ID.
             Use the returned 'id' in status_post's media_ids parameter.
    """
    validate_write()
    client = get_client()
    return fmt(client.media_post(file_path, description=description))


# ─── DIRECTORY ───────────────────────────────────────────────────────────────

@mcp.tool()
def directory(
    limit: int = 20,
    order: str = "active",
    local: bool = False,
) -> str:
    """Browse the profile directory of the instance.

    Args:
        limit: Maximum number of accounts (default 20, max 80).
        order: 'active' (recently active) or 'new' (recently joined).
        local: Only show local accounts (default False).

    Returns:
        str: JSON list of account objects.
    """
    client = get_client()
    return fmt(client.directory(limit=limit, order=order, local=local))


# ─── MASTODON.PY >= 2.0.1 (python3-mastodon >= 2.0.1, Debian 13 / trixie) ───
#
# The tools below require Mastodon.py 2.0.1+, available as python3-mastodon
# in Debian 13 (trixie). Ubuntu 24.04 (noble) ships Mastodon.py 1.8.x and
# does NOT have these methods. Uncomment once the target distribution provides
# python3-mastodon >= 2.0.1 and update debian/control accordingly:
#
#   python3-mastodon (>= 2.0.1)
#
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def status_update(
    status_id: str,
    content: str,
    spoiler_text: Optional[str] = None,
    sensitive: Optional[bool] = None,
    media_ids: Optional[List[str]] = None,
) -> str:
    """Edit an existing status.

    Args:
        status_id: Numeric ID of the status to edit.
        content: New text content of the status.
        spoiler_text: New content warning text (None keeps existing).
        sensitive: Mark media as sensitive (None keeps existing).
        media_ids: New list of media attachment IDs (None keeps existing).

    Returns:
        str: JSON with the updated status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_update(
        id=status_id,
        status=content,
        spoiler_text=spoiler_text,
        sensitive=sensitive,
        media_ids=media_ids,
    ))


@mcp.tool()
def status_history(status_id: str) -> str:
    """Get the edit history of a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON list of StatusEdit objects, oldest first.
    """
    client = get_client()
    return fmt(client.status_history(id=status_id))


@mcp.tool()
def status_source(status_id: str) -> str:
    """Get the plain-text source of a status for editing.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with 'id', 'text', and 'spoiler_text' fields.
    """
    client = get_client()
    return fmt(client.status_source(id=status_id))


@mcp.tool()
def status_translate(status_id: str, language: Optional[str] = None) -> str:
    """Translate a status to another language.

    Args:
        status_id: Numeric status ID.
        language: Target ISO 639-1 language code (e.g. 'en', 'cs').
                  Defaults to the authenticated account's language.

    Returns:
        str: JSON with translated 'content', 'detected_source_language', and 'provider'.
    """
    client = get_client()
    return fmt(client.status_translate(id=status_id, lang=language))


@mcp.tool()
def conversations(limit: int = 20) -> str:
    """Get direct-message conversations.

    Args:
        limit: Maximum number of conversations (default 20, max 40).

    Returns:
        str: JSON list of Conversation objects, each containing the last status
             and a list of involved accounts.
    """
    client = get_client()
    return fmt(client.conversations(limit=limit))


@mcp.tool()
def scheduled_statuses(limit: int = 20) -> str:
    """Get statuses scheduled for future posting.

    Args:
        limit: Maximum number of results (default 20, max 40).

    Returns:
        str: JSON list of ScheduledStatus objects with 'id' and 'scheduled_at'.
    """
    client = get_client()
    return fmt(client.scheduled_statuses(limit=limit))


@mcp.tool()
def scheduled_status_update(status_id: str, scheduled_at: str) -> str:
    """Reschedule a scheduled status.

    Args:
        status_id: Numeric scheduled-status ID.
        scheduled_at: New ISO 8601 datetime string (e.g. '2026-01-01T12:00:00Z').

    Returns:
        str: JSON with the updated ScheduledStatus object.
    """
    from datetime import datetime
    validate_write()
    client = get_client()
    return fmt(client.scheduled_status_update(id=status_id, scheduled_at=datetime.fromisoformat(scheduled_at)))


@mcp.tool()
def scheduled_status_delete(status_id: str) -> str:
    """Cancel and delete a scheduled status.

    Args:
        status_id: Numeric scheduled-status ID.

    Returns:
        str: JSON confirmation.
    """
    validate_write()
    client = get_client()
    client.scheduled_status_delete(id=status_id)
    return fmt({"success": True, "status_id": status_id})


@mcp.tool()
def notifications_unread_count() -> str:
    """Get the number of unread notifications.

    Returns:
        str: JSON with 'count' field.
    """
    client = get_client()
    return fmt(client.notifications_unread_count())


# ─── ADDITIONAL TOOLS (Mastodon.py 2.2+) ────────────────────────────────────────

@mcp.tool()
def account_lookup(acct: str) -> str:
    """Look up a Mastodon account by its handle (e.g., '@user@instance').

    Args:
        acct: Account handle.

    Returns:
        str: JSON with account details.
    """
    client = get_client()
    return fmt(client.account_lookup(acct))


@mcp.tool()
def status_pin(status_id: str) -> str:
    """Pin a status to the authenticated account's profile.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the pinned status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_pin(id=status_id))


@mcp.tool()
def status_unpin(status_id: str) -> str:
    """Unpin a status from the authenticated account's profile.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the unpinned status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_unpin(id=status_id))


@mcp.tool()
def status_mute(status_id: str) -> str:
    """Mute a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the muted status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_mute(id=status_id))


@mcp.tool()
def status_unmute(status_id: str) -> str:
    """Unmute a status.

    Args:
        status_id: Numeric status ID.

    Returns:
        str: JSON with the unmuted status.
    """
    validate_write()
    client = get_client()
    return fmt(client.status_unmute(id=status_id))


@mcp.tool()
def tag_follow(hashtag: str) -> str:
    """Follow a hashtag.

    Args:
        hashtag: Hashtag name (without # prefix).

    Returns:
        str: JSON with the tag details.
    """
    validate_write()
    client = get_client()
    return fmt(client.tag_follow(hashtag))


@mcp.tool()
def tag_unfollow(hashtag: str) -> str:
    """Unfollow a hashtag.

    Args:
        hashtag: Hashtag name (without # prefix).

    Returns:
        str: JSON with the tag details.
    """
    validate_write()
    client = get_client()
    return fmt(client.tag_unfollow(hashtag))


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    from importlib.metadata import version, PackageNotFoundError
    try:
        pkg_version = version("mastodon-mcp-server")
    except PackageNotFoundError:
        pkg_version = "unknown"

    parser = argparse.ArgumentParser(
        prog="mastodon-mcp",
        description="Model Context Protocol server for Mastodon integration.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  MASTODON_INSTANCE          Mastodon instance URL (required)
  MASTODON_ACCESS_TOKEN      OAuth access token (required)
  MASTODON_MCP_TRANSPORT     Transport mode: stdio (default) or streamable-http
  MASTODON_MCP_HOST          HTTP bind address (default: 127.0.0.1)
  MASTODON_MCP_PORT          HTTP port (default: 8000)
  MASTODON_MCP_STATELESS_HTTP  Disable HTTP session state (default: false)
  READ_ONLY                  Restrict to read-only operations (default: false)
  DEBUG                      Enable verbose logging (default: false)

Examples:
  # Run as stdio MCP server (for use with AI clients):
  MASTODON_INSTANCE=https://mastodon.social MASTODON_ACCESS_TOKEN=<token> mastodon-mcp

  # Run as HTTP MCP server:
  MASTODON_MCP_TRANSPORT=streamable-http MASTODON_MCP_PORT=8080 \\
    MASTODON_INSTANCE=https://mastodon.social MASTODON_ACCESS_TOKEN=<token> mastodon-mcp
""",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {pkg_version}")
    parser.parse_args()

    transport = os.getenv("MASTODON_MCP_TRANSPORT", "stdio").lower()

    if transport == "streamable-http":
        host = os.getenv("MASTODON_MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MASTODON_MCP_PORT", "8000"))
        stateless = os.getenv("MASTODON_MCP_STATELESS_HTTP", "false").lower() in ("true", "1", "yes")
        logger.info(f"Starting MCP server with HTTP transport on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port, stateless=stateless)
    else:
        logger.info("Starting MCP server with stdio transport")
        mcp.run()


if __name__ == "__main__":
    main()
