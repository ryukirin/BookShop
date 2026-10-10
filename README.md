# BookShop

网上书店（软件项目管理课程设计）。

原版是 Java Servlet/JSP + MySQL 实现的，现已迁移到 **Python/Flask + SQLite**。迁移保留了原有的 URL、页面结构和提示文案，同时修复了原版的安全缺陷。旧的 Java 版原样保留在 [`BookShop/`](BookShop/) 目录中，只作参考，不再运行。

## 功能

**会员**

- 注册、登录、退出，修改密码，个人页
- 浏览书目：按分类筛选、按书名搜索、查看书籍详情和封面
- 购买书籍（扣减库存），查看我的订单

**管理员**

- 会员管理：列表、搜索、停用
- 书籍管理：列表、搜索、分两步新增（先填信息，再上传封面）、修改、下架
- 账目统计：订单明细和总金额

有订单的会员和书籍采用停用、下架的方式处理，不做物理删除，历史订单和账目统计不受影响。订单记录的是成交时的价格。

## 技术栈

| | 迁移版（当前） | 原版（`BookShop/`） |
|---|---|---|
| 语言与框架 | Python 3.12.10、Flask 3.1 | Java、Servlet/JSP |
| 服务器 | waitress（单进程，默认只监听 127.0.0.1） | Tomcat |
| 数据存储 | SQLite（STRICT 表、WAL） | MySQL |
| 前端 | Bootstrap 5.3.8、Bootstrap Icons 1.13.1（本地提供） | Bootstrap 3.3.7、jQuery 1.12.4（CDN） |
| 运行环境 | 仅 Windows | — |

安全方面的改动：口令用 scrypt 哈希保存，表单带 CSRF 令牌，SQL 全部参数化，页面输出统一转义，会话有空闲和绝对两种超时并可吊销，上传封面限制在 5 MiB 以内且只接受 PNG 和 JPEG。

## 快速开始

需要 Windows 和 Python 3.12.10（用 `py -3.12` 调用）。在仓库根目录执行：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.txt

# 配置：把 config.example.ps1 复制到仓库之外并填好，再加载
. $HOME\bookshop-config.ps1

# 初始化数据库（会提示输入两次管理员口令）
$env:PYTHONUTF8 = "1"
.venv\Scripts\python.exe -m bookshop_web init-db

# 启动和停止
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop.ps1
```

启动后访问 <http://127.0.0.1:8080/BookShop/>，管理员账号是 `admin`。初始化时导入的分类、书籍和封面都是演示用的占位数据，见 [docs/demo-data.md](docs/demo-data.md)。

配置项、日志、备份恢复、切换与回滚、常见问题等，详见 [docs/运行说明.md](docs/运行说明.md)。

## 测试

```powershell
.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-test.txt
$env:PYTHONUTF8 = "1"
.venv\Scripts\python.exe -m pytest
```

测试分四层：`tests/unit`（单元）、`tests/web`（Flask 测试客户端）、`tests/server`（真实 waitress 和启停脚本）、`tests/static`（仓库扫描）。GitHub Actions 的 `bookshop-ci` 在 windows-latest 上运行全部测试和迁移检查。

## 目录结构

| 路径 | 内容 |
|---|---|
| `bookshop_web/` | 迁移版应用：视图、模板、静态资源、数据库结构、演示数据 |
| `tests/` | 测试 |
| `scripts/` | 启动和停止脚本 |
| `docs/` | 运行说明、演示数据说明 |
| `BookShop/` | 原 Java 版（只作参考）；`BookShop/db/` 是依据旧代码复原的 MySQL 表结构和数据 |
| `migration-plans/bookshop/` | 迁移规划：旧系统清单、行为基线、迁移策略、原型实验 |
| `openspec/` | 迁移变更 `migrate-bookshop-to-flask` 的需求规格、设计、测试计划和任务 |

## 感谢

本项目是半年前的项目，有一部分使用了第三方库来实现，老师也给予了我很多帮助，谢谢谢谢。
使用了 Bootstrap，第三方许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
