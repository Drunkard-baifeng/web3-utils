# Web3 Utils

<div align="center">

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)

🔐 **专业多链钱包工具集** - 支持 EVM、Bitcoin、Tron、Cosmos 生态的钱包生成和管理工具

[English](README_EN.md) | [中文文档](README.md)

</div>

## ✨ 核心特性

### 🌐 **支持的区块链生态**
| 生态系统 | 支持网络 | 功能特性 |
|---------|---------|---------|
| **EVM 生态** | Ethereum, BSC, Polygon, Arbitrum, Optimism | 主网币/代币转账、Gas优化、消息签名 |
| **Bitcoin 生态** | BTC 主网/测试网 | 多地址格式、Taproot支持、余额查询 |
| **Tron 生态** | TRX, TRC-20 代币 | 智能合约交互、实时监控、交易查询 |
| **Cosmos 生态** | Cosmos, Persistence, Osmosis, Juno | 多链支持、IBC转账、质押功能 |

### 🛠️ **专业功能**
- ✅ **钱包管理** - 生成、恢复、导入钱包，支持批量操作
- ✅ **标准兼容** - BIP-44/BIP-39 标准，多地址索引派生
- ✅ **安全可靠** - 离线钱包生成，私钥本地管理
- ✅ **交易支持** - 主网币/代币转账，智能合约交互
- ✅ **实时监控** - 区块链交易监控，回调通知机制
- ✅ **多网络** - 主网/测试网切换，自定义RPC节点
- ✅ **专业工具** - Gas费估算、交易状态跟踪、消息签名

## 📦 安装

### 从 GitHub 安装（推荐）
```bash
pip install git+https://github.com/Drunkard-baifeng/web3-utils.git
```

### 从源码安装
```bash
# 克隆仓库
git clone https://github.com/Drunkard-baifeng/web3-utils.git
cd web3-utils

# 创建虚拟环境
python -m venv web3env
source web3env/bin/activate  # Linux/Mac
# 或 web3env\Scripts\activate  # Windows

# 开发模式安装
pip install -e .
```

## 🚀 快速开始

### 💡 简单导入
```python
# 一次性导入所有钱包类
from web3_utils import EVMWallet, BTCWallet, TronWallet, CosmosWallet

# 或者单独导入特定钱包
from web3_utils import EVMWallet
```

### 🔗 EVM 生态钱包 (Ethereum/BSC/Polygon)
```python
from web3_utils import EVMWallet

# 创建钱包实例（支持自定义RPC）
wallet = EVMWallet(
    rpc_url="https://bsc-dataseed1.binance.org",  # BSC主网
    chain_id=56  # BSC链ID
)

# 生成新钱包
success, new_wallet, error = wallet.generate_wallet(index=0)
if success:
    print(f"地址: {new_wallet.address}")
    print(f"私钥: {new_wallet.private_key}")
    print(f"助记词: {new_wallet.mnemonic}")

# 从助记词恢复钱包
mnemonic = "your twelve word mnemonic phrase here"
success, restored_wallet, error = wallet.recover_wallet_from_mnemonic(mnemonic, index=0)

# 转账示例
success, tx_hash, msg = wallet.transfer_coin(
    private_key="your_private_key",
    to_address="0x...",
    amount_ether="0.1",
    wait_for_confirmation=True
)
```

### ₿ Bitcoin 钱包 (多地址格式支持)
```python
from web3_utils import BTCWallet

# 创建Bitcoin钱包实例
wallet = BTCWallet(network="bitcoin")  # 或 "testnet"

# 生成不同格式的地址
address_types = ["legacy", "p2sh-segwit", "segwit", "taproot"]
for addr_type in address_types:
    success, btc_wallet, error = wallet.generate_wallet(
        index=0, 
        address_type=addr_type
    )
    if success:
        print(f"{addr_type}: {btc_wallet.address}")
        print(f"私钥: {btc_wallet.private_key}")

# 查询余额
success, balance, error = wallet.get_balance("bc1p...")
if success:
    print(f"余额: {balance} BTC")
```

### 🌊 Tron 钱包 (TRX + TRC-20)
```python
from web3_utils import TronWallet

# 创建Tron钱包实例（支持API密钥）
wallet = TronWallet(
    network='mainnet',
    api_key="your_trongrid_api_key"
)

# 生成新钱包
success, tron_wallet, error = wallet.generate_wallet()
if success:
    print(f"地址: {tron_wallet.address}")
    print(f"私钥: {tron_wallet.private_key}")

# TRC-20代币转账
result = wallet.transfer_token(
    contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # USDT
    from_private_key="your_private_key",
    to_address="target_address",
    amount=100.0,
    wait_confirmation=True
)
```

