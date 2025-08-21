#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cosmos 钱包工具演示
"""

from .wallet import CosmosWallet
import time

def demo_generate_new_wallet():
    """演示生成新钱包"""
    print("=== 生成新钱包 ===")
    
    wallet = CosmosWallet()
    
    # 生成 Persistence 钱包
    success, paxi_wallet, error = wallet.generate_wallet("paxi", 0)
    
    if success:
        print(f"Persistence 钱包:")
        print(f"助记词: {paxi_wallet.mnemonic}")
        print(f"私钥: {paxi_wallet.private_key}")
        print(f"地址: {paxi_wallet.address}")
        print(f"索引: {paxi_wallet.index}")
    else:
        print(f"生成失败: {error}")
    print()


def demo_restore_from_mnemonic():
    """演示从助记词恢复钱包"""
    print("=== 从助记词恢复钱包 ===")
    
    mnemonic = "mercy swamp hamster hunt gaze doctor legal ranch cake badge blind subject"
    expected_address = "paxi1paahe3amcgeepstrwylsrvwr002j7rx546evqx"
    
    # Persistence 钱包:
    # 助记词: pigeon quick chaos strong flower approve reunion alone thing deputy similar immense
    # 私钥: 01933db9af48bb633aee7491ef31e231509637b94762a6fd003bbab8e182c4a1
    # 公钥: 03a225a13777b0ada6d6d0940cb8065b3041d873aca8abfe427d53d7c2a31d96c3
    # 地址: paxi1cu92mcvufv2w3yfxzsss2jryx3c9zx69py76zk
    # 索引: 0
    # mnemonic = "pigeon quick chaos strong flower approve reunion alone thing deputy similar immense"
    
    
    wallet = CosmosWallet()
    
    # 恢复钱包
    success, restored_wallet, error = wallet.recover_from_mnemonic(mnemonic, "paxi", 0)
    
    if success:
        print(f"恢复的 Persistence 钱包:")
        print(f"助记词: {restored_wallet.mnemonic}")
        print(f"私钥: {restored_wallet.private_key}")
        print(f"地址: {restored_wallet.address}")
        print(f"索引: {restored_wallet.index}")
    else:
        print(f"恢复失败: {error}")
    
    # 展示不同索引的地址
    print("\n=== 同一助记词的不同地址索引 ===")
    for i in range(3):
        success, wallet_info, _ = wallet.recover_from_mnemonic(mnemonic, "paxi", i)
        if success:
            print(f"索引 {i}: {wallet_info.address}")
    print()


def demo_private_key_import():
    """演示从私钥导入钱包"""
    print("=== 从私钥导入钱包 ===")
    
    private_key = "4d499dd6c987f4e8f3f5d7bbe7c86f052ae96de9ded03527f49c0bb0d94a8922"
    
    wallet = CosmosWallet()
    success, wallet_info, error = wallet.recover_from_private_key(private_key, "paxi")
    
    if success:
        print(f"从私钥导入的钱包:")
        print(f"私钥: {wallet_info.private_key}")
        print(f"地址: {wallet_info.address}")
    else:
        print(f"导入失败: {error}")
    print()


def demo_multi_chain():
    """演示多链钱包"""
    print("=== 多链钱包 ===")
    
    mnemonic = "mercy swamp hamster hunt gaze doctor legal ranch cake badge blind subject"
    chains = [
        ("cosmos", "Cosmos Hub"),
        ("paxi", "Persistence"),
        ("osmo", "Osmosis"),
        ("juno", "Juno"),
    ]
    
    wallet = CosmosWallet()
    
    for prefix, name in chains:
        success, wallet_info, error = wallet.recover_from_mnemonic(mnemonic, prefix, 0)
        if success:
            print(f"{name}: {wallet_info.address}")
        else:
            print(f"{name}: 失败 - {error}")
    print()


def demo_transfer_functions():
    """演示转账功能"""
    print("=== 转账功能演示 ===")
    
    # Persistence主网LCD节点
    paxi_lcd = 'https://mainnet-lcd.paxinet.io'
    
    # 创建钱包实例（连接到Persistence网络）
    wallet = CosmosWallet(lcd_url=paxi_lcd)
    
    # 示例助记词和私钥（仅用于演示，请勿在生产环境使用）
    mnemonic = "mercy swamp hamster hunt gaze doctor legal ranch cake badge blind subject"
    to_address = "paxi109hp7zwd70mrq0mxajadteeknkf83c4lmghqnw"
    
    # 从助记词恢复钱包
    success, wallet_info, error = wallet.recover_from_mnemonic(mnemonic, "paxi", 0)
    if success:
        print(f"发送方地址: {wallet_info.address}")
        print(f"私钥: {wallet_info.private_key}")
        
        # 使用简化的转账接口（带等待确认功能）
        success, tx_hash, error = wallet.transfer_coin(
            private_key_hex=wallet_info.private_key,
            to_address=to_address,  # 替换为实际的接收地址
            amount=5.2,  # 转账金额（PAXI）
            fee=0.006,    # 手续费（PAXI）
            memo="Test transfer via Python SDK",
            wait_for_confirmation=True,  # 等待交易确认
            timeout=30  # 30秒超时
        )
        
        if success:
            print(f"转账结果: {error}")  # error字段包含详细的成功信息
            print(f"交易哈希: {tx_hash}")
        else:
            print(f"转账失败: {error}")
        
    else:
        print(f"恢复钱包失败: {error}")
    
    print()



def main():
    """主演示函数"""
    print("Cosmos 钱包工具演示\n")
    
    demo_generate_new_wallet()
    demo_restore_from_mnemonic()
    demo_private_key_import()
    demo_multi_chain()
    demo_transfer_functions()


if __name__ == "__main__":
    main()