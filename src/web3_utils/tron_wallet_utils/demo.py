from tron_wallet_utils.wallet import TronWallet
from loguru import logger
import json
from tron_wallet_utils.tron_monitor import TronBlockScanner
import asyncio
import signal
from typing import Dict


# USDT合约地址（测试网）
# USDT_CONTRACT = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"
USDT_CONTRACT="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
# 测试用地址
# TEST_ADDRESS = "TXmXQffTduCNaaeirVMNNaxSMe21gyN6Fe"
TEST_ADDRESS="TUFxc4XMFkXHsxZ42nDLd353dhJ4HQPmGS"
# 测试用私钥
# TEST_PRIVATE_KEY = "0xf0d4116db7c066e873ba705651556119056d9da6c21e39571df908b159a1b0f4"
TEST_PRIVATE_KEY = "0xf0d4116db7c066e873ba705651556119056d9da6c21e39571df908b159a1b0f4"
# 接收地址
# RECEIVER_ADDRESS = "TUhkMKp13Dnk4JyFESQnxyw5LG1CP3dHk3"
RECEIVER_ADDRESS = "TDq85Q8HvuBV1DaNZUhbpaUjvC34FH37nG"


def test_wallet():
    main()


def main():
    # 创建TRC20Token实例（测试网）
    # trc20 = TRC20Token(network='nile')
    trc20 = TronWallet(network='mainnet', api_key="8a6ae74d-303e-4872-8d39-439abb077bfd")
    
    try:
        
        # # 测试获取代币信息
        # print("\n1. 测试获取代币信息:")
        # info = trc20.get_token_info(USDT_CONTRACT)
        # print(f"代币信息: {info}")

        # 测试查询代币余额
        TEST_ADDRESS="TGVFWuXM9wkbaYDg538Mbzo89Eg3Lpifte"
        print("\n2. 测试查询代币余额:")
        balance = trc20.get_token_balance(USDT_CONTRACT, TEST_ADDRESS)
        print(f"账户 {TEST_ADDRESS} 的USDT余额: {balance}")

        # # 测试查询账户信息
        # print("\n4. 测试查询账户信息:")
        # account_info = trc20.get_account_info(TEST_ADDRESS)
        # logger.info(json.dumps(account_info, indent=4, ensure_ascii=False))

        # # 测试转账功能
        # print("\n5. 测试转账功能:")
        # result = trc20.transfer_token(
        #     USDT_CONTRACT,
        #     TEST_PRIVATE_KEY,
        #     RECEIVER_ADDRESS,
        #     amount=20,
        #     fee_limit=20,
        #     auto_fee_limit=True,
        #     wait_confirmation=False
        # )
        # print(f"转账结果: {result}")

        # # 测试交易查询
        # print("\n6. 测试交易查询:")
        # for i in range(10):
        #     tx_info = trc20.get_transaction_info(result["data"]["transaction_id"])
        #     # tx_info = trc20.get_transaction_info("52b4f6a31be2c0e664ab0479b63db7193b04e04586a384aa694a31bd053f6ba1")
        #     print(f"交易详情: {tx_info}")
        #     if tx_info["code"] == 200:
        #         if tx_info["data"]["status"] != "确认中":
        #             break
        #     time.sleep(1)

        # # 测试TRX转账功能
        # print("\n7. 测试TRX转账功能:")
        # result = trc20.transfer_trx(
        #     TEST_PRIVATE_KEY,
        #     RECEIVER_ADDRESS,
        #     1.11,  # 转账0.1 TRX
        #     wait_confirmation=False
        # )
        # print(f"转账结果: {result}")
        

        # # 测试交易查询
        # print("\n8. 测试交易查询:")
        # for i in range(10):
        #     tx_info = trc20.get_transaction_info(result["data"]["transaction_id"])
        #     # tx_info = trc20.get_transaction_info("4144b6132f1328d9797ea550f7235b513d8cde1f285b2080e450c27ab6efdbc1")
        #     print(f"交易详情: {tx_info}")
        #     if tx_info["code"] == 200:
        #         if tx_info["data"]["status"] != "确认中":
        #             break
        #     time.sleep(1)

        # # 测试查询TRX转账记录
        # print("\n9. 测试查询TRX转账记录:")
        # trx_transfers = trc20.get_trx_transfers(TEST_ADDRESS, limit=10)
        # logger.info(json.dumps(trx_transfers, indent=2, ensure_ascii=False))

        # # 测试查询代币转账记录
        # print("\n10. 测试查询代币转账记录:")
        # token_transfers = trc20.get_token_transfers(USDT_CONTRACT, TEST_ADDRESS, limit=10)
        # logger.info(json.dumps(token_transfers, indent=2, ensure_ascii=False))
        
        # # 测试创建私钥钱包
        # print("\n11. 测试创建私钥钱包:")
        # wallet = trc20.create_wallet_by_private_key()
        # logger.info(f"新创建的私钥钱包: {json.dumps(wallet, indent=2, ensure_ascii=False)}")

        # 测试创建助记词钱包（12个词）
        print("\n12. 测试创建助记词钱包(12词):")
        wallet_12 = trc20.create_wallet_by_mnemonic(num_words=12)
        logger.info(f"12词助记词钱包: {json.dumps(wallet_12, indent=2, ensure_ascii=False)}")

        # # 测试创建助记词钱包（24个词）
        # print("\n13. 测试创建助记词钱包(24词):")
        # wallet_24 = trc20.create_wallet_by_mnemonic(num_words=24)
        # logger.info(f"24词助记词钱包: {json.dumps(wallet_24, indent=2, ensure_ascii=False)}")

        # # 测试通过助记词恢复钱包
        # print("\n14. 测试通过助记词恢复钱包:")
        # mnemonic = wallet_12["data"]["mnemonic"]  # 使用刚创建的12词助记词
        # recovered_wallet = trc20.recover_wallet_by_mnemonic(mnemonic)
        # logger.info(f"恢复的钱包: {json.dumps(recovered_wallet, indent=2, ensure_ascii=False)}")
        
        # # 验证恢复的钱包是否正确
        # assert recovered_wallet["data"]["address"] == wallet_12["data"]["address"], "助记词恢复的地址不匹配"
        # assert recovered_wallet["data"]["private_key"] == wallet_12["data"]["private_key"], "助记词恢复的私钥不匹配"
        # print("助记词恢复钱包验证通过!")

        # # 测试通过私钥恢复地址
        # print("\n15. 测试通过私钥恢复地址:")
        # # 使用已知的测试私钥
        # result = trc20.recover_address_by_private_key(TEST_PRIVATE_KEY)
        # logger.info(f"从私钥恢复的地址信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # # 验证恢复的地址是否正确
        # assert result["data"]["address"] == TEST_ADDRESS, "私钥恢复的地址不匹配"
        # print("私钥恢复地址验证通过!")


        # # print("\n所有钱包相关测试通过!")
        
        # # 测试通过助记词恢复钱包
        # print("\n16. 测试通过助记词恢复钱包:")
        # mnemonic = ""
        # for i in range(10):
        #     recovered_wallet = trc20.recover_wallet_by_mnemonic(mnemonic, account_index=0, address_index=i)
        #     logger.info(f"恢复的钱包{i}: {recovered_wallet['data']['address']}, 私钥: {recovered_wallet['data']['private_key']}, 路径: {recovered_wallet['data']['path']}")
        
    except AssertionError as e:
        print(f"测试断言失败: {str(e)}")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

