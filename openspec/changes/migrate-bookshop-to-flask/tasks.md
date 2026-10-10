# Migration Tasks

约定：

- 下文的 `pytest` 指 `.venv\Scripts\python.exe -m pytest -p no:cacheprovider`；
- 所有命令都在仓库根目录、设置了 `PYTHONUTF8=1` 的 PowerShell 中执行；
- `.venv` 一律用 `py -3.12 -m venv .venv` 创建（MIG-RULE-022）。

每个批次的顺序都是：先写测试并确认失败（红），再实现到测试全部通过（绿），最后确认退出标准和回滚方式。

## 1. Baseline Protection

- [x] 1.1 编写静态特征测试，在改动之前把基线固定下来，并确认它们因为还没有实现而失败（红）：
  - TEST-012：页面结构和文案，依据 `legacy-baseline.md` 中 LEGACY-001、LEGACY-006、LEGACY-011、LEGACY-014、LEGACY-017、LEGACY-021、LEGACY-022、LEGACY-024、LEGACY-026～LEGACY-028、LEGACY-031、LEGACY-035 描述的标题、导航、侧栏、列名、字段和按钮；
  - TEST-007：7 条旧 alert 文案和跳转；
  - TEST-004：旧 URL、opttype 和 302 目标的路由矩阵。

  批次：BATCH-001。验证：`pytest tests/web/test_page_structure.py tests/web/test_alerts.py tests/web/test_route_matrix.py`，应以失败结束，并把失败清单记进提交说明。
- [x] 1.2 编写注册和改密码的检查顺序特征测试（TEST-020、TEST-026，依据 LEGACY-007、LEGACY-012），并确认它们失败。批次：BATCH-003 开始前。验证：`pytest tests/web/test_register.py tests/web/test_change_password.py`。

## 2. BATCH-001: 工程骨架与平台

- [x] 2.1 提交上一轮迁移产物的删除，并整理仓库：
  - 新建 `bookshop_web/` 包骨架和 `tests/` 的四个分层目录；
  - 在 `.gitignore` 中加入 `.venv/`、`*.db`、`*.db-wal`、`*.db-shm`；
  - 新建 `config.example.ps1`，里面只放示例占位值。

  对应：BATCH-001、DEC-001、DEC-022。验证：`pytest tests/static/test_repo_hygiene.py`（TEST-043 中关于 `.gitignore`、本机路径和密钥的部分）。

  进度备注：工作区的删除和新骨架已完成。按用户决定，所有提交（包括这次删除）推迟到全部批次完成后统一进行。
- [x] 2.2 写 `requirements.in`（Flask 3.1.3、Werkzeug 3.1.9、Jinja2 3.1.6、waitress 3.0.2）和 `requirements-test.in`（`-c requirements.txt`，pytest 9.1.1），然后用 pip-tools 7.6.2 加 `--generate-hashes --allow-unsafe --strip-extras` 生成锁文件。对应：BATCH-001、REQ-PLATFORM-012、DEC-014。验证（TEST-001）：在全新的 `.venv-check` 中执行 `pip install --require-hashes -r requirements-test.txt`，应安装成功。
- [x] 2.3 实现 `config.py`：读取 `BOOKSHOP_*` 环境变量，并做启动自检（解释器必须是 3.12.10，数据目录必须存在且可写，密钥不少于 32 字节且不是示例值，端口要在范围内）；默认 host 为 127.0.0.1、端口为 8080。对应：BATCH-001、REQ-PLATFORM-012、DEC-019。验证（TEST-002）：`pytest tests/unit/test_config.py`。
- [x] 2.4 实现应用框架：
  - `create_app()`，路由统一加 `/BookShop` 前缀；
  - 四个 `*.action` 的分派表，登记全部 opttype，业务处理暂时返回 501；
  - JSP 页面路由表；
  - MIG-RULE-019 的检查顺序；
  - 未迁移的路径返回 404。

  对应：BATCH-001、REQ-PLATFORM-003、REQ-PLATFORM-004、REQ-PLATFORM-015、DEC-002、DEC-003。验证（TEST-004）：`pytest tests/web/test_route_matrix.py`，本批次断言检查顺序和 501。
