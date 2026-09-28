# TEST-002 首次红灯

- 命令：`python -m unittest tests.test_routes`
- 阶段：应用骨架尚未创建，先写冻结矩阵及逐批路由特征测试。
- 结果：退出码 1；运行 11 个测试，11 个错误，均为 `ModuleNotFoundError: No module named 'bookshop_app'`。这证明测试不会在目标应用缺席时假阳性通过；不代表旧端运行结果。
- 后续：BATCH-001 只要求 `FoundationRouteTests` 转绿。其余身份、目录、购买、管理分支保持红灯，分别在 BATCH-003～006 验收；全量 TEST-002 最终在 BATCH-006 验收。
- 基线：源修订 `eff378ba25960fd5c16d621a5940378504b7c1b1`；路由矩阵见 `artifacts/migration-evidence/TEST-002/route-matrix.md`。
