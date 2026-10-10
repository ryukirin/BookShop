# Test Plan

## Test Strategy

- **判定依据**：旧系统无法运行（GAP-001、GAP-002），所以没有运行期的黄金样本。判定依据有两个：一是 8 份 spec 里的需求和场景；二是 `migration-plans/bookshop/legacy-baseline.md` 的静态描述，用于 PRESERVE 的文案、检查顺序、页面结构和跳转目标。种子数据里的占位值只用于结构断言，不当作旧系统事实（MIG-RULE-015）。
- **先红后绿**：每个批次先写好本批次的 TEST 并确认它们失败，再实现，直到全部通过。下表“执行阶段”一列标出了“实施前必须失败”的测试。
- **分层**（DEC-020）：
  - `tests/unit`：纯函数；
  - `tests/web`：Flask 测试客户端，每个测试用一个新的临时数据目录并执行 `init-db`；
  - `tests/server`：真实的 waitress，带 `server` 标记；
  - `tests/static`：仓库和配置扫描；
  - 另有端到端旅程测试（TEST-040、TEST-041）和过程检查（TEST-045）。
- **运行环境**：本机通过 `py -3.12` 建立的 `.venv`，设置 `PYTHONUTF8=1`。CI 用 GitHub Actions 的 windows-latest，Python 3.12.10（DEC-015）。下表每一行都标明“GitHub Actions：是/否”。
- **回滚保护**：标有“保护回滚”的测试，保证依赖能复现安装、数据库不会被意外覆盖、数据目录可以备份和恢复。
- **统一命令前缀**：表中的 `pytest` 指 `.venv\Scripts\python.exe -m pytest -p no:cacheprovider`。
- **证据**：CI 生成 `reports/junit.xml`，作为 workflow 的 artifact 上传；本机运行时，以 pytest 的终端输出为证据。

### EXP 检查项转写为 TEST（MIG-RULE-023）

| 实验 | 检查项 | TEST |
|---|---|---|
| EXP-001 | 固定版本能装到 3.12.10 上 | TEST-001 |
| EXP-002 | 旧 URL、查询后 302 到 JSP、中文 GET 参数、缺少或未知 opttype 返回 400、方法不对返回 405 | TEST-004、TEST-005 |
| EXP-003 | 外键、唯一、CHECK、STRICT 的转换行为、原子购买、成交价、分组与排序、LIKE、下架、精确合计 | TEST-015、TEST-016、TEST-027、TEST-030、TEST-039 |
| EXP-004 | scrypt 参数、口令校验、耗时 | TEST-020 |
| EXP-005 | 自动转义 | TEST-009 |
| EXP-006 | 登录后换新 Cookie、HttpOnly、SameSite、过期时间、退出 | TEST-021、TEST-022、TEST-024 |
| EXP-007 | 413、伪装文件、大写扩展名、封面类型、路径穿越、不存在的封面返回 404 | TEST-014、TEST-029、TEST-036 |
| EXP-008 | 带哈希的锁能完整安装 | TEST-001 |
| EXP-009 | waitress 服务、未迁移路径返回 404 | TEST-003、TEST-004 |
| EXP-010 | CI 能固定用 3.12.10 | TEST-042 |
| EXP-011 | 最坏情况下的 Cookie 大小 | TEST-022 |
| EXP-012 | waitress 的两层上限、分块上传、相对 302、封面类型 | TEST-014、TEST-029 |
| EXP-013 | WAL、并发购买、并发注册、NOCASE、文件清理 | TEST-015、TEST-016、TEST-020、TEST-031 |

## Traceability