- [x] 2.5 实现 `responses.py`：alert 的文案和目标做成常量表，并补齐 400、403、404、405、413、500 的 `error.html`。对应：BATCH-001、REQ-PLATFORM-006、DEC-017。验证（TEST-007 中的机制部分）：`pytest tests/web/test_alerts.py -k mechanism`。
- [x] 2.6 实现 CSRF：会话令牌、模板全局函数 `csrf_token()`、对 POST 做常量时间比较；令牌缺失、错误或没有会话时返回 400。对应：BATCH-001、REQ-PLATFORM-007、DEC-005。验证（TEST-008）：`pytest tests/web/test_csrf.py`。
- [x] 2.7 实现 `logging_setup.py`：日志写到 stdout，并以轮转方式写到数据目录；请求日志只记方法、路径和状态码。对应：BATCH-001、REQ-PLATFORM-013、DEC-018。验证（TEST-013 中的框架部分）：`pytest tests/web/test_logging.py -k framework`。
- [x] 2.8 引入前端库：
  - 从 npm 发布包取 Bootstrap 5.3.8 的 `bootstrap.min.css`、`bootstrap.bundle.min.js`，以及 Bootstrap Icons 1.13.1 的 `bootstrap-icons.min.css` 和 `fonts/*.woff2`、`*.woff`；
  - 按 `dist.integrity` 校验，把来源和 sha512 写进 `bookshop_web/static/VENDOR.md`，附上 LICENSE；
  - 按 Bootstrap 5 改写 `carousel.css`、`dashboard.css`、`offcanvas.css`、`signin.css`；
  - 从 `BookShop/WebContent/img/` 复制 `1.jpg`、`2.jpg`、`default.jpg`。

  对应：BATCH-001、REQ-PLATFORM-010、DEC-011。验证：`pytest tests/web/test_static_assets.py tests/static/test_repo_hygiene.py`（TEST-011、TEST-043）。
- [x] 2.9 编写三套布局模板（会员端、管理端、登录注册页），以及 `index.html`、`login.html`、`register.html` 的静态部分。对应：BATCH-001、REQ-PLATFORM-001、REQ-PLATFORM-011、REQ-PLATFORM-002、DEC-012。验证：`pytest tests/web/test_page_structure.py -k "index or login or register" tests/web/test_encoding.py -k charset`（TEST-012、TEST-005）。
- [x] 2.10 实现 `python -m bookshop_web serve`（waitress，`threads=4`，`max_request_body_size` 为 6 MiB）、Flask 的 `MAX_CONTENT_LENGTH`（5 MiB），以及 `scripts/start.ps1` 和 `scripts/stop.ps1`（用虚拟环境的解释器，设置 `PYTHONUTF8=1`，写 PID 文件）。对应：BATCH-001、REQ-PLATFORM-012、REQ-PLATFORM-014、DEC-013。验证：`pytest -m server tests/server/test_waitress_smoke.py tests/server/test_body_limit.py` 和 `pytest tests/web/test_body_limit.py`（TEST-003、TEST-014）。
- [ ] 2.11 编写 `.github/workflows/bookshop-ci.yml`：
  - 在 `master` 的 push 和 pull_request 上触发；
  - windows-latest，`setup-python` 固定为 3.12.10，设置 `PYTHONUTF8=1`；
  - 安装时用 `--require-hashes`；
  - 运行 pytest（含 `-m server`），生成 `--junitxml=reports/junit.xml` 并上传为 artifact；
  - 运行 gate 的 coverage 和 lint。

  对应：BATCH-001、DEC-015、MIG-RULE-013。验证（TEST-042）：`pytest tests/static/test_workflow.py`，并推送到分支，确认 Actions 中这次运行为绿色。

  进度备注：workflow 已写好，`pytest tests/static/test_workflow.py` 通过；推送和确认 CI 按用户决定放到最后，届时再勾选。
