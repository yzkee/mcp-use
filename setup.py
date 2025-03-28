"""
Setup script for the Model-Agnostic MCP Library for LLMs.
"""

from setuptools import find_packages, setup

# Read the contents of README.md
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcpeer",
    version="0.1.0",
    author="Pietro Zullo",
    author_email="pietro.zullo@gmail.com",
    description="Model-Agnostic MCP Library for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pietrozullo/mcpeer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=[
        "mcp",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "websockets>=12.0",
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.8.0",
        "jsonschema-pydantic>=0.1.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "ruff>=0.1.0",
        ],
        "anthropic": [
            "anthropic>=0.15.0",
        ],
        "openai": [
            "openai>=1.10.0",
        ],
    },
)
