# Target Design

## Context and Constraints

- **依据**：规划包 `migration-plans/bookshop/`，以及本 change 的 proposal 和 8 份 spec。目标栈、范围、行为策略和规则以 `migration-strategy.md` 为准（MIG-DEC-001～MIG-DEC-013，MIG-RULE-001～MIG-RULE-023）；这里只写怎么实现，不重复策略内容。
- **旧系统只读**：`BookShop/`（INV-001～INV-039）不修改，只作为对照参考。旧系统无法运行（GAP-001、GAP-002），所以对照的依据是 `legacy-baseline.md` 的静态描述。
- **环境约束**：只在 Windows 上；Python 3.12.10，通过 `py -3.12` 的虚拟环境运行；`PYTHONUTF8=1`；默认只监听 127.0.0.1（COMP-001、MIG-RULE-022）。
- **Windows 路径约束**：仓库根目录已有 `BookShop/`，而 Windows 文件系统不区分大小写，所以新代码的包名不能是 `bookshop`（DEC-001）。

## Goals and Non-Goals

**Goals**

- 实现 8 份 spec 的 48 条需求，每条都有自动化测试。
- 保留旧 URL、页面结构和中文文案，按 Bootstrap 5 重做样式。
- 修复策略列出的全部缺陷和安全问题。
- 本机和 GitHub Actions 的 windows-latest 上全量测试稳定通过。
- 数据库由初始化命令建立，演示数据可复现。

**Non-Goals**

- 迁移历史数据，或者和原库对拷。
- 运行旧系统做黄金样本对照。
- 像素级还原。
- Linux 部署、多实例、HTTPS 终止。
- 策略 Out of Scope 里列出的任何功能。

## Target Architecture

```
bookshop_web/                 Flask 应用包（DEC-001）
  __init__.py                 create_app()：读配置、注册路由、错误页、会话钩子
  __main__.py                 命令行：serve、init-db（DEC-010、DEC-013）
  config.py                   读取 BOOKSHOP_* 环境变量，检查解释器版本（DEC-019）
  dispatch.py                 *.action 的 opttype 分派表和检查顺序（DEC-003）
  security.py                 会话加载与吊销、CSRF、管理员校验（DEC-004、DEC-005）
  db.py                       连接、PRAGMA、写事务上下文（DEC-006）
  schema.sql                  STRICT 表、约束、索引（DEC-007）
  money.py, validation.py     金额换算、输入校验（DEC-008、MIG-RULE-018）
  responses.py                alert 跳转、错误页（DEC-017）
  covers.py                   封面白名单、文件头识别、存取（DEC-021）
  logging_setup.py            日志配置（DEC-018）
  views/                      account.py、catalogue.py、orders.py、admin_members.py、admin_books.py、admin_revenue.py、pages.py
  templates/                  每个旧 JSP 对应一个 .html，另有三套布局（DEC-012）
  static/                     bootstrap/（5.3.8）、bootstrap-icons/（1.13.1）、css/、img/（DEC-011）
  seed/                       seed_data.py（从 BookShop/db/seed.sql 转写）、covers/（10 张封面）（DEC-010）
scripts/start.ps1, stop.ps1   Windows 启停（DEC-013）
requirements*.in/.txt         带哈希的依赖锁（DEC-014）
tests/                        unit/、web/、server/、static/（DEC-020）
.github/workflows/bookshop-ci.yml   windows-latest 上的 CI（DEC-015）
<BOOKSHOP_DATA_DIR>/          bookshop.db、covers/、logs/、run/（DEC-009）
```

**请求处理流程**：

1. waitress（请求体上限 6 MiB）把请求交给 Flask。
2. 路由匹配，没注册的路径返回 404。
3. `before_request` 从会话加载用户并校验（会话版本号、是否停用、绝对有效期）。
4. 对 `*.action` 请求，`dispatch` 按 MIG-RULE-019 的顺序检查：登录、管理员、opttype、方法、413、CSRF、参数。
5. 业务处理：读操作直接用连接；写操作在 `write_tx()` 里完成。
6. 返回 302、页面渲染结果，或者 alert 响应。
7. `teardown` 关闭数据库连接。

## Legacy-to-Target Mapping