| Test ID | Rule/legacy/requirement IDs | Test level | Oracle | Fixture/data | Command | Pass criteria | Execution stage / CI suitability | Evidence location |
|---|---|---|---|---|---|---|---|---|
| TEST-001 | REQ-PLATFORM-012、MIG-RULE-014、DEC-014、EXP-001、EXP-008 | 过程 | DEC-014 | 全新的虚拟环境 | `py -3.12 -m venv .venv-check` 后执行 `.venv-check\Scripts\python.exe -m pip install --require-hashes -r requirements-test.txt` | 安装成功；`pip freeze` 和锁文件一致 | BATCH-001；实施前必须失败（锁文件还不存在）；保护回滚；GitHub Actions：是（安装步骤） | CI 安装步骤的日志 |
| TEST-002 | REQ-PLATFORM-012、MIG-RULE-010、MIG-RULE-022、DEC-019 | unit | REQ-PLATFORM-012 的场景 | 用 monkeypatch 设置环境变量和 `sys.version_info` | `pytest tests/unit/test_config.py` | 分别缺少数据目录、密钥过短、用示例密钥、解释器不是 3.12.10、端口越界时，都以非零退出码拒绝；默认 host 为 127.0.0.1、端口为 8080 | BATCH-001；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-003 | REQ-PLATFORM-001、REQ-PLATFORM-012、DEC-013、EXP-009 | server | REQ-PLATFORM-001 的场景 | 临时数据目录；用随机端口起 waitress | `pytest -m server tests/server/test_waitress_smoke.py` | `/BookShop/` 和 `/BookShop/login.jsp` 返回 200，含中文和 `charset=utf-8`；只监听 127.0.0.1 | BATCH-001；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-004 | REQ-PLATFORM-003、REQ-PLATFORM-004、REQ-PLATFORM-015、MIG-RULE-001、MIG-RULE-019、LEGACY-005、LEGACY-039、EXP-002、EXP-009 | web | MIG-RULE-019 的顺序和分派表 | 四种身份：未登录、会员、停用会员、管理员；路由矩阵按分派表自动生成 | `pytest tests/web/test_route_matrix.py` | 每个“URL × 方法 × 身份”的组合，状态码和跳转目标都与 MIG-RULE-019 一致，包括 spec 中的四个顺序场景；未迁移的路径返回 404 | BATCH-001（框架，业务返回 501）；BATCH-003 起改为断言真实状态码；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-005 | REQ-PLATFORM-002、LEGACY-002、LEGACY-063、EXP-002 | web | REQ-PLATFORM-002 的场景 | 演示数据 | `pytest tests/web/test_encoding.py` | 中文分类“散文”能筛出书 6、7、8；POST 的中文能正确存取；`Content-Type` 含 `charset=utf-8` | BATCH-001（编码）、BATCH-004（筛选断言）；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-006 | REQ-PLATFORM-005、LEGACY-033、DEC-017 | web | REQ-PLATFORM-005 的场景 | 让数据库文件不可读，或用 monkeypatch 让连接抛出 `sqlite3.Error` | `pytest tests/web/test_errors.py` | 返回 500 错误页；日志里有异常类型和路径；400、403、404、405、413 的错误页都含状态码 | BATCH-002；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-007 | REQ-PLATFORM-006、MIG-RULE-020、LEGACY-034、DEC-017 | web | 旧文案出自 `legacy-baseline.md`，新文案出自 MIG-RULE-020 | 演示数据 | `pytest tests/web/test_alerts.py` | 7 条旧文案和 8 个新场景的文案、跳转目标都与预期一致，状态码都是 200 | BATCH-001（机制）；各功能批次补齐对应场景；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-008 | REQ-PLATFORM-007、MIG-RULE-004、LEGACY-051、LEGACY-070、DEC-005 | web | REQ-PLATFORM-007 的场景 | 演示数据，管理员会话 | `pytest tests/web/test_csrf.py` | 对每个 POST 的 opttype、`login.action`、`logout.action`，不带令牌、令牌错误、没有会话时都返回 400，数据不变；令牌正确时通过 | BATCH-001；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-009 | REQ-PLATFORM-008、MIG-RULE-005、LEGACY-052、EXP-005 | web 加 static | REQ-PLATFORM-008 的场景 | 在书名、简介、出版社、会员名里放 XSS 载荷 | `pytest tests/web/test_escaping.py tests/static/test_templates_no_safe.py` | 购买页、详情页、管理页的输出都已转义；模板里没有对数据使用 `safe` 或 `Markup` | BATCH-004；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-010 | REQ-PLATFORM-009、MIG-RULE-002、LEGACY-048 | web 加 static | REQ-PLATFORM-009 的场景 | 注入载荷 | `pytest tests/web/test_injection.py tests/static/test_sql_params.py` | 登录、注册、搜索、分类、bid、uid 的注入都被当作字面值；静态扫描没发现 `execute` 中拼接 SQL | BATCH-002（静态扫描）；BATCH-004 起补齐注入用例；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-011 | REQ-PLATFORM-010、MIG-RULE-011、LEGACY-037、LEGACY-047、DEC-011 | web | REQ-PLATFORM-010 的场景 | 演示数据，四种身份 | `pytest tests/web/test_static_assets.py` | 渲染所有页面，`src`、`href` 和本地 CSS 中 `url()` 引用的资源都返回 200，其中包括 `bootstrap-icons.woff2`；没有外部 URL；没有 jQuery | BATCH-001；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-012 | REQ-PLATFORM-011、REQ-PLATFORM-001、MIG-RULE-016、LEGACY-001、LEGACY-006、LEGACY-035、LEGACY-062 | web | `legacy-baseline.md` 中各页面的结构和文案 | 演示数据 | `pytest tests/web/test_page_structure.py` | 每个页面的标题、导航项、侧栏项、表格列名、字段名、按钮文字和链接目标都和基线一致；HTML 能被严格解析；首页登录后有“退出” | BATCH-001（首页、登录页、注册页）；各批次补齐对应页面；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-013 | REQ-PLATFORM-013、MIG-RULE-017、LEGACY-038、DEC-018 | web | REQ-PLATFORM-013 的场景 | 用 caplog 捕获日志 | `pytest tests/web/test_logging.py` | 完成注册、登录、改密码、触发一次 500 后，日志里没有口令、表单值和 SQL 文本；请求日志只有方法、路径和状态码 | BATCH-001（框架）、BATCH-003（口令场景）；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-014 | REQ-PLATFORM-014、MIG-RULE-009、LEGACY-054、EXP-007、EXP-012 | web 加 server | REQ-PLATFORM-014 的场景 | 管理员会话 | `pytest tests/web/test_body_limit.py` 和 `pytest -m server tests/server/test_body_limit.py` | 测试客户端：6 MiB 的上传返回 413。真实 waitress：5.5 MiB 返回应用的 413；声明 100 MiB 的请求不等收完就返回 413；分块上传超过 6 MiB 返回 413 | BATCH-001；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-015 | REQ-DATA-001、LEGACY-064、LEGACY-065、GAP-001、EXP-003、EXP-013 | unit | REQ-DATA-001 的场景和 `schema.sql` | 用 `schema.sql` 建一个临时库 | `pytest tests/unit/test_schema.py` | 外键、NOCASE 唯一、`role IN (1, 2)`、CHECK 都生效；STRICT 拒绝 `'abc'`；`'5.00'` 被转成 5（这一点作为记录断言）；没有 `customer` 表；`journal_mode` 为 wal | BATCH-002；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-016 | REQ-DATA-002、MIG-RULE-012、LEGACY-058、COMP-006、EXP-003、EXP-013 | unit 加 web | REQ-DATA-002 的场景 | 临时数据目录，多线程 | `pytest tests/unit/test_db.py tests/web/test_db_lifecycle.py` | 每个连接的 `foreign_keys` 都是 1；`write_tx` 出错时回滚；20 个线程用 `BEGIN IMMEDIATE` 并发写入时没有锁错误；一组请求之后，数据库文件和 `-wal`、`-shm` 文件都能删除 | BATCH-002；实施前必须失败；保护回滚；GitHub Actions：是 | `reports/junit.xml` |
| TEST-017 | REQ-DATA-003、MIG-RULE-015、LEGACY-066、GAP-002、DEC-010 | web 加 unit | REQ-DATA-003 的场景；对照 `BookShop/db/seed.sql` | 空的临时数据目录；口令来自 fixture 环境变量 | `pytest tests/web/test_init_db.py tests/unit/test_seed_transcription.py` | 有 3 个分类、10 本书、1 个管理员，没有会员和订单；`covers/` 有 10 个文件；`seed_data.py` 的书名、出版社、分类、价格（分）与解析 `seed.sql` 得到的值一致；口令为空、为 123456、超长、用参数传入时都拒绝；已有数据库时拒绝覆盖 | BATCH-002；实施前必须失败；保护回滚；GitHub Actions：是 | `reports/junit.xml` |
| TEST-018 | REQ-DATA-004、MIG-RULE-007、LEGACY-045、DEC-008 | unit | REQ-DATA-004 的场景 | 无 | `pytest tests/unit/test_money.py` | `parse_price` 能解析 0、0.1、99999.99；`25.555`、`-1`、`abc` 和超范围的值被拒绝；`fmt` 输出两位小数；0.10 + 0.20 + 39.80 = 40.10 | BATCH-002；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-019 | REQ-DATA-005、MIG-RULE-018、LEGACY-059 | unit 加 web | MIG-RULE-018 的上下限 | 演示数据 | `pytest tests/unit/test_validation.py tests/web/test_input_bounds.py` | 每个字段的最小值、最大值、超出 1、非数字、负数、三位小数、超大整数都按规则处理（alert 或 400）；没有出现 500；数据库里没有 NULL | BATCH-002（校验函数）；功能批次补齐页面用例；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-020 | REQ-ACCOUNT-001、LEGACY-007、LEGACY-049、LEGACY-065、LEGACY-073、EXP-004、EXP-013 | web 加 server | REQ-ACCOUNT-001 的场景；基线中的检查顺序和文案 | 演示数据 | `pytest tests/web/test_register.py` 和 `pytest -m server tests/server/test_register_concurrency.py` | 五个场景都通过；`upwd` 以 `scrypt:32768:8:1$` 开头，单次哈希低于 1000 ms；10 个并发注册恰好成功 1 个；没有 `customer` 表 | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-021 | REQ-ACCOUNT-002、LEGACY-008、LEGACY-057、LEGACY-065、EXP-006 | web | REQ-ACCOUNT-002 的场景 | 演示数据，外加一个会员和一个已停用的会员 | `pytest tests/web/test_login.py` | 会员和管理员的跳转正确；大小写不同的用户名能登录；停用会员和错误口令都得到同一条提示；登录后会话 Cookie 和登录前不同 | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-022 | REQ-ACCOUNT-003、MIG-RULE-021、DEC-004、DEC-016、LEGACY-003、LEGACY-010、LEGACY-063、EXP-006、EXP-011 | web | REQ-ACCOUNT-003 的场景 | 演示数据；用冻结或伪造的时间测 8 小时和 30 分钟 | `pytest tests/web/test_session.py` | 未登录、退出后重放、版本号不符、超过 8 小时、空闲超过 30 分钟，都 302 到登录页；Cookie 带 HttpOnly 和 SameSite=Lax；最大输入下（含两个 bid）`Set-Cookie` 不超过 3000 字节 | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-023 | REQ-ACCOUNT-004、MIG-RULE-003、LEGACY-050、LEGACY-011 | web | REQ-ACCOUNT-004 的场景 | 演示数据，四种身份 | `pytest tests/web/test_admin_authz.py` | 会员访问 7 个管理端 URL 都返回 403；管理员先访问个人页再访问管理端仍然正常；把会员在库里的 role 改为 2 后，下一次请求立即获得管理员权限 | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-024 | REQ-ACCOUNT-005、LEGACY-006、LEGACY-010、LEGACY-057 | web | REQ-ACCOUNT-005 的场景 | 同一账号在两个会话中登录 | `pytest tests/web/test_logout.py` | 退出后 302 到登录页，两个会话都失效；用 GET 退出返回 405；会员端和管理端所有页面都有“退出”按钮 | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-025 | REQ-ACCOUNT-006、LEGACY-011 | web | REQ-ACCOUNT-006 的场景 | 演示数据 | `pytest tests/web/test_profile.py` | 会员页显示“会员”，管理员页显示“管理员”；改库里的用户名后，刷新页面就能看到新名字 | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-026 | REQ-ACCOUNT-007、LEGACY-012、LEGACY-049 | web | REQ-ACCOUNT-007 的场景；基线中的检查顺序和文案 | 同一账号在两个会话中登录 | `pytest tests/web/test_change_password.py` | 三条文案和跳转都正确；改成功后当前会话保持登录，另一个会话失效；新口令能登录、旧口令不能；新口令超长时提示 `check new password!` | BATCH-003；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-027 | REQ-CATALOG-001、REQ-CATALOG-002、REQ-CATALOG-003、REQ-CATALOG-004、LEGACY-013、LEGACY-014、LEGACY-015、LEGACY-016、LEGACY-046、EXP-003 | web | 各需求的场景 | 演示数据，加上用 SQL 插入的订单、同名书、下架书 | `pytest tests/web/test_catalogue.py` | 销量降序、同销量按 bid 升序；同名书分开列出；下架书不出现；筛选和搜索的结果正确；`python` 能匹配“Python入门”；`%` 返回全部；参数超长返回 400；页面上没有价格 | BATCH-004；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-028 | REQ-CATALOG-005、REQ-CATALOG-006、LEGACY-017、LEGACY-032、DEC-016 | web | 各需求的场景 | 演示数据 | `pytest tests/web/test_detail_and_reopen.py` | 详情页字段齐全，价格两位小数；下架的书返回 404，非法 bid 返回 400；302 的 Location 是 `bookdetails.jsp`；直接打开结果页时按保存的条件重新查询；从没查询过时是空列表 | BATCH-004；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-029 | REQ-CATALOG-007、REQ-CATALOG-008、LEGACY-004、LEGACY-018、LEGACY-053、LEGACY-069、EXP-007、EXP-012 | web 加 server | 各需求的场景 | 演示封面，以及一个上传的封面 | `pytest tests/web/test_covers.py` 和 `pytest -m server tests/server/test_covers.py` | b6、b8 是 `image/png`，其余是 `image/jpeg`；`../`、非白名单名字、不存在的文件都返回 404；未登录用户能取 `/BookShop/img/`，取不到 `showpic.jsp` | BATCH-004；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-030 | REQ-ORDER-001、REQ-ORDER-002、LEGACY-019、LEGACY-020、LEGACY-040、LEGACY-041、LEGACY-042、EXP-003 | web | 各需求的场景 | 演示数据 | `pytest tests/web/test_purchase.py` | 购买成功后库存减 1，成交价等于当时的售价；库存为 0 时提示 `out of stock!`；下架或不存在的书返回 404，非法 bid 返回 400；改价后成交价不变；用 GET 购买返回 405 | BATCH-005；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-031 | REQ-ORDER-001、LEGACY-040、EXP-013 | server | REQ-ORDER-001 的并发场景 | 一本库存为 5 的书；20 个已登录会话 | `pytest -m server tests/server/test_purchase_concurrency.py` | 恰好 5 个 302、15 个 `out of stock!`；库存为 0，订单数为 5；没有 500 | BATCH-005；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-032 | REQ-ORDER-003、LEGACY-021 | web | REQ-ORDER-003 的场景 | 两笔订单，其中一本书随后被下架 | `pytest tests/web/test_my_orders.py` | 按 oid 升序；列名正确；金额为成交价、两位小数；已下架的书的订单仍显示；不显示订单号和合计 | BATCH-005；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-033 | REQ-MEMBER-001、REQ-MEMBER-002、LEGACY-022、LEGACY-023 | web | 各需求的场景 | 两个会员，其中一个已停用 | `pytest tests/web/test_admin_members_list.py` | 只列出未停用的会员，按 uid 升序，不含管理员；搜索不区分大小写；搜索词超过 20 字返回 400；“删除”是 POST 表单 | BATCH-006；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-034 | REQ-MEMBER-003、LEGACY-030、LEGACY-044、MIG-RULE-008 | web | REQ-MEMBER-003 的场景 | 一个有订单的会员 | `pytest tests/web/test_admin_members_disable.py` | 停用后从列表消失，订单仍计入账目；不能登录，原会话失效；停用管理员自己、已停用的会员、不存在的 uid 都返回 404 | BATCH-006；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-035 | REQ-BOOK-001、REQ-BOOK-002、LEGACY-024、LEGACY-025 | web | 各需求的场景 | 演示数据 | `pytest tests/web/test_admin_books_list.py` | 列名和顺序正确，售价两位小数；搜索“玄”只得到书 8；有“添加”链接；“删除”是 POST 表单 | BATCH-007；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-036 | REQ-BOOK-003、REQ-BOOK-004、LEGACY-026、LEGACY-027、LEGACY-055、LEGACY-071、LEGACY-072、COMP-024、DEC-021 | web | 各需求的场景 | 管理员会话；真实的 PNG、JPEG 和 GIF 字节 | `pytest tests/web/test_admin_books_add.py` | 第一步的 Location 没有参数，Cookie 不超过 3000 字节；三位小数和伪造的分类被拒绝；没有草稿时有提示；上传 `封面.PNG` 后新书出现，文件名是 32 位十六进制；GIF 被拒且没有残留文件；用 monkeypatch 让事务失败时，文件被删除并返回 500 | BATCH-007；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-037 | REQ-BOOK-005、LEGACY-028、DEC-016 | web | REQ-BOOK-005 的场景 | 演示数据，以及一笔订单 | `pytest tests/web/test_admin_books_edit.py` | `editbook.jsp` 只有三个可编辑字段；改价成功，订单的成交价不变；库存为 -1 时提示；下架或不存在的书返回 404 | BATCH-007；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-038 | REQ-BOOK-006、LEGACY-029、LEGACY-043、MIG-RULE-008 | web | REQ-BOOK-006 的场景 | 书 1 有一笔订单 | `pytest tests/web/test_admin_books_offshelf.py` | 下架后书目、管理列表、详情、购买中都没有书 1；订单和账目保留；`covers/b1.jpg` 仍在；重复下架返回 404 | BATCH-007；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-039 | REQ-REVENUE-001、LEGACY-031、LEGACY-042、LEGACY-045、EXP-003 | web | REQ-REVENUE-001 的场景 | 三笔成交价分别为 0.10、0.20、39.80 的订单，其中一本书已下架、一位会员已停用 | `pytest tests/web/test_revenue.py` | 按 oid 升序，四个列名正确；最后一行是“总金额：40.10元”；改价后合计不变 | BATCH-006；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-040 | REQ-ACCOUNT-001、REQ-ACCOUNT-002、REQ-ACCOUNT-005、REQ-ACCOUNT-006、REQ-ACCOUNT-007、REQ-CATALOG-001、REQ-CATALOG-004、REQ-CATALOG-005、REQ-ORDER-001、REQ-ORDER-003 | 旅程 | 策略的验收标准（会员端） | 新执行 `init-db` 的临时数据目录 | `pytest tests/web/test_journey_customer.py` | 用测试客户端按页面上的链接和表单依次完成：注册、登录、浏览、搜索、筛选、详情、购买、我的订单、个人页、改密码、退出。每一步的状态码和页面内容都符合 spec | BATCH-008；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-041 | REQ-MEMBER-001、REQ-MEMBER-002、REQ-MEMBER-003、REQ-BOOK-001、REQ-BOOK-002、REQ-BOOK-003、REQ-BOOK-004、REQ-BOOK-005、REQ-BOOK-006、REQ-REVENUE-001 | 旅程 | 策略的验收标准（管理端） | 新执行 `init-db` 的临时数据目录，外加一个会员和一笔订单 | `pytest tests/web/test_journey_admin.py` | 依次完成：会员列表、搜索、停用；书籍列表、搜索、两步新增（含上传）、修改、下架；账目统计。每一步都符合 spec | BATCH-008；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-042 | REQ-PLATFORM-012、MIG-RULE-013、MIG-RULE-014、MIG-RULE-022、DEC-015、EXP-010 | static | DEC-015 | `.github/workflows/bookshop-ci.yml` | `pytest tests/static/test_workflow.py` | workflow 只在 `master` 的 push 和 pull_request 上触发；`runs-on` 为 windows-latest；Python 固定为 3.12.10；设置了 `PYTHONUTF8=1`；安装时用 `--require-hashes`；运行 pytest（含 server 标记）和 gate；上传 junit 报告 | BATCH-001；实施前必须失败；GitHub Actions：是 | `reports/junit.xml` |
| TEST-043 | REQ-PLATFORM-012、REQ-PLATFORM-010、MIG-RULE-010、MIG-RULE-011、DEC-011、DEC-022 | static | MIG-RULE-010、MIG-RULE-011 | 整个仓库（排除 `.venv`、`BookShop/`、`.git`） | `pytest tests/static/test_repo_hygiene.py` | 没有真实密钥（只允许示例占位值）；没有盘符或用户目录形式的本机路径；模板里没有外部 URL；`static/VENDOR.md` 里的哈希和文件一致；有许可证文件；`.gitignore` 含 `.venv/` 和 `*.db` | BATCH-001；GitHub Actions：是 | `reports/junit.xml` |
| TEST-044 | REQ-PLATFORM-012、REQ-DATA-003、DEC-009、DEC-013 | server（PowerShell） | 设计中的切换与回滚 | 临时数据目录；随机端口 | `pytest -m server tests/server/test_start_stop_rollback.py` | 测试用 `scripts/start.ps1` 启动、`scripts/stop.ps1` 停止，PID 文件随之出现和清理；对运行中的实例做冒烟检查：首页 200、登录页 200、未登录访问 `jsp/my.jsp` 时 302、`/BookShop/img/b1.jpg` 200；然后停服、备份数据目录、修改数据、再停服、恢复，数据和备份一致 | BATCH-008；实施前必须失败；保护回滚；GitHub Actions：是 | `reports/junit.xml` |
| TEST-045 | MIG-RULE-023 | 过程 | schema 的 gate | 本 change 和规划包 | `node openspec/schemas/code-migration/scripts/migration_gate.mjs coverage --root migration-plans/bookshop --change openspec/changes/migrate-bookshop-to-flask`，以及对本 change 执行 `lint`（`--defs migration-plans/bookshop "*.md" "**/*.md"`） | 两条命令都输出 OK；上面的 EXP 转写表里每一项都有对应的 TEST | BATCH-008（每个批次结束时也要跑）；GitHub Actions：是 | CI 日志 |