### 🌌 Cosmos 生态钱包 (多链支持)
```python
from web3_utils import CosmosWallet

# 创建Cosmos钱包实例
wallet = CosmosWallet(lcd_url="https://mainnet-lcd.paxinet.io")

# 支持的链前缀
chains = {
    "cosmos": "Cosmos Hub",
    "paxi": "Persistence", 
    "osmo": "Osmosis",
    "juno": "Juno Network"
}

# 同一助记词生成多链地址
mnemonic = "your cosmos mnemonic here"
for prefix, name in chains.items():
    success, wallet_info, error = wallet.recover_wallet_from_mnemonic(
        mnemonic, prefix, 0
    )
    if success:
        print(f"{name}: {wallet_info.address}")

# 转账示例
success, tx_hash, msg = wallet.transfer_coin(
    private_key_hex="your_private_key",
    to_address="paxi1...",
    amount=5.0,
    fee=0.04,
    wait_for_confirmation=True
)
```

### 📊 实时监控 (Tron网络)
```python
import asyncio
from web3_utils.tron_wallet_utils.tron_monitor import TronBlockScanner

async def on_transaction(tx_data):
    print(f"发现交易: {tx_data['tx_id']}")
    print(f"金额: {tx_data['amount']} {tx_data['token']}")

# 创建监控实例
scanner = TronBlockScanner(api_key="your_api_key")
scanner.set_trx_callback(on_transaction)

# 开始监控
addresses = ["TUFxc4XMFkXHsxZ42nDLd353dhJ4HQPmGS"]
await scanner.start_scan(addresses, interval=3)
```

## 📁 项目架构

```
web3_utils/                     # 🏠 项目根目录
├── src/web3_utils/            # 📦 源代码目录
│   ├── __init__.py           # 🔗 统一导出接口
│   ├── evm_wallet_utils/     # 🔗 EVM 生态钱包工具
│   │   ├── wallet.py        # 💼 EVMWallet 核心类 (585行)
│   │   └── demo.py          # 🎯 使用示例和测试
│   ├── btc_wallet_utils/     # ₿ Bitcoin 钱包工具  
│   │   ├── wallet.py        # 💼 BTCWallet 核心类 (358行)
│   │   └── demo.py          # 🎯 使用示例和测试
│   ├── tron_wallet_utils/    # 🌊 Tron 生态钱包工具
│   │   ├── wallet.py        # 💼 TronWallet 核心类 (755行)
│   │   ├── demo.py          # 🎯 使用示例和测试
│   │   └── tron_monitor.py  # 📊 实时区块链监控 (369行)
│   └── cosmos_wallet_utils/  # 🌌 Cosmos 生态钱包工具
│       ├── wallet.py        # 💼 CosmosWallet 核心类 (465行)
│       └── demo.py          # 🎯 使用示例和测试
├── pyproject.toml            # ⚙️ 项目配置和依赖管理
├── requirements.txt          # 📋 Python 依赖清单
├── test.py                   # 🧪 统一测试入口
└── README.md                 # 📖 项目文档
```

## 🔧 技术架构

### 核心模块功能

| 模块 | 核心类 | 主要功能 | 代码量 |
|------|-------|---------|--------|
| **EVM 生态** | `EVMWallet` | 以太坊系钱包、ERC-20代币、Gas优化 |
| **Bitcoin** | `BTCWallet` | 多地址格式、Taproot、BIP-44派生 |
| **Tron** | `TronWallet` | TRX/TRC-20、智能合约、交易查询 |
| **Cosmos** | `CosmosWallet` | 多链支持、IBC转账、质押功能 |
| **监控系统** | `TronBlockScanner` | 实时区块扫描、异步处理、回调通知 |

### 依赖技术栈

```python
# 🔗 区块链交互核心库
eth-account>=0.8.0      # 以太坊账户管理
web3>=6.0.0            # Web3 协议交互
bitcoinlib>=0.12.0     # Bitcoin 网络操作
tronpy>=0.4.0          # Tron 网络交互
cosmpy>=0.11.1         # Cosmos 生态支持
mospy-wallet>=0.6.0    # Cosmos 钱包实现

# 🛠️ 工具库
mnemonic>=0.20         # BIP-39 助记词
loguru>=0.7.0          # 专业日志系统
requests>=2.28.0       # HTTP 请求
bech32>=1.2.0          # Bech32 地址编码
ecdsa>=0.18.0          # 椭圆曲线数字签名
```

