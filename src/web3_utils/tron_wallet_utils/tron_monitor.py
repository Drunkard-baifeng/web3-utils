import asyncio
import json
import time
import threading
from typing import Dict, List, Union, Callable
from decimal import Decimal
from loguru import logger

from .wallet import TronWallet  # 使用相对导入

class TronBlockScanner:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self, network: str = 'mainnet', api_key: Union[str, List[str]] = None, jw_token: str = None):
        """
        初始化TronBlockScanner类
        :param network: 'mainnet' 或 'nile' (测试网)
        :param api_key: 可选的API密钥 支持单个秘钥 或 多个秘钥字符串列表
        :param jw_token: 可选的JWT密钥
        """
        if not hasattr(self, '_initialized'):
            self.client = TronWallet(network=network, api_key=api_key, jw_token=jw_token).client
            
            # USDT合约地址
            self.usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # 主网USDT合约地址
            
            # 记录已扫描的区块
            self.last_block_number = 0
            self._running = False
            self._scan_task = None
            
            # 回调函数
            self._on_trx_callback = None
            self._on_usdt_callback = None
            
            # 记录已处理的交易ID（使用字典存储，value为区块号）
            self._processed_tx_ids = {}
            # 保留的区块数量
            self._keep_blocks = 5
            # 并发锁
            self._tx_lock = asyncio.Lock()
            
            # 监控地址管理
            self._monitored_addresses = set()  # 使用集合存储监控地址
            self._address_lock = asyncio.Lock()  # 地址修改锁
            
            self._initialized = True
        
    def set_trx_callback(self, callback: Callable[[Dict], None]):
        """
        设置TRX交易回调函数
        :param callback: 回调函数，接收交易数据字典
        """
        self._on_trx_callback = callback
        
    def set_usdt_callback(self, callback: Callable[[Dict], None]):
        """
        设置USDT交易回调函数
        :param callback: 回调函数，接收交易数据字典
        """
        self._on_usdt_callback = callback
        
    async def add_addresses(self, addresses: List[str]):
        """
        添加监控地址
        :param addresses: 要添加的地址列表
        """
        async with self._address_lock:
            self._monitored_addresses.update(addresses)
            logger.info(f"添加监控地址: {addresses}")
            
    async def remove_addresses(self, addresses: List[str]):
        """
        移除监控地址
        :param addresses: 要移除的地址列表
        """
        async with self._address_lock:
            self._monitored_addresses.difference_update(addresses)
            logger.info(f"移除监控地址: {addresses}")
            
    async def get_monitored_addresses(self) -> List[str]:
        """
        获取当前监控的地址列表
        :return: 当前监控的地址列表
        """
        async with self._address_lock:
            return list(self._monitored_addresses)
            
    async def start_scan(self, addresses: List[str], interval: int = 3, block_range: int = 3):
        """
        开始扫描区块
        Args:
            addresses: 要监控的地址列表
            interval: 扫描间隔(秒)
            block_range: 区块区间范围，从最新区块往前查多少个区块
        """
        if self._running:
            logger.warning("扫描已经在运行中")
            return
            
        self._running = True
        try:
            # 添加初始监控地址
            await self.add_addresses(addresses)
            
            self.last_block_number = self.client.get_latest_block_number()
            logger.info(f"启动扫描，当前最新区块: {self.last_block_number}")
        except Exception as e:
            logger.error(f"启动扫描失败: {type(e).__name__}: {str(e)}")
            return
        
        # 创建扫描任务
        self._scan_task = asyncio.create_task(self._scan_loop(addresses, interval, block_range))
        
    async def _scan_loop(self, addresses: List[str], interval: int, block_range: int = 3):
        """
        扫描循环
        Args:
            addresses: 要监控的地址列表
            interval: 扫描间隔(秒)
            block_range: 区块区间范围，从最新区块往前查多少个区块
        """
        while self._running:
            try:
                # 获取最新区块号
                try:
                    current_block = self.client.get_latest_block_number()
                    # logger.info(f"当前最新区块: {current_block}")
                except Exception as e:
                    logger.error(f"获取最新区块失败: {type(e).__name__}: {str(e)}")
                    continue
                
                # 计算起始区块号
                start_block = max(current_block - block_range + 1, self.last_block_number + 1)
                
                # 扫描新区块
                if current_block > self.last_block_number:
                    # 获取当前监控地址
                    monitored_addresses = await self.get_monitored_addresses()
                    if not monitored_addresses:
                        logger.warning("没有监控地址，暂停扫描")
                        await asyncio.sleep(interval)
                        continue
                    
                    # 批量获取区块数据
                    start_time = time.time()
                    blocks = await self._get_blocks_batch(start_block, current_block)
                    end_time = time.time()
                    # logger.info(f"获取区块数据耗时: {end_time - start_time} 秒")
                    
                    # 并发处理所有区块的交易
                    process_tasks = [
                        self._process_block_transactions(block, monitored_addresses)
                        for block in blocks
                    ]
                    await asyncio.gather(*process_tasks, return_exceptions=True)
                    
                    # 更新最新区块号
                    self.last_block_number = current_block
                    
            except Exception as e:
                logger.error(f"扫描区块失败: {type(e).__name__}: {str(e)}")
                
            await asyncio.sleep(interval)
            
    async def _get_blocks_batch(self, start_block: int, end_block: int) -> List[Dict]:
        """
        批量获取区块数据
        """
        try:
            # 创建获取区块的任务列表
            get_block_tasks = []
            for block_num in range(start_block, end_block + 1):
                # 确保get_block是异步调用
                task = asyncio.create_task(self._get_block_async(block_num))
                get_block_tasks.append(task)
            
            # 并发获取所有区块数据
            blocks = await asyncio.gather(*get_block_tasks, return_exceptions=True)
            
            # 过滤掉异常和空结果
            valid_blocks = []
            for block in blocks:
                if isinstance(block, Exception):
                    logger.error(f"获取区块失败: {type(block).__name__}: {str(block)}")
                    continue
                if block:
                    valid_blocks.append(block)
                    
            return valid_blocks
            
        except Exception as e:
            logger.error(f"批量获取区块失败: {type(e).__name__}: {str(e)}")
            return []
            
    async def _get_block_async(self, block_number: int) -> Dict:
        """
        异步获取区块数据
        """
        try:
            return await asyncio.to_thread(self.client.get_block, block_number)
        except Exception as e:
            logger.error(f"获取区块 {block_number} 失败: {type(e).__name__}: {str(e)}")
            return None
            
    async def _process_block_transactions(self, block: Dict, addresses: List[str]):
        """
        处理区块中的交易
        """
        try:
            # 获取当前区块号
            current_block = block.get("block_header", {}).get("raw_data", {}).get("number", 0)
            if not current_block:
                return
                
            # 收集需要处理的交易
            transactions_to_process = []
            
            for tx in block.get("transactions", []):
                tx_id = tx.get("txID")
                if not tx_id:
                    continue
                    
                # 检查交易是否已处理
                async with self._tx_lock:
                    # 清理过期的交易ID（只保留最近N个区块的交易）
                    min_block = current_block - self._keep_blocks
                    self._processed_tx_ids = {
                        tx_id: block_num 
                        for tx_id, block_num in self._processed_tx_ids.items()
                        if block_num >= min_block
                    }
                    
                    # 如果交易已处理，跳过
                    if tx_id in self._processed_tx_ids:
                        continue
                        
                    # 记录区块号
                    self._processed_tx_ids[tx_id] = current_block
                    transactions_to_process.append(tx)
            
            # 批量处理交易
            if transactions_to_process:
                process_tasks = [
                    self._process_transaction(tx, addresses)
                    for tx in transactions_to_process
                ]
                await asyncio.gather(*process_tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"处理区块交易失败: {type(e).__name__}: {str(e)}")
            
    async def _process_transaction(self, tx: Dict, addresses: List[str]):
        """
        处理交易
        """
        try:
            tx_id = tx.get("txID")
            contract = tx.get("raw_data", {}).get("contract", [{}])[0]
            contract_type = contract.get("type")
            
            if contract_type == "TransferContract":
                # 处理TRX转账
                value = contract.get("parameter", {}).get("value", {})
                from_address = value.get("owner_address")
                to_address = value.get("to_address")
                amount = value.get("amount", 0)
                
                # 转换地址格式
                from_address = self.client.to_base58check_address(from_address)
                to_address = self.client.to_base58check_address(to_address)
                
                # 检查是否是需要监控的地址
                if from_address in addresses or to_address in addresses:
                    # 转换金额
                    amount_trx = Decimal(amount) / Decimal(1_000_000)
                    
                    # 判断交易方向
                    direction = "IN" if to_address in addresses else "OUT"
                    
                    # 获取交易状态
                    status = tx.get("ret", [{}])[0].get("contractRet", "UNKNOWN")
                    
                    # 构建交易数据
                    tx_data = {
                        "tx_id": tx_id,
                        "from_address": from_address,
                        "to_address": to_address,
                        "amount": amount_trx,
                        "direction": direction,
                        "status": status,
                        "token": "TRX"
                    }
                    
                    # 调用回调函数
                    if self._on_trx_callback:
                        await self._on_trx_callback(tx_data)
                    
            elif contract_type == "TriggerSmartContract":
                # 处理智能合约调用（如USDT转账）
                value = contract.get("parameter", {}).get("value", {})
                contract_address = value.get("contract_address")
                
                if contract_address == self.usdt_contract:
                    # 解析USDT转账数据
                    data = value.get("data", "")
                    if data.startswith("a9059cbb"):  # USDT transfer method signature
                        # 解析转账参数
                        to_address = "41" + data[32:72]
                        amount = int(data[72:], 16)
                        
                        # 转换地址格式
                        to_address = self.client.to_base58check_address(to_address)
                        from_address = self.client.to_base58check_address(value.get("owner_address"))
                        
                        # 检查是否是需要监控的地址
                        if from_address in addresses or to_address in addresses:
                            # 转换金额
                            amount_usdt = Decimal(amount) / Decimal(1_000_000)
                            
                            # 判断交易方向
                            direction = "IN" if to_address in addresses else "OUT"
                            
                            # 获取交易状态
                            status = tx.get("ret", [{}])[0].get("contractRet", "UNKNOWN")
                            
                            # 构建交易数据
                            tx_data = {
                                "tx_id": tx_id,
                                "from_address": from_address,
                                "to_address": to_address,
                                "amount": amount_usdt,
                                "direction": direction,
                                "status": status,
                                "token": "USDT"
                            }
                            
                            # 调用回调函数
                            if self._on_usdt_callback:
                                await self._on_usdt_callback(tx_data)
                            
        except Exception as e:
            logger.error(f"处理交易失败: {type(e).__name__}: {str(e)}")
            logger.error(f"交易数据: {json.dumps(tx, ensure_ascii=False)}")
            
    async def stop_scan(self):
        """
        停止扫描
        """
        if not self._running:
            return
            
        self._running = False
        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
                
        logger.info("扫描已停止")