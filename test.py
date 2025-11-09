#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包工具测试入口
"""

from src.web3_utils.evm_wallet_utils.demo import test_wallet_offline, test_wallet_online, approve_usdt_to_contract, proxy_contract_transfer, contract_call_with_address, claim_mining_rewards
from src.web3_utils.cosmos_wallet_utils.demo import demo_generate_new_wallet, demo_restore_from_mnemonic, demo_transfer_functions
from src.web3_utils.btc_wallet_utils.demo import test_wallet as test_btc_wallet
from src.web3_utils.tron_wallet_utils.demo import test_wallet as test_tron_wallet


if __name__ == "__main__":
    # # EVM钱包测试
    # test_wallet_offline()
    # test_wallet_online()
    
    # # BTC钱包测试
    # test_btc_wallet()

    # demo_generate_new_wallet()
    # demo_restore_from_mnemonic()
    # demo_transfer_functions()
    
    # test_tron_wallet()
    
        # 中间合约交互流程：
    # 1. 先授权（只需执行一次）
    # approve_usdt_to_contract()
    
    # 2. 再转账（可多次执行）
    # proxy_contract_transfer()
    
    # 3. 调用合约函数（传入地址参数）
    # contract_call_with_address()
    
    # 4. 领取挖矿奖励（发送ETH调用）
    claim_mining_rewards()