- [ ] 2.12 确认 BATCH-001 的退出标准：TEST-001～TEST-005、TEST-007、TEST-008、TEST-011～TEST-014、TEST-042、TEST-043 在本机和 windows-latest 上都通过。确认回滚方式：`git revert` 本批次提交可以把工作区恢复到批次开始前的状态（在临时分支上演练一次）。验证：`pytest` 全量，加上 Actions 的运行记录。

## 3. BATCH-002: 数据层

- [x] 3.1 先写 TEST-006、TEST-010（静态扫描部分）、TEST-015～TEST-019，确认它们失败。对应：BATCH-002。验证：`pytest tests/unit/test_schema.py tests/unit/test_db.py tests/unit/test_money.py tests/unit/test_validation.py tests/web/test_init_db.py tests/web/test_errors.py`，应以失败结束。
- [x] 3.2 编写 `bookshop_web/schema.sql`：5 张 STRICT 表、外键、NOCASE 唯一约束、CHECK（按 MIG-RULE-018）；初始化时设置 WAL 和 `user_version=1`；不建 `customer` 表。对应：BATCH-002、REQ-DATA-001、DEC-007、GAP-001。验证（TEST-015）：`pytest tests/unit/test_schema.py`。
- [x] 3.3 实现 `db.py`：`get_db()`（`isolation_level=None`、`foreign_keys`、`busy_timeout`、`sqlite3.Row`）、在 teardown 时关闭连接、`write_tx()`（`BEGIN IMMEDIATE`，出错时回滚）。对应：BATCH-002、REQ-DATA-002、DEC-006。验证（TEST-016）：`pytest tests/unit/test_db.py tests/web/test_db_lifecycle.py`。
- [x] 3.4 实现 `money.py`（Decimal 转整数分、两位小数显示）和 `validation.py`（MIG-RULE-018 的全部上下限、正整数 ID）。对应：BATCH-002、REQ-DATA-004、REQ-DATA-005、DEC-008。验证：`pytest tests/unit/test_money.py tests/unit/test_validation.py`（TEST-018、TEST-019）。
- [x] 3.5 准备种子数据和初始化命令：
  - 把 `BookShop/db/seed.sql` 转写为 `bookshop_web/seed/seed_data.py`，价格转成分，文件头注明占位值；
  - 把 10 张封面复制到 `bookshop_web/seed/covers/`；
  - 实现 `python -m bookshop_web init-db`：没有口令参数；口令取自 `BOOKSHOP_ADMIN_PASSWORD` 或 getpass；拒绝空口令、`123456` 和超长口令；已有数据库时拒绝覆盖；
  - 编写 `docs/demo-data.md`。

  对应：BATCH-002、REQ-DATA-003、DEC-010、GAP-002、MIG-RULE-015。验证（TEST-017）：`pytest tests/web/test_init_db.py tests/unit/test_seed_transcription.py`。
- [x] 3.6 让数据库异常走 500 错误页并记录日志，不再吞掉异常。对应：BATCH-002、REQ-PLATFORM-005、DEC-017。验证（TEST-006）：`pytest tests/web/test_errors.py`。
- [x] 3.7 编写 SQL 拼接的静态扫描（所有 `execute` 和 `executemany` 的 SQL 参数必须是字面量）。对应：BATCH-002、REQ-PLATFORM-009、DEC-006。验证（TEST-010 中的静态部分）：`pytest tests/static/test_sql_params.py`。
- [x] 3.8 确认 BATCH-002 的退出标准：TEST-006、TEST-010（静态部分）、TEST-015～TEST-019 通过；在临时目录执行一次 `init-db` 后，数据与 seed 一致。确认回滚：`git revert` 本批次，再删除临时数据目录。验证：`pytest` 全量。

