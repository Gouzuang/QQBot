from setuptools import setup, find_packages

setup(
    name="QQBotAPI",
    version="0.1.0dev0",
    author="Gouzuang",
    description="QQ Bot API implementation",
    packages=find_packages(include=['QQBotAPI', 'QQBotAPI.*', 'shared', 'shared.*']),
    install_requires=[
        "requests>=2.31.0",
        "websockets>=12.0",
        "aiohttp>=3.9.1",
        "pytest>=8.0.0",
        "pytest-asyncio>=0.23.5",
        "python-dotenv>=1.0.0",
        "pydantic>=2.6.1",
    ],
    python_requires=">=3.9",
)