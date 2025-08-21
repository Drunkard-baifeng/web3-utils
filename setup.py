#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# 读取 README 文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements 文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="web3-wallet-utils",
    version="1.0.0",
    author="baifeng",
    author_email="1765311475@qq.com",
    description="🔐 多链钱包工具集 - 支持 EVM、Bitcoin、Tron、Cosmos 生态",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drunkard-baifeng/web3-wallet-utils",
    project_urls={
        "Bug Tracker": "https://github.com/Drunkard-baifeng/web3-wallet-utils/issues",
        "Documentation": "https://github.com/Drunkard-baifeng/web3-wallet-utils#readme",
        "Source Code": "https://github.com/Drunkard-baifeng/web3-wallet-utils",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords=[
        "web3", "wallet", "cryptocurrency", "blockchain", 
        "bitcoin", "ethereum", "tron", "cosmos", 
        "bip44", "mnemonic", "private-key", "address-generation"
    ],
    include_package_data=True,
    zip_safe=False,
)