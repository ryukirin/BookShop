# TEST-010 核心用例首次红灯

- 命令：`node --test tests/browser/catalog.test.mjs`
- 结果：退出码 1；目标 Jinja 模板尚不存在（ENOENT）。
- 预言机来源：GOLD-014／015／019 的目录链接、分类和页面决定；见 `openspec/changes/migrate-bookshop-to-python-sqlite/test-plan.md` 对应 TEST-010。
- 边界：这是实施前核心特征红灯，不是旧端动态结果，也不代表 本 TEST 的全部边界已覆盖。对应批次必须补充计划规定的完整用例、运行绿灯、记录前后状态与退出码。
