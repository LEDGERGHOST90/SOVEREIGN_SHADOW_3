# This is the rewritten content of /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop/multi-exchange-crypto-mcp/setup.py

from setuptools import setup, find_packages

setup(
    name="multi-exchange-crypto-mcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "python-dotenv>=1.0.0",
        "schedule>=1.2.0",
        "websocket-client>=1.2.1",
        "pandas>=1.2.4"
    ],
    entry_points={
        'console_scripts': [
            'mcp=mcp_exchange_server:main',
        ],
    },
)
