# TEST-015 核心用例首次红灯

- 命令：`python -m unittest tests.test_admin_members`
- 结果：退出码 1；目标 bookshop_app 包尚不存在（ModuleNotFoundError）。
- 预言机来源：GOLD-017／018 有单拒删、无单原子删除；见 `openspec/changes/migrate-bookshop-to-python-sqlite/test-plan.md` 对应 TEST-015。
- 边界：这是实施前核心特征红灯，不是旧端动态结果，也不代表 本 TEST 的全部边界已覆盖。对应批次必须补充计划规定的完整用例、运行绿灯、记录前后状态与退出码。
