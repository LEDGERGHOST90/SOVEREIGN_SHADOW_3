"""
🏴 Shadow SDK - Setup Configuration

Install with: pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadow-sdk",
    version="0.1.0",
    author="Sovereign Shadow Empire",
    description="Internal SDK for the Sovereign Shadow Trading Empire",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sovereignshadow/shadow-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ccxt>=4.0.0",
        "aiohttp>=3.8.0",
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
)