## 4. BATCH-003: 账号与会话

- [x] 4.1 先写 TEST-020～TEST-026，以及 TEST-013 中关于口令的场景；把 TEST-004 里会员端和管理端 URL 的断言，从 501 改为真实的 302 和 403；确认这些测试失败。对应：BATCH-003。验证：`pytest tests/web/test_login.py tests/web/test_session.py tests/web/test_admin_authz.py tests/web/test_logout.py tests/web/test_profile.py`，应以失败结束。
- [x] 4.2 实现会话加载与吊销：
  - `before_request` 加载用户，检查是否停用、`session_version`、8 小时绝对有效期；
  - 会话设为 permanent，有效期 30 分钟，Cookie 带 HttpOnly 和 SameSite=Lax，`Path` 为 `/BookShop`；
  - 会话里只放 DEC-004 和 DEC-016 列出的字段。

  对应：BATCH-003、REQ-ACCOUNT-003、DEC-004、DEC-016。验证（TEST-022）：`pytest tests/web/test_session.py`。
- [x] 4.3 实现管理员校验：只看数据库里的 role，非管理员访问管理端 URL 返回 403。对应：BATCH-003、REQ-ACCOUNT-004、DEC-003。验证：`pytest tests/web/test_admin_authz.py tests/web/test_route_matrix.py`（TEST-023、TEST-004）。
- [x] 4.4 实现注册 `addusers`：按检查顺序处理，用户名查重不区分大小写，口令用 scrypt 哈希，查重和插入在同一个写事务里，不建 `customer` 表。对应：BATCH-003、REQ-ACCOUNT-001。验证（TEST-020）：`pytest tests/web/test_register.py` 和 `pytest -m server tests/server/test_register_concurrency.py`。
- [x] 4.5 实现登录 `checkUsers`：用户名大小写不敏感，校验口令哈希，停用账号与口令错误给同一条提示，登录成功后重新签发会话，按数据库里的 role 跳转。对应：BATCH-003、REQ-ACCOUNT-002、DEC-004、DEC-005。验证（TEST-021）：`pytest tests/web/test_login.py`。
- [x] 4.6 实现 `POST /BookShop/logout.action`：递增 `session_version`，清空会话，302 到登录页；用 GET 访问返回 405；在三套布局里加上“退出”按钮。对应：BATCH-003、REQ-ACCOUNT-005。验证：`pytest tests/web/test_logout.py tests/web/test_page_structure.py -k logout`（TEST-024、TEST-012）。
- [x] 4.7 实现 `initMypage` 和 `my.html`：用户名和角色名从数据库读取，页面上有默认头像。对应：BATCH-003、REQ-ACCOUNT-006。验证（TEST-025）：`pytest tests/web/test_profile.py`。
- [x] 4.8 实现 `updatePwd` 和 `changepwd.html`：按检查顺序处理，旧文案不变，新口令用哈希保存，改成功后递增版本号、当前会话保持登录。对应：BATCH-003、REQ-ACCOUNT-007。验证：`pytest tests/web/test_change_password.py tests/web/test_logging.py`（TEST-026、TEST-013）。
- [x] 4.9 确认 BATCH-003 的退出标准：TEST-020～TEST-026 通过，TEST-004 中的 302 和 403 断言通过。确认回滚：`git revert` 本批次后，相关 opttype 回到返回 501 的状态。验证：`pytest` 全量。

## 5. BATCH-004: 书目与封面