## 🔐 安全最佳实践

### ⚠️ **关键安全原则**

| 安全要点 | 说明 | 建议做法 |
|---------|------|---------|
| 🔑 **私钥管理** | 私钥是资产控制权 | 使用硬件钱包、加密存储、环境变量 |
| 📝 **助记词保护** | 助记词可恢复所有资产 | 离线备份、多重备份、物理存储 |
| 🔒 **离线生成** | 降低网络攻击风险 | 断网环境生成、冷钱包方案 |
| 🧪 **测试验证** | 避免主网资产损失 | 测试网先行、小额验证 |
| 🔍 **代码审计** | 确保代码安全性 | 安全审计、开源透明 |

### 🛡️ **生产环境安全建议**

```python
import os
from web3_utils import EVMWallet

# ✅ 推荐：使用环境变量
private_key = os.getenv('WALLET_PRIVATE_KEY')
rpc_url = os.getenv('RPC_URL')

# ❌ 避免：硬编码敏感信息
# private_key = "0x123456..."  # 危险！

# ✅ 推荐：使用加密配置
wallet = EVMWallet(rpc_url=rpc_url)

# ✅ 推荐：异常处理
try:
    success, result, error = wallet.transfer_coin(
        private_key=private_key,
        to_address=to_address,
        amount_ether="0.01"
    )
    if success:
        logger.info(f"交易成功: {result}")
    else:
        logger.error(f"交易失败: {error}")
except Exception as e:
    logger.error(f"程序异常: {e}")
```

### 🚨 **风险提示**

- 🚫 **永远不要**将私钥提交到代码仓库
- 🚫 **永远不要**在生产日志中打印私钥
- 🚫 **永远不要**通过不安全的渠道传输私钥
- 🚫 **永远不要**在未验证的环境中使用真实资产

## 🌟 支持的区块链网络

### 🌌 Cosmos 生态链

| 链名 | 前缀 | 主币 | 特色功能 | 状态 |
|------|------|------|---------|------|
| **Cosmos Hub** | `cosmos` | ATOM | 🏛️ 生态中心枢纽 | ✅ 完全支持 |
| **Persistence** | `paxi` | XPRT | 🔄 流动性质押协议 | ✅ 完全支持 |
| **Osmosis** | `osmo` | OSMO | 🔄 去中心化交易所 | ✅ 完全支持 |
| **Juno** | `juno` | JUNO | 📜 智能合约平台 | ✅ 完全支持 |
| **Akash** | `akash` | AKT | ☁️ 去中心化云计算 | ✅ 完全支持 |
| **Secret** | `secret` | SCRT | 🔒 隐私计算网络 | ✅ 完全支持 |

### 🔗 EVM 兼容网络

| 网络 | Chain ID | RPC 端点 | 特色 |
|------|----------|----------|------|
| **Ethereum** | 1 | `https://mainnet.infura.io/v3/YOUR_KEY` | 🏛️ 原生以太坊 |
| **BSC** | 56 | `https://bsc-dataseed1.binance.org` | ⚡ 高速低费用 |
| **Polygon** | 137 | `https://polygon-rpc.com` | 🔺 Layer2 扩展 |
| **Arbitrum** | 42161 | `https://arb1.arbitrum.io/rpc` | 🚀 Optimistic Rollup |

### ₿ Bitcoin 地址格式

| 格式 | 前缀 | 特点 | 推荐度 |
|------|------|------|-------|
| **Legacy** | `1` | 传统格式，兼容性最好 | ⭐⭐⭐ |
| **P2SH-SegWit** | `3` | 兼容隔离见证 | ⭐⭐⭐⭐ |
| **Native SegWit** | `bc1q` | 原生隔离见证，费用最低 | ⭐⭐⭐⭐⭐ |
| **Taproot** | `bc1p` | 最新格式，隐私性最好 | ⭐⭐⭐⭐⭐ |

## 🛠️ 开发指南

### 🧪 运行测试和演示

```bash
# 🔗 EVM 钱包测试
python -m web3_utils.evm_wallet_utils.demo

# ₿ Bitcoin 钱包测试  
python -m web3_utils.btc_wallet_utils.demo

# 🌊 Tron 钱包测试
python -m web3_utils.tron_wallet_utils.demo

# 🌌 Cosmos 钱包测试
python -m web3_utils.cosmos_wallet_utils.demo

# 🎯 运行所有测试
python test.py
```

### 🔧 开发环境配置

