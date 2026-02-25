from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sharepoint-mcp",
    version="0.1.0",
    author="yourname",  # Update this with your name
    author_email="your.email@example.com",  # Update this with your email
    description="SharePoint Model Context Protocol (MCP) server for LLM applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DEmodoriGatsuO/sharepoint-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=0.1.0",
        "msal>=1.20.0",
        "requests>=2.28.0",
        "pandas>=1.5.0",
        "python-dotenv>=0.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.3.0",
            "ruff>=0.0.169",
        ],
    },
    entry_points={
        "console_scripts": [
            "sharepoint-mcp=server:main",
        ],
    },
)