| Legacy ID/component | Target component | Related requirement | Decision ID | Migration batch |
|---|---|---|---|---|
| INV-001、INV-002、INV-004（Eclipse 工程、Tomcat、上下文路径） | `bookshop_web` 包、waitress、`/BookShop` 前缀、`requirements*.txt` | REQ-PLATFORM-001、REQ-PLATFORM-012 | DEC-001、DEC-002、DEC-013、DEC-014 | BATCH-001 |
| INV-003、INV-005（web.xml、编码过滤器） | `create_app()` 中的配置；UTF-8 由 Flask/Werkzeug 默认处理 | REQ-PLATFORM-002、REQ-PLATFORM-015 | DEC-002 | BATCH-001 |
| INV-006（MyFilter 登录过滤） | `security.load_user`、`dispatch` 的会话检查和管理员检查 | REQ-ACCOUNT-003、REQ-ACCOUNT-004 | DEC-003、DEC-004 | BATCH-001（框架）、BATCH-003（实现） |
| INV-007（LoginServlet） | `views/account.py`：`addusers`、`checkUsers`、`logout` | REQ-ACCOUNT-001、REQ-ACCOUNT-002、REQ-ACCOUNT-005 | DEC-004、DEC-005 | BATCH-003 |
| INV-009（MyServlet） | `views/account.py`（`initMypage`、`updatePwd`）、`views/orders.py`（`queryMyorder`） | REQ-ACCOUNT-006、REQ-ACCOUNT-007、REQ-ORDER-003 | DEC-004 | BATCH-003、BATCH-005 |
| INV-008（BookServlet） | `views/catalogue.py`（查询类 opttype）、`views/orders.py`（`buybook`） | REQ-CATALOG-001～REQ-CATALOG-006、REQ-ORDER-001 | DEC-003、DEC-016 | BATCH-004、BATCH-005 |
| INV-010（AdminServlet） | `views/admin_members.py`、`views/admin_books.py`、`views/admin_revenue.py` | REQ-MEMBER-001～REQ-MEMBER-003、REQ-BOOK-001～REQ-BOOK-006、REQ-REVENUE-001 | DEC-003、DEC-021 | BATCH-006、BATCH-007 |
| INV-011、INV-023、INV-028（失效控制器、残留页面、CKEditor） | 不迁移；路径没有注册，返回 404 | REQ-PLATFORM-015 | DEC-003 | BATCH-001 |
| INV-012～INV-016（SQLHelper 和 DAO） | `db.py`，以及各 view 模块内的参数化 SQL | REQ-DATA-002、REQ-PLATFORM-009 | DEC-006 | BATCH-002 起 |
| INV-017、INV-035（表结构：旧推断和复原） | `schema.sql`（GAP-001） | REQ-DATA-001 | DEC-007 | BATCH-002 |
| INV-037、INV-026（种子数据、封面） | `seed/seed_data.py`、`seed/covers/`，由 `init-db` 导入（GAP-002） | REQ-DATA-003 | DEC-010 | BATCH-002 |
| INV-018、INV-036（硬编码的数据库连接、复原的 my.ini） | 环境变量配置；SQLite 文件放在数据目录 | REQ-PLATFORM-012 | DEC-009、DEC-019 | BATCH-001 |
| INV-019（实体类） | 不再需要实体类，行数据直接用 `sqlite3.Row` | REQ-DATA-001 | DEC-006 | BATCH-002 |
| INV-020～INV-022（JSP 视图） | `templates/` 下同名的 `.html`，用 Bootstrap 5 | REQ-PLATFORM-011 及各能力的页面需求 | DEC-012 | 各功能批次 |
| INV-024（showpic 和上传） | `covers.py`、`/BookShop/jsp/showpic.jsp`、`/BookShop/img/<name>`、`addBooksimg` | REQ-CATALOG-007、REQ-CATALOG-008、REQ-BOOK-004 | DEC-021 | BATCH-004、BATCH-007 |
| INV-025、INV-027、INV-029（CSS、Bootstrap 3、CDN） | `static/css`、`static/bootstrap`（5.3.8）、`static/bootstrap-icons`（1.13.1），全部本地提供 | REQ-PLATFORM-010 | DEC-011 | BATCH-001 |
| INV-030、INV-031（会话属性、用会话传数据） | 签名 Cookie 会话，只存身份、版本号、令牌和页面查询条件 | REQ-ACCOUNT-003、REQ-CATALOG-006 | DEC-004、DEC-016 | BATCH-001、BATCH-003、BATCH-004 |
| INV-032（stdout 日志） | `logging_setup.py` | REQ-PLATFORM-013 | DEC-018 | BATCH-001 |
| INV-034（没有测试） | `tests/` 和 CI | 全部需求 | DEC-015、DEC-020 | BATCH-001 起 |

## Migration Batches

每个批次都能单独验证和回退；tasks.md 按批次分组。在 BATCH-008 切换之前，没有任何生产数据，所以各批次的回退都是“`git revert` 本批次的提交，再删除测试用的临时数据目录”。

