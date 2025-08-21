from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from typing import Dict, Any, Union, List
from loguru import logger
import time
from mnemonic import Mnemonic
import requests
from tronpy.abi import trx_abi

class TronWallet:
    def __init__(self, network: str = 'mainnet', api_key: Union[str, List[str]] = None, jw_token: str = None):
        """
        初始化TRC20Token类
        :param network: 'mainnet' 或 'nile' (测试网)
        :param api_key: 可选的API密钥 支持单个秘钥 或 多个秘钥字符串列表
        :param jw_token: 可选的JWT密钥
        """
        if api_key:
            self.client = Tron(
                network=network,
                provider=HTTPProvider(
                api_key=api_key,
                jw_token=jw_token
                )
            )
            if jw_token:
                self.headers = {"Tron-Pro-Api-Key": api_key, "Authorization": "Bearer " + jw_token}
            else:
                self.headers = {"Tron-Pro-Api-Key": api_key}
        else:
            self.client = Tron(
                network=network
            )
        # 设置API端点
        self.api_endpoint = {
            'mainnet': 'https://api.trongrid.io',
            'nile': 'https://nile.trongrid.io'
        }.get(network, 'https://api.trongrid.io')
        
        
    def get_account_info(self, address: str) -> Dict[str, Any]:
        """
        异步查询账户信息
        """
        try:
            account = self.client.get_account(address)
            # logger.info(json.dumps(account, indent=4))
            
            balance_in_sun = account.get("balance", 0)
            balance = balance_in_sun / 1_000_000
            
            # 处理时间戳，如果时间戳不存在或无效则返回空字符串
            def format_timestamp(ts):
                try:
                    if ts and isinstance(ts, (int, float)) and ts > 0:
                        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts/1000))  # 转换毫秒为秒
                    return ""
                except:
                    return ""
            
            # 获取账户资源信息
            account_resource_info = self.client.get_account_resource(address)
            # logger.info(json.dumps(account_resource_info, indent=4))
           
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "address": address,
                    "balance": balance,  
                    "balance_in_sun": balance_in_sun,
                    "create_time": format_timestamp(account.get("create_time")),
                    "latest_opration_time": format_timestamp(account.get("latest_opration_time")),
                    "latest_consume_free_time": format_timestamp(account.get("latest_consume_free_time")),
                    "is_frozen": len(account.get("frozen", [])) > 0,
                    "freeNetUsed": account_resource_info.get("freeNetUsed", 0),
                    "freeNetLimit": account_resource_info.get("freeNetLimit", 0),
                    "freeNet": account_resource_info.get("freeNetLimit", 0) - account_resource_info.get("freeNetUsed", 0),
                    "EnergyUsed": account_resource_info.get("EnergyUsed", 0),
                    "EnergyLimit": account_resource_info.get("EnergyLimit", 0),
                    "Energy": account_resource_info.get("EnergyLimit", 0) - account_resource_info.get("EnergyUsed", 0),
                }
            }
        except Exception as e:
            logger.error(f"获取账户信息失败: {str(e)}")
            return {
                "code": 500,
                "message": f"获取账户信息失败: {str(e)}",
                "data": {}
            }
    
    def get_token_info(self, contract_address: str) -> Dict[str, Any]:
        """
        异步获取代币基本信息
        """
        try:
            # tronpy的合约调用暂时保持同步
            contract = self.client.get_contract(contract_address)
            name = contract.functions.name()
            symbol = contract.functions.symbol()
            decimals = contract.functions.decimals()
            total_supply = contract.functions.totalSupply()
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "name": name,
                    "symbol": symbol,
                    "decimals": decimals,
                    "total_supply": total_supply / (10 ** decimals)
                }
            }
        except Exception as e:
            return {
                "code": 500,
                "message": f"获取代币信息失败: {str(e)}",
                "data": {}
            }

    def get_token_balance(self, contract_address: str, address: str) -> Dict[str, Any]:
        """
        异步查询地址代币余额
        """
        try:
            # tronpy的合约调用暂时保持同步
            contract = self.client.get_contract(contract_address)
            name = contract.functions.name()
            symbol = contract.functions.symbol()
            decimals = contract.functions.decimals()
            balance = contract.functions.balanceOf(address)
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "name": name,
                    "symbol": symbol,
                    "decimals": decimals,
                    "address": address,
                    "balance": balance / (10 ** decimals)
                }
            }
        except Exception as e:
            return {
                "code": 500,
                "message": f"查询余额失败: {str(e)}",
                "data": {}
            }
     
    def get_transaction_info(self, tx_id: str) -> Dict[str, Any]:
        """
        异步查询交易详情
        """
        try:
            # 获取交易信息
            tx = {}
            try:
                tx = self.client.get_transaction(tx_id)
                # logger.debug(f"tx: {tx}")
            except Exception as e:
                return {
                "code": 500,
                "message": f"交易不存在：{str(e)}",
                "data": {}
                }

            
            tx_info = {}
            try:
                tx_info = self.client.get_transaction_info(tx_id)
                # logger.info(f"tx_info: {tx_info}")
            except Exception as e:
                pass

            
            # 判断交易状态
            status = "未知状态"
            if tx_info:
                # logger.info(f"tx_info: {tx_info}")
                status = tx.get("ret", [{}])[0].get("contractRet")
                if status == "SUCCESS":
                    status = "已完成"
                elif status == "REVERT":
                    status = "已回滚"
                elif status == "OUT_OF_ENERGY":
                    status = "能量不足"
                elif status == "TRANSFER_FAILED":
                    status = "转账失败"
                else:
                    status = "未知状态"
            else:  # 如果tx_info为空，说明交易还在pending
                status = "确认中"
            
            
            # 获取交易基本信息
            contract_data = tx.get("raw_data", {}).get("contract", [])[0]
            contract_type = contract_data.get("type", "")
            value_data = contract_data.get("parameter", {}).get("value", {})
            
            # 获取from地址
            from_address = value_data.get("owner_address", "")
            if from_address.startswith("41"):  # 如果是hex格式
                from_address = self.client.to_base58check_address(from_address)
            
            # 基础交易信息
            result = {
                "transaction_id": tx_id,
                "status": status,
                "from": from_address,
                "block_timestamp": time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(tx_info.get("blockTimeStamp", 0)/1000)
                ) if tx_info.get("blockTimeStamp") else ""
            }

            # 根据交易类型解析详细信息
            if contract_type == "TransferContract":  # TRX转账
                to_address = value_data.get("to_address", "")
                if to_address.startswith("41"):
                    to_address = self.client.to_base58check_address(to_address)
                amount_in_sun = value_data.get("amount", 0)
                
                result.update({
                    "to": to_address,
                    "type": "TRX",
                    "token_info": {
                        "symbol": "TRX",
                        "decimals": 6,
                        "amount": amount_in_sun / 1_000_000,
                        "amount_in_sun": amount_in_sun
                    }
                })
                
            elif contract_type == "TriggerSmartContract":  # 智能合约调用（TRC20转账）
                try:
                    contract_address = value_data.get("contract_address", "")
                    if contract_address.startswith("41"):
                        contract_address = self.client.to_base58check_address(contract_address)
                    
                    data = value_data.get("data", "")
                    if data and len(data) >= 72 and data.startswith("a9059cbb"):  # 标准TRC20转账方法ID
                        # 解析接收地址
                        to_address_hex = "41" + data[32:72]
                        to_address = self.client.to_base58check_address(to_address_hex)
                        
                        # 解析转账金额
                        amount_hex = data[72:]
                        amount_int = int(amount_hex, 16)
                        
                        # 获取代币信息
                        contract = self.client.get_contract(contract_address)
                        name = contract.functions.name()
                        symbol = contract.functions.symbol()
                        decimals = contract.functions.decimals()
                        amount = amount_int / (10 ** decimals)
                        
                        result.update({
                            "to": to_address,
                            "type": "TRC20",
                            "token_info": {
                                "address": contract_address,
                                "name": name,
                                "symbol": symbol,
                                "decimals": decimals,
                                "amount": amount
                            }
                        })
                except Exception as e:
                    logger.warning(f"解析合约信息失败: {str(e)}")
            else:
                result["type"] = contract_type  # 其他类型的交易

            return {
                "code": 200,
                "message": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"获取交易信息失败: {str(e)}")
            return {
                "code": 500,
                "message": f"获取交易信息失败: {str(e)}",
                "data": {}
            }
    def _get_energy_price(self) -> int:
        """
        获取能量单价
        Returns:
            int: 能量单价（单位：SUN/能量）
        """
        try:
            # 获取链上资源价格信息
            chain_parameters = self.client.get_chain_parameters()
            
            # 遍历参数找到能量单价
            for param in chain_parameters:
                if param['key'] == 'getEnergyFee':
                    return int(param['value'])
            
            # 如果找不到，返回默认值420 sun/能量
            return 420
            
        except Exception as e:
            logger.error(f"获取能量单价失败: {str(e)}")
            # 如果获取失败，返回默认值
            return 420
    
    def transfer_token(self, 
                contract_address: str, 
                from_private_key: str,
                to_address: str, 
                amount: float,
                fee_limit: int = 10,  # 默认10 TRX
                auto_fee_limit: bool = True,
                wait_confirmation: bool = True) -> Dict[str, Any]:
        """
        异步转账TRC20代币
        :param contract_address: 合约地址
        :param from_private_key: 发送方私钥
        :param to_address: 接收方地址
        :param amount: 转账金额
        :param fee_limit: 交易费用上限(单位: TRX, 默认10 TRX)
        :param auto_fee_limit: 是否自动计算交易费用
        :param wait_confirmation: 是否等待交易确认
        """
        if from_private_key.startswith("0x"):
            from_private_key = from_private_key[2:]
        
        try:
            # tronpy的合约调用暂时保持同步
            contract = self.client.get_contract(contract_address)
            private_key = PrivateKey(bytes.fromhex(from_private_key))
            
            from_address = private_key.public_key.to_base58check_address()
            
            # 获取代币信息
            name = contract.functions.name()
            symbol = contract.functions.symbol()
            decimals = contract.functions.decimals()
            
            amount_in_sun = int(amount * (10 ** decimals))
            
            
            encoded_params = trx_abi.encode_abi(['address', 'uint256'], [to_address, amount_in_sun])
            # print("encoded_params", encoded_params.hex())
            
            # decoded_params = trx_abi.decode_abi(['address', 'uint256'],
            # bytes.fromhex(encoded_params.hex()))
            # print("decoded_params", decoded_params)
            
            energy_fee = self._get_energy_price()
            # print(f"energy_fee: {energy_fee}")
            
            # 获取交易费用
            if auto_fee_limit:
                try:
                    result = self.client.trigger_constant_contract(
                        private_key.public_key.to_hex_address(),
                        self.client.to_hex_address(contract_address),
                        "transfer(address,uint256)",
                        encoded_params.hex()
                    )
                    # print(f"result: {result}", result["energy_used"])
                    
                    if isinstance(result, dict) and "energy_used" in result:
                        energy_used = result["energy_used"]
                        fee_limit_in_sun = int(energy_used * energy_fee * 1.5)
                    else:
                        fee_limit_in_sun = 40_000_000
                except Exception as e:
                    logger.error(f"获取交易费用失败: {str(e)}")
                    fee_limit_in_sun = 25_000_000
            else:
                fee_limit_in_sun = int(fee_limit * (10 ** decimals))
            
            # print(f"fee_limit_in_sun: {fee_limit_in_sun}")

            txn = (
                contract.functions.transfer(to_address, amount_in_sun)
                .with_owner(from_address)
                .fee_limit(fee_limit_in_sun)  # 在这里设置fee_limit
                .build()
                .sign(private_key)
            )
            
            # 广播交易
            result = txn.broadcast()
            transaction_id = result.get("txid", "")
            if wait_confirmation:
                result.wait()  # 等待交易确认
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "transaction_id": transaction_id,
                    "status": "已完成" if wait_confirmation else "确认中",
                    "from": from_address,
                    "to": to_address,
                    "amount": amount,
                    "confirmed": wait_confirmation,
                    "contract_info": {
                        "address": contract_address,
                        "name": name,
                        "symbol": symbol,
                        "decimals": decimals
                    }
                }
            }
        except Exception as e:
            logger.error(f"转账失败: {str(e)}")
            return {
                "code": 500,
                "message": f"转账失败: {str(e)}",
                "data": {}
            }

    def transfer_trx(self,
                from_private_key: str,
                to_address: str,
                amount: float,
                wait_confirmation: bool = True) -> Dict[str, Any]:
        """
        异步转账TRX
        :param from_private_key: 发送方私钥
        :param to_address: 接收方地址
        :param amount: 转账金额(TRX)
        :param wait_confirmation: 是否等待交易确认
        """
        if from_private_key.startswith("0x"):
            from_private_key = from_private_key[2:]
        
        try:
            private_key = PrivateKey(bytes.fromhex(from_private_key))
            from_address = private_key.public_key.to_base58check_address()
            
            # TRX的最小单位是sun，1 TRX = 1,000,000 sun
            amount_in_sun = int(amount * 1_000_000)
            
            # 创建交易
            txn = (
                self.client.trx.transfer(from_address, to_address, amount_in_sun)
                .build()
                .sign(private_key)
            )
            
            # 广播交易
            result = txn.broadcast()
            transaction_id = result.get("txid", "")
            if wait_confirmation:
                result.wait()  # 等待交易确认

            return {
                "code": 200,
                "message": "success",
                "data": {
                    "transaction_id": transaction_id,
                    "status": "已完成" if wait_confirmation else "确认中",
                    "from": from_address,
                    "to": to_address,
                    "amount": amount,
                    "amount_in_sun": amount_in_sun,
                    "confirmed": wait_confirmation,
                    "token_info": {
                        "symbol": "TRX",
                        "decimals": 6
                    }
                }
            }
        except Exception as e:
            logger.error(f"转账失败: {str(e)}")
            return {
                "code": 500,
                "message": f"转账失败: {str(e)}",
                "data": {}
            }

    def get_trx_transfers(self, 
                          address: str,
                          limit: int = 20,
                          only_confirmed: bool = True) -> Dict[str, Any]:
        """
        查询TRX转账记录
        :param address: 要查询的地址
        :param limit: 返回的记录数量限制
        :param only_confirmed: 是否只返回已确认的交易
        """
        try:

            api_url = f"{self.api_endpoint}/v1/accounts/{address}/transactions"
            params = {
                "only_confirmed": str(only_confirmed).lower(),  # 转换为 'true' 或 'false'
                "limit": str(limit),  # 转换为字符串
                "order_by": "block_timestamp,desc"
            }

            response = requests.get(api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # logger.info(f"data: {response.text}")
                
            if not data.get("data"):
                return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "address": address,
                        "transfers": []
                    }
                }
            
            # 解析交易记录
            transfers = []
            for tx in data["data"]:
                try:
                    # 获取交易基本信息
                    contract_data = tx.get("raw_data", {}).get("contract", [])[0]
                    if contract_data.get("type") != "TransferContract":
                        continue
                   
                    status = tx.get("ret", [{}])[0].get("contractRet", "UNKNOWN")
                    
                    value_data = contract_data.get("parameter", {}).get("value", {})
                    
                    # 解析地址
                    from_addr = value_data.get("owner_address", "")
                    to_addr = value_data.get("to_address", "")
                    if from_addr.startswith("41"):
                        from_addr = self.client.to_base58check_address(from_addr)
                    if to_addr.startswith("41"):
                        to_addr = self.client.to_base58check_address(to_addr)
                    
                    # 判断是转出还是转入
                    direction = "OUT" if from_addr == address else "IN"
                    
                    
                    # 解析金额和时间戳
                    amount_in_sun = value_data.get("amount", 0)  

                    timestamp = tx.get("block_timestamp", 0)
                    tx_time = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(timestamp/1000)
                    ) if timestamp else ""
                    
                    transfers.append({
                        "transaction_id": tx.get("txID", ""),
                        "from": from_addr,
                        "to": to_addr,
                        "amount": amount_in_sun / 1_000_000,
                        "amount_in_sun": amount_in_sun,
                        "timestamp": tx_time,
                        "type": "TRX",
                        "status": status,
                        "direction": direction
                    })
                    
                except Exception as e:
                    # logger.warning(f"解析交易记录失败: {str(e)}")
                    continue
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "address": address,
                    "transfers": transfers
                }
            }
        except Exception as e:
            logger.error(f"获取TRX转账记录失败: {str(e)}")
            return {
                "code": 500,
                "message": f"获取TRX转账记录失败: {str(e)}",
                "data": {}
            }

    def get_token_transfers(self,
                            contract_address: str,
                            address: str,
                            limit: int = 20,
                            only_confirmed: bool = True) -> Dict[str, Any]:
        """
        查询TRC20代币转账记录
        :param contract_address: 合约地址
        :param address: 要查询的地址
        :param limit: 返回的记录数量限制
        :param only_confirmed: 是否只返回已确认的交易
        """
        try:
            api_url = f"{self.api_endpoint}/v1/accounts/{address}/transactions/trc20"
            params = {
                "contract_address": contract_address,
                "only_confirmed": str(only_confirmed).lower(),  # 转换为 'true' 或 'false'
                "limit": str(limit),  # 转换为字符串
                "order_by": "block_timestamp,desc"
            }
            response = requests.get(api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # logger.info(f"data: {response.text}")
            if not data.get("data"):
                return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "address": address,
                        "contract_info": {
                            "address": contract_address,
                        },
                        "transfers": []
                    }
                }
            
            # 解析交易记录
            name = ""
            symbol = ""
            decimals = None
            transfers = []
            for tx in data["data"]:
                try: 
                    # 解析转账数据
                    token_info = tx.get("token_info", {})
                    name = token_info.get("name", "")
                    symbol = token_info.get("symbol", "")
                    decimals = token_info.get("decimals", 0)
                    
                    from_addr = tx.get("from", "")
                    to_addr = tx.get("to", "")
                    amount_in_sun = tx.get("value", 0)
                    amount = float(amount_in_sun) / (10 ** decimals)
                    
                    # 解析时间戳
                    timestamp = tx.get("block_timestamp", 0)
                    tx_time = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(timestamp/1000)
                    ) if timestamp else ""
                    
                    # 判断是转出还是转入
                    direction = "OUT" if from_addr == address else "IN"
                    
                    transfers.append({
                        "transaction_id": tx.get("transaction_id", ""),
                        "from": from_addr,
                        "to": to_addr,
                        "amount": amount,
                        "amount_in_sun": amount_in_sun,
                        "timestamp": tx_time,
                        "type": "TRC20",
                        "status": "SUCCESS",
                        "direction": direction
                    })
                    
                except Exception as e:
                    logger.warning(f"解析交易记录失败: {str(e)}")
                    continue
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "address": address,
                    "contract_info": {
                        "address": contract_address,
                        "name": name,
                        "symbol": symbol,
                        "decimals": decimals
                    },
                    "transfers": transfers
                }
            }
        except Exception as e:
            logger.error(f"获取代币转账记录失败: {str(e)}")
            return {
                "code": 500,
                "message": f"获取代币转账记录失败: {str(e)}",
                "data": {}
            }

    def create_wallet_by_private_key(self) -> Dict[str, Any]:
        """
        创建私钥钱包
        :return: 包含私钥和地址的字典
        """
        try:
            address_info = self.client.generate_address()
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "private_key": address_info["private_key"],
                    "address": address_info["base58check_address"]
                }
            }
        except Exception as e:
            logger.error(f"创建私钥钱包失败: {str(e)}")
            return {
                "code": 500,
                "message": f"创建私钥钱包失败: {str(e)}",
                "data": {}
            }
  
    def create_wallet_by_mnemonic(self,
                               num_words: int = 12, 
                               account_index: int = 0,
                               address_index: int = 0) -> Dict[str, Any]:
        """
        创建助记词钱包，使用波场标准路径 m/44'/195'/account'/0/address
        :param num_words: 与种子短语一起使用的单词数量。默认是12个单词。必须是[12,15,18,21,24]中的一个。
        :param account_index: 账户索引，用于生成多个账户
        :param address_index: 地址索引，用于在同一账户下生成多个地址
        """
        try:

            
            account_info, mnemonic = self.client.generate_address_with_mnemonic(
                num_words=num_words,
                account_path=f"m/44'/195'/{account_index}'/0/{address_index}"
            )
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "mnemonic": mnemonic,
                    "private_key": account_info["private_key"],
                    "address": account_info["base58check_address"],
                    "path": f"m/44'/195'/{account_index}'/0/{address_index}"
                }
            }
        except Exception as e:
            logger.error(f"创建助记词钱包失败: {str(e)}")
            return {
                "code": 500,
                "message": f"创建助记词钱包失败: {str(e)}",
                "data": {}
            }
    
    def recover_wallet_by_mnemonic(self,
                                         mnemonic: str,
                                account_index: int = 0,
                                address_index: int = 0) -> Dict[str, Any]:
        """
        通过助记词恢复钱包，使用波场标准路径 m/44'/195'/account'/0/address
        :param mnemonic: 助记词字符串
        :param account_index: 账户索引，用于恢复特定账户
        :param address_index: 地址索引，用于恢复特定地址
        """
        try:
            # 验证助记词
            mnemo = Mnemonic("english")
            if not mnemo.check(mnemonic):
                return {
                    "code": 400,
                    "message": "无效的助记词",
                    "data": {}
                }
            
            # 从助记词恢复账户
            account_info = self.client.generate_address_from_mnemonic(
                mnemonic,
                account_path=f"m/44'/195'/{account_index}'/0/{address_index}"
            )
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "mnemonic": mnemonic,
                    "private_key": account_info["private_key"],
                    "address": account_info["base58check_address"],
                    "path": f"m/44'/195'/{account_index}'/0/{address_index}"
                }
            }
        except Exception as e:
            logger.error(f"恢复助记词钱包失败: {str(e)}")
            return {
                "code": 500,
                "message": f"恢复助记词钱包失败: {str(e)}",
                "data": {}
            }

    def recover_address_by_private_key(self,
                                            private_key: str) -> Dict[str, Any]:
        """
        通过私钥恢复地址
        :param private_key: 私钥字符串（可以带0x前缀）
        :return: 包含地址的字典
        """
        try:
            # 移除0x前缀
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            
            # 验证私钥格式
            if not all(c in '0123456789abcdefABCDEF' for c in private_key) or len(private_key) != 64:
                return {
                    "code": 400,
                    "message": "无效的私钥格式",
                    "data": {}
                }
            
            # 从私钥生成地址
            private_key_obj = PrivateKey(bytes.fromhex(private_key))
            address_info = self.client.generate_address(priv_key=private_key_obj)
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "private_key": address_info["private_key"],
                    "address": address_info["base58check_address"]
                }
            }
        except Exception as e:
            logger.error(f"通过私钥恢复地址失败: {str(e)}")
            return {
                "code": 500,
                "message": f"通过私钥恢复地址失败: {str(e)}",
                "data": {}
            }

    

    

    