- [x] 5.1 先写 TEST-027～TEST-029、TEST-009、TEST-010（注入用例）和 TEST-005（筛选部分），确认它们失败。对应：BATCH-004。验证：`pytest tests/web/test_catalogue.py tests/web/test_detail_and_reopen.py tests/web/test_covers.py tests/web/test_escaping.py tests/web/test_injection.py`，应以失败结束。
- [x] 5.2 实现 `queryAllbook`（把条件存进会话，302 到 `buy.jsp`）和 `buy.html`：
  - 书目按 bid 分组；
  - 销量降序，同销量按 bid 升序；
  - 只列在架的书；
  - 分类侧栏，以及用 GET 提交的搜索表单。

  对应：BATCH-004、REQ-CATALOG-001、REQ-CATALOG-002。验证（TEST-027）：`pytest tests/web/test_catalogue.py -k "list or buy_page"`。
- [x] 5.3 实现 `queryBytag`（分类名大小写不敏感，超过 20 字返回 400）和 `queryByname`（LIKE，`%` 和 `_` 仍是通配符，超过 100 字返回 400）。对应：BATCH-004、REQ-CATALOG-003、REQ-CATALOG-004。验证：`pytest tests/web/test_catalogue.py tests/web/test_encoding.py`（TEST-027、TEST-005）。
- [x] 5.4 实现 `bookDetail`：把 `detail_bid` 存进会话，302 到 `bookdetails.jsp`；页面上的“立即购买”是 POST 表单；书不存在或已下架返回 404，非法 bid 返回 400。同时实现“直接打开各结果页时按保存的条件重新查询”。对应：BATCH-004、REQ-CATALOG-005、REQ-CATALOG-006、DEC-016。验证（TEST-028）：`pytest tests/web/test_detail_and_reopen.py`。
- [x] 5.5 实现 `covers.py`、`jsp/showpic.jsp`（需要登录）和 `/BookShop/img/<name>`（公开）：文件名白名单、`resolve()` 越界检查、按文件头设置 Content-Type、各种异常都返回 404。对应：BATCH-004、REQ-CATALOG-007、REQ-CATALOG-008、DEC-021。验证（TEST-029）：`pytest tests/web/test_covers.py` 和 `pytest -m server tests/server/test_covers.py`。
- [x] 5.6 用 XSS 载荷检查会员端各页面的转义，并扫描模板，确认没有对数据使用 `safe` 或 `Markup`；同时补齐登录、搜索、分类、bid 的注入用例。对应：BATCH-004、REQ-PLATFORM-008、REQ-PLATFORM-009。验证：`pytest tests/web/test_escaping.py tests/static/test_templates_no_safe.py tests/web/test_injection.py`（TEST-009、TEST-010）。
- [x] 5.7 确认 BATCH-004 的退出标准：TEST-009、TEST-027～TEST-029 通过。确认回滚：`git revert` 本批次。验证：`pytest` 全量。

## 6. BATCH-005: 购买与我的订单

- [x] 6.1 先写 TEST-030～TEST-032，确认它们失败。对应：BATCH-005。验证：`pytest tests/web/test_purchase.py tests/web/test_my_orders.py`，应以失败结束。
- [x] 6.2 实现 `buybook`：在一个 `BEGIN IMMEDIATE` 事务里完成在架检查、库存检查、库存减 1，以及写入带成交价的订单；库存为 0 时提示 `out of stock!`，书不存在或已下架返回 404，成功后 302 到 `my.action?opttype=queryMyorder`。对应：BATCH-005、REQ-ORDER-001、REQ-ORDER-002、DEC-006。验证：`pytest tests/web/test_purchase.py` 和 `pytest -m server tests/server/test_purchase_concurrency.py`（TEST-030、TEST-031）。
- [x] 6.3 实现 `queryMyorder` 和 `myorder.html`：按成交价显示金额、按 oid 升序、已下架书的订单也显示。对应：BATCH-005、REQ-ORDER-003。验证（TEST-032）：`pytest tests/web/test_my_orders.py`。
- [x] 6.4 确认 BATCH-005 的退出标准：TEST-030～TEST-032 通过，20 个并发购买时不超卖。确认回滚：`git revert` 本批次。验证：`pytest` 全量。

## 7. BATCH-006: 管理端会员与账目

