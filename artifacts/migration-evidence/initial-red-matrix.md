# 核心特征预言机红灯总表

第一次实现前运行：`python -m unittest discover -s tests`，42 项／42 错误／退出码 1，目标应用包缺失；`node --test tests/browser/*.test.mjs`，2 项失败／退出码 1，目标模板缺失。各 TEST 目录保留首轮红灯与批准预言机来源。

2026-09-28 校准 CSRF 与未登录重定向后，逐模块复验当前核心用例。下列 Python 模块全部退出码 1，因目标数据库模块尚不存在而失败；此时 BATCH-001 应用骨架已存在，未冒报未实现业务为成功。

| TEST | 模块 | 用例数 | 退出码 |
|---|---|---:|---:|
| 003 | tests.test_schema | 2 | 1 |
| 004 | tests.test_queries | 3 | 1 |
| 005 | tests.test_data_lifecycle | 3 | 1 |
| 006 | tests.test_auth_flows | 2 | 1 |
| 007 | tests.test_session_security | 2 | 1 |
| 008 | tests.test_input_security | 3 | 1 |
| 011 | tests.test_account | 2 | 1 |
| 012 | tests.test_purchase | 2 | 1 |
| 013 | tests.test_my_orders | 1 | 1 |
| 014 | tests.test_admin_reads | 2 | 1 |
| 015 | tests.test_admin_members | 2 | 1 |
| 016 | tests.test_admin_books | 2 | 1 |
| 017 | tests.test_media_validation | 2 | 1 |
| 018 | tests.test_media_recovery | 1 | 1 |
| 019 | tests.test_recovery | 2 | 1 |

TEST-009／010 的 Node 核心静态用例各 1 项，组合 2 项全部失败、退出码 1（目标模板不存在）。它们不代替后续 Edge 实测、截图签字、离线控制台与像素回归。

这些是入场核心预言机，不是完整退出测试：每批仍必须扩展到 test-plan.md 规定的全部 GOLD、边界、并发、故障注入、HTTP／Session／数据库副作用，不能用本表为尚未实现的业务验收。