## Characterization and Golden-Master Tests

旧系统不能运行，所以没有运行期的黄金样本。PRESERVE 的行为改用“静态特征测试”来固定，依据是 `legacy-baseline.md` 中逐条记录的结构、文案、检查顺序和跳转：

- TEST-012：每个页面的标题、导航、侧栏、表格列、字段、按钮和链接目标；
- TEST-007：旧系统的 7 条 alert 文案和对应的跳转目标；
- TEST-004：旧 URL、opttype 和 302 目标；
- TEST-020、TEST-026：注册和改密码的检查顺序。

每个批次开始时，先写本批次涉及的特征测试，并确认它们失败。

## Unit and Integration Tests

- **单元测试**：TEST-002（配置）、TEST-015（表结构）、TEST-016（连接与事务）、TEST-018（金额）、TEST-019（校验）、TEST-017 中的种子转写核对。
- **集成测试**（Flask 测试客户端，加上真实的临时 SQLite）：TEST-004～TEST-013，TEST-020～TEST-039。

## Contract and Interface Tests

URL 和参数名就是对外的契约：

- TEST-004：路由矩阵，覆盖每个 URL、每个 opttype、方法和身份；
- TEST-005：编码；
- TEST-008：所有 POST 都要带 `csrf_token`；
- TEST-028：302 的 Location 不带查询参数；
- TEST-036：新增书籍第一步的 Location 不带字段值；
- TEST-029：图片 URL 和 Content-Type。

