# AI Agents Guide: mastodon-mcp-server

This document provides guidelines and best practices for AI agents (such as Hermes, Cline, and others) contributing to the mastodon-mcp-server project.

## Core Principles

1. **Dependency Minimization**: The server uses a custom, stdlib-only MCP implementation in `mastodon_mcp_server/_mcp.py`. Avoid adding external dependencies unless absolutely necessary for core functionality.
2. **Professional Documentation**: All documentation, including commit messages and README updates, must be professional and free of emojis.
3. **Transparency**: All changes made by AI agents should be clearly documented, and credits must be maintained for both human developers and the AI tools used.
4. **Test-Driven Maintenance**: Every tool addition or modification must be reflected in the test suite to ensure regression safety.
5. **Exactitude**: Ensure .yml, .yaml, .py files are correctly indented everytime you edit them

## Development Workflow for Agents

When adding a new tool or modifying existing functionality:

1. **Implement the Tool**: Add the function to `mastodon_mcp_server/server.py` using the `@mcp.tool()` decorator.
2. **Update Tests**: 
   - Open `scripts/test_server.py`.
   - Add the new tool name to the `EXPECTED_TOOLS` list.
   - If the tool has a specific behavior, add a live connectivity test case in Section 5.
3. **Update Documentation**: Update the "Available Tools" table in `README.md`.
4. **Verify**: Run `python3 scripts/test_server.py` to confirm that all tools are registered and functioning correctly.

## Credits and Attribution

This project is a collaborative effort between human intelligence and artificial intelligence.

- **Lead Developer**: Vítězslav Dvořák (<info@vitexsoftware.cz>)
- **AI Contributors**: Hermes AI Agent, Cline

## Maintenance Checklist

- [ ] Ensure `mastodon_mcp_server/_mcp.py` remains stdlib-only.
- [ ] Verify `README.md` reflects all currently active tools.
- [ ] Check that `scripts/test_server.py` contains all tool names in `EXPECTED_TOOLS`.
- [ ] Confirm no emojis are present in any `.md` or code documentation.
- [ ] Validate that the `READ_ONLY` mode is respected by all write operations.