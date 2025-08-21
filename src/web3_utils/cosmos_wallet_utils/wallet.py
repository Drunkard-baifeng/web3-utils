#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cosmos 钱包生成和管理工具
使用 cosmpy 和 mospy-wallet 的专业实现
"""

from mospy import Account, Transaction
from mnemonic import Mnemonic
from typing import Tuple


class Wallet:
    """钱包数据类"""
    def __init__(self, address: str, private_key: str, mnemonic: str, index: int):
        self.address = address
        self.private_key = private_key
        self.mnemonic = mnemonic
        self.index = index


class CosmosWallet:
    """Cosmos 钱包类"""
    
    def __init__(self):
        self.mnemo = Mnemonic("english")
    
    def generate_wallet(self, prefix: str = "cosmos", index: int = 0) -> Tuple[bool, Wallet, str]:
        """
        生成新钱包
        
        Args:
            prefix: 地址前缀 (如 'cosmos', 'paxi', 'osmo')
            index: 地址索引 (默认0)
            
        Returns:
            (成功标志, 钱包对象, 错误信息)
        """
        try:
            # 生成12个单词的助记词
            mnemonic = self.mnemo.generate(strength=128)  # 128位熵 = 12个单词
            
            # 从助记词恢复钱包
            success, wallet, error = self.recover_from_mnemonic(mnemonic, prefix, index)
            return success, wallet, error
            
        except Exception as e:
            return False, None, str(e)
    
    def recover_from_mnemonic(self, mnemonic: str, prefix: str = "cosmos", 
                            index: int = 0) -> Tuple[bool, Wallet, str]:
        """
        从助记词恢复钱包
        
        Args:
            mnemonic: 助记词
            prefix: 地址前缀
            index: 地址索引
            
        Returns:
            (成功标志, 钱包对象, 错误信息)
        """
        try:
            if not self.mnemo.check(mnemonic):
                return False, None, "无效的助记词"
            
            # 从助记词创建账户 (使用正确的mospy API)
            account = Account(
                seed_phrase=mnemonic,
                hrp=prefix,  # 使用传入的前缀
                next_sequence=0,
                account_number=0,
                address_index=index
            )
            
            # 获取地址
            address = account.address
            
            # 获取私钥和公钥
            private_key = account.private_key
            
            wallet = Wallet(
                address=address,
                private_key=private_key.hex(),
                mnemonic=mnemonic,
                index=index
            )
            
            return True, wallet, ""
            
        except Exception as e:
            return False, None, str(e)
    
    def recover_from_private_key(self, private_key_hex: str, 
                                prefix: str = "cosmos") -> Tuple[bool, Wallet, str]:
        """
        从私钥恢复钱包
        
        Args:
            private_key_hex: 十六进制私钥
            prefix: 地址前缀
            
        Returns:
            (成功标志, 钱包对象, 错误信息)
        """
        try:
            # 从私钥恢复钱包
            private_key_bytes = bytes.fromhex(private_key_hex)
            
            # 使用 mospy Account 从私钥恢复
            account = Account(
                private_key=private_key_bytes,
                hrp=prefix,
                next_sequence=0,
                account_number=0
            )
            
            wallet = Wallet(
                address=account.address,
                private_key=private_key_hex,
                mnemonic="",
                index=0
            )
            
            return True, wallet, ""
            
        except Exception as e:
            return False, None, str(e)