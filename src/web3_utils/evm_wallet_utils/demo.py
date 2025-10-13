#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVM钱包工具类使用示例
"""

from .wallet import EVMWallet

def test_wallet_offline():
    """离线功能测试"""
    # 创建钱包工具实例
    evm = EVMWallet()
    
    # print("=== EVM钱包工具类演示 ===\n")
    
    # address_list = []
    
    # for _ in range(20):
    #     success, wallet, msg = evm.generate_wallet()
    #     if success:
    #         print(wallet.address)
    #         address_list.append((wallet.address, wallet.private_key, wallet.mnemonic))
    
    # with open("wallet_list.txt", "w") as f:
    #     for address, private_key, mnemonic in address_list:
    #         f.write(f"{address}----{private_key}----{mnemonic}\n")
    
    # success, wallet, msg = evm.generate_wallet()
    # if success:
    #     print(wallet.address)
    #     print(wallet.private_key)
    #     print(wallet.mnemonic)
    #     print(wallet.index)
    # address_list = []
    # mnemonic = "kid swing merry employ senior elder switch until lyrics purpose cotton injury"
    # for i in range(20):
    #     success, wallet, msg = evm.recover_wallet_from_mnemonic(mnemonic, index=i)
    #     if success:
    #         print(wallet.address)
    #         address_list.append((wallet.address, wallet.private_key))
        
    # with open("wallet_list.txt", "w") as f:
    #     for address, private_key in address_list:
    #         f.write(f"{address}----{private_key}\n")
    
    # with open("wallet.txt", "w") as f:
    #     for address, private_key in address_list:
    #         f.write(f"{address}\n")
        
        
    # success, wallet, msg = evm.recover_wallet_from_private_key(wallet.private_key)
    # if success:
    #     print(wallet.address)
    #     print(wallet.private_key)
        
        
#     message = "RichWorld"
#     success, sign_message, msg = evm.sign_message("0xa0cae50832449d0f7d38f7fed002066f1e04b467d782dc5cb908e2100c647997", message)
#     if success:
#         print(sign_message.signature)
#         print(sign_message.signature_r)
#         print(sign_message.signature_s)
#         print(sign_message.signature_v)
        
#     success, msg = evm.verify_signature(message, sign_message.signature, "0xD63FA832915ec48c837BAab82dFaFf35699C02cb")
#     print(success, msg)


# address = "0x9c86c9369a5f49de3c09c17002d5f49afb2c486c"
# private_key = "0x6f8180c346eacfa31a84e347397384ceb2c9d3ca80e968a6f11bbc47dd8c5deb"
# to_address = "0x0c2c9b6d0fdabdf8478143a054200ba50e90bcf4"
# amount_ether = "1"
# contract_address = "0x55d398326f99059ff775485246999027b3197955"

def test_wallet_online():
    evm = EVMWallet(rpc_url="https://bsc-dataseed1.binance.org")
    # success, balance, msg = evm.get_balance(address)
    # print(success, balance, msg)
    
    # success, tx_hash, msg = evm.transfer_coin(
    #     private_key=private_key,
    #     to_address=to_address,
    #     amount_ether=amount_ether,
    #     wait_for_confirmation=True
    # )
    
    # if success:
    #     print(f"转账成功!")
    #     print(f"交易哈希: {tx_hash}")
    #     print(f"转账金额: {amount_ether}")
    #     print(f"接收地址: {to_address}")
    
    # success, balance, msg = evm.get_token_balance(address, contract_address)
    # print(success, balance, msg)
    
    # success, tx_hash, msg = evm.transfer_token(
    #     private_key=private_key,
    #     to_address=to_address,
    #     amount=amount_ether,
    #     contract_address=contract_address,
    #     wait_for_confirmation=True
    # )
    # print(success, tx_hash, msg)

if __name__ == "__main__":
    test_wallet_offline()
    # test_wallet_online()