```bash
# 克隆项目
git clone https://github.com/Drunkard-baifeng/web3-utils.git
cd web3-utils

# 创建虚拟环境
python -m venv web3env
source web3env/bin/activate  # Linux/Mac
# web3env\Scripts\activate   # Windows

# 安装开发依赖
pip install -e .
pip install pytest black flake8  # 开发工具

# 代码格式化
black src/
flake8 src/
```

### 📈 性能优化建议

```python
# 🚀 批量操作优化
from web3_utils import EVMWallet
import asyncio

async def batch_generate_wallets(count: int):
    """批量生成钱包的高效方式"""
    wallet = EVMWallet()
    tasks = []
    
    for i in range(count):
        task = asyncio.to_thread(wallet.generate_wallet, i)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# 🔄 连接池复用
wallet = EVMWallet(rpc_url="https://bsc-dataseed1.binance.org")
# 复用同一个实例进行多次操作，避免重复连接
```

### 🆕 扩展新链支持

1. **创建新的钱包模块**
   ```python
   # src/web3_utils/new_chain_utils/wallet.py
   class NewChainWallet:
       def generate_wallet(self):
           # 实现钱包生成逻辑
           pass
   ```

2. **添加到主接口**
   ```python
   # src/web3_utils/__init__.py
   from .new_chain_utils.wallet import NewChainWallet
   __all__.append('NewChainWallet')
   ```

3. **编写测试用例**
   ```python
   # src/web3_utils/new_chain_utils/demo.py
   def test_new_chain_wallet():
       # 添加测试逻辑
       pass
   ```

## 🎯 使用场景

### 💼 企业级应用
- **钱包服务** - 为DApp提供多链钱包后端
- **资产管理** - 企业数字资产批量管理
- **支付网关** - 区块链支付解决方案
- **DeFi集成** - 去中心化金融应用开发

### 🏗️ 开发工具
- **钱包生成器** - 批量生成测试钱包
- **交易监控** - 实时监控链上活动
- **地址验证** - 多链地址格式验证
- **私钥管理** - 安全的私钥操作工具

### 🎓 教育研究
- **区块链教学** - 区块链技术学习工具
- **协议研究** - 不同链协议对比研究
- **安全测试** - 钱包安全性测试
- **开发培训** - Web3开发技能培训

## 📊 项目统计

```
📈 项目规模统计
├── 💻 总代码行数: 2,532+ 行
├── 🏗️ 核心模块数: 4 个主要生态
├── 🔧 支持功能数: 20+ 核心功能
├── 🌐 支持网络数: 15+ 区块链网络
├── 📦 依赖包数量: 11 个专业库
└── 🧪 测试覆盖率: 100% 功能演示
```

## 📞 技术支持

### 🐛 问题反馈
- **GitHub Issues**: [提交问题](https://github.com/Drunkard-baifeng/web3-utils/issues)
- **功能建议**: [功能请求](https://github.com/Drunkard-baifeng/web3-utils/issues/new)

### 📖 文档资源
- **API 文档**: 详见各模块代码注释
- **示例代码**: 查看 `demo.py` 文件
- **最佳实践**: 参考安全指南章节

### 🤝 社区贡献

我们欢迎各种形式的贡献：

- 🐛 **Bug 修复** - 发现并修复代码问题
- ✨ **新功能** - 添加新的区块链支持
- 📖 **文档改进** - 完善文档和示例
- 🧪 **测试用例** - 增加测试覆盖率
- 🌍 **国际化** - 多语言支持

#### 贡献流程
1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 **MIT License** 开源许可证 - 详见 [LICENSE](LICENSE) 文件

## 🌟 致谢

感谢以下开源项目的支持：
- [eth-account](https://github.com/ethereum/eth-account) - 以太坊账户管理
- [bitcoinlib](https://github.com/1200wd/bitcoinlib) - Bitcoin 操作库
- [tronpy](https://github.com/andelf/tronpy) - Tron 网络交互
- [cosmpy](https://github.com/fetchai/cosmpy) - Cosmos 生态支持

---

<div align="center">

### 💝 如果这个项目对你有帮助，请给个 ⭐ Star！

**让更多开发者发现这个有用的工具** 🚀

[![GitHub stars](https://img.shields.io/github/stars/Drunkard-baifeng/web3-utils?style=social)](https://github.com/Drunkard-baifeng/web3-utils/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Drunkard-baifeng/web3-utils?style=social)](https://github.com/Drunkard-baifeng/web3-utils/network/members)

**Web3 Utils - 让区块链开发更简单** 🔐

</div>