| Batch ID | Scope | Requirement IDs | Depends on | Exit criteria | Rollback |
|---|---|---|---|---|---|
| BATCH-001 | 工程骨架与平台：<br>• 包结构、配置、解释器自检；<br>• 分派表与检查顺序（业务处理暂时返回 501）；<br>• 错误页、alert、CSRF、日志；<br>• 静态资源和三套布局；首页、登录页、注册页的静态部分；<br>• waitress 与启停脚本；依赖锁；CI；<br>• 提交上一轮产物的删除 | REQ-PLATFORM-001、REQ-PLATFORM-002、REQ-PLATFORM-003、REQ-PLATFORM-004、REQ-PLATFORM-006、REQ-PLATFORM-007、REQ-PLATFORM-010、REQ-PLATFORM-011、REQ-PLATFORM-012、REQ-PLATFORM-013、REQ-PLATFORM-014、REQ-PLATFORM-015 | 无 | TEST-001～TEST-005、TEST-007、TEST-008、TEST-011～TEST-014、TEST-042、TEST-043 通过；windows-latest 上的 CI 为绿色 | `git revert` 本批次提交；被删除的上一轮产物可从 HEAD `425edd4` 恢复 |
| BATCH-002 | 数据层：<br>• `schema.sql`、连接与写事务；<br>• 金额、输入校验；<br>• `init-db`、演示数据和封面；<br>• 数据库异常的错误页；<br>• SQL 静态扫描 | REQ-DATA-001～REQ-DATA-005、REQ-PLATFORM-005、REQ-PLATFORM-009 | BATCH-001 | TEST-006、TEST-010、TEST-015～TEST-019 通过；在临时目录执行 `init-db` 后，数据与 seed 一致 | `git revert`；删除临时数据目录 |
| BATCH-003 | 账号与会话：注册、登录、会话加载与吊销、管理员校验、退出、个人页、修改密码 | REQ-ACCOUNT-001～REQ-ACCOUNT-007 | BATCH-002 | TEST-020～TEST-026 通过；在路由矩阵中，会员端和管理端 URL 的 302、403 判定都正确 | `git revert`；BATCH-001 的 501 处理自动恢复 |
| BATCH-004 | 书目与封面：书目、购买页、筛选、搜索、详情、直接打开结果页、封面输出、公开图片；XSS 用例 | REQ-CATALOG-001～REQ-CATALOG-008、REQ-PLATFORM-008 | BATCH-003 | TEST-009、TEST-027～TEST-029 通过 | `git revert` |
| BATCH-005 | 购买与我的订单 | REQ-ORDER-001～REQ-ORDER-003 | BATCH-004 | TEST-030～TEST-032 通过；20 个线程并发购买时不超卖 | `git revert` |
| BATCH-006 | 管理端：会员列表、搜索、停用，账目统计 | REQ-MEMBER-001～REQ-MEMBER-003、REQ-REVENUE-001 | BATCH-005 | TEST-033、TEST-034、TEST-039 通过 | `git revert` |
| BATCH-007 | 管理端书籍：列表、搜索、两步新增与上传、修改、下架 | REQ-BOOK-001～REQ-BOOK-006 | BATCH-006 | TEST-035～TEST-038 通过；事务失败后 `covers/` 里没有残留文件 | `git revert`；删除测试用的封面目录 |
| BATCH-008 | 收尾与切换：<br>• 两端端到端旅程；<br>• 运行与部署文档、演示数据说明；<br>• 切换和回滚演练；<br>• 全量 CI 为绿色；<br>• gate 的 coverage 和 lint 通过 | 全部需求（回归） | BATCH-001～BATCH-007 | TEST-040、TEST-041、TEST-044、TEST-045 通过；全量测试在本机和 windows-latest 上通过 | 停止服务；从切换前的备份恢复数据目录；把代码检出到切换前的标签 |

## Design Decisions

### DEC-001: 代码布局与包名

- Related IDs: MIG-RULE-013、MIG-RULE-022、INV-001
- Decision: 新代码放在仓库根目录的包 `bookshop_web/`，测试在 `tests/`，脚本在 `scripts/`。包里自带模板、静态资源和种子数据，运行时不读取旧系统的 `BookShop/` 目录。
- Rationale: Windows 不区分大小写，`bookshop/` 会和 `BookShop/` 冲突；新系统不能依赖旧目录还存在。
- Alternatives considered: `src/` 布局（需要安装包或配置路径，对单进程本机部署来说多余）；沿用上一轮的 `bookshop_app/`（已决定不复用上一轮产物）。
- Consequences: 用 `python -m bookshop_web` 运行；pytest 通过 `pythonpath = .` 导入。
- Verification: TEST-003、TEST-043

### DEC-002: URL 前缀与应用工厂

- Related IDs: MIG-RULE-001、REQ-PLATFORM-001、REQ-PLATFORM-002
- Decision: `create_app(config)` 注册所有路由，路由里直接写死 `/BookShop` 前缀，不用 `APPLICATION_ROOT` 或反向代理的 `SCRIPT_NAME`。会话 Cookie 的 `Path` 设为 `/BookShop`。
- Rationale: waitress 直接对外服务，没有反向代理；把前缀写死最容易和旧 URL 一一对照。
- Alternatives considered: 挂一个 `DispatcherMiddleware`（多一层，测试也更绕）。
- Consequences: 302 的相对 Location 和旧系统一致（EXP-012 已验证）。
- Verification: TEST-004、TEST-005

### DEC-003: opttype 分派表与检查顺序

- Related IDs: MIG-RULE-001、MIG-RULE-019、REQ-PLATFORM-003、REQ-PLATFORM-004
- Decision: 每个 `*.action` URL 有一张声明式分派表，每个 opttype 登记方法、处理函数、是否需要管理员。统一的 `dispatch()` 严格按 MIG-RULE-019 的顺序检查，业务函数只处理已经通过检查的请求。JSP 页面路由（`buy.jsp` 等）登记“是否需要登录、是否需要管理员”，走同样的前几步检查。
- Rationale: 检查顺序集中在一个地方实现，路由矩阵测试可以对着分派表逐项生成。
- Alternatives considered: 每个视图自己写装饰器（顺序容易乱，评审第 11 条指出的正是这个问题）。
- Consequences: BATCH-001 先登记全部 opttype，处理函数暂时返回 501；之后各批次逐个替换成真实实现。
- Verification: TEST-004

### DEC-004: 会话与用户加载

