# TEST-020 BATCH-001 基础交付证据

日期：2026-09-28；仅验证本批基础交付，备份恢复与全量中文手册仍待 BATCH-007。

- 下载本机固定版本的 Windows x64／CPython 3.11 wheel，计算真实 SHA-256 后写入锁；全新虚拟环境采用 `--no-index --require-hashes -r requirements-test.lock` 离线安装，退出码 0。
- SBOM 覆盖 15 个运行依赖＋1 个仅测试 Pillow；与两份锁的名称／版本／哈希相等。Windows 传递依赖 colorama、cffi、pycparser、setuptools 均使用本机已有版本。
- `BOOKSHOP_VERIFY_ENV=1` 在干净虚拟环境核对实际安装集合与锁／SBOM 相等（排除安装工具 pip）；每个发行包内完整许可证原文存在，中文 notices 已登记。
- 外部配置示例只有占位符，无真实签名密钥；运行测试密钥临时生成，不写入仓库或证据。
- 已创建 `.github/workflows/bookshop-check.yml`，无交互 Windows 安装／基础测试；没有推送，不能声称 GitHub 上已跑绿。
- Bootstrap 和 jQuery 的目标端本地资源接入仍属于 BATCH-004，本批只登记预定版本和许可，不冒称其目标资源已经交付。

最终复验命令：`python -m unittest tests.test_runtime tests.test_routes.FoundationRouteTests tests.test_delivery.FoundationDeliveryTests`（在新虚拟环境并设置精确集合核对标志）。最终运行 18 项，全部通过，退出码 0；无跳过项。

BATCH-001 任务 2.3 的目标骨架提交回退尚未执行，不能宣称本批退出门禁已全部通过。
