from setuptools import setup, find_packages

setup(
    name="mastodon-mcp-server",
    version="1.0.1",
    description="A comprehensive MCP server for Mastodon integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vítězslav Dvořák",
    author_email="info@vitexsoftware.cz",
    url="https://github.com/VitexSoftware/mastodon-mcp-server",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Mastodon.py>=2.2.1",
        "python-dotenv>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "mastodon-mcp=mastodon_mcp_server.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet",
        "Topic :: Communications",
    ],
    python_requires=">=3.10",
)