- Related IDs: MIG-RULE-021、MIG-DEC-012、REQ-ACCOUNT-003、REQ-ACCOUNT-004
- Decision:
  - **会话形式**：用 Flask 的签名 Cookie 会话，设为 `permanent`，`PERMANENT_SESSION_LIFETIME` 为 30 分钟；HttpOnly，SameSite=Lax。
  - **会话里的字段**：`uid`、`sv`（会话版本号）、`login_at`（epoch 秒）、`csrf`，以及页面查询条件 `q_catalogue`、`q_admin_books`、`q_admin_customers`、`detail_bid`、`edit_bid`。
  - **每个请求**：`before_request` 按 uid 读取 `user` 行；不存在、`active=0`、`sv` 不一致，或者 `now - login_at > 8h` 时，清空会话并把 `g.user` 设为空。
  - **授权**：只看 `g.user.role`，也就是数据库里的值。
  - **递增版本号**：登录时清空会话再写入；退出、改密码、停用时，在同一个写事务里执行 `UPDATE user SET session_version = session_version + 1`。
- Rationale: 实现策略里的会话吊销，又不必引入服务端会话存储。
- Alternatives considered: 服务端会话表（每个请求都要写库，和签名 Cookie 相比收益很小）。
- Consequences: 退出会让该用户在所有设备上的会话一起失效（策略已接受）。
- Verification: TEST-021、TEST-022、TEST-023、TEST-024、TEST-026

### DEC-005: CSRF 实现

- Related IDs: MIG-RULE-004、REQ-PLATFORM-007
- Decision:
  - **生成**：会话里的令牌 `csrf` 用 `secrets.token_urlsafe(32)` 生成，登录时换新。
  - **渲染**：模板全局函数 `csrf_token()` 输出隐藏字段 `csrf_token`；访问登录页和注册页时，如果没有令牌就新建一个（这时会建立一个匿名会话）。
  - **校验**：对 POST 用 `hmac.compare_digest` 比较，失败时返回 400；放在方法检查和 413 之后、参数检查之前。
- Rationale: 不引入 Flask-WTF（COMP-010）。
- Alternatives considered: Flask-WTF 的 CSRFProtect（会多带进 WTForms）。
- Consequences: 没有会话就直接 POST 登录时返回 400（LEGACY-070）。
- Verification: TEST-008

### DEC-006: 数据访问层

- Related IDs: MIG-RULE-002、MIG-RULE-012、REQ-DATA-002、REQ-PLATFORM-009
- Decision:
  - **连接**：`db.get_db()` 每个请求开一个连接，挂在 `g` 上，参数为 `isolation_level=None, timeout=5.0`；连接后执行 `PRAGMA foreign_keys=ON` 和 `PRAGMA busy_timeout=5000`，`row_factory` 用 `sqlite3.Row`；`teardown_appcontext` 负责关闭。
  - **写事务**：`db.write_tx()` 上下文执行 `BEGIN IMMEDIATE`，正常退出时 COMMIT，异常时 ROLLBACK 后重新抛出。
  - **SQL**：所有 SQL 都写在 view 模块内，用 `?` 传参，不用 ORM，也不用实体类。
- Rationale: 照搬 EXP-013 验证过的做法。
- Alternatives considered: 3.12 的 `autocommit=True`（效果相同，但没有实测过，COMP-023）。
- Consequences: 读操作不开显式事务，WAL 模式下读不会阻塞写。
- Verification: TEST-010、TEST-016

### DEC-007: 表结构 DDL

- Related IDs: GAP-001、MIG-RULE-018、REQ-DATA-001
- Decision: `schema.sql` 定义 5 张 STRICT 表（`user`、`tag`、`book`、`orders`、`addbook_draft`）：
  - **列**：`user.uname TEXT NOT NULL COLLATE NOCASE UNIQUE`；`tag.tname TEXT NOT NULL COLLATE NOCASE UNIQUE`；`book.price_cents`、`orders.unit_price_cents` 为 INTEGER；`book.on_sale`、`user.active` 用 CHECK 限定为 0 或 1；`user.session_version INTEGER NOT NULL DEFAULT 0`。
  - **草稿表**：`addbook_draft` 以 `uid` 为主键（外键指向 `user`），列与 book 的可编辑列相同。
  - **CHECK**：长度用 `length()`，数值用范围限定。
  - **初始化时**：执行 `PRAGMA journal_mode=WAL` 和 `PRAGMA user_version=1`。
- Rationale: 落实 GAP-001 的决定和输入上限。
- Alternatives considered: 不加 CHECK、只在应用层校验（数据库没有兜底，COMP-003）。
- Consequences: 以后改表结构要按 `user_version` 判断版本；本 change 只有版本 1。
- Verification: TEST-015

### DEC-008: 金额换算

- Related IDs: MIG-RULE-007、REQ-DATA-004
- Decision:
  - **解析**：`money.parse_price(text)` 用 `Decimal` 解析，只接受 0～99999.99、最多两位小数的十进制串，转成整数分；
  - **显示**：`money.fmt(cents)` 输出形如 `39.80`；
  - **合计**：用整数相加。
- Rationale: 消除浮点误差（LEGACY-045）。
- Alternatives considered: 存 TEXT 或 REAL（会有比较和求和误差）。
- Consequences: 种子里的价格乘 100 存入。
- Verification: TEST-018、TEST-039

