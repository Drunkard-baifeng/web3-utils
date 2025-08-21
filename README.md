# Web3 Utils

🔐 **多链钱包工具集** - 支持 EVM、Bitcoin、Tron、Cosmos 生态的钱包生成和管理工具

## ✨ 功能特性

### 🌐 **支持的区块链**
- **EVM 生态** - Ethereum, BSC, Polygon, Arbitrum 等
- **Bitcoin 生态** - BTC 主网和测试网
- **Tron 生态** - TRX 和 TRC-20 代币
- **Cosmos 生态** - Cosmos, Persistence, Osmosis, Juno, Akash 等

### 🔧 **核心功能**
- ✅ 生成新钱包（助记词 + 私钥 + 地址）
- ✅ 从助记词恢复钱包
- ✅ 从私钥导入钱包
- ✅ 多地址索引支持
- ✅ 离线钱包生成（安全）
- ✅ 标准 BIP-44 路径派生

## 📦 安装

### 从 GitHub 安装（推荐）
```bash
pip install git+https://github.com/Drunkard-baifeng/web3-wallet-utils.git
```

### 从源码安装
```bash
# 克隆仓库
git clone https://github.com/Drunkard-baifeng/web3-wallet-utils.git
cd web3-wallet-utils

# 创建虚拟环境
python -m venv web3env
source web3env/bin/activate  # Linux/Mac
# 或 web3env\Scripts\activate  # Windows

# 开发模式安装
pip install -e .
```

## 🚀 快速开始

### 简单导入
```python
# 一次性导入所有钱包类
from web3_utils import EVMWallet, BTCWallet, TronWallet, CosmosWallet

# 或者单独导入
from web3_utils import CosmosWallet
```

### EVM 钱包 (Ethereum/BSC/Polygon)
```python
from web3_utils import EVMWallet

# 创建钱包实例
wallet = EVMWallet()

# 生成新钱包
success, new_wallet, error = wallet.generate_wallet(index=0)
if success:
    print(f"地址: {new_wallet.address}")
    print(f"私钥: {new_wallet.private_key}")
    print(f"助记词: {new_wallet.mnemonic}")

# 从助记词恢复
mnemonic = "your twelve word mnemonic phrase here"
success, restored_wallet, error = wallet.recover_wallet_from_mnemonic(mnemonic, index=0)
```

### Bitcoin 钱包
```python
from web3_utils import BTCWallet

wallet = BTCWallet()

# 生成新钱包
success, btc_wallet, error = wallet.generate_wallet(index=0)
if success:
    print(f"地址: {btc_wallet.address}")
    print(f"私钥: {btc_wallet.private_key}")
    print(f"WIF: {btc_wallet.wif}")
```

### Tron 钱包
```python
from web3_utils import TronWallet

wallet = TronWallet()

# 生成新钱包
success, tron_wallet, error = wallet.generate_wallet(index=0)
if success:
    print(f"地址: {tron_wallet.address}")
    print(f"私钥: {tron_wallet.private_key}")
```

### Cosmos 钱包 (支持多链)
```python
from web3_utils import CosmosWallet

wallet = CosmosWallet()

# 生成 Persistence 钱包
success, paxi_wallet, error = wallet.generate_wallet("paxi", index=0)

# 生成 Osmosis 钱包  
success, osmo_wallet, error = wallet.generate_wallet("osmo", index=0)

# 同一助记词，不同链
mnemonic = "your cosmos mnemonic here"
success, cosmos_wallet, error = wallet.recover_from_mnemonic(mnemonic, "cosmos", 0)
success, paxi_wallet, error = wallet.recover_from_mnemonic(mnemonic, "paxi", 0)
```

## 📁 项目结构

```
web3_utils/                    # 项目根目录
├── src/                       # 源代码目录
│   └── web3_utils/           # 主包目录
│       ├── __init__.py        # 包初始化文件
│       ├── evm_wallet_utils/  # EVM 生态钱包
│       │   ├── wallet.py     # 核心钱包类
│       │   └── demo.py       # 使用示例
│       ├── btc_wallet_utils/  # Bitcoin 钱包
│       │   ├── wallet.py
│       │   └── demo.py
│       ├── tron_wallet_utils/ # Tron 钱包
│       │   ├── wallet.py
│       │   ├── demo.py
│       │   └── tron_monitor.py # 链上监控
│       └── cosmos_wallet_utils/ # Cosmos 生态钱包
│           ├── wallet.py
│           └── demo.py
├── pyproject.toml            # 项目配置
├── requirements.txt          # Python 依赖
└── README.md                # 项目文档
```

## 🔐 安全提醒

⚠️ **重要安全注意事项**:

1. **私钥安全** - 永远不要在生产环境中明文存储私钥
2. **助记词保护** - 助记词是恢复钱包的唯一方式，请妥善保管
3. **离线生成** - 建议在离线环境中生成钱包
4. **测试先行** - 在主网使用前，请先在测试网验证
5. **代码审计** - 生产使用前请进行代码安全审计

## 🌟 支持的 Cosmos 生态链

| 链名 | 前缀 | 代币 | 说明 |
|------|------|------|------|
| Cosmos Hub | `cosmos` | ATOM | 生态中心 |
| Persistence | `paxi` | XPRT | 流动性质押 |
| Osmosis | `osmo` | OSMO | DEX 交易所 |
| Juno | `juno` | JUNO | 智能合约 |
| Akash | `akash` | AKT | 云计算 |
| Secret | `secret` | SCRT | 隐私计算 |

## 🛠️ 开发说明

### 运行测试
```bash
# 运行所有演示
python -m web3_utils.evm_wallet_utils.demo
python -m web3_utils.btc_wallet_utils.demo  
python -m web3_utils.tron_wallet_utils.demo
python -m web3_utils.cosmos_wallet_utils.demo
```

### 添加新链支持
1. 在对应模块中添加链配置
2. 实现地址生成逻辑
3. 添加测试用例
4. 更新文档

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

⭐ **如果这个项目对你有帮助，请给个 Star！**