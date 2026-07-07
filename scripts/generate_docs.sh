#!/bin/bash

# Generate static HTML documentation using pdoc3
echo "Generating documentation..."
.venv/bin/pdoc --html mastodon_mcp_server --output-dir docs

echo "Documentation generated in docs/ directory."