### DEC-009: 数据目录布局

- Related IDs: MIG-RULE-010、REQ-PLATFORM-012
- Decision: `BOOKSHOP_DATA_DIR` 下的布局为 `bookshop.db`（及其 `-wal`、`-shm`）、`covers/`、`logs/bookshop.log`、`run/bookshop.pid`。这个目录必须在仓库之外，或者被 `.gitignore` 排除。
- Rationale: 代码和数据分开，备份和回滚只要复制这一个目录。
- Alternatives considered: Flask 的 `instance/` 目录（会和代码目录混在一起）。
- Consequences: 切换前的备份是“停服后复制整个数据目录”。
- Verification: TEST-002、TEST-044

### DEC-010: 初始化命令与种子数据

- Related IDs: GAP-002、MIG-RULE-015、REQ-DATA-003
- Decision:
  - **命令**：`python -m bookshop_web init-db` 用 argparse 实现，不定义任何口令参数。
  - **管理员口令**：先读 `BOOKSHOP_ADMIN_PASSWORD`；没设置并且是交互终端时，用 `getpass` 输入两次；口令为空、等于 `123456`、长度不在 1～64 字时拒绝。
  - **已有数据库**：数据库已存在时拒绝执行。
  - **种子数据**：从 `BookShop/db/seed.sql` 一次性转写到 `bookshop_web/seed/seed_data.py`，价格转成分；文件头注明哪些是占位值。10 张封面复制到 `bookshop_web/seed/covers/`，初始化时再复制进数据目录。
  - **说明文档**：演示数据的说明写在 `docs/demo-data.md`。
- Rationale: 新系统不依赖旧目录，种子可审阅、可复现。
- Alternatives considered: 运行时直接执行 `seed.sql`（那是 MySQL 方言，也会让新系统依赖旧目录）。
- Consequences: seed 有变化时，要同步修改 `seed_data.py`。
- Verification: TEST-017

### DEC-011: 静态资源的引入

- Related IDs: MIG-RULE-011、MIG-DEC-010、REQ-PLATFORM-010
- Decision:
  - **Bootstrap 5.3.8**：从 npm registry 的发布包取 `dist/css/bootstrap.min.css` 和 `dist/js/bootstrap.bundle.min.js`。
  - **Bootstrap Icons 1.13.1**：取 `font/bootstrap-icons.min.css` 和 `font/fonts/*.woff2`、`*.woff`。
  - **完整性**：下载后按 npm 的 `dist.integrity`（sha512）校验，同时把 LICENSE 一并放入，并在 `static/VENDOR.md` 里记下来源和哈希。
  - **URL**：分别映射到 `/BookShop/bootstrap/...` 和 `/BookShop/bootstrap-icons/...`。
  - **自有 CSS**：`carousel.css`、`dashboard.css`、`offcanvas.css`、`signin.css` 按 Bootstrap 5 改写后放到 `/BookShop/css/`。
  - **图片**：`1.jpg`、`2.jpg`、`default.jpg` 放到 `static/img/`。
- Rationale: 不依赖 CDN，版本和来源可以核对。
- Alternatives considered: 复用旧仓库里的 Bootstrap 3 源码树（策略已决定改用 5）。
- Consequences: 升级前端库要重新校验哈希。
- Verification: TEST-011、TEST-043

### DEC-012: 模板映射

- Related IDs: MIG-RULE-016、REQ-PLATFORM-011
- Decision:
  - **一一对应**：每个旧 JSP 对应一个同名 Jinja2 模板，例如 `buy.jsp` 对应 `buy.html`；路由仍然是旧的 `.jsp` 路径，比如 `GET /BookShop/jsp/buy.jsp` 渲染 `buy.html`。
  - **三套布局**：`layout_customer.html`（会员端导航栏，加上登录后的“退出”）、`layout_admin.html`（管理端导航栏和侧栏）、`layout_plain.html`（登录页、注册页）。
  - **改为表单的操作**：修改数据的链接（删除、立即购买）改成 POST 表单按钮，样式仍是链接或按钮。
  - **保留的旧细节**：`add.jsp`、`addnext.jsp`、`editbook.jsp` 导航栏里没有绑定动作的搜索框照旧保留。
- Rationale: 结构和文案逐页对照，页面测试也好写。
- Alternatives considered: 合并相似页面（会改变 URL 和结构）。
- Consequences: 模板数量和旧页面一样多。
- Verification: TEST-012

### DEC-013: 服务进程与启停

- Related IDs: MIG-RULE-009、MIG-RULE-022、REQ-PLATFORM-012、REQ-PLATFORM-014
- Decision:
  - **启动服务**：`python -m bookshop_web serve` 调用 `waitress.serve(app, host=BOOKSHOP_HOST, port=BOOKSHOP_PORT, threads=4, max_request_body_size=6 MiB)`。默认 host 为 `127.0.0.1`，端口默认为 `8080`，和旧 Tomcat 的默认端口一致。
  - **启动脚本**：`scripts/start.ps1` 用 `Start-Process` 以虚拟环境里的解释器启动后台进程，设置 `PYTHONUTF8=1`，把 PID 写进 `run/bookshop.pid`，然后等待端口可用。
  - **停止脚本**：`scripts/stop.ps1` 按 PID 结束进程，并删除 PID 文件。
