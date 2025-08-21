#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cosmos 钱包生成和管理工具
简单易用的 Cosmos 生态钱包工具
"""

import hashlib
import hmac
from mnemonic import Mnemonic
import bech32
import ecdsa
from typing import  Tuple


class Wallet:
    """钱包数据类"""
    def __init__(self, address: str, private_key: str, public_key: str, mnemonic: str, index: int):
        self.address = address
        self.private_key = private_key
        self.public_key = public_key
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
            # 生成助记词
            mnemonic = self.mnemo.generate(strength=128)  # 12个单词
            
            # 从助记词生成钱包
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
            
            # 生成种子
            seed = self.mnemo.to_seed(mnemonic)
            
            # 派生私钥 (使用标准 Cosmos 路径)
            path = f"m/44'/118'/0'/0/{index}"
            private_key = self._derive_private_key(seed, path)
            
            # 生成公钥
            public_key = self._private_to_public_key(private_key)
            
            # 生成地址
            address = self._public_key_to_address(public_key, prefix)
            
            wallet = Wallet(
                address=address,
                private_key=private_key.hex(),
                public_key=public_key.hex(),
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
            private_key = bytes.fromhex(private_key_hex)
            public_key = self._private_to_public_key(private_key)
            address = self._public_key_to_address(public_key, prefix)
            
            wallet = Wallet(
                address=address,
                private_key=private_key_hex,
                public_key=public_key.hex(),
                mnemonic="",
                index=0
            )
            
            return True, wallet, ""
            
        except Exception as e:
            return False, None, str(e)
    
    def _derive_private_key(self, seed: bytes, path: str) -> bytes:
        """从种子派生私钥"""
        path_elements = path.split('/')[1:]  # 跳过 'm'
        
        # 主密钥
        master_key, master_chain_code = self._get_master_key(seed)
        
        # 逐级派生
        private_key = master_key
        chain_code = master_chain_code
        
        for element in path_elements:
            if element.endswith("'"):
                index = int(element[:-1]) + 0x80000000
            else:
                index = int(element)
            
            private_key, chain_code = self._derive_child_key(private_key, chain_code, index)
        
        return private_key
    
    def _get_master_key(self, seed: bytes) -> Tuple[bytes, bytes]:
        """获取主密钥"""
        hmac_result = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        return hmac_result[:32], hmac_result[32:]
    
    def _derive_child_key(self, parent_key: bytes, parent_chain_code: bytes, 
                            index: int) -> Tuple[bytes, bytes]:
        """派生子密钥"""
        if index >= 0x80000000:
            data = b'\x00' + parent_key + index.to_bytes(4, 'big')
        else:
            sk = ecdsa.SigningKey.from_string(parent_key, curve=ecdsa.SECP256k1)
            vk = sk.get_verifying_key()
            public_key = vk.to_string("compressed")
            data = public_key + index.to_bytes(4, 'big')
        
        hmac_result = hmac.new(parent_chain_code, data, hashlib.sha512).digest()
        
        child_key_int = (int.from_bytes(hmac_result[:32], 'big') + 
                        int.from_bytes(parent_key, 'big')) % ecdsa.SECP256k1.order
        
        if child_key_int == 0:
            raise ValueError("无效的子密钥")
        
        return child_key_int.to_bytes(32, 'big'), hmac_result[32:]
    
    def _private_to_public_key(self, private_key: bytes) -> bytes:
        """私钥生成公钥"""
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        return vk.to_string("compressed")
    
    def _public_key_to_address(self, public_key: bytes, prefix: str) -> str:
        """公钥生成地址"""
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        converted = bech32.convertbits(ripemd160_hash, 8, 5)
        if converted is None:
            raise ValueError("地址转换失败")
        
        address = bech32.bech32_encode(prefix, converted)
        if address is None:
            raise ValueError("Bech32 编码失败")
        
        return address