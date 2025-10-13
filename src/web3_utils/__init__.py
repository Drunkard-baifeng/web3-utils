"""
Web3 Utils - 多链钱包工具集

支持 EVM、Bitcoin、Tron、Cosmos 生态的钱包生成和管理
"""

__version__ = "1.0.5"
__author__ = "Baifeng"
__email__ = "1765311475@qq.com"

# 导入所有钱包类，方便直接使用
from .evm_wallet_utils.wallet import EVMWallet
from .btc_wallet_utils.wallet import BTCWallet
from .tron_wallet_utils.wallet import TronWallet
from .cosmos_wallet_utils.wallet import CosmosWallet

# 定义公开接口
__all__ = [
    'EVMWallet',
    'BTCWallet', 
    'TronWallet',
    'CosmosWallet'
] 