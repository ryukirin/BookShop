# 第三方组件与许可证

本清单对应 Windows x64／Python 3.11.3 固定 wheel；精确版本与 SHA-256 见 `requirements.lock`、`requirements-test.lock` 和 `sbom.json`。所有 Python 发行包的完整许可证原文随 wheel 安装到各自 `.dist-info`，TEST-020 核对这些原文实际存在；重分发不得剥离它们。法律许可原文保留第三方原语言，中文说明不替代原文。SQLite 属于 public domain；CPython 3.11.3 使用 PSF License 及历史许可。

| 组件 | 版本 | 许可证 | 范围 |
|---|---|---|---|
| blinker | 1.6.2 | MIT | 运行时 |
| cffi | 2.0.0 | MIT | 运行时 |
| click | 8.3.1 | BSD-3-Clause | 运行时 |
| colorama | 0.4.6 | BSD-3-Clause | 运行时 |
| Flask | 2.3.2 | BSD-3-Clause | 运行时 |
| gevent | 24.2.1 | MIT | 运行时 |
| greenlet | 3.0.3 | MIT | 运行时 |
| itsdangerous | 2.1.2 | BSD-3-Clause | 运行时 |
| Jinja2 | 3.1.2 | BSD-3-Clause | 运行时 |
| MarkupSafe | 2.1.3 | BSD-3-Clause | 运行时 |
| pycparser | 2.21 | BSD-3-Clause | 运行时 |
| setuptools | 65.5.0 | MIT | 运行时 |
| Werkzeug | 2.3.6 | BSD-3-Clause | 运行时 |
| zope.event | 5.0 | ZPL-2.1 | 运行时 |
| zope.interface | 6.4.post2 | ZPL-2.1 | 运行时 |
| Pillow | 9.5.0 | HPND | 仅测试 |
| Bootstrap | 3.3.7 | MIT | 本地静态资源；后续 BATCH-004 核对完整许可文本 |
| jQuery | 1.12.4 | MIT | BATCH-004 本地化时加入并核对许可头 |

许可核对来源：本机已安装包元数据与下载 wheel 的 `.dist-info`，及迁移规划包的目标依赖与许可矩阵。安装工具 pip 不属于应用运行／测试集合；SBOM 核对排除 pip，包含 zope 在运行时依赖的 setuptools。Bootstrap／jQuery 的目标端本地文件与许可证在 BATCH-004 接入时加入资源清单，不将尚未本地化的 jQuery 冒称为已交付资源。