- Rationale: 本机单进程，用 PowerShell 管理最直接。
- Alternatives considered: 注册成 Windows 服务（超出“本机单进程”的范围）。
- Consequences: 端口可以通过 `BOOKSHOP_PORT` 修改。
- Verification: TEST-003、TEST-044

### DEC-014: 依赖锁

- Related IDs: MIG-RULE-014、REQ-PLATFORM-012
- Decision:
  - **两份锁**：`requirements.in` 只放运行期依赖（Flask 3.1.3、Werkzeug 3.1.9、Jinja2 3.1.6、waitress 3.0.2）；`requirements-test.in` 以 `-c requirements.txt` 约束，再加 pytest 9.1.1。
  - **生成**：都用 pip-tools 7.6.2 加 `--generate-hashes --allow-unsafe --strip-extras` 生成，并且只在 Python 3.12.10 下重新生成。
  - **安装**：一律加 `--require-hashes`。
- Rationale: 安装可复现（EXP-008）。
- Alternatives considered: uv 或 poetry（策略没有选，会引入新工具）。
- Consequences: 升级依赖要重新生成锁并重跑全量测试。
- Verification: TEST-001

### DEC-015: CI

- Related IDs: MIG-DEC-011、MIG-RULE-013、MIG-RULE-022
- Decision:
  - **触发与环境**：`.github/workflows/bookshop-ci.yml` 在 `master` 的 push 和 pull request 上触发；`runs-on: windows-latest`；`actions/setup-python` 固定为 `3.12.10`；`env: PYTHONUTF8: "1"`。
  - **步骤**：
    1. 建立虚拟环境；
    2. `pip install --require-hashes -r requirements-test.txt`；
    3. `pytest -p no:cacheprovider`，包括 `server` 标记的真实 waitress 用例；
    4. 用 Node 运行 gate 的 coverage 和 lint。
  - **旧 workflow**：上一轮的 `bookshop-check.yml` 已删除，删除随 BATCH-001 提交。
- Rationale: CI 和部署环境一致（MIG-DEC-011）。
- Alternatives considered: 用矩阵同时跑多个 Python 版本（和固定 3.12.10 的决定冲突）。
- Consequences: 每次推送都要跑完整套件。
- Verification: TEST-042

### DEC-016: 详情页和编辑页的 bid 存在会话里

- Related IDs: LEGACY-017、LEGACY-028、LEGACY-032、MIG-RULE-021、REQ-ACCOUNT-003、REQ-CATALOG-005、REQ-CATALOG-006、REQ-BOOK-005
- Decision: `bookDetail` 和 `showBooks` 把 bid 存进会话的 `detail_bid`、`edit_bid`，然后 302 到不带查询参数的 `bookdetails.jsp` 和 `editbook.jsp`，和旧系统一致。直接打开这两个页面时，按保存的 bid 重新查询。
- Rationale: 用户在本次 propose 中选定（ASKED）。这是对 MIG-RULE-021 中“三个列表页的查询条件”的放宽：会话里多两个整数，Cookie 仍远低于 3000 字节（EXP-011 的最坏情况是 1238 字节）。
- Alternatives considered: 改为 302 到 `bookdetails.jsp?bid=<bid>`（用户没有选）。
- Consequences: migration-strategy 里 MIG-RULE-021 的文字比本决定窄。之后如果对策略做修订，应把这两个 bid 补进会话字段清单。
- Verification: TEST-022、TEST-028、TEST-037

### DEC-017: 错误页与 alert 响应

- Related IDs: MIG-RULE-020、REQ-PLATFORM-005、REQ-PLATFORM-006
- Decision:
  - **alert 响应**：`responses.alert(text, location)` 返回 200，`Content-Type: text/html; charset=utf-8`，响应体为 `<script>alert('<text>'); window.location='<location>' </script>`。文案和目标都是常量表，不拼接用户输入。
  - **错误页**：400、403、404、405、413、500 的 `errorhandler` 渲染 `error.html`，页面上有状态码和中文说明。
  - **数据库异常**：`sqlite3.Error` 在 500 处理中记录日志。
- Rationale: 文案和状态码集中管理，测试可以直接对常量断言。
- Alternatives considered: 用 flash 消息（会改变旧系统的提示方式）。
- Consequences: 新增提示时只需要在常量表里加一行。
- Verification: TEST-006、TEST-007

### DEC-018: 日志

- Related IDs: MIG-RULE-017、REQ-PLATFORM-013
- Decision:
  - **输出**：根 logger 同时写到 stdout 和 `logs/bookshop.log`（`RotatingFileHandler`，5 MiB × 5）。
  - **请求日志**：只记录方法、路径（不含查询串）和状态码。
  - **异常**：只记录异常类型和路径。
  - **禁止项**：不记录表单、会话和 SQL。
- Rationale: 落实 MIG-RULE-017。
- Alternatives considered: 结构化 JSON 日志（本机单用户，用不上）。
- Consequences: 排查问题时拿不到请求参数，需要在本地复现。
- Verification: TEST-013

### DEC-019: 启动自检