## Browser Journey Tests

不引入浏览器自动化（不在策略的技术栈里）。端到端旅程用测试客户端，从页面上解析链接和表单，再按顺序提交：TEST-040 是会员端，TEST-041 是管理端。Bootstrap 5 的视觉效果和 JS 交互（窄屏导航折叠、轮播、上传预览）放在 BATCH-008 人工检查，见文末的例外表。

## Data Migration and Reconciliation Tests

没有历史数据要迁移（GAP-002）。核对的对象是演示数据，由 TEST-017 完成：解析 `BookShop/db/seed.sql`，与 `seed_data.py` 和初始化后的数据库逐行比对书名、出版社、分类、价格（分）、库存和封面名，并确认 `covers/` 里的 10 个文件与 `bookshop_web/seed/covers/` 字节一致。这项测试只核对“转写没有出错”，不把这些值当作原书店的数据。

## Error, Recovery, and Rollback Tests

- TEST-006：数据库异常时返回 500 并记录日志。
- TEST-016：写事务回滚；数据库文件能被删除和替换，所以备份和恢复可行。
- TEST-036：上传后事务失败时，清理已写入的文件。
- TEST-017：已有数据库时拒绝覆盖。
- TEST-044：启停，以及备份和恢复的演练。
- TEST-001：依赖能复现安装，所以回滚到旧版本时能重新部署。

