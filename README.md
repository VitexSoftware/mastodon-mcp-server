![Packaging: deb](https://img.shields.io/badge/packaging-.deb-red?logo=debian&logoColor=white)


<p align="center">
  <img src="mastodon-mcp-server.svg" alt="mastodon-mcp-server" width="128">
</p>

# mastodon-mcp-server

A comprehensive MCP (Model Context Protocol) server for Mastodon integration. Enables AI assistants and other MCP clients to interact with Mastodon instances — read timelines, post statuses, manage accounts, search, and more.

## Features

- **Timelines**: home, local, public, hashtag
- **Statuses**: post, delete, favourite, reblog, bookmark
- **Accounts**: follow, unfollow, block, mute, relationships, profile update
- **Notifications**: read, dismiss individual or all
- **Search**: accounts, statuses, hashtags
- **Trending**: tags, statuses, links
- **Lists**: create, delete, manage members
- **Media**: upload attachments
- **Polls**: vote
- **Read-only mode**: safe browsing without write access
- **STDIO and HTTP transports**: works with any MCP-compatible client

## Installation

### Debian 13+ / Ubuntu 24+

```bash
apt install mastodon-mcp-server
```

### pip

```bash
pip install mastodon-mcp-server
```

### From source

```bash
git clone https://github.com/VitexSoftware/mastodon-mcp-server.git
cd mastodon-mcp-server
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable                      | Required | Default     | Description                                                                      |
| ----------------------------- | -------- | ----------- | -------------------------------------------------------------------------------- |
| `MASTODON_INSTANCE`           | yes      | —           | Mastodon instance URL (e.g. `https://mastodon.social` or just `mastodon.social`) |
| `MASTODON_ACCESS_TOKEN`       | yes      | —           | OAuth access token                                                               |
| `READ_ONLY`                   | no       | `true`      | Disable all write operations                                                     |
| `MASTODON_MCP_TRANSPORT`      | no       | `stdio`     | Transport: `stdio` or `streamable-http`                                          |
| `MASTODON_MCP_HOST`           | no       | `127.0.0.1` | HTTP transport bind address                                                      |
| `MASTODON_MCP_PORT`           | no       | `8000`      | HTTP transport port                                                              |
| `MASTODON_MCP_STATELESS_HTTP` | no       | `false`     | Disable HTTP session state                                                       |
| `DEBUG`                       | no       | `false`     | Enable verbose logging                                                           |

### Getting an Access Token

1. Go to your Mastodon instance → **Preferences → Development → New application**
2. Grant required scopes: `read`, `write`, `follow`
3. Copy the **Your access token** value

## Client Setup

### Claude Code (CLI)

```bash
claude mcp add --scope user mastodon /usr/bin/mastodon-mcp \
  -e MASTODON_INSTANCE=mastodon.social \
  -e MASTODON_ACCESS_TOKEN=your-token-here
```

### Claude Desktop

`~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mastodon": {
      "command": "mastodon-mcp",
      "env": {
        "MASTODON_INSTANCE": "https://mastodon.social",
        "MASTODON_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Warp Terminal

`~/.warp/mcp_config.json`:

```json
{
  "mcpServers": {
    "mastodon": {
      "command": "/usr/bin/mastodon-mcp",
      "args": [],
      "env": {
        "MASTODON_INSTANCE": "https://mastodon.social",
        "MASTODON_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

### VSCode (GitHub Copilot / Continue)

`~/.config/Code/User/mcp.json`:

```json
{
  "servers": {
    "MastodonMCP": {
      "type": "stdio",
      "command": "/usr/bin/mastodon-mcp",
      "args": [],
      "env": {
        "MASTODON_INSTANCE": "https://mastodon.social",
        "MASTODON_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```

### HTTP transport (any MCP client)

```bash
MASTODON_MCP_TRANSPORT=streamable-http mastodon-mcp
```

## Usage

```text
usage: mastodon-mcp [-h] [--version]

Model Context Protocol server for Mastodon integration.

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

Environment variables:
  MASTODON_INSTANCE          Mastodon instance URL (required)
  MASTODON_ACCESS_TOKEN      OAuth access token (required)
  MASTODON_MCP_TRANSPORT     Transport mode: stdio (default) or streamable-http
  MASTODON_MCP_HOST          HTTP bind address (default: 127.0.0.1)
  MASTODON_MCP_PORT          HTTP port (default: 8000)
  MASTODON_MCP_STATELESS_HTTP  Disable HTTP session state (default: false)
  READ_ONLY                  Restrict to read-only operations (default: true)
  DEBUG                      Enable verbose logging (default: false)
```

## Available Tools

### Instance

| Tool            | Description                                |
| --------------- | ------------------------------------------ |
| `instance_info` | Instance name, description, version, rules |

### Accounts

| Tool                                      | Description                                 |
| ----------------------------------------- | ------------------------------------------- |
| `account_verify`                          | Own profile                                 |
| `account_get`                             | Account by numeric ID                       |
| `account_search`                          | Search accounts by username or display name |
| `account_statuses`                        | Posts by an account                         |
| `account_followers` / `account_following` | Social graph                                |
| `account_follow` / `account_unfollow`     | Follow management                           |
| `account_block` / `account_unblock`       | Block management                            |
| `account_mute` / `account_unmute`         | Mute management                             |
| `account_relationships`                   | Relationship to one or more accounts        |
| `account_update`                          | Update own display name, bio, locked status |

### Timelines

| Tool               | Description                       |
| ------------------ | --------------------------------- |
| `timeline_home`    | Home timeline (followed accounts) |
| `timeline_local`   | Local instance public timeline    |
| `timeline_public`  | Federated public timeline         |
| `timeline_hashtag` | Statuses with a specific hashtag  |

### Statuses

| Tool                                           | Description                                               |
| ---------------------------------------------- | --------------------------------------------------------- |
| `status_get`                                   | Single status by ID                                       |
| `status_context`                               | Thread ancestors and descendants                          |
| `status_post`                                  | Post a new status (supports CW, visibility, media, polls) |
| `status_delete`                                | Delete own status                                         |
| `status_favourite` / `status_unfavourite`      | Favourite management                                      |
| `status_reblog` / `status_unreblog`            | Boost management                                          |
| `status_bookmark` / `status_unbookmark`        | Bookmark management                                       |
| `status_favourited_by` / `status_reblogged_by` | Who engaged with a status                                 |

### Notifications

| Tool                   | Description                             |
| ---------------------- | --------------------------------------- |
| `notifications_get`    | List notifications (filterable by type) |
| `notification_dismiss` | Dismiss a single notification           |
| `notifications_clear`  | Clear all notifications                 |

### Search & Discovery

| Tool                | Description                             |
| ------------------- | --------------------------------------- |
| `search`            | Search accounts, statuses, and hashtags |
| `trending_tags`     | Trending hashtags                       |
| `trending_statuses` | Trending statuses                       |
| `trending_links`    | Trending links/articles                 |
| `directory`         | Browse the instance profile directory   |

### Collections

| Tool         | Description             |
| ------------ | ----------------------- |
| `favourites` | Own favourited statuses |
| `bookmarks`  | Own bookmarked statuses |
| `mutes`      | Muted accounts          |
| `blocks`     | Blocked accounts        |

### Lists

| Tool                                         | Description             |
| -------------------------------------------- | ----------------------- |
| `lists_get`                                  | All lists               |
| `list_accounts`                              | Accounts in a list      |
| `list_create` / `list_delete`                | Create/delete lists     |
| `list_accounts_add` / `list_accounts_delete` | Add/remove list members |

### Polls

| Tool        | Description    |
| ----------- | -------------- |
| `poll_vote` | Vote in a poll |

### Follow Requests

| Tool                                                 | Description             |
| ---------------------------------------------------- | ----------------------- |
| `follow_requests`                                    | Pending follow requests |
| `follow_request_authorize` / `follow_request_reject` | Accept/reject requests  |

### Media

| Tool         | Description                         |
| ------------ | ----------------------------------- |
| `media_post` | Upload image/video/audio attachment |

## Future Tools (Mastodon.py ≥ 2.x / Mastodon server ≥ 3.5)

The following tools are implemented but commented out in `server.py`. Uncomment them when your distribution ships `python3-mastodon >= 2.0.1` (already available on Debian 13/trixie):

| Tool                         | Requirement                      |
| ---------------------------- | -------------------------------- |
| `status_update`              | Edit a status (server 3.5+)      |
| `status_history`             | Edit history (server 3.5+)       |
| `status_source`              | Plain-text source for editing    |
| `status_translate`           | Translate a status (server 4.0+) |
| `conversations`              | Direct-message conversations     |
| `scheduled_statuses`         | List scheduled posts             |
| `scheduled_status_update`    | Reschedule a post                |
| `scheduled_status_delete`    | Cancel a scheduled post          |
| `notifications_unread_count` | Unread notification count        |

## Testing

```bash
# Offline (tool registration + helper functions + version check)
python3 scripts/test_server.py

# With live instance
MASTODON_INSTANCE=mastodon.social \
MASTODON_ACCESS_TOKEN=your-token \
python3 scripts/test_server.py
```

## Architecture

The server uses a bundled stdlib-only MCP implementation (`mastodon_mcp_server/_mcp.py`) so it has **no dependency on `python3-fastmcp`** or its deep dependency chain. This makes packaging for Debian/Ubuntu straightforward. The implementation is compatible with the FastMCP decorator API (`@mcp.tool()`).

## Citation

This project is built on [Mastodon.py](https://github.com/halcy/Mastodon.py). If you use it in academic work, please cite:

```bibtex
@article{Diener2026,
  author  = {Diener, Lorenz and Delcourt, Corentin},
  title   = {Mastodon.py: A Python library for the Mastodon API},
  journal = {Journal of Open Source Software},
  year    = {2026},
  volume  = {11},
  number  = {120},
  pages   = {8946},
  doi     = {10.21105/joss.08946},
  url     = {https://doi.org/10.21105/joss.08946}
}
```

See [Mastodon.py's CITATION.cff](https://github.com/halcy/Mastodon.py/blob/master/CITATION.cff) for details.

## License

MIT — Vítězslav Dvořák <info@vitexsoftware.cz>
