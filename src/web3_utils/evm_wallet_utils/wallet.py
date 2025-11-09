#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVM钱包工具类
提供钱包生成、恢复、签名、转账等功能
"""

from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from typing import Tuple
from loguru import logger
from decimal import Decimal

class Wallet:
    def __init__(self, address: str, private_key: str, mnemonic: str, index: int):
        self.address = address
        self.private_key = private_key
        self.mnemonic = mnemonic
        self.index = index

class SignMessage:
    def __init__(self, signature: str, signature_r: str, signature_s: str, signature_v: int):
        self.signature = signature
        self.signature_r = signature_r
        self.signature_s = signature_s
        self.signature_v = signature_v

class EVMWallet:
    """EVM钱包工具类"""
    
    # 标准ERC-20合约ABI（适用于所有EVM兼容网络）
    STANDARD_ERC20_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol", 
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]
    
    def __init__(self, rpc_url: str = None, chain_id: int = None):
        """
        初始化钱包工具类
        
        Args:
            rpc_url: RPC节点URL，如果不提供则只能离线操作
            chain_id: 链ID（1=主网，11155111=Sepolia测试网，137=Polygon等）
        """
        # 启用实验性功能
        Account.enable_unaudited_hdwallet_features()
        
        # Web3连接
        self.web3 = None
        self.chain_id = chain_id
        
        if rpc_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(rpc_url))
                if self.web3.is_connected():
                    logger.info(f"成功连接到区块链网络: {rpc_url}")
                    
                    # 如果没有指定chain_id，自动从网络获取
                    if self.chain_id is None:
                        self.chain_id = self.web3.eth.chain_id
                        logger.info(f"自动获取链ID: {self.chain_id}")
                else:
                    logger.warning(f"无法连接到区块链网络: {rpc_url}")
                    self.web3 = None
            except Exception as e:
                logger.error(f"连接区块链网络失败: {e}")
                self.web3 = None
                
        # 如果没有连接到网络且没有指定chain_id，使用默认值
        if self.chain_id is None:
            self.chain_id = 1  # 默认以太坊主网
    
    # 生成钱包
    def generate_wallet(self, index: int = 0) -> Tuple[bool, Wallet, str]:
        """
        方法1：生成钱包（地址、私钥、助记词【需要带索引的】）
        
        Args:
            index: 钱包索引，默认为0
            
        Returns:
            包含地址、私钥、助记词、索引的字典
        """
        try:
            # 生成助记词和账户
            account, mnemonic = Account.create_with_mnemonic(passphrase="", num_words=12, account_path=f"m/44'/60'/0'/0/{index}")
            
            private_key = "0x" + account.key.hex()
            address = account.address
            
            return True, Wallet(address, private_key, mnemonic, index), ""
        except Exception as e:
            logger.error(f"生成钱包失败: {str(e)}")
            return False, None, str(e)
    
    # 从助记词恢复钱包
    def recover_wallet_from_mnemonic(self, mnemonic: str, index: int = 0) -> Tuple[bool, Wallet, str]:
        """
        方法2：使用助记词恢复地址和私钥
        
        Args:
            mnemonic: 助记词
            index: 钱包索引，默认为0
            
        Returns:
            包含地址和私钥的字典
        """
        try:
            # 从助记词派生账户
            account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{index}")
            
            private_key = "0x" + account.key.hex()
            address = account.address
            
            return True, Wallet(address, private_key, mnemonic, index), ""
        except Exception as e:
            logger.error(f"从助记词恢复钱包失败: {str(e)}")
            return False, None, str(e)
        
    # 从私钥恢复钱包
    def recover_wallet_from_private_key(self, private_key: str) -> Tuple[bool, Wallet, str]:
        """
        方法3：使用私钥恢复钱包
        """
        try:
            account = Account.from_key(private_key) 
            address = account.address
            return True, Wallet(address, private_key, "", 0), ""
        except Exception as e:
            logger.error(f"从私钥恢复钱包失败: {str(e)}")
            return False, None, str(e)
    
    # 签名消息
    def sign_message(self, private_key: str, message: str) -> Tuple[bool, SignMessage, str]:
        """
        方法4：私钥签名
        
        Args:
            private_key: 私钥（十六进制字符串，可以带或不带0x前缀）
            message: 要签名的消息
            
        Returns:
            包含签名信息的字典
        """
        try:
            # 确保私钥格式正确
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            # 创建账户对象
            account = Account.from_key(private_key)
            
            # 编码消息（使用以太坊标准格式）
            encoded_message = encode_defunct(text=message)
            
            # 签名消息
            signed_message = account.sign_message(encoded_message)
            
            return True, SignMessage(signed_message.signature.hex(), hex(signed_message.r), hex(signed_message.s), signed_message.v), ""
        except Exception as e:
            logger.error(f"签名失败: {str(e)}")
            return False, None, str(e)
    
    # 验证签名
    def verify_signature(self, message: str, signature: str, address: str) -> Tuple[bool, str]:
        """
        验证签名
        
        Args:
            message: 原始消息
            signature: 签名
            address: 签名者地址
            
        Returns:
            验证结果
        """
        try:
            # 编码消息（使用以太坊标准格式）
            encoded_message = encode_defunct(text=message)
            
            # 恢复签名者地址
            recovered_address = Account.recover_message(encoded_message, signature=signature)
            return recovered_address.lower() == address.lower(), ""
        except Exception as e:
            logger.error(f"验证签名失败: {str(e)}")
            return False, str(e)
    
    # 估算Gas费用
    def estimate_gas_fee(self, from_address: str, to_address: str, amount_ether: str, data: str = None, gas_price_buffer: float = 1.2):
        """
        自动估算本次转账或合约调用的gas费用
        
        Args:
            from_address: 发送方地址
            to_address: 接收方地址  
            amount_ether: 转账金额（ether）
            data: 交易数据（calldata），用于合约交互
            gas_price_buffer: gas价格缓冲比例，默认1.2（增加20%）
            
        Returns:
            (费用ETH, gas限制, gas价格wei)
        """
        try:
            tx = {
                "from": from_address,
                "to": Web3.to_checksum_address(to_address),
                "value": self.web3.to_wei(amount_ether, "ether"),
                "chainId": self.chain_id,
            }
            
            # 如果有 data，添加到交易中
            if data and data != "0x":
                tx["data"] = data
            
            gas_limit = self.web3.eth.estimate_gas(tx)
            gas_price = self.web3.eth.gas_price
            
            logger.info(f"gas_price: {gas_price}")
            # 如果gas_price为0，使用合理的默认值
            if gas_price == 0:
                if self.chain_id == 42161:  # Arbitrum
                    gas_price = self.web3.to_wei(1, 'gwei')
                elif self.chain_id == 137:  # Polygon
                    gas_price = self.web3.to_wei(50, 'gwei')
                else:  # 以太坊主网
                    gas_price = self.web3.to_wei(20, 'gwei')
            else:
                # 增加缓冲比例，防止base fee上涨导致交易失败
                gas_price = int(gas_price * gas_price_buffer)
            
            fee_wei = gas_limit * gas_price
            fee_eth = self.web3.from_wei(fee_wei, "ether")
            
            logger.info(f"估算Gas - 限制: {gas_limit}, 价格: {self.web3.from_wei(gas_price, 'gwei')} Gwei, 手续费: {fee_eth}")
            return fee_eth, gas_limit, gas_price
            
        except Exception as e:
            logger.error(f"估算Gas费失败: {str(e)}")
            return None, None, None
    
    # 获取账户余额
    def get_balance(self, address: str) -> Tuple[bool, str, str]:
        """
        获取主网余额
        
        Args:
            address: 钱包地址
            
        Returns:
            (是否成功, 余额, 错误信息)
        """
        try:
            if not self.web3:
                return False, "0", "未连接到区块链网络"
            
            address = Web3.to_checksum_address(address)
            balance_wei = self.web3.eth.get_balance(address)
            balance_ether = self.web3.from_wei(balance_wei, 'ether')
            
            return True, str(balance_ether), ""
        except Exception as e:
            logger.error(f"获取余额失败: {str(e)}")
            return False, "0", str(e)
    
    # 转账主网币种
    def transfer_coin(self, private_key: str, to_address: str, amount_ether: str, gas_price_gwei: int = None, gas_limit: int = None, data: str = None, gas_price_buffer: float = 1.2, gas_limit_buffer: float = 1.2, wait_for_confirmation: bool = False) -> Tuple[bool, str, str]:
        """
        转账主网币种(ETH BNB) 或 调用合约
        
        Args:
            private_key: 发送方私钥
            to_address: 接收方地址（可以是普通地址或合约地址）
            amount_ether: 转账金额（以ether为单位）
            gas_price_gwei: Gas价格（以Gwei为单位，如果不指定则自动获取）
            gas_limit: Gas限制（如果不指定则自动估算）
            data: 交易数据（calldata），用于合约交互。不传或传"0x"表示普通转账
            gas_price_buffer: gas价格缓冲比例，默认1.2（增加20%）
            gas_limit_buffer: gas限制缓冲比例，默认1.2（增加20%）
            wait_for_confirmation: 是否等待交易确认
            
        Returns:
            (是否成功, 交易哈希, 错误信息)
        """
        is_contract_call = False  # 初始化变量，避免在异常处理时未定义
        try:
            if not self.web3:
                return False, "", "未连接到区块链网络"
            
            # 确保私钥格式正确
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            # 获取发送方地址
            account = Account.from_key(private_key)
            from_address = account.address
            
            # 检查余额
            balance_wei = self.web3.eth.get_balance(from_address)
            balance_ether = self.web3.from_wei(balance_wei, 'ether')
            
            if Decimal(balance_ether) < Decimal(amount_ether):
                return False, "", f"余额不足，当前余额: {balance_ether}"
            
            # 获取nonce
            to_address = Web3.to_checksum_address(to_address)
            nonce = self.web3.eth.get_transaction_count(from_address)
            
            # 处理data参数
            if data is None or data == "" or data == "0x":
                data = "0x"
                is_contract_call = False
            else:
                is_contract_call = True
                # 确保data格式正确
                if not data.startswith('0x'):
                    data = '0x' + data
            
            # 估算Gas费用和参数（传入data以支持合约调用）
            fee_eth, estimated_gas_limit, gas_price_wei = self.estimate_gas_fee(from_address, to_address, amount_ether, data, gas_price_buffer)
            
            # 处理估算结果
            if fee_eth is None:
                # 估算失败
                if is_contract_call and gas_limit is None:
                    # 合约调用估算失败，且用户没有手动指定gas_limit，返回错误
                    return False, "", "合约调用Gas估算失败，请检查合约地址和data是否正确，或手动指定gas_limit参数"
                
                # 普通转账估算失败，或用户手动指定了gas_limit，使用默认值
                if gas_limit is None:
                    logger.warning("Gas估算失败，使用默认值")
                    estimated_gas_limit = 100000 if self.chain_id == 42161 else 21000
                else:
                    estimated_gas_limit = gas_limit  # 使用用户指定的值
                
                # 处理gas_price
                if gas_price_gwei is None:
                    gas_price_gwei = 1 if self.chain_id == 42161 else 20
                gas_price_wei = self.web3.to_wei(gas_price_gwei, 'gwei')
            else:
                # 使用估算的值，如果用户没有指定gas_price_gwei则使用估算值
                if gas_price_gwei is None:
                    gas_price_gwei = int(self.web3.from_wei(gas_price_wei, 'gwei'))
                else:
                    # 用户指定了gas_price，使用用户指定的值
                    gas_price_wei = self.web3.to_wei(gas_price_gwei, 'gwei')
            
            # 处理gas_limit
            if gas_limit is None:
                # 添加缓冲比例（无论普通转账还是合约调用，统一标准）
                # 多余的gas不会被扣费，所以宁可多设置一点
                gas_limit = int(estimated_gas_limit * gas_limit_buffer)
            
            # 构建最终交易
            transaction = {
                'nonce': nonce,
                'to': to_address,
                'gas': gas_limit,
                'gasPrice': gas_price_wei,
                'value': self.web3.to_wei(amount_ether, 'ether'),
                'data': data,
                'chainId': self.chain_id
            }
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = self.web3.to_hex(tx_hash)
            
            # 如果需要等待确认
            if wait_for_confirmation:
                try:
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                    if receipt['status'] == 1:
                        return True, tx_hash_hex, f"转账成功并已确认，Gas使用量: {receipt['gasUsed']}"
                    else:
                        return False, tx_hash_hex, "交易失败（状态为0）"
                except Exception as e:
                    return True, tx_hash_hex, f"转账已发送但确认失败: {str(e)}"
            
            msg = "合约调用已发送" if is_contract_call else "转账已发送"
            return True, tx_hash_hex, msg
        except Exception as e:
            error_msg = f"合约调用失败: {str(e)}" if is_contract_call else f"主网币种转账失败: {str(e)}"
            logger.error(error_msg)
            return False, "", str(e)
    
    # 代币转账
    def transfer_token(self, private_key: str, to_address: str, amount: str, contract_address: str, contract_abi: list = None, gas_price_gwei: int = None, gas_limit: int = None, gas_price_buffer: float = 1.2, gas_limit_buffer: float = 1.2, wait_for_confirmation: bool = False) -> Tuple[bool, str, str]:
        """
        代币转账
        
        Args:
            private_key: 发送方私钥
            to_address: 接收方地址
            amount: 转账金额（以ether为单位）
            contract_address: 代币合约地址
            contract_abi: 合约ABI
            gas_price_gwei: Gas价格（以Gwei为单位，如果不指定则自动获取）
            gas_limit: Gas限制（如果不指定则自动估算）
            gas_price_buffer: gas价格缓冲比例，默认1.2（增加20%）
            gas_limit_buffer: gas限制缓冲比例，默认1.2（增加20%）
            wait_for_confirmation: 是否等待交易确认
            
        Returns:
            (是否成功, 交易哈希, 错误信息)
        """
        try:
            if not self.web3:
                return False, "", "未连接到区块链网络"
            
            # 确保私钥格式正确
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            # 获取发送方地址
            account = Account.from_key(private_key)
            from_address = account.address
            
            if contract_abi is None:
                contract_abi = self.STANDARD_ERC20_ABI
            
            # 创建合约实例
            contract_address = Web3.to_checksum_address(contract_address)
            contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
            
            amount = self.web3.to_wei(amount, 'ether')
            # 检查代币余额
            token_balance = contract.functions.balanceOf(from_address).call()
            if Decimal(token_balance) < Decimal(amount):
                return False, "", f"代币余额不足，当前余额: {token_balance}"
            
            # 检查ETH余额（用于支付Gas费）
            eth_balance_wei = self.web3.eth.get_balance(from_address)
            eth_balance_ether = self.web3.from_wei(eth_balance_wei, 'ether')
            
            # 获取nonce
            to_address = Web3.to_checksum_address(to_address)
            nonce = self.web3.eth.get_transaction_count(from_address)
            
            # 处理Gas价格
            if gas_price_gwei is None:
                try:
                    gas_price_wei = self.web3.eth.gas_price
                    logger.info(f"获取网络Gas价格: {gas_price_wei}")
                    
                    # 如果gas_price为0，使用合理的默认值
                    if gas_price_wei == 0:
                        if self.chain_id == 42161:  # Arbitrum
                            gas_price_wei = self.web3.to_wei(1, 'gwei')
                        elif self.chain_id == 137:  # Polygon
                            gas_price_wei = self.web3.to_wei(50, 'gwei')
                        else:  # 以太坊主网
                            gas_price_wei = self.web3.to_wei(20, 'gwei')
                        logger.info(f"网络Gas价格为0，使用默认值: {self.web3.from_wei(gas_price_wei, 'gwei')} Gwei")
                    else:
                        # 增加缓冲比例，防止base fee上涨导致交易失败
                        gas_price_wei = int(gas_price_wei * gas_price_buffer)
                except Exception as e:
                    # 获取失败，使用默认值
                    if self.chain_id == 42161:  # Arbitrum
                        gas_price_wei = self.web3.to_wei(1, 'gwei')
                    elif self.chain_id == 137:  # Polygon
                        gas_price_wei = self.web3.to_wei(50, 'gwei')
                    else:  # 以太坊主网
                        gas_price_wei = self.web3.to_wei(20, 'gwei')
                    logger.warning(f"获取Gas价格失败，使用默认值: {self.web3.from_wei(gas_price_wei, 'gwei')} Gwei")
            else:
                gas_price_wei = self.web3.to_wei(gas_price_gwei, 'gwei')
            
            # 构建基础交易
            base_transaction = {
                'from': from_address,
                'nonce': nonce,
                'gasPrice': gas_price_wei,
                'chainId': self.chain_id
            }
            
            # 构建代币转账交易（用于Gas估算）
            txn = contract.functions.transfer(to_address, int(amount)).build_transaction(base_transaction)
            
            # 处理gas_limit
            if gas_limit is None:
                try:
                    estimated_gas = self.web3.eth.estimate_gas(txn)
                    gas_limit = int(estimated_gas * gas_limit_buffer)  # 添加缓冲比例
                    logger.info(f"代币转账自动估算Gas: {estimated_gas}, 使用Gas: {gas_limit}")
                except Exception as e:
                    # 估算失败，使用网络特定的默认值
                    if self.chain_id == 42161:  # Arbitrum
                        gas_limit = 200000
                    elif self.chain_id == 137:  # Polygon
                        gas_limit = 150000
                    else:  # 以太坊主网
                        gas_limit = 100000
                    logger.warning(f"代币转账Gas估算失败，使用默认值 {gas_limit}: {e}")
            
            # 检查ETH余额是否足够支付Gas费
            estimated_gas_cost_wei = gas_limit * gas_price_wei
            estimated_gas_cost_ether = self.web3.from_wei(estimated_gas_cost_wei, 'ether')
            
            if Decimal(eth_balance_ether) < Decimal(estimated_gas_cost_ether):
                return False, "", f"ETH余额不足支付Gas费，需要: {estimated_gas_cost_ether} ETH，当前余额: {eth_balance_ether} ETH"
            
            # 更新最终的gas限制
            txn['gas'] = gas_limit
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = self.web3.to_hex(tx_hash)
            
            # 如果需要等待确认
            if wait_for_confirmation:
                try:
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                    if receipt['status'] == 1:
                        return True, tx_hash_hex, f"代币转账成功并已确认，Gas使用量: {receipt['gasUsed']}"
                    else:
                        return False, tx_hash_hex, "交易失败（状态为0）"
                except Exception as e:
                    return True, tx_hash_hex, f"代币转账已发送但确认失败: {str(e)}"
            
            return True, tx_hash_hex, "代币转账已发送"
        except Exception as e:
            logger.error(f"代币转账失败: {str(e)}")
            return False, "", str(e)
    
    # 获取代币余额
    def get_token_balance(self, address: str, contract_address: str, contract_abi: list = None) -> Tuple[bool, str, str]:
        """
        获取代币余额
        
        Args:
            address: 钱包地址
            contract_address: 代币合约地址
            contract_abi: 合约ABI
            
        Returns:
            (是否成功, 余额, 错误信息)
        """
        try:
            if not self.web3:
                return False, "0", "未连接到区块链网络"
            
            address = Web3.to_checksum_address(address)
            contract_address = Web3.to_checksum_address(contract_address)
            
            if contract_abi is None:
                contract_abi = self.STANDARD_ERC20_ABI
            
            # 创建合约实例
            contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
            
            # 获取余额
            balance = contract.functions.balanceOf(address).call()
            balance = self.web3.from_wei(balance, 'ether')
            
            return True, str(balance), ""
        except Exception as e:
            logger.error(f"获取代币余额失败: {str(e)}")
            return False, "0", str(e)
    
    # 等待交易确认
    def wait_for_transaction_receipt(self, tx_hash: str, timeout: int = 120) -> Tuple[bool, dict, str]:
        """
        等待交易确认
        
        Args:
            tx_hash: 交易哈希
            timeout: 超时时间（秒）
            
        Returns:
            (是否成功, 交易收据, 错误信息)
        """
        try:
            if not self.web3:
                return False, {}, "未连接到区块链网络"
            
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt["status"] == 1:
                return True, dict(receipt), ""
            else:
                return False, dict(receipt), "交易失败"
        except Exception as e:
            logger.error(f"等待交易确认失败: {str(e)}")
            return False, {}, str(e)