## Security Tests

| 风险 | 测试 |
|---|---|
| SQL 注入 | TEST-010 |
| XSS | TEST-009 |
| CSRF | TEST-008 |
| 越权 | TEST-023 |
| 会话固定与吊销 | TEST-021、TEST-022、TEST-024、TEST-026、TEST-034 |
| 路径穿越 | TEST-029 |
| 上传伪装与超限 | TEST-036、TEST-014 |
| 口令哈希 | TEST-020 |
| 日志脱敏 | TEST-013 |
| 密钥和本机路径扫描 | TEST-043 |
| 停用会员登录 | TEST-021 |

## Performance and Resource Tests

- TEST-031：20 个并发购买，不超卖，没有锁错误。
- TEST-020：并发注册，以及单次 scrypt 低于 1000 ms。
- TEST-022：最大输入下，会话 Cookie 不超过 3000 字节。
- TEST-014：waitress 不会把超大请求体收完。

本机单用户规模，不做吞吐量压测。

## Cutover Verification

按 design 的“Cutover and Rollback Design”执行：

1. CI 为绿色（TEST-001～TEST-045），打上 `pre-cutover` 标签；
2. 在正式数据目录执行 `init-db`，TEST-017 的断言对这个库同样成立（3 个分类、10 本书、1 个管理员）；
3. `scripts/start.ps1` 启动后，执行下一节的冒烟检查；
4. 停服，备份数据目录，再启动。