- Related IDs: MIG-RULE-010、MIG-RULE-022、REQ-PLATFORM-012
- Decision: `config.load()` 在启动时检查：
  - `sys.version_info[:3] == (3, 12, 10)`；
  - `BOOKSHOP_DATA_DIR` 存在并且可写；
  - `BOOKSHOP_SECRET_KEY` 解码后不少于 32 字节，并且不等于 `config.example.ps1` 里的示例值；
  - 端口在 1～65535 之间。

  任何一项不满足，都退出并给出中文说明（非零退出码），不监听任何端口。
- Rationale: 把配置错误挡在启动前（COMP-025）。
- Alternatives considered: 只给警告（问题会拖到运行中才暴露）。
- Consequences: 升级 Python 小版本时要同步修改这里和 CI。
- Verification: TEST-002

### DEC-020: 测试分层

- Related IDs: MIG-RULE-023
- Decision: 测试分四层：
  - `tests/unit`：纯函数，例如金额、校验、白名单；
  - `tests/web`：Flask 测试客户端，每个测试在临时数据目录里执行 `init-db`；
  - `tests/server`：真实的 waitress，带 `server` 标记；
  - `tests/static`：仓库扫描，例如 SQL 拼接、外部 URL、密钥、本机路径、workflow。

  EXP-002～EXP-013 的检查项按 test-plan 转写。
- Rationale: 不同层级的风险用不同的手段覆盖，服务器层的行为必须用真实 waitress 测。
- Alternatives considered: 引入浏览器自动化（不在策略的技术栈里）。
- Consequences: 视觉效果只做人工检查（见 test-plan 中的例外）。
- Verification: TEST-045

### DEC-021: 封面存取

- Related IDs: MIG-RULE-009、MIG-RULE-012、REQ-CATALOG-007、REQ-CATALOG-008、REQ-BOOK-004
- Decision:
  - **校验**：`covers.is_valid_name()` 用白名单正则；`covers.sniff()` 读前 8 个字节识别 PNG 或 JPEG。
  - **读取**：先 `resolve()` 路径，确认它在 `covers/`（或 `static/img/`）之下，再交给 `send_file`，`mimetype` 按文件头设置。
  - **上传**：
    1. 先 sniff，确认是 PNG 或 JPEG；
    2. 生成 `uuid4().hex` 加对应扩展名，以独占模式（`xb`）写入 `covers/`；
    3. 进入写事务，插入书籍并删除草稿；
    4. 事务出错时删除该文件，再抛给 500 处理。
- Rationale: 落实 COMP-024 的顺序。
- Alternatives considered: 先写临时文件再改名（多一步，安全性没有提高）。
- Consequences: 只有进程在写文件和提交事务之间崩溃时，才可能留下没被引用的文件，这种文件不会被访问到。
- Verification: TEST-029、TEST-036

### DEC-022: 上一轮产物与仓库卫生

- Related IDs: MIG-DEC-011
- Decision:
  - **上一轮产物**：工作区里已删除的上一轮产物（`bookshop_app/`、`tests/` 的旧内容、`artifacts/`、`scripts/` 的旧脚本、`docs/运行说明.md`、`requirements*.lock`、`sbom.json`、`THIRD_PARTY_NOTICES.md`、`config.example.ps1`、`.github/workflows/bookshop-check.yml`），其删除在 BATCH-001 一并提交。同名路径（`tests/`、`scripts/`、`config.example.ps1`）用新内容重建。
  - **`.gitignore`**：追加 `.venv/`、`*.db`、`*.db-wal`、`*.db-shm` 和本地数据目录。
  - **第三方声明**：重建 `THIRD_PARTY_NOTICES.md`，列出本次的依赖和前端库许可证。
- Rationale: 落实策略 Scope 中的这一项。
- Alternatives considered: 保留上一轮产物，在其基础上修改（策略已决定不复用）。
- Consequences: 上一轮产物仍可以从 `425edd4` 找回。
- Verification: TEST-043

## Interfaces and Data Conversion

- **URL 接口**：沿用旧路径和参数名（`opttype`、`bname`、`tname`、`bid`、`uid`、`uname`、`inputName`、`inputPassword`、`inputUname`、`checkPassword`、`oldpwd`、`newpwd`、`anewpwd`、`publishers`、`stock`、`price`、`cont`、`file`）。有两处变化：新增书籍时分类字段从自由文本 `tname` 改为下拉框 `tid`（LEGACY-055）；所有 POST 都多一个 `csrf_token`。新增的 URL 只有 `POST /BookShop/logout.action`。
- **数据转换**：没有历史数据要转换（GAP-002）。种子从 `BookShop/db/seed.sql` 转写：
  - 价格乘 100 存成整数分；
  - 库存、tid、bid 照抄；
  - `url` 保留 `b1.jpg` 等原名；
  - 简介照抄，并标注为占位文字；
  - 管理员口令不从 seed 取（MIG-RULE-015）。
- **金额显示**：一律两位小数。旧系统的显示格式取决于未知的列类型，不做对照（LEGACY-064）。

## Error, Transaction, and Concurrency Semantics

