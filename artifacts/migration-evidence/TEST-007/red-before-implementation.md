# TEST-007 核心用例首次红灯

- 命令：`python -m unittest tests.test_session_security`
- 结果：退出码 1；目标 bookshop_app 包尚不存在（ModuleNotFoundError）。
- 预言机来源：30 分钟／8 小时服务端 Session 与危险 GET 安全决定；见 `openspec/changes/migrate-bookshop-to-python-sqlite/test-plan.md` 对应 TEST-007。
- 边界：这是实施前核心特征红灯，不是旧端动态结果，也不代表 本 TEST 的全部边界已覆盖。对应批次必须补充计划规定的完整用例、运行绿灯、记录前后状态与退出码。