- [x] 7.1 先写 TEST-033、TEST-034、TEST-039，确认它们失败。对应：BATCH-006。验证：`pytest tests/web/test_admin_members_list.py tests/web/test_admin_members_disable.py tests/web/test_revenue.py`，应以失败结束。
- [x] 7.2 实现 `queryAllcustomers`、`queryCustomers` 和 `admin.html`：只列未停用的会员，按 uid 升序；搜索不区分大小写，超过 20 字返回 400；“删除”是 POST 表单。对应：BATCH-006、REQ-MEMBER-001、REQ-MEMBER-002。验证（TEST-033）：`pytest tests/web/test_admin_members_list.py`。
- [x] 7.3 实现 `deleteCustomers`：只能停用未停用的会员（role 为 1）；在一个写事务里把 `active` 设为 0 并递增 `session_version`；其他情况返回 404。对应：BATCH-006、REQ-MEMBER-003、DEC-004。验证（TEST-034）：`pytest tests/web/test_admin_members_disable.py`。
- [x] 7.4 实现 `showAllmoney` 和 `oderadmin.html`：按成交价显示，按 oid 升序，用整数分求合计，最后一行显示“总金额：<合计>元”。对应：BATCH-006、REQ-REVENUE-001、DEC-008。验证（TEST-039）：`pytest tests/web/test_revenue.py`。
- [x] 7.5 确认 BATCH-006 的退出标准：TEST-033、TEST-034、TEST-039 通过。确认回滚：`git revert` 本批次。验证：`pytest` 全量。

## 8. BATCH-007: 管理端书籍

- [x] 8.1 先写 TEST-035～TEST-038，确认它们失败。对应：BATCH-007。验证：`pytest tests/web/test_admin_books_list.py tests/web/test_admin_books_add.py tests/web/test_admin_books_edit.py tests/web/test_admin_books_offshelf.py`，应以失败结束。
- [x] 8.2 实现 `queryAllbooks`、`queryBooks` 和 `bookadmin.html`：列名、售价两位小数、“添加”链接、“修改”链接、“删除”表单。对应：BATCH-007、REQ-BOOK-001、REQ-BOOK-002。验证（TEST-035）：`pytest tests/web/test_admin_books_list.py`。
- [x] 8.3 实现 `add.html` 的分类下拉框，以及 `addBooks`：按规则校验字段，写入 `addbook_draft`，302 到 `addnext.jsp`（URL 不带字段值）。对应：BATCH-007、REQ-BOOK-003。验证（TEST-036 中的第一步部分）：`pytest tests/web/test_admin_books_add.py -k step1`。
- [x] 8.4 实现 `addnext.html` 和 `addBooksimg`：
  - 没有草稿时提示；
  - 按文件头校验 PNG 或 JPEG，不是就提示；
  - 用服务器生成的文件名以 `xb` 模式写入；
  - 在一个写事务里插入书籍并删除草稿，事务失败时删除刚写的文件。

  对应：BATCH-007、REQ-BOOK-004、DEC-021。验证：`pytest tests/web/test_admin_books_add.py tests/web/test_body_limit.py`（TEST-036、TEST-014）。
- [x] 8.5 实现 `showBooks`（把 `edit_bid` 存进会话，302 到 `editbook.jsp`）、`editbook.html`（只有三个可编辑字段）和 `editBooks`（校验后在一个事务里更新）。对应：BATCH-007、REQ-BOOK-005、DEC-016。验证（TEST-037）：`pytest tests/web/test_admin_books_edit.py`。
- [x] 8.6 实现 `deleteBooks` 的下架逻辑：书不存在或已下架时返回 404；订单和封面文件都保留。对应：BATCH-007、REQ-BOOK-006。验证（TEST-038）：`pytest tests/web/test_admin_books_offshelf.py`。
- [x] 8.7 确认 BATCH-007 的退出标准：TEST-035～TEST-038 通过，事务失败后 `covers/` 里没有残留文件。确认回滚：`git revert` 本批次，再删除测试用的封面目录。验证：`pytest` 全量。

