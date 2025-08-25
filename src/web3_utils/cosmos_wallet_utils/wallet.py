#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cosmos 钱包生成和管理工具
使用 cosmpy 和 mospy-wallet 的专业实现
"""

from mospy import Account, Transaction
from mnemonic import Mnemonic
from typing import Tuple, Dict, Any
import requests
import json
from loguru import logger
from cosmpy.crypto.address import Address


class Wallet:
    """钱包数据类"""
    def __init__(self, address: str, private_key: str, mnemonic: str, index: int):
        self.address = address
        self.private_key = private_key
        self.mnemonic = mnemonic
        self.index = index


class CosmosWallet:
    """Cosmos 钱包类"""
    
    def __init__(self, lcd_url: str = None, rpc_url: str = None):
        """
        初始化Cosmos钱包
        
        Args:
            lcd_url: LCD节点URL (用于查询和发送交易)
            rpc_url: RPC节点URL (备用)
        """
        self.mnemo = Mnemonic("english")
        self.lcd_url = lcd_url
        self.rpc_url = rpc_url
    
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
            logger.error(f"生成钱包失败: {str(e)}")
            return False, None, str(e)
    
    def recover_wallet_from_mnemonic(self, mnemonic: str, prefix: str = "cosmos", 
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
            logger.error(f"从助记词恢复钱包失败: {str(e)}")
            return False, None, str(e)
    
    def recover_wallet_from_private_key(self, private_key_hex: str, 
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
            # 使用 mospy Account 从私钥恢复（传递十六进制字符串，不是bytes）
            account = Account(
                private_key=private_key_hex,
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
            logger.error(f"从私钥恢复钱包失败: {str(e)}")
            return False, None, str(e)
    
    def fetch_chain_id(self, lcd_url: str = None) -> Tuple[bool, str, str]:
        """
        获取链ID信息
        
        Args:
            lcd_url: LCD节点URL，如果不提供则使用初始化时的URL
            
        Returns:
            (是否成功, 链ID, 错误信息)
        """
        try:
            url = lcd_url or self.lcd_url
            if not url:
                return False, "", "未提供LCD节点URL"
            
            resp = requests.get(f"{url}/cosmos/base/tendermint/v1beta1/node_info")
            resp.raise_for_status()
            chain_id = resp.json()["default_node_info"]["network"]
            return True, chain_id, ""
        except Exception as e:
            logger.error(f"获取链ID失败: {str(e)}")
            return False, "", str(e)
    
    def fetch_account_info(self, address: str, lcd_url: str = None) -> Tuple[bool, Dict[str, int], str]:
        """
        获取账户信息（account_number和sequence）
        
        Args:
            address: 钱包地址
            lcd_url: LCD节点URL，如果不提供则使用初始化时的URL
            
        Returns:
            (是否成功, 包含account_number和sequence的字典, 错误信息)
        """
        try:
            url = lcd_url or self.lcd_url
            if not url:
                return False, {}, "未提供LCD节点URL"
            
            resp = requests.get(f"{url}/cosmos/auth/v1beta1/accounts/{address}")
            resp.raise_for_status()
            data = resp.json()
            base_account = data.get("account", {})
            
            account_info = {
                "account_number": int(base_account.get("account_number", 0)),
                "sequence": int(base_account.get("sequence", 0))
            }
            
            return True, account_info, ""
        except Exception as e:
            logger.error(f"获取账户信息失败: {str(e)}")
            return False, {}, str(e)
    
    def is_valid_bech32_address(self, addr: str, hrp: str = "cosmos") -> Tuple[bool, str]:
        """
        验证bech32地址格式是否有效
        
        Args:
            addr: 要验证的地址
            hrp: 地址前缀（如 "cosmos", "paxi", "osmo"）
            
        Returns:
            (是否有效, 错误信息)
        """
        try:
            if not addr.startswith(hrp):
                return False, f"地址前缀不正确，应以{hrp}开头"
            
            Address(addr)  # 如果地址无效会抛出异常
            return True, ""
        except Exception as e:
            return False, f"地址验证失败: {str(e)}"
    
    def send_tx(self, account: Account, to_address: str, amount: float, fee: float, 
                chain_id: str, denom: str = "upaxi", memo: str = "", 
                lcd_url: str = None) -> Tuple[bool, str, str]:
        """
        发送转账交易
        
        Args:
            account: mospy Account对象（需要设置account_number和next_sequence）
            to_address: 接收地址
            amount: 转账金额（以主币为单位，如1.5 PAXI）
            fee: 手续费（以主币为单位，如0.04 PAXI）
            chain_id: 链ID
            denom: 币种单位（如"upaxi"）
            memo: 备注信息
            lcd_url: LCD节点URL，如果不提供则使用初始化时的URL
            
        Returns:
            (是否成功, 交易哈希, 错误信息)
        """
        try:
            url = lcd_url or self.lcd_url
            if not url:
                return False, "", "未提供LCD节点URL"
            
            # 验证接收地址格式
            is_valid, error_msg = self.is_valid_bech32_address(to_address, to_address.split('1')[0])
            if not is_valid:
                return False, "", f"接收地址无效: {error_msg}"
            
            # 创建交易
            tx = Transaction(
                account=account,
                gas=int(fee * 10**6 / 0.05),  # 根据费用计算gas
                chain_id=chain_id,
                memo=memo
            )
            
            # 设置手续费
            tx.set_fee(amount=int(fee * 10**6), denom=denom)
            
            # 添加转账消息
            tx.add_msg(
                tx_type="transfer",
                sender=account,
                recipient=to_address,
                amount=int(amount * 10**6),  # 转换为最小单位
                denom=denom
            )
            
            # 构建交易数据
            payload = {
                "tx_bytes": tx.get_tx_bytes_as_string(),
                "mode": "BROADCAST_MODE_ASYNC"
            }
            
            # 发送交易
            resp = requests.post(f"{url}/cosmos/tx/v1beta1/txs", json=payload)
            resp.raise_for_status()
            
            tx_response = resp.json().get("tx_response", {})
            tx_hash = tx_response.get("txhash")
            
            if tx_hash:
                return True, tx_hash, "交易已发送"
            else:
                return False, "", "交易发送失败，未获取到交易哈希"
                
        except Exception as e:
            logger.error(f"发送交易失败: {str(e)}")
            return False, "", str(e)
    
    def fetch_tx_status(self, tx_hash: str, lcd_url: str = None) -> Dict[str, Any]:
        """
        查询交易状态（按照官方示例实现）
        
        Args:
            tx_hash: 交易哈希
            lcd_url: LCD节点URL，如果不提供则使用初始化时的URL
            
        Returns:
            交易状态字典
        """
        url = lcd_url or self.lcd_url
        if not url:
            return {"status": "error", "detail": "未提供LCD节点URL"}
        
        resp = requests.get(f"{url}/cosmos/tx/v1beta1/txs/{tx_hash}")
        if resp.status_code != 200:
            return {"status": "pending", "detail": "Node unreachable"}
        
        data = resp.json().get("tx_response", {})
        code = data.get("code", 0)
        if code == 0:
            return {"status": "success", "height": data.get("height")}
        return {"status": "failed", "code": code, "raw_log": data.get("raw_log")}
    
    def transfer_coin(self, private_key_hex: str, to_address: str, amount: float, 
                        fee: float = 0.04, denom: str = "upaxi", memo: str = "", 
                        hrp: str = "paxi", lcd_url: str = None, 
                        wait_for_confirmation: bool = False, timeout: int = 120) -> Tuple[bool, str, str]:
        """
        简化的转账接口（完全按照官方示例实现）
        
        Args:
            private_key_hex: 发送方私钥（十六进制字符串）
            to_address: 接收地址
            amount: 转账金额（以主币为单位）
            fee: 手续费（以主币为单位，默认0.04）
            denom: 币种单位（默认"upaxi"）
            memo: 备注信息
            hrp: 地址前缀（默认"paxi"）
            lcd_url: LCD节点URL，如果不提供则使用初始化时的URL
            wait_for_confirmation: 是否等待交易确认（默认False）
            timeout: 等待确认的超时时间（秒，默认120）
            
        Returns:
            (是否成功, 交易哈希, 错误信息)
        """
        try:
            url = lcd_url or self.lcd_url
            if not url:
                return False, "", "未提供LCD节点URL"
            
            # 1. Import account from private key (按照官方示例)
            account = Account(private_key=private_key_hex, hrp=hrp)
            
            # 2. Fetch account info and set it (按照官方示例)
            success, account_info, error = self.fetch_account_info(account.address, url)
            if not success:
                return False, "", f"获取账户信息失败: {error}"
            
            account.account_number = account_info["account_number"]
            account.next_sequence = account_info["sequence"]
            
            # 3. Get chain ID (按照官方示例)
            success, chain_id, error = self.fetch_chain_id(url)
            if not success:
                return False, "", f"获取链ID失败: {error}"
            
            # 4. Send transaction (按照官方示例)
            success, tx_hash, error = self.send_tx(account, to_address, amount, fee, chain_id, denom, memo, url)
            
            if not success:
                return success, tx_hash, error
            
            # 5. Wait for confirmation if requested (类似EVM钱包)
            if wait_for_confirmation:
                import time
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    status_info = self.fetch_tx_status(tx_hash, url)
                    
                    if status_info["status"] == "success":
                        height = status_info.get("height", "unknown")
                        return True, tx_hash, f"转账成功并已确认，区块高度: {height}"
                    elif status_info["status"] == "failed":
                        code = status_info.get("code", "unknown")
                        raw_log = status_info.get("raw_log", "")
                        return False, tx_hash, f"交易失败，错误码: {code}, 详情: {raw_log}"
                    
                    # 等待1秒后重试
                    time.sleep(1)
                
                # 超时了但交易可能还在处理中
                return True, tx_hash, f"转账已发送但确认超时（{timeout}秒），请手动查询交易状态"
            
            return success, tx_hash, error
            
        except Exception as e:
            logger.error(f"转账失败: {str(e)}")
            return False, "", str(e)
    
    def transfer_from_mnemonic(self, mnemonic: str, to_address: str, amount: float,
                                fee: float = 0.04, denom: str = "upaxi", memo: str = "",
                                hrp: str = "paxi", lcd_url: str = None,
                                wait_for_confirmation: bool = False, timeout: int = 120) -> Tuple[bool, str, str]:
        """
        从助记词直接转账（按照官方示例实现）
        
        Args:
            mnemonic: 助记词
            to_address: 接收地址
            amount: 转账金额（以主币为单位）
            fee: 手续费（以主币为单位，默认0.04）
            denom: 币种单位（默认"upaxi"）
            memo: 备注信息
            hrp: 地址前缀（默认"paxi"）
            lcd_url: LCD节点URL，如果不提供则使用初始化时的URL
            wait_for_confirmation: 是否等待交易确认（默认False）
            timeout: 等待确认的超时时间（秒，默认120）
            
        Returns:
            (是否成功, 交易哈希, 错误信息)
        """
        try:
            url = lcd_url or self.lcd_url
            if not url:
                return False, "", "未提供LCD节点URL"
            
            # 1. Import account from mnemonic (按照官方示例)
            account = Account(seed_phrase=mnemonic, hrp=hrp)
            
            # 2. Fetch account info and set it (按照官方示例)
            success, account_info, error = self.fetch_account_info(account.address, url)
            if not success:
                return False, "", f"获取账户信息失败: {error}"
            
            account.account_number = account_info["account_number"]
            account.next_sequence = account_info["sequence"]
            
            # 3. Get chain ID (按照官方示例)
            success, chain_id, error = self.fetch_chain_id(url)
            if not success:
                return False, "", f"获取链ID失败: {error}"
            
            # 4. Send transaction (按照官方示例)
            success, tx_hash, error = self.send_tx(account, to_address, amount, fee, chain_id, denom, memo, url)
            
            if not success:
                return success, tx_hash, error
            
            # 5. Wait for confirmation if requested (类似EVM钱包)
            if wait_for_confirmation:
                import time
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    status_info = self.fetch_tx_status(tx_hash, url)
                    
                    if status_info["status"] == "success":
                        height = status_info.get("height", "unknown")
                        return True, tx_hash, f"转账成功并已确认，区块高度: {height}"
                    elif status_info["status"] == "failed":
                        code = status_info.get("code", "unknown")
                        raw_log = status_info.get("raw_log", "")
                        return False, tx_hash, f"交易失败，错误码: {code}, 详情: {raw_log}"
                    
                    # 等待1秒后重试
                    time.sleep(1)
                
                # 超时了但交易可能还在处理中
                return True, tx_hash, f"转账已发送但确认超时（{timeout}秒），请手动查询交易状态"
            
            return success, tx_hash, error
            
        except Exception as e:
            logger.error(f"从助记词转账失败: {str(e)}")
            return False, "", str(e)