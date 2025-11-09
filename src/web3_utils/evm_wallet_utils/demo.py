#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVM钱包工具类使用示例
"""

from .wallet import EVMWallet
from eth_abi import encode

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
    address_list = []
    mnemonic = "tiger jelly liberty tree obvious prevent desk hint sentence onion lady display"
    for i in range(250):
        success, wallet, msg = evm.recover_wallet_from_mnemonic(mnemonic, index=i)
        if success:
            print(wallet.address)
            address_list.append((wallet.address, wallet.private_key))
        
    with open("wallet_list.txt", "w") as f:
        for address, private_key in address_list:
            f.write(f"{address}----{private_key}\n")
    
    with open("wallet.txt", "w") as f:
        for address, private_key in address_list:
            f.write(f"{address}\n")
        
        
    # success, wallet, msg = evm.recover_wallet_from_private_key(wallet.private_key)
    # if success:
    #     print(wallet.address)
    #     print(wallet.private_key)
        
        
    # message = "RichWorld"
    # success, sign_message, msg = evm.sign_message("0xa0cae50832449d0f7d38f7fed002066f1e04b467d782dc5cb908e2100c647997", message)
    # if success:
    #     print(sign_message.signature)
    #     print(sign_message.signature_r)
    #     print(sign_message.signature_s)
    #     print(sign_message.signature_v)
        
    # success, msg = evm.verify_signature(message, sign_message.signature, "0xD63FA832915ec48c837BAab82dFaFf35699C02cb")
    # print(success, msg)

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

def proxy_contract_transfer():
    """
    通过中间合约转账USDT
    
    交易示例: 0x995ed17013028b5b1013ca96d637b7ef51712b946fa2624ee38064204ba32e7f
    接口返回: {"orderId":350, "contractAddress":"0xd9cd8b53a31aef44482866ba5634736993929d47", 
                "tokenAddress":"0x55d398326f99059ff775485246999027b3197955", "payUsdt":1.21}
    """
    wallet = EVMWallet(rpc_url="https://bsc-dataseed1.binance.org")
    
    # 从接口获取的数据
    order_id = 354
    contract_address = "0xd9cd8b53a31aef44482866ba5634736993929d47"
    token_address = "0x55d398326f99059ff775485246999027b3197955"
    pay_usdt = "1.24"
    
    # 构造 data
    method_id = "0x4f292f8f"
    amount = wallet.web3.to_wei(pay_usdt, 'ether')
    encoded_params = encode(
        ['address', 'uint256', 'uint256'],
        [wallet.web3.to_checksum_address(token_address), amount, order_id]
    )
    
    data = method_id + encoded_params.hex()
    
    # 发送交易
    private_key = "0xcd5d4e8967b3dc989212d4e5211953be6c7c3b2557ce403631d1bb3614367374"
    
    success, tx_hash, msg = wallet.transfer_coin(
        private_key=private_key,
        to_address=contract_address,
        amount_ether="0",
        data=data,
        wait_for_confirmation=True
    )
    
    print(f"结果: {success}")
    print(f"哈希: {tx_hash}")
    print(f"消息: {msg}")

def approve_usdt_to_contract():
    """
    授权USDT给中间合约（只需执行一次）
    """
    wallet = EVMWallet(rpc_url="https://bsc-dataseed1.binance.org")
    
    # approve(address spender, uint256 amount)
    method_id = "0x095ea7b3"
    spender = "0xd9cd8b53a31aef44482866ba5634736993929d47"
    amount = 2**256 - 1  # 无限授权

    encoded_params = encode(
        ['address', 'uint256'],
        [wallet.web3.to_checksum_address(spender), amount]
    )
    
    data = method_id + encoded_params.hex()
    
    # 发送交易
    private_key = "0xcd5d4e8967b3dc989212d4e5211953be6c7c3b2557ce403631d1bb3614367374"
    usdt_contract = "0x55d398326f99059ff775485246999027b3197955"
    
    success, tx_hash, msg = wallet.transfer_coin(
        private_key=private_key,
        to_address=usdt_contract,
        amount_ether="0",
        data=data,
        wait_for_confirmation=True
    )
    
    print(f"授权结果: {success}")
    print(f"哈希: {tx_hash}")


def contract_call_with_address():
    """
    调用合约函数（传入一个地址参数）
    
    交易示例: 0x8caccf0a22586da003a9d65e5d11830f7c398336eacf91ab60f28674c5ea14ee
    可能用途: 绑定推荐人、注册、设置代理等
    """
    wallet = EVMWallet(rpc_url="https://arb1.arbitrum.io/rpc")
    
    # 配置参数
    contract_address = "0xd99be2a0bb6c3c569984634de1cd76eec691eef1"
    method_id = "0x04f618cb"
    param_address = "0x6cccdff7c394c97d19bed98699cd9dc7ef6f9ad2"  # 要传入的地址参数
    
    # 构造 data
    encoded_params = encode(
        ['address'],
        [wallet.web3.to_checksum_address(param_address)]
    )
    
    data = method_id + encoded_params.hex()
    
    # 发送交易
    private_key = "0x46c19f16c282f93296fc8f4daebd453462bcef90a2852506d8fed7b35cb6b2c2"
    
    success, tx_hash, msg = wallet.transfer_coin(
        private_key=private_key,
        to_address=contract_address,
        amount_ether="0",  # 不发送ETH
        data=data,
        wait_for_confirmation=True
    )
    
    print(f"结果: {success}")
    print(f"哈希: {tx_hash}")
    print(f"消息: {msg}")


def claim_mining_rewards():
    """
    领取挖矿奖励
    
    交易示例: 0x655380256863b300def628572eb88bcceb75b77e5c154b40e6a700c794c42d9f
    操作: 发送0.0001 ETH，触发奖励领取，获得300 CONV代币
    """
    wallet = EVMWallet(rpc_url="https://arb1.arbitrum.io/rpc")
    
    # 配置参数
    contract_address = "0x79baa25d3f369eed0621f45cfab8421cf56b085d"
    method_id = "0x99f4b251"  # 无参数函数
    value_eth = "0.0001"  # 发送0.0001 ETH
    
    # 发送交易
    private_key = "0x46c19f16c282f93296fc8f4daebd453462bcef90a2852506d8fed7b35cb6b2c2"
    
    success, tx_hash, msg = wallet.transfer_coin(
        private_key=private_key,
        to_address=contract_address,
        amount_ether=value_eth,  # 发送ETH
        data=method_id,  # 只需要函数选择器，无参数
        wait_for_confirmation=True
    )
    
    print(f"结果: {success}")
    print(f"哈希: {tx_hash}")
    print(f"消息: {msg}")
    if success:
        print("💰 奖励已领取，CONV代币会自动到账")


if __name__ == "__main__":
    test_wallet_offline()
    # test_wallet_online()
    
    # 合约交互示例：
    # 1. 先授权USDT给中间合约（只需执行一次）
    # approve_usdt_to_contract()
    
    # 2. 通过中间合约转账USDT（可多次执行）
    # proxy_contract_transfer()
    
    # 3. 调用合约函数（传入地址参数，如绑定推荐人）
    # contract_call_with_address()
    
    # 4. 领取挖矿奖励（发送ETH调用）
    # claim_mining_rewards()