## 9. BATCH-008: 收尾与切换

- [x] 9.1 编写并通过两条端到端旅程：会员端 TEST-040、管理端 TEST-041。对应：BATCH-008，覆盖全部能力。验证：`pytest tests/web/test_journey_customer.py tests/web/test_journey_admin.py`。
- [x] 9.2 编写文档：
  - `docs/运行说明.md`：安装、`init-db`、启停、备份与恢复、COMP-001 的风险说明；
  - 补全 `docs/demo-data.md`；
  - 重建 `THIRD_PARTY_NOTICES.md`。

  对应：BATCH-008、REQ-PLATFORM-012、DEC-022。验证（TEST-043）：`pytest tests/static/test_repo_hygiene.py`。
- [x] 9.3 编写并通过启停与回滚演练：`start.ps1`、`stop.ps1`、对运行中实例的冒烟检查、数据目录的备份与恢复。对应：BATCH-008、DEC-009、DEC-013。验证（TEST-044）：`pytest -m server tests/server/test_start_stop_rollback.py`。
- [ ] 9.4 人工检查两端主要页面的 Bootstrap 5 视觉效果和 JS 交互（窄屏导航折叠、轮播、上传预览），把结论记进 PR 说明，交给用户确认（见 test-plan 中的例外表）。对应：BATCH-008、MIG-DEC-010、REQ-PLATFORM-011。验证：用户在 PR 中确认。
- [ ] 9.5 按 design 的“Cutover and Rollback Design”切换：
  1. 打上 `pre-cutover` 标签；
  2. 在正式数据目录执行 `init-db`；
  3. 运行 `start.ps1`；
  4. 执行冒烟检查；
  5. 停服、备份数据目录，再启动。

  对应：BATCH-008。验证：test-plan 的“Post-Deployment Smoke Tests”全部通过，备份文件存在。
- [ ] 9.6 确认 BATCH-008 的退出标准：TEST-040、TEST-041、TEST-044、TEST-045 通过；全量测试在本机和 windows-latest 上都通过。确认回滚：停服，从备份恢复数据目录，必要时把代码检出到 `pre-cutover`。验证：`pytest` 全量，加上 Actions 的运行记录。

## 10. Operational Readiness

- [ ] 10.1 让 GitHub Actions 的检查稳定可复现：
  - Python 固定为 3.12.10，依赖用哈希锁安装（TEST-001、TEST-042）；
  - 全局设置 `PYTHONUTF8=1`；
  - 测试不访问网络，前端资源都在本地；
  - server 测试用随机端口，并设置连接超时；
  - 每个测试用独立的临时数据目录，用完清理；
  - 用 `-p no:cacheprovider` 禁用缓存；
  - 冻结时间的测试不依赖真实时钟。

  对同一个提交重跑 CI 两次，结果必须一致。对应：BATCH-001～BATCH-008、DEC-015、DEC-020。验证：`pytest tests/static/test_workflow.py`，并检查两次 Actions 运行都为绿色。
- [x] 10.2 每个批次结束时，以及最终交付前，运行 gate 的 coverage 和 lint，并修复所有报告的问题。对应：BATCH-008、MIG-RULE-023。验证（TEST-045）：
  - `node openspec/schemas/code-migration/scripts/migration_gate.mjs coverage --root migration-plans/bookshop --change openspec/changes/migrate-bookshop-to-flask`
  - `node openspec/schemas/code-migration/scripts/migration_gate.mjs lint --root openspec/changes/migrate-bookshop-to-flask --defs migration-plans/bookshop "*.md" "**/*.md"`

  其中 `"*.md"` 用来把 proposal、design、test-plan、tasks 这些根目录文件也纳入检查，因为单独的 `"**/*.md"` 只匹配子目录里的文件。
