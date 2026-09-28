# TEST-020 基础交付首次红灯

命令：`python -m unittest tests.test_runtime tests.test_delivery.FoundationDeliveryTests`。组合测试退出码 1；其中交付用例因配置示例、固定哈希锁和 SBOM 文件不存在而失败。缺失文件确实被检出，不是无断言占位用例。