## Post-Deployment Smoke Tests

对正在运行的实例（默认 `http://127.0.0.1:8080`），检查项和 TEST-044 中的冒烟部分相同：首页 200、登录页 200、未登录访问 `jsp/my.jsp` 时 302 到登录页、`/BookShop/img/b1.jpg` 200。再加一步人工检查：用管理员登录，看到会员管理页。

## Untestable Behaviour and Approved Exceptions

| Related ID | Reason | Compensating evidence | Human approval |
|---|---|---|---|
| MIG-DEC-010、REQ-PLATFORM-011 | Bootstrap 5 的外观和 JS 交互（导航折叠、轮播、上传预览）没有自动化的视觉判定方法，策略也没有引入浏览器自动化 | TEST-012 固定结构和文案；TEST-011 保证资源都能加载；BATCH-008 人工浏览两端主要页面 | 外观会变化已在 MIG-DEC-010 中确认；视觉验收由用户在 BATCH-008 人工确认 |
| GAP-001、GAP-002 | 旧系统无法运行，做不了运行期的黄金样本对照 | 以 `legacy-baseline.md` 的静态描述为判定依据（见“Characterization and Golden-Master Tests”） | MIG-DEC-005、MIG-DEC-006 |
| COMP-001 | Python 3.12.10 缺少后续安全补丁，测试无法消除这个风险 | TEST-003 和 TEST-002 保证默认只监听 127.0.0.1 | MIG-DEC-009 |