async def on_trx_transaction(tx_data: Dict):
    """
    TRX交易回调函数
    """
    # 发送通知
    logger.info(
        f"发现新的TRX交易\n"
        f"交易ID: {tx_data['tx_id']}\n"
        f"发送方: {tx_data['from_address']}\n"
        f"接收方: {tx_data['to_address']}\n"
        f"金额: {tx_data['amount']} TRX\n"
        f"方向: {tx_data['direction']}\n"
        f"状态: {tx_data['status']}"
    )
    

async def on_usdt_transaction(tx_data: Dict):
    """
    USDT交易回调函数
    """
    # 发送通知
    logger.info(
        f"发现新的USDT交易\n"
        f"交易ID: {tx_data['tx_id']}\n"
        f"发送方: {tx_data['from_address']}\n"
        f"接收方: {tx_data['to_address']}\n"
        f"金额: {tx_data['amount']} USDT\n"
        f"方向: {tx_data['direction']}\n"
        f"状态: {tx_data['status']}"
    )
    


async def async_main():
    # 创建扫描器实例
    scanner = TronBlockScanner(
        api_key="8a6ae74d-303e-4872-8d39-439abb077bfd",
        network="mainnet"  # 或 'nile' 测试网
    )

    # 要监控的地址列表
    addresses = [
        "TUFxc4XMFkXHsxZ42nDLd353dhJ4HQPmGS",
        "TGoJt7p6pW2b1pktg2SDi4k25bfSfFEmsi",
        "TMkCQMbZTRD2YF2Tar2n5hwc6Hm7RyDLAz",
        "TLTiXxmCJunDxSckhPBs7wyjoJLuTyHrz2",
        "TWz9XUGpNbeMpyMR1xM8gXtatrnWbgSii3",
        "TThCTg2ujUWWAWmqUExGt2EF9vyNPt2hW4",
        "TSbueURjJSKQa8xEmkaeo8m82oJXaPWehb",
        "TQ1GNVqFzq6EZteHNc8EqaiARkr2NWDWgX",
        "TCDXt6beqorVTMufDLDHJUaYCqEmyhihUo"
    ]
    
    # 设置回调函数
    scanner.set_trx_callback(on_trx_transaction)
    scanner.set_usdt_callback(on_usdt_transaction)

    # 开始扫描
    try:
        await scanner.start_scan(addresses, interval=2, block_range=5)  # 每3秒检查一次新区块
    except Exception as e:
        return
    
    # 创建停止事件
    stop_event = asyncio.Event()
    
    # 设置信号处理（Windows兼容方式）
    def signal_handler(signum, frame):
        stop_event.set()
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 等待停止事件
        await stop_event.wait()
    finally:
        # 确保清理资源
        await scanner.stop_scan()
        logger.info("程序已优雅停止")

if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("程序已停止")
    