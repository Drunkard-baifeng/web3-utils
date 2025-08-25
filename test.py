#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钱包工具测试入口
"""

from src.web3_utils.evm_wallet_utils.demo import test_wallet_offline, test_wallet_online
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
    
    test_tron_wallet()