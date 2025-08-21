#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC钱包工具类使用示例
"""

from .wallet import BTCWallet

def test_wallet():
    """BTC钱包功能测试"""
    print("\n=== BTC钱包工具类演示 ===\n")
    
    # 创建BTC钱包工具实例（使用测试网进行演示）
    btc = BTCWallet(network="bitcoin")
    
    # address_list = []
    
    # for _ in range(30):
    #     success, wallet, msg = btc.generate_wallet(address_type="taproot")
    #     if success:
    #         print(wallet.address)
    #         address_list.append((wallet.address, wallet.private_key, wallet.mnemonic))
    
    # with open("wallet_list.txt", "w") as f:
    #     for address, private_key, mnemonic in address_list:
    #         f.write(f"{address}----{private_key}----{mnemonic}\n")
    
    
    # # 测试生成钱包
    # print("1. 生成新钱包：")
    # success, wallet, msg = btc.generate_wallet()
    # if success:
    #     print(f"地址: {wallet.address}")
    #     print(f"私钥: {wallet.private_key}")
    #     print(f"助记词: {wallet.mnemonic}")
    #     print(f"索引: {wallet.index}")
        
    #     # 保存钱包信息用于后续测试
    #     test_mnemonic = wallet.mnemonic
    #     test_private_key = wallet.private_key
    #     test_address = wallet.address
    # else:
    #     print(f"生成钱包失败: {msg}")
    #     return
    
    # print("\n2. 从助记词恢复钱包：")
    # success, wallet, msg = btc.recover_wallet_from_mnemonic(test_mnemonic)
    # if success:
    #     print(f"地址: {wallet.address}")
    #     print(f"私钥: {wallet.private_key}")
    #     print(f"助记词: {wallet.mnemonic}")
    #     print(f"索引: {wallet.index}")
    #     print(f"地址验证: {'成功' if wallet.address == test_address else '失败'}")
    # else:
    #     print(f"从助记词恢复失败: {msg}")
    
    # print("\n3. 从私钥恢复钱包：")
    # success, wallet, msg = btc.recover_wallet_from_private_key(test_private_key)
    # if success:
    #     print(f"地址: {wallet.address}")
    #     print(f"私钥: {wallet.private_key}")
    #     print(f"地址验证: {'成功' if wallet.address == test_address else '失败'}")
    # else:
    #     print(f"从私钥恢复失败: {msg}")
        
        
        
    mnemonic = "swing kitchen wreck slim filter name tennis spell garden fog seek science"
    
    # taproot
    private_key = "KwoquikkhFXnA2V5i5NCC2c6sYtJa8nE8qgii7xmvZfYTTV97NHV"
    address = "bc1psce69jzm8x9za2d68fyr3y9cesewxuqq0ue2m70ywlt4vg0ev86spw53l3"
    
    # # legacy
    # private_key = "L4yWrKhVK9QzTnRJ21vodTUnzWwtHGtcdVnDM883uGUvVLEQaPpi"
    # address = "17DNjRDbdAjjTS8w4fT7MdZgSXHhfSaVQe"
    
    # # p2sh-segwit
    # private_key = "KzntKXANZpb9VZTM87Ewea2P9kapviKpMoyWYMRmmkorH4MARJUy"
    # address = "36hynDoe6w2EJnRsDvnAv7kZvN5Tw2EXKK"
    
    # segwit
    # private_key = "L3nt3dzC6t84PkKj6Rx7rWD56gcX9YS2H3jZ4NNv5Es1fL7aHGgx"
    # address = "bc1qr6hkxdel6h7ww3y6f0lwt8rs8kvaw2m3hmzykx"
    
    
    # success, wallet, msg = btc.recover_wallet_from_mnemonic(mnemonic, address_type="legacy")
    # if success:
    #     print(f"地址: {wallet.address}")
    #     print(f"私钥: {wallet.private_key}")
    #     print(f"助记词: {wallet.mnemonic}")
    #     print(f"索引: {wallet.index}")
    # else:
    #     print(f"从助记词恢复失败: {msg}")
    
    # success, wallet, msg = btc.recover_wallet_from_private_key(private_key, address_type="taproot")
    # if success:
    #     print(f"地址: {wallet.address}")
    #     print(f"私钥: {wallet.private_key}")
    #     print(f"助记词: {wallet.mnemonic}")
    #     print(f"索引: {wallet.index}")
    # else:
    #     print(f"从私钥恢复失败: {msg}")
    
    success, balance, msg = btc.get_balance(address)
    if success:
        print(f"余额: {balance} BTC")
    else:
        print(f"查询余额失败: {msg}")
        
    success, balance, msg = btc.get_balance("bc1pqmyjjgvk0eal7e6pkdcd8nycxh0aqr3pydykqcgacg6yvpe5frlq40yutk")
    if success:
        print(f"余额: {balance} BTC")
    else:
        print(f"查询余额失败: {msg}")
    
    # with open("wallet_list.txt", "r") as f:
    #     for line in f:
    #         address, private_key, mnemonic = line.strip().split("----")
    #         success, balance, msg = btc.get_balance(address)
    #         if success:
    #             print(f"地址: {address} 余额: {balance} BTC")
    #         else:
    #             print(f"查询余额失败: {msg}")
    

if __name__ == "__main__":
    test_wallet() 