- **状态码**：按 MIG-RULE-019 的顺序判定，见 DEC-003。业务校验失败返回 200 加 alert（DEC-017）。
- **写操作**：注册、登录（写会话版本号的场景）、修改密码、购买、新增书籍的两步、修改书籍、下架、停用、退出，都在 `BEGIN IMMEDIATE` 事务里完成。所需的状态校验，比如重名、在架、库存、草稿存在、目标是未停用的会员，都在同一个事务里。
- **并发**：多个写请求排队拿写锁，最多等 5 秒（busy timeout）；读请求在 WAL 模式下不受影响。并发购买和并发注册的正确性在 EXP-013 里验证过。
- **出错时**：事务回滚；如果此前写了封面文件，就删除它；然后返回 500 错误页并记录日志（REQ-PLATFORM-005）。

## Security and Privacy

| 风险点 | 措施 |
|---|---|
| SQL 注入（LEGACY-048） | 全部参数化，并加静态扫描（DEC-006） |
| 明文口令（LEGACY-049） | scrypt 哈希（REQ-ACCOUNT-001） |
| 越权（LEGACY-050） | 授权以数据库里的 role 为准（DEC-004） |
| CSRF（LEGACY-051） | 令牌，并且修改操作只接受 POST（DEC-005） |
| XSS（LEGACY-052） | 自动转义（REQ-PLATFORM-008） |
| 路径穿越（LEGACY-053） | 文件名白名单加 `resolve()` 校验（DEC-021） |
| 上传（LEGACY-054） | 两层大小限制、文件头校验、服务器生成文件名 |
| 硬编码凭据（LEGACY-056） | 配置走环境变量，加启动自检（DEC-019） |
| 会话（LEGACY-057） | 重新签发、版本号吊销、空闲 30 分钟和绝对 8 小时过期（DEC-004） |

- **隐私**：日志里没有口令、表单值和会话内容（DEC-018）。
- **运行时补丁**：Python 运行时缺少后续安全补丁的风险已由用户接受（COMP-001）。缓解措施是默认只监听 127.0.0.1。

## Deployment, Coexistence, and Observability

- **部署**：
  1. 在 Windows 本机用 `py -3.12 -m venv .venv` 建立虚拟环境；
  2. `.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.txt`；
  3. 设置 `BOOKSHOP_*` 环境变量；
  4. 执行 `init-db`；
  5. 运行 `scripts/start.ps1`。

  完整步骤写在 `docs/运行说明.md`（BATCH-008）。
- **共存**：旧系统无法运行，也不在任何地方运行，所以不存在两套系统同时服务的问题。新系统默认端口 8080，和 Tomcat 的默认端口相同；如果本机另有程序占用，用 `BOOKSHOP_PORT` 修改。`BookShop/` 目录原样保留，只作参考。
- **可观测性**：日志写到 stdout 和 `logs/bookshop.log`；启动时记录版本、监听地址和数据目录（不记录密钥）；没有指标系统（本机单用户）。

## Cutover and Rollback Design

**切换**（BATCH-008）：

1. 确认 windows-latest 上的 CI 为绿色，打上切换前的标签 `pre-cutover`；
2. 在正式数据目录执行 `init-db`，设置管理员口令；
3. 运行 `scripts/start.ps1`；
4. 按 test-plan 的冒烟清单验证；
5. 备份数据目录（先停服，再复制整个目录）。

**回滚**：

- **服务异常**：执行 `scripts/stop.ps1`，从最近的备份恢复数据目录，必要时把代码检出到 `pre-cutover`，再启动。
- **切换前**：任何批次都可以 `git revert`，因为没有生产数据。
- **能否回到旧系统**：旧系统无法运行，所以“回退到旧系统”不是一个可行的选项；回滚只回到新系统的上一个可用版本。这一点由 GAP-001、GAP-002 的决定决定。
- **演练**：回滚演练由 TEST-044 覆盖，即备份、改动、恢复后，数据与备份一致。

## Risks and Trade-offs

| Risk | Related IDs | Mitigation | Verification |
|---|---|---|---|
| Python 3.12.10 没有后续安全补丁 | COMP-001、MIG-DEC-009 | 默认只监听 127.0.0.1；文档中写明风险 | TEST-003（监听地址） |
| 签名 Cookie 在 8 小时内被盗用 | COMP-007、DEC-004 | HttpOnly、SameSite=Lax、版本号吊销、空闲 30 分钟 | TEST-022 |
| SQLite 写锁竞争 | COMP-020、DEC-006 | WAL、busy timeout、写事务尽量短 | TEST-016、TEST-031 |
| 前端库升级时引入不明来源的文件 | DEC-011 | 按 npm 的 integrity 校验，并在 VENDOR.md 中记录 | TEST-011、TEST-043 |
| 演示数据被误当作原数据 | MIG-RULE-015、DEC-010 | 种子文件头和 `docs/demo-data.md` 注明占位值；测试只断言结构，不断言旧事实 | TEST-017 |
| 视觉效果和旧系统有差异 | MIG-DEC-010 | 结构和文案用自动测试保证，视觉效果人工检查 | TEST-012；test-plan 中的例外 |
| 进程崩溃留下未被引用的封面文件 | COMP-024、DEC-021 | 不会被访问到，可以接受 | TEST-036 |

## Open Questions

没有。会影响行为、可行性或任务范围的问题都已在策略或本次 propose 中确定，包括 DEC-016。
