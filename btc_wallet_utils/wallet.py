#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC钱包工具类
提供钱包生成、恢复功能
"""

from typing import Tuple, Literal
from loguru import logger
from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
from bitcoinlib.encoding import pubkeyhash_to_addr_bech32
from bitcoinlib.services.services import Service
import hashlib
import ecdsa
from ecdsa import SECP256k1

# 地址类型定义
AddressType = Literal['legacy', 'segwit', 'p2sh-segwit', 'taproot']



class Wallet:
    def __init__(self, address: str, private_key: str, mnemonic: str = "", index: int = 0):
        self.address = address
        self.private_key = private_key
        self.mnemonic = mnemonic
        self.index = index


class BTCWallet:
    """BTC钱包工具类"""
    
    def __init__(self, network: str = "bitcoin"):
        """
        初始化BTC钱包工具类
        
        Args:
            network: 网络类型，可选 "bitcoin" 或 "testnet"
        """
        self.network = network
    
    def _taproot_tweak_pubkey(self, pubkey_bytes):
        """对公钥进行 Taproot tweaking"""
        try:
            # Taproot tweaking: P' = P + H_taptweak(P || m) * G
            # 对于单个密钥支出（key path），m 为空
            taptweak_tag = b'TapTweak'
            tagged_hash_prefix = hashlib.sha256(taptweak_tag).digest() + hashlib.sha256(taptweak_tag).digest()
            
            # 计算 taptweak
            taptweak = hashlib.sha256(tagged_hash_prefix + pubkey_bytes).digest()
            
            # 从 x-only 公钥恢复完整公钥（假设 y 坐标为偶数）
            x = int.from_bytes(pubkey_bytes, 'big')
            p = SECP256k1.generator.curve().p()
            
            # 计算 y^2 = x^3 + 7 (mod p)
            y_squared = (pow(x, 3, p) + 7) % p
            y = pow(y_squared, (p + 1) // 4, p)
            
            # 选择偶数 y
            if y % 2 != 0:
                y = p - y
            
            # 创建点
            point = ecdsa.ellipticcurve.Point(SECP256k1.generator.curve(), x, y)
            
            # 计算 taptweak * G
            taptweak_int = int.from_bytes(taptweak, 'big')
            taptweak_point = taptweak_int * SECP256k1.generator
            
            # P' = P + taptweak * G
            tweaked_point = point + taptweak_point
            
            # 返回 tweaked x-only 公钥
            return tweaked_point.x().to_bytes(32, 'big')
        except ImportError:
            logger.error("需要安装 ecdsa 库来支持 Taproot 地址生成: pip install ecdsa")
            return None
        except Exception as e:
            logger.error(f"Taproot tweaking 失败: {e}")
            return None
    
    def _generate_taproot_address(self, child_key) -> str:
        """
        生成 Taproot 地址
        
        Args:
            child_key: bitcoinlib HDKey 对象
            
        Returns:
            Taproot 地址字符串
        """
        try:
            # 获取 x-only 公钥
            pubkey_bytes = child_key.public_byte
            if len(pubkey_bytes) == 33:
                # 压缩公钥，去掉前缀
                x_only_pubkey = pubkey_bytes[1:]
            else:
                # 假设已经是 x-only
                x_only_pubkey = pubkey_bytes[:32]
            
            # 进行 Taproot tweaking
            tweaked_pubkey = self._taproot_tweak_pubkey(x_only_pubkey)
            if tweaked_pubkey is None:
                raise ValueError("Taproot tweaking 失败")
            
            # 使用 bitcoinlib 的 bech32m 编码生成地址
            prefix = "bc" if self.network == "bitcoin" else "tb"
            address = pubkeyhash_to_addr_bech32(tweaked_pubkey, prefix=prefix, witver=1)
            return address
            
        except Exception as e:
            logger.error(f"Taproot 地址生成失败: {e}")
            # 回退到 bitcoinlib 的实现
            return child_key.address(script_type='p2tr')
    
    def _get_address_params(self, address_type: AddressType) -> tuple:
        """
        获取不同地址类型的参数
        
        Args:
            address_type: 地址类型
            
        Returns:
            (script_type, encoding, purpose) 元组
        """
        if address_type == 'legacy':
            return 'p2pkh', 'base58', 44
        elif address_type == 'p2sh-segwit':
            return 'p2sh_p2wpkh', 'base58', 49
        elif address_type == 'segwit':
            return 'p2wpkh', 'bech32', 84
        elif address_type == 'taproot':
            return 'p2tr', 'bech32m', 86
        else:
            raise ValueError(f"不支持的地址类型: {address_type}")
    
    def _get_wallet_from_master_key(
        self,
        master_key: HDKey,
        index: int = 0,
        mnemonic: str = "",
        address_type: AddressType = 'segwit'
    ) -> Wallet:
        """
        从主密钥派生指定索引的钱包
        
        Args:
            master_key: HD钱包主密钥
            index: 派生路径索引
            mnemonic: 助记词（如果有的话）
            address_type: 地址类型，可选 'legacy', 'segwit', 'p2sh-segwit', 'taproot'
            
        Returns:
            钱包对象
        """
        # 获取地址类型参数
        script_type, encoding, purpose = self._get_address_params(address_type)
        
        # 使用对应的BIP路径派生子密钥
        # purpose'/coin_type'/account'/change/index
        # purpose: 44-legacy, 49-p2sh-segwit, 84-native-segwit, 86-taproot
        # coin_type: 0-mainnet, 1-testnet
        coin_type = 1 if self.network == "testnet" else 0
        path = f"m/{purpose}'/{coin_type}'/0'/0/{index}"
        
        # 派生子密钥
        child_key = master_key.key_for_path(path)
        
        # 获取地址
        if address_type == 'taproot':
            # 使用封装的 Taproot 地址生成函数
            address = self._generate_taproot_address(child_key)
        else:
            address = child_key.address(script_type=script_type, encoding=encoding)
        
        # 获取私钥（WIF格式）
        private_key = child_key.wif_key()
            
        return Wallet(
            address=address,
            private_key=private_key,
            mnemonic=mnemonic,
            index=index
        )
    
    # 生成钱包
    def generate_wallet(
        self,
        index: int = 0,
        address_type: AddressType = 'segwit'
    ) -> Tuple[bool, Wallet, str]:
        """
        生成BTC钱包（地址、私钥、助记词）
        
        Args:
            index: 钱包索引，默认为0。可以生成多个地址，每个地址的索引不同
            address_type: 地址类型，可选：
                - 'legacy': 传统地址（1开头）
                - 'p2sh-segwit': 兼容隔离见证地址（3开头）
                - 'segwit': 原生隔离见证地址（bc1q开头）
                - 'taproot': Taproot地址（bc1p开头）
            
        Returns:
            (是否成功, 钱包对象, 错误信息)
        """
        try:
            # 生成助记词
            mnemonic = Mnemonic().generate()
            
            # 从助记词生成种子
            seed = Mnemonic().to_seed(mnemonic)
            
            # 创建主密钥
            master_key = HDKey.from_seed(
                seed,
                network=self.network
            )
            
            # 派生钱包
            wallet = self._get_wallet_from_master_key(
                master_key,
                index,
                mnemonic,
                address_type
            )
            return True, wallet, ""
            
        except Exception as e:
            logger.error(f"生成BTC钱包失败: {str(e)}")
            return False, None, str(e)
    
    # 使用助记词恢复钱包
    def recover_wallet_from_mnemonic(
        self,
        mnemonic: str,
        index: int = 0,
        address_type: AddressType = 'segwit'
    ) -> Tuple[bool, Wallet, str]:
        """
        使用助记词恢复钱包
        
        Args:
            mnemonic: 助记词
            index: 钱包索引，默认为0。可以恢复多个地址，每个地址的索引不同
            address_type: 地址类型，可选：
                - 'legacy': 传统地址（1开头）
                - 'p2sh-segwit': 兼容隔离见证地址（3开头）
                - 'segwit': 原生隔离见证地址（bc1q开头）
                - 'taproot': Taproot地址（bc1p开头）
            
        Returns:
            (是否成功, 钱包对象, 错误信息)
        """
        try:
            # 验证助记词 - 通过尝试生成种子来验证
            try:
                seed = Mnemonic().to_seed(mnemonic)
            except Exception:
                return False, None, "无效的助记词"
            
            # 创建主密钥
            master_key = HDKey.from_seed(
                seed,
                network=self.network
            )
            
            # 派生钱包
            wallet = self._get_wallet_from_master_key(
                master_key,
                index,
                mnemonic,
                address_type
            )
            return True, wallet, ""
            
        except Exception as e:
            logger.error(f"从助记词恢复BTC钱包失败: {str(e)}")
            return False, None, str(e)
    
    # 使用私钥恢复钱包
    def recover_wallet_from_private_key(
        self,
        private_key: str,
        address_type: AddressType = 'segwit'
    ) -> Tuple[bool, Wallet, str]:
        """
        使用私钥恢复钱包
        
        Args:
            private_key: WIF格式的私钥
            address_type: 地址类型，可选：
                - 'legacy': 传统地址（1开头）
                - 'p2sh-segwit': 兼容隔离见证地址（3开头）
                - 'segwit': 原生隔离见证地址（bc1q开头）
                - 'taproot': Taproot地址（bc1p开头）
            
        Returns:
            (是否成功, 钱包对象, 错误信息)
        """
        try:
            # 直接从WIF私钥创建HDKey对象
            key = HDKey(private_key, network=self.network)
            
            # 获取对应类型的地址
            script_type, encoding, _ = self._get_address_params(address_type)
            
            # 获取地址
            if address_type == 'taproot':
                # 使用封装的 Taproot 地址生成函数
                address = self._generate_taproot_address(key)
            else:
                address = key.address(script_type=script_type, encoding=encoding)
            
            # 获取WIF格式私钥
            wif_private_key = key.wif_key()
            
            return True, Wallet(
                address=address,
                private_key=wif_private_key,
                mnemonic="",
                index=0
            ), ""
            
        except Exception as e:
            logger.error(f"从私钥恢复BTC钱包失败: {str(e)}")
            return False, None, str(e)
    
    # 查询余额
    def get_balance(self, address: str) -> Tuple[bool, float, str]:
        """
        查询BTC地址余额
        
        Args:
            address: BTC地址
            
        Returns:
            (是否成功, 余额(BTC), 错误信息)
        """
        try:
            # 创建服务实例
            service = Service(network=self.network, timeout=10)
            
            # 查询地址余额
            balance_satoshi = service.getbalance(address)
            
            logger.info(f"余额1: {balance_satoshi}")
            
            balance_btc = balance_satoshi / 100000000.0  # 1 BTC = 100,000,000 satoshi
            
            return True, balance_btc, ""
            
        except Exception as e:
            logger.error(f"查询余额失败: {e}")
            return False, 0.0, str(e) 