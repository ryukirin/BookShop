# Migration Strategy

FEASIBILITY: FEASIBLE_WITH_CONDITIONS

可行，但有三个前提：

1. **CI 完整验证留到实施时。** 本机已在 Windows 上完成带哈希的完整安装（EXP-008）。GitHub Actions 上 windows-latest 的安装加全量测试，要在实施时跑通。部署和 CI 都只在 Windows 上（MIG-DEC-011）。
2. **Python 运行时风险已由用户接受。** 本机 Python 3.12.10 拿不到后续安全补丁（COMP-001，MIG-DEC-009）。
3. **占位值不能当成旧系统事实。** 种子数据里的占位值不得在规格或测试中被当作原书店的数据（MIG-RULE-015）。

2026-10-10 按 migration-review（strategy 模式）的 15 条意见做了修订：补齐了默认 PRESERVE 的冲突项，统一了相互矛盾的处置，并定下字段上限、会话、事务、上传、检查顺序、提示文案和运行环境，同时补做了 EXP-011～EXP-013。

## Source and Target

| Dimension | Source | Target |
|---|---|---|
| Language and version | Java 8（源码为 GBK 编码） | Python 3.12.10 |
| Runtime and version | Apache Tomcat 8.5 或 9.0（Servlet 3.1），实际版本未知 | CPython 3.12.10 + waitress 3.0.2（WSGI 服务器，单进程多线程，请求体上限 6 MiB） |
| Frameworks and versions | Servlet + JSP + JSTL（版本未知）；Bootstrap 3.3.7；jQuery 1.12.4（CDN） | Flask 3.1.3、Werkzeug 3.1.9、Jinja2 3.1.6（自动转义）；Bootstrap 5.3.8、Bootstrap Icons 1.13.1，全部本地提供，不再使用 jQuery |
| Data store and version | MySQL 库 `book`，原版本未知（复原环境用 8.0.x），驱动 Connector/J 8.0.11 | SQLite 单文件数据库（Python 自带模块，本机 SQLite 3.49.1）：STRICT 表、WAL 日志模式，写操作用 `BEGIN IMMEDIATE`，不用 ORM |
| Build/package system | Eclipse 工程，没有构建脚本，jar 不在仓库里 | pip；用 pip-tools 7.6.2 生成带哈希的 `requirements.txt` 和 `requirements-test.txt`，安装时加 `--require-hashes`；测试用 pytest 9.1.1 |
| Deployment environment | Tomcat，上下文路径 `/BookShop`，运行在作者的 Windows 机器上 | Windows 本机单进程，用 `py -3.12` 创建的虚拟环境运行，默认只监听 127.0.0.1，URL 前缀仍是 `/BookShop`；GitHub Actions 只在 windows-latest 上跑测试 |

## Scope

### In Scope

- 会员端和管理端的全部在用功能（LEGACY-001～LEGACY-035、LEGACY-037、LEGACY-038、LEGACY-073），按下面的 Behaviour Policy 迁移。
- 基线中所有疑似缺陷和安全问题的修复（LEGACY-039～LEGACY-062，LEGACY-061 除外，它直接去掉）。
- 为修复安全问题而新增的能力：退出登录 `POST /BookShop/logout.action`（LEGACY-057）、CSRF 令牌（LEGACY-051）、管理端角色校验（LEGACY-050）、会话版本号和绝对过期时间（MIG-DEC-012）。
- 软删除：删除书籍改为下架，删除会员改为停用（LEGACY-043、LEGACY-044，MIG-DEC-007）。
- 新增书籍第一步的草稿改存在服务端的数据库里（MIG-RULE-021，EXP-011）。
- 按 GAP-001 新建数据库表结构，按 GAP-002 准备初始化命令和演示数据，包括 10 张封面图、轮播图和默认头像。
- 配置外置、依赖锁定、Windows 本机启停说明，以及 GitHub Actions（windows-latest）测试。新的 workflow 在 `master` 分支的 push 和 pull request 上触发。
- 上一轮迁移的产物（`bookshop_app/`、`tests/`、`artifacts/`、`.github/workflows/bookshop-check.yml` 等）已在工作区删除，本次不复用。它们的删除随本次迁移一并提交，旧 workflow 由新 workflow 取代。

### Out of Scope

- 残留页面 `download.jsp`、`upload.jsp`、`wirte.jsp`、`useredit.jsp`，被注释掉的 Servlet，以及 CKEditor（LEGACY-036、LEGACY-061）。
- 迁移会员和订单历史；恢复原库的结构、分类名、价格、库存和简介（GAP-001、GAP-002）。
- 旧系统里没有的业务功能：分类管理、管理员账号管理、重新上架、恢复停用的会员、订单时间、购买数量。
- 和旧系统像素级一致；重建旧系统的 Java/Tomcat 运行环境做对照。
- 多实例部署、HTTPS 终止、多语言界面、Linux 部署。

## Readiness Gap Decisions

| Gap ID | Strategy | Consequence accepted |
|---|---|---|
| GAP-001 | 按旧代码重建 SQLite 表结构（MIG-DEC-005）。<br>**沿用旧列名**：`user(uid, uname, upwd, role)`、`tag(tid, tname)`、`book(bid, bname, publishers, stock, tid, url, cont)`、`orders(oid, bid, uid)`。只写不读的 `customer` 表不再保留，会员身份只看 `role`（LEGACY-073）。<br>**补上约束**：主键；外键（每个连接都开 `PRAGMA foreign_keys`）；NOT NULL；`role IN (1, 2)`；`uname` 和 `tname` 都用 `COLLATE NOCASE` 加唯一约束（MIG-DEC-013）；用 CHECK 落实 MIG-RULE-018 的长度和数值范围。<br>**金额改存整数分**：`book.price_cents`。<br>**新增列**：`book.on_sale`（下架）、`user.active`（停用）、`user.session_version`（会话版本，MIG-DEC-012）、`orders.unit_price_cents`（成交价）。<br>**新增表** `addbook_draft`：每个管理员一行，存新增书籍第一步的草稿。<br>**日志模式**：建库时设为 WAL。<br>**复原库的定位**：`BookShop/db/` 里的复原 MySQL 库只作为理解旧行为的参考，不做数据对拷，也不作为目标结构的依据 | 目标库和原库结构不一致。凡是依赖原库未知设置的旧行为（LEGACY-044、LEGACY-046、LEGACY-055、LEGACY-064、LEGACY-065），在目标系统里一律按修复后的行为定义，不再和原库对照 |
| GAP-002 | 用初始化命令建库并导入演示数据（MIG-DEC-006）。<br>**分类和书目**：`BookShop/db/seed.sql` 里的 3 个分类和 10 本书（bid 1～9、11）。<br>**封面**：`b1.jpg`～`b9.jpg` 和 `b11.jpg` 按原文件名复制到数据目录的 `covers/` 下，`book.url` 只存文件名（MIG-RULE-009）。<br>**占位值**：价格、库存、简介沿用 seed 里的占位值，在数据说明里标为“演示占位”。<br>**管理员**：账号名 `admin`，口令只能从环境变量 `BOOKSHOP_ADMIN_PASSWORD` 读取，或者在终端里交互输入（不回显）；不接受命令行参数，不允许是 `123456`，也不允许为空。<br>**历史数据**：不迁移会员和订单 | 系统一上线就是演示数据，不是原书店的数据。原来的分类名、价格、库存、简介，以及全部会员和订单历史，都永久丢失 |

## Behaviour Policy

没有列在下表里的 LEGACY 行为一律 PRESERVE。所有页面都用 Bootstrap 5 重做样式（MIG-DEC-010），但页面结构、字段、链接目标和中文文案保持不变（MIG-RULE-016）；原来用链接触发、会修改数据的操作，一律改成样式相同的 POST 表单按钮（MIG-RULE-004）。这两点对所有页面都成立，下表不再逐页列出。各类请求的检查顺序见 MIG-RULE-019，新增的提示文案见 MIG-RULE-020。

| Legacy ID | Disposition | Rationale |
|---|---|---|
| LEGACY-003 | CHANGE | `/jsp/*` 的登录要求不变。另外：管理端 URL 要求 role 为 2（LEGACY-050）；停用的会员、会话版本不符或超过绝对有效期的会话都按未登录处理（MIG-RULE-021）；`jsp/ckeditor/` 和残留页面不再存在，先返回 404（MIG-RULE-019） |
| LEGACY-004 | CHANGE | 公开和受保护的 URL 划分不变。`/bootstrap/*` 下的资源改为 Bootstrap 5.3.8 和 Bootstrap Icons 1.13.1。`/BookShop/img/<文件名>` 仍然公开、不需要登录，既提供轮播图和默认头像，也提供数据目录里的封面，包括上传的封面（MIG-RULE-009） |
| LEGACY-005 | CHANGE | 查询类 opttype 只接受 GET，用 POST 访问返回 405；修改数据的 opttype 只接受 POST 并校验 CSRF 令牌，用 GET 访问返回 405（LEGACY-051） |
| LEGACY-006 | CHANGE | 首页内容不变；登录后导航栏多一个“退出”按钮（MIG-RULE-001）。会员端和管理端的所有页面都一样 |
| LEGACY-007 | CHANGE | 注册的检查顺序、跳转和原有的三条 alert 文案都不变。具体改动：<br>• 口令以 scrypt 哈希保存（LEGACY-049）；<br>• 不再写 `customer` 表；<br>• 用户名查重不区分 ASCII 大小写，已停用会员的用户名也算被占用（MIG-DEC-013）；<br>• 用户名限 1～20 字，口令限 1～64 字，超出时提示 `please check user name or password!`（MIG-RULE-018、MIG-RULE-020）；<br>• 查重和插入放在同一个事务里，并发重名时只有一个成功，其余提示 `please change uer name!`（EXP-013）；<br>• `fail,try again!` 只在其他数据库写入失败时出现 |
| LEGACY-008 | CHANGE | 提示文案和跳转目标不变。具体改动：<br>• 登录只接受 POST，必须带 CSRF 令牌；<br>• 登录成功后重新签发会话 Cookie（LEGACY-057）；<br>• 跳转用的角色从数据库读取；<br>• 用户名匹配不区分 ASCII 大小写（MIG-DEC-013）；<br>• 停用的会员不能登录，提示和密码错误时相同；<br>• 用户名唯一，“同名取最后一行”的情况不会再出现 |
| LEGACY-009 | REMOVE | 数据库约束让 role 只能是 1 或 2，这个分支已不可能出现 |
| LEGACY-010 | CHANGE | 新增退出登录（MIG-RULE-001）。会话空闲 30 分钟过期，和 Tomcat 默认值一致（LEGACY-063）；另加 8 小时的绝对有效期（MIG-RULE-021） |
| LEGACY-011 | CHANGE | 页面显示的用户名和角色名（“会员”或“管理员”）每次都从数据库读取，会话里不再存 `uname` 和 `role`。这样就不会出现旧系统那种“改写会话里的 role”的副作用，授权也一律以数据库里的角色为准（MIG-RULE-021） |
| LEGACY-012 | CHANGE | 检查顺序、alert 文案和跳转都不变。改动：新口令以哈希保存；新口令为空或超过 64 字时提示 `check new password!`；改成功后递增会话版本号，其他设备上的会话全部失效，当前会话换新值后保持登录（MIG-RULE-021） |
| LEGACY-013 | CHANGE | 按 bid 分组（LEGACY-046），下架的书不出现；排序为销量降序，销量相同时按 bid 升序，补上旧系统没定义的部分 |
| LEGACY-015 | CHANGE | 返回内容和排序同 LEGACY-013。分类名按等值匹配，不区分 ASCII 大小写（MIG-DEC-013）；参数超过 20 字返回 400（MIG-RULE-018） |
| LEGACY-016 | CHANGE | 返回内容和排序同 LEGACY-013。搜索对 ASCII 字母不区分大小写，对其他字符区分（SQLite 的 LIKE，见 COMP-004）。用户输入的 `%` 和 `_` 仍按通配符处理，和旧系统一样。搜索词超过 100 字返回 400（MIG-RULE-018） |
| LEGACY-017 | CHANGE | bid 不存在或书已下架时返回 404，旧系统是返回一个没有内容的页面。“立即购买”改成 POST 表单按钮 |
| LEGACY-018 | CHANGE | 按文件内容设置 `image/png` 或 `image/jpeg`；文件名不符合白名单格式、文件不存在或不是图片时，返回 404（LEGACY-053、LEGACY-069，MIG-RULE-009） |
| LEGACY-019 | CHANGE | 购买改为 POST 加 CSRF。校验库存、扣库存、记录成交价、插入订单，全在同一个 `BEGIN IMMEDIATE` 事务里完成（EXP-013）。库存为 0 时提示 `out of stock!` 并回到详情页；书不存在或已下架时返回 404（LEGACY-041）。成功后仍然 302 到 `my.action?opttype=queryMyorder` |
| LEGACY-020 | CHANGE | 订单多记录一项成交价 `unit_price_cents`（LEGACY-042），仍然不记录时间和数量 |
| LEGACY-021 | CHANGE | 金额取成交价，按 oid 升序排列；已下架的书的订单照常显示 |
| LEGACY-022 | CHANGE | 不显示停用的会员，按 uid 升序排列。“删除”改成 POST 表单按钮 |
| LEGACY-023 | CHANGE | 不包括停用的会员。用户名按等值匹配，不区分 ASCII 大小写（MIG-DEC-013）；搜索词超过 20 字返回 400 |
| LEGACY-024 | CHANGE | 分组同 LEGACY-013，下架的书不出现，按 bid 升序排列。“删除”改成 POST 表单按钮，“修改”仍是链接 |
| LEGACY-025 | CHANGE | 返回内容同 LEGACY-024；搜索词超过 100 字返回 400 |
| LEGACY-026 | CHANGE | 第一步的六个字段改存为当前管理员在 `addbook_draft` 里的草稿，会话里不再存，跳转到 `addnext.jsp` 的 URL 也不带字段值（LEGACY-071，EXP-011）。另外：改为 POST 加 CSRF；分类改成下拉框，只能选已有分类（LEGACY-055）；服务端按 MIG-RULE-018 校验，不通过时提示 `please check book info!` 并回到 `add.jsp` |
| LEGACY-027 | CHANGE | 第二步的处理：<br>• 没有第一步的草稿：提示 `please fill in book info first!` 并回到 `add.jsp`；<br>• 没选文件，或者不是 PNG/JPEG：提示 `please upload a png or jpg image!` 并回到 `addnext.jsp`；<br>• 请求体超过上限：返回 413（MIG-RULE-009）。<br>封面先写进数据目录，再在同一个事务里插入书籍、删除草稿；事务失败时删掉刚写的文件（COMP-024） |
| LEGACY-028 | CHANGE | 改为 POST 加 CSRF；校验规则同 LEGACY-026，不通过时提示 `please check book info!` 并回到编辑页；三项修改在同一个事务里完成；bid 不存在或书已下架时返回 404 |
| LEGACY-029 | CHANGE | “删除”改为下架（MIG-DEC-007）：书从所有书目、搜索、详情中消失，不能再买；订单和账目保留；封面文件保留。改为 POST 加 CSRF；bid 不存在或书已下架时返回 404；成功后 302 到 `admin.action?opttype=queryAllbooks` |
| LEGACY-030 | CHANGE | “删除”改为停用（MIG-DEC-007）：<br>• 只能停用未停用的会员（role 为 1），否则返回 404，所以管理员停用不了自己，也停用不了其他管理员；<br>• 被停用的会员从会员列表和搜索中消失，不能再登录；<br>• 递增他的会话版本号，已有会话立即失效；<br>• 订单和账目保留，用户名仍然被占用；<br>• 改为 POST 加 CSRF；成功后 302 到 `admin.action?opttype=queryAllcustomers` |
| LEGACY-031 | CHANGE | 金额取成交价，用整数分精确求和，显示两位小数；已下架的书和已停用会员的订单都计入；按 oid 升序排列 |
| LEGACY-032 | CHANGE | “查询后 302 到 JSP”的流程不变，但会话里只保存查询条件，不再保存结果；三个列表页各存一份，条件的长度有上限（MIG-RULE-018），最坏情况下 Cookie 也只有 1238 字节（EXP-011）。JSP 页面按保存的条件重新查询，看到的是最新数据；从没查询过时显示空列表 |
| LEGACY-033 | CHANGE | 数据库出错时记录日志，返回 500 错误页，不再悄悄显示空列表或空白页 |
| LEGACY-034 | CHANGE | 旧的 alert 提示机制和英文原文保留，新增失败场景的文案按 MIG-RULE-020。400、403、404、405、413、500 改由应用自己的错误页呈现；只有超过 6 MiB 的请求，是由 waitress 直接返回 413 纯文本（MIG-RULE-009） |
| LEGACY-036 | REMOVE | 残留页面不迁移，这些 URL 返回 404 |
| LEGACY-037 | CHANGE | 静态资源全部本地提供：Bootstrap 5.3.8 和 Bootstrap Icons 1.13.1；不再使用 jQuery，也不引用任何 CDN（MIG-DEC-010） |
| LEGACY-038 | CHANGE | 改用 Python logging；不记录密码、SQL 参数、表单值和会话内容（MIG-RULE-017） |
| LEGACY-039 | BUG_NOT_PRESERVED | `opttype` 缺失或无法识别时返回 400 错误页（EXP-002）；它和登录、角色检查的先后关系见 MIG-RULE-019 |
| LEGACY-040 | BUG_NOT_PRESERVED | 库存检查和扣减放在同一个 `BEGIN IMMEDIATE` 事务里，库存为 0 时拒绝；20 个线程并发购买时没有超卖（EXP-003、EXP-013） |
| LEGACY-041 | BUG_NOT_PRESERVED | 购买不存在或已下架的书返回 404；bid 不是正整数时返回 400 |
| LEGACY-042 | BUG_NOT_PRESERVED | 下单时记录成交价，“我的订单”和账目统计都用成交价，改价不影响历史订单（EXP-003） |
| LEGACY-043 | BUG_NOT_PRESERVED | 删除书籍改为下架，不再删除订单（MIG-DEC-007） |
| LEGACY-044 | BUG_NOT_PRESERVED | 删除会员改为停用，订单保留并继续计入账目；不会再出现“只删了一半”的状态（MIG-DEC-007） |
| LEGACY-045 | BUG_NOT_PRESERVED | 金额用整数分精确计算，显示两位小数（MIG-RULE-007） |
| LEGACY-046 | BUG_NOT_PRESERVED | 按 bid 分组，同名书分开列出；SQLite 下这样写合法，不依赖 `sql_mode`（EXP-003） |
| LEGACY-047 | BUG_NOT_PRESERVED | 页面和 CSS 引用的资源全部本地提供，路径都要核对，包括字体和图标（MIG-RULE-011） |
| LEGACY-048 | SECURITY_FIX_REQUIRED | 所有 SQL 一律参数化（MIG-RULE-002） |
| LEGACY-049 | SECURITY_FIX_REQUIRED | 密码用 Werkzeug 的 scrypt 哈希保存和校验（MIG-RULE-006，EXP-004） |
| LEGACY-050 | SECURITY_FIX_REQUIRED | 管理端 URL 要求数据库里的 role 为 2，其他已登录用户访问返回 403（MIG-RULE-003、MIG-RULE-021） |
| LEGACY-051 | SECURITY_FIX_REQUIRED | 所有修改数据的操作（包括登录和退出）只接受 POST，并校验会话里的 CSRF 令牌（MIG-RULE-004）；会话 Cookie 设为 SameSite=Lax（EXP-006） |
| LEGACY-052 | SECURITY_FIX_REQUIRED | 模板自动转义，不对数据库或请求数据使用 `safe` 过滤器或 `Markup`（MIG-RULE-005，EXP-005） |
| LEGACY-053 | SECURITY_FIX_REQUIRED | 文件名必须符合白名单格式，并且只在封面目录里查找；路径越界一律返回 404（MIG-RULE-009，EXP-007） |
| LEGACY-054 | SECURITY_FIX_REQUIRED | 文件名由服务器生成；按文件头只接受 PNG 和 JPEG，扩展名不区分大小写；应用层限制请求体 5 MiB，waitress 层限制 6 MiB；文件存到代码目录之外的数据目录（MIG-RULE-009，EXP-007、EXP-012） |
| LEGACY-055 | BUG_NOT_PRESERVED | 分类只能从下拉框选择，服务端再校验分类是否存在；不存在时提示 `please check book info!`，书不会插入 |
| LEGACY-056 | SECURITY_FIX_REQUIRED | 不再有数据库凭据（SQLite 文件）；密钥、数据目录、监听地址、管理员初始口令都来自环境变量，管理员口令也可以交互输入（MIG-RULE-010、MIG-RULE-015） |
| LEGACY-057 | SECURITY_FIX_REQUIRED | 修复内容（MIG-RULE-021，MIG-DEC-012）：<br>• 登录时清空并重新签发会话（EXP-006）；<br>• 新增退出登录；<br>• 用会话版本号实现服务端吊销，退出、改密码、停用时都会递增；<br>• 空闲 30 分钟、绝对 8 小时过期；<br>• Cookie 设为 HttpOnly 和 SameSite=Lax |
| LEGACY-058 | BUG_NOT_PRESERVED | 每个请求单独开一个连接，用完关闭；写操作用 `BEGIN IMMEDIATE`，依赖数据库状态的校验和写入放在同一个事务里；启用 WAL 和 busy timeout（MIG-RULE-012，EXP-013） |
| LEGACY-059 | BUG_NOT_PRESERVED | 列都设为 NOT NULL，写入前校验；不会再因为某一行的空值让整页报 500 |
| LEGACY-060 | BUG_NOT_PRESERVED | 路径一律用 pathlib 拼接，不写死分隔符（MIG-RULE-013）。部署和 CI 都只在 Windows 上，不要求 Linux 兼容（MIG-DEC-011） |
| LEGACY-061 | REMOVE | 失效的 servlet 映射和 `useredit.jsp` 不迁移，这些 URL 返回 404（EXP-009） |
| LEGACY-062 | BUG_NOT_PRESERVED | 模板重写时修正残缺的标签，不再带任何本机路径 |
| LEGACY-063 | CHANGE | 结论：查询参数统一按 UTF-8 解码（EXP-002，和 Tomcat 8 起默认的 URIEncoding 一致）；会话空闲超时取 30 分钟（Tomcat 默认值）；不再依赖 Tomcat 的版本 |
| LEGACY-064 | CHANGE | 结论：目标表结构按 GAP-001 新建，不依赖原库的类型和约束 |
| LEGACY-065 | CHANGE | 结论：目标用 SQLite，不再依赖原 MySQL 的版本、`sql_mode`、字符集和认证插件。用户名和分类名的等值匹配用 `COLLATE NOCASE`，不区分 ASCII 大小写，和 MySQL 常见的 `_ci` 排序规则一致；非 ASCII 字母仍然区分大小写（MIG-DEC-013，EXP-013）。LIKE 搜索的规则见 LEGACY-016 |
| LEGACY-066 | CHANGE | 结论：初始数据按 GAP-002 处理，不追查原数据 |
| LEGACY-067 | REMOVE | 目标系统不用 JSP 和 JSTL，这个问题已不存在 |
| LEGACY-068 | REMOVE | 结论：`/uploadServlet.do` 和 `/downloadServlet.do` 在目标系统里返回 404（EXP-009） |
| LEGACY-069 | CHANGE | 结论：封面输出不再依赖平台路径和 JSP 的输出流，按 LEGACY-018 处理（EXP-007、EXP-012） |
| LEGACY-070 | CHANGE | 结论：旧系统那种“响应已提交、无法再建会话”的异常不会再出现。但登录要求带会话里的 CSRF 令牌，所以没先打开 `login.jsp` 就直接 POST 登录（不带令牌）会返回 400。从 `login.jsp` 进入的正常流程不受影响 |
| LEGACY-071 | CHANGE | 结论：第一步的字段存进服务端草稿，跳转 URL 不带字段值，按 LEGACY-026 处理 |
| LEGACY-072 | BUG_NOT_PRESERVED | 结论：文件名由服务器生成，不再使用客户端提供的名字，不会因此出现同名覆盖 |
| LEGACY-073 | CHANGE | 目标系统没有 `customer` 表，会员身份只由 `user.role` 决定。所以“role 为 1 的用户不论有没有 `customer` 行都能正常使用”这一可观察结果仍然成立 |

## Rules

| Rule ID | Rule | How it is verified |
|---|---|---|
| MIG-RULE-001 | 保留旧 URL：在用页面和操作沿用旧路径（`/BookShop/...`、`*.jsp`、`*.action?opttype=...`）。查询走 GET，修改数据走 POST，方法不对时返回 405。新增的退出登录是 `POST /BookShop/logout.action`，要带 CSRF 令牌：成功后递增会话版本号、清空会话，302 到 `/BookShop/login.jsp`；用 GET 访问返回 405。登录后，会员端、管理端所有页面和首页的导航栏都显示“退出”按钮 | 路由矩阵测试：逐一请求旧 URL 和退出 URL，断言状态码、跳转目标和方法限制 |
| MIG-RULE-002 | 所有 SQL 都用 `?` 占位符传参，禁止用字符串拼接、格式化或 f-string 组装 SQL | 注入用例测试（登录、注册、搜索、分类、bid）；再静态检查执行 SQL 的调用里没有拼接 |
| MIG-RULE-003 | `/BookShop/jsp/*` 要求有效会话（见 MIG-RULE-021），否则 302 到 `/BookShop/login.jsp`。管理端 URL 要求数据库里当前的 role 为 2，否则返回 403；管理端 URL 包括 `admin.action`、`admin.jsp`、`bookadmin.jsp`、`add.jsp`、`addnext.jsp`、`editbook.jsp`、`oderadmin.jsp` | 用未登录、会员、停用会员、会话版本不符、管理员这几种身份逐一请求各个 URL |
| MIG-RULE-004 | 每个修改数据的请求，包括登录、注册、退出，都必须带上会话里的 CSRF 令牌，比较用 `hmac.compare_digest`；令牌缺失或不对时返回 400 | 测试：不带令牌、令牌错误、令牌正确、没有会话四种情况 |
| MIG-RULE-005 | Jinja2 自动转义保持开启；不对来自数据库或请求的数据使用 `safe` 过滤器或 `Markup` | 在书名、简介、出版社、会员名里放 XSS 载荷，断言页面输出被转义；再静态检查模板 |
| MIG-RULE-006 | 密码只保存 `generate_password_hash` 的结果（默认 scrypt），用 `check_password_hash` 校验；日志和页面里都不出现明文密码 | 单元测试，以及对日志内容的断言 |
| MIG-RULE-007 | 金额在数据库里存整数分；计算用整数或 Decimal；页面显示两位小数；订单保存成交价 | 测试改价后订单金额不变、总金额精确，以及 0.1 + 0.2 一类的累加 |
| MIG-RULE-008 | 软删除：下架的书不出现在任何书目、搜索、详情里，也不能购买；停用的会员不能登录，不出现在会员列表和搜索里，会话立即失效；只能停用未停用的会员（role 为 1）；订单和账目照常保留 | 下架和停用前后的列表、登录、购买、账目测试；用管理员自己的 uid 去停用，应返回 404 |
| MIG-RULE-009 | 上传和封面：<br>• **大小**：应用层 `MAX_CONTENT_LENGTH` 为 5 MiB，超过时返回应用的 413 错误页；waitress 的 `max_request_body_size` 为 6 MiB，超过时由 waitress 直接返回 413，不会先收完请求体（EXP-012）。<br>• **类型**：按文件头只接受 PNG 和 JPEG。<br>• **文件名**：封面存在数据目录的 `covers/` 下，名字必须符合 `^[A-Za-z0-9_-]{1,64}\.(jpg\|jpeg\|png)$`（扩展名不区分大小写）；种子封面沿用 `b1.jpg` 等原名，上传的封面由服务器命名为“32 位十六进制 + 扩展名”；`book.url` 只存文件名。<br>• **访问**：`/BookShop/img/<文件名>` 公开，提供轮播图、默认头像和封面；`/BookShop/jsp/showpic.jsp?img=` 需要登录，只提供封面。两者都按白名单校验，不符合就返回 404，Content-Type 按文件头设置 | 测试：超大文件（分别经过 Flask 测试客户端和真实 waitress）、伪装扩展名、大写扩展名、没选文件、路径穿越、非白名单文件名、两个 URL 是否需要登录 |
| MIG-RULE-010 | 配置从 `BOOKSHOP_` 开头的环境变量读取：数据目录、`SECRET_KEY`（至少 32 字节随机值）、监听地址（默认 127.0.0.1）、端口。缺少配置或用的是示例值时拒绝启动；仓库里不放真实密钥 | 启动配置的单元测试，以及扫描仓库确认没有密钥 |
| MIG-RULE-011 | 页面不引用任何外部 URL。Bootstrap 5.3.8 和 Bootstrap Icons 1.13.1 随仓库提供，并附许可证。页面里引用的每个静态资源，以及本地 CSS 里用 `url()` 引用的每个资源（比如字体），都必须能返回 200 | 测试：渲染每个页面，抓出所有 `src` 和 `href`，再递归解析本地 CSS 里的 `url()`；断言没有外部 URL，且每个资源都返回 200 |
| MIG-RULE-012 | 数据库连接和事务：<br>• **连接**：每个请求单独开一个 SQLite 连接，用 `isolation_level=None`（自动提交，事务由应用显式控制）；连接时执行 `PRAGMA foreign_keys = ON` 和 `PRAGMA busy_timeout = 5000`；请求结束时关闭（Windows 上不关会锁住数据库文件，见 COMP-006）。<br>• **日志模式**：建库时设为 WAL。<br>• **写操作**：一律用 `BEGIN IMMEDIATE ... COMMIT`，出异常就 ROLLBACK；依赖数据库状态的校验（是否存在、是否下架、库存、重名、草稿）和写入放在同一个事务里。<br>• **上传**：先把封面文件写好，再开写事务；事务失败就删掉这个文件 | 测试：外键开关；20 个线程并发购买、并发同名注册（EXP-013）；请求结束后能删除数据库文件；事务失败后没有残留的封面文件 |
| MIG-RULE-013 | 文件路径一律用 pathlib 拼接，不写死任何平台的分隔符；全部测试在本机 Windows 和 GitHub Actions 的 windows-latest 上都要通过（MIG-DEC-011） | 静态检查代码里没有写死的路径分隔符；windows-latest 上的 CI |
| MIG-RULE-014 | 依赖版本由 pip-tools 生成并带哈希，安装时加 `--require-hashes`；锁文件要能在本机和 windows-latest 上安装（EXP-008） | 本机和 windows-latest 上 CI 的安装步骤 |
| MIG-RULE-015 | 种子数据里的占位值（价格、库存、简介、分类归属）在数据说明里标出来；规格和测试不得把它们当作旧系统的事实来断言。管理员初始口令只能来自环境变量 `BOOKSHOP_ADMIN_PASSWORD`，或者在终端里交互输入（不回显）；初始化命令不接受口令参数 | 评审规格和测试；初始化命令的测试（没给口令、给的是 123456、试图用命令行参数传口令时都拒绝） |
| MIG-RULE-016 | 页面用 Bootstrap 5 重做样式，但保留页面结构（导航、侧栏、表格列、表单字段、按钮）和中文文案；alert 提示保留旧系统的英文原文 | 页面测试：断言关键文案、表格列名、字段名和链接目标 |
| MIG-RULE-017 | 日志里不出现密码、SQL 参数、表单值和会话内容；出错时只记录异常类型和请求路径 | 测试：触发登录、注册、出错等场景，检查捕获到的日志 |
| MIG-RULE-018 | 输入长度和取值范围（按 Unicode 字符计，数据库里同时用 CHECK 约束）：<br>• **注册和改密码**：用户名 1～20 字，口令 1～64 字；<br>• **书籍**：书名 1～100 字，出版社 1～100 字，简介 1～4000 字；库存为 0～999999 的整数；售价 0～99999.99，最多两位小数；<br>• **查询参数**：书名搜索词最多 100 字，会员搜索词最多 20 字，分类筛选参数最多 20 字；<br>• **ID 参数**：`bid`、`uid` 必须是正整数。<br>表单字段不合规时按 MIG-RULE-020 提示；查询参数或 ID 参数不合规时返回 400 | 边界值测试：每个字段测最小值、最大值、超出 1、非数字、负数、三位小数、超大整数 |
| MIG-RULE-019 | 检查按以下顺序进行，先命中的为准：<br>(1) 路径没注册，返回 404，包括已移除的页面和 `jsp/ckeditor/`；<br>(2) 请求体超过 6 MiB，由 waitress 返回 413；<br>(3) `/jsp/*` 下没有有效会话，302 到登录页；<br>(4) 管理端 URL 而当前用户不是管理员，返回 403；<br>(5) `*.action` 的 opttype 缺失或未知，返回 400；<br>(6) 方法不对，返回 405；<br>(7) 读取请求体时超过 5 MiB，返回应用的 413；<br>(8) 修改类请求的 CSRF 令牌无效，返回 400；<br>(9) 查询参数或 ID 不合规，返回 400；<br>(10) 资源不存在、已下架或已停用，返回 404；<br>(11) 业务校验失败，按 MIG-RULE-020 提示。<br>`/BookShop/login.action` 和 `/BookShop/logout.action` 是公开的，跳过第 3、4 步 | 路由矩阵测试，覆盖各步之间的组合，例如：未登录访问已移除的页面得 404；会员用 GET 请求修改类的管理操作得 403；会员请求未知的管理 opttype 得 403；未登录、又没带令牌的 POST 到 `/jsp/*` 得 302 |
| MIG-RULE-020 | 业务校验失败时，按旧系统的方式返回 HTTP 200，响应体是 `alert` 脚本加 `window.location` 跳转。文案和跳转目标见下表的“新增提示文案” | 每个场景各一个测试，断言状态码、文案和跳转目标 |
| MIG-RULE-021 | 会话里只存 `uid`、会话版本号、登录时间、CSRF 令牌和三个列表页的查询条件；最坏情况下 Cookie 只有 1238 字节（EXP-011）。每个请求都从数据库读取当前用户，遇到下面任一情况就清空会话、按未登录处理：用户不存在、已停用、会话版本号和数据库里不一致、登录已超过 8 小时。空闲超时 30 分钟，每次请求续期。角色一律以数据库为准。退出、改密码、停用时递增 `user.session_version`；改密码后，当前会话换新的版本号，继续保持登录 | 测试：退出后重放旧 Cookie、改密码后用另一个会话访问、停用后用原会话访问、伪造超过 8 小时的登录时间，都应按未登录处理；再测量会话 Cookie 的大小 |
| MIG-RULE-022 | 运行环境：<br>• 一律用 `py -3.12` 创建的虚拟环境，执行 `.venv\Scripts\python.exe`，不依赖 PATH 上的 `python`（本机 PATH 上的是 3.11.3）；<br>• 启停脚本、初始化命令和 CI 都设置 `PYTHONUTF8=1`；<br>• CI 在 `master` 的 push 和 pull request 上触发 | 启停脚本和 workflow 评审；用错解释器版本启动时，启动检查应报错 |
| MIG-RULE-023 | `migration-plans/bookshop/experiments/` 里 EXP-002～EXP-013 的每一个 PASS 检查项，都要在 test-plan 里转成正式的 TEST；EXP-012 的检查项必须对真实的 waitress 运行 | 评审 test-plan，确认每个 EXP 检查项都有对应的 TEST |

### 新增提示文案

这些是旧系统没有的失败场景，都按 MIG-RULE-020 返回 HTTP 200 加 alert 脚本。

| 场景 | alert 文案 | 跳转目标 |
|---|---|---|
| 注册：用户名或口令长度不合规 | `please check user name or password!` | `register.jsp` |
| 注册：用户名已被占用（包括只差大小写的、已停用会员的，以及并发注册时撞名） | `please change uer name!`（沿用旧文案） | `register.jsp` |
| 修改密码：新口令长度不合规 | `check new password!`（沿用旧文案） | `changepwd.jsp` |
| 购买：库存为 0 | `out of stock!` | `book.action?opttype=bookDetail&bid=<bid>` |
| 新增书籍第一步：字段不合规或分类不存在 | `please check book info!` | `add.jsp` |
| 新增书籍第二步：没有第一步的草稿 | `please fill in book info first!` | `add.jsp` |
| 新增书籍第二步：没选文件，或者不是 PNG/JPEG | `please upload a png or jpg image!` | `addnext.jsp` |
| 修改书籍：字段不合规 | `please check book info!` | `admin.action?opttype=showBooks&bid=<bid>` |

## Acceptance Criteria

- gate 的 coverage 检查通过：每个不是 REMOVE 的 LEGACY 都有规格覆盖，每个规格都有对应的 TEST。
- 全部 pytest 测试通过，覆盖两个环境：本机 Windows 上的 Python 3.12.10，以及 GitHub Actions 的 windows-latest（同样用 Python 3.12.10）。
- 安全用例全部被拦下：SQL 注入、XSS、CSRF、越权访问管理端、路径穿越、伪装或超大的上传（包括在真实 waitress 上测）、停用会员登录、退出或改密码后重放旧会话。
- 路由矩阵按 MIG-RULE-019 的顺序给出确定的状态码；MIG-RULE-020 的每条提示文案都有测试。
- 并发测试通过：多线程同时购买不超卖，同时注册同名只有一个成功。
- 用演示数据初始化后，两端主流程都能从头走到尾：
  - 会员端：注册、登录、浏览、按名搜索、按分类筛选、详情、购买、我的订单、个人页、修改密码、退出；
  - 管理端：会员列表、搜索、停用；书籍列表、搜索、两步新增（含上传封面）、修改、下架；账目统计。
- 页面和 CSS 不引用任何外部 URL；仓库里没有真实密钥；依赖锁带哈希，能复现安装。
- 服务能在 Windows 本机用 waitress 单进程启动，默认只监听 127.0.0.1；启动、停止和初始化都有书面步骤，并且明确指定了解释器和 `PYTHONUTF8=1`。

## Decisions

| Decision ID | Question | Source | Options considered | Choice and rationale |
|---|---|---|---|---|
| MIG-DEC-001 | 目标技术栈 | ASKED | Python 3.12 + Flask 3.1 + Jinja2 + SQLite；Java 25 + Spring Boot 4 + Thymeleaf + MySQL 8.4；Node.js 24 + Express 5 + Nunjucks + SQLite | Python + Flask + SQLite。本机现成就有运行时，可以马上做实验；Jinja2 默认转义；SQLite 不用装服务 |
| MIG-DEC-002 | 迁移范围 | ASKED | 迁移全部在用功能；在用功能之外再补管理缺口；先迁会员端 | 迁移全部在用功能。残留页面、被注释的 Servlet 和 CKEditor 不迁；除安全修复需要的以外，不新增业务功能 |
| MIG-DEC-003 | 界面和 URL 的保真程度 | ASKED | 行为等价并保留 URL；行为等价、界面和 URL 都重做；像素级一致 | 行为等价并保留 URL：页面结构、中文文案和旧 URL 都保留，只有安全修复必须时才改。外观部分后来被 MIG-DEC-010 改为 Bootstrap 5 |
| MIG-DEC-004 | 部署环境 | ASKED | Windows 本机单进程；Linux Docker 容器 | Windows 本机单进程。选项说明里原有的“CI 同时在 Ubuntu 上跑”，已被 MIG-DEC-011 取消 |
| MIG-DEC-005 | GAP-001 怎么处理 | ASKED | 按代码重建 SQLite 表结构；暂停去找原库；把复原结构原样搬过来 | 按代码重建 SQLite 表结构，并补上约束；复原库只作为参考 |
| MIG-DEC-006 | GAP-002 怎么处理 | ASKED | 用 seed 作演示数据、不迁历史；只建分类和管理员；暂停去找原数据 | 用 seed 作演示数据，标明哪些是占位值；管理员口令从外部提供；不迁移历史数据 |
| MIG-DEC-007 | 删除有订单的书或会员时怎么处理 | ASKED | 有订单就禁止删除；软删除（下架、停用）；连同订单一起删除 | 软删除：删书改为下架，删会员改为停用，订单和账目都保留。没有订单的书和会员也一样走软删除 |
| MIG-DEC-008 | 疑似缺陷的处置表 | ASKED | 全部按推荐表执行；推荐表照用，但订单金额保留旧行为 | 全部按推荐表执行：安全问题全部修复，功能缺陷修复，LEGACY-061 去掉，订单改用成交价。表里原定的“升级到 Bootstrap 3.4.1 和 jQuery 3.x”被 MIG-DEC-010 取代 |
| MIG-DEC-009 | Python 3.12.10 之后的补丁只出源码，选哪个 Python 版本 | ASKED | 改用 Python 3.14；保留 3.12.10、接受风险 | 保留 3.12.10，接受运行时拿不到后续安全补丁的风险（COMP-001）；默认只监听 127.0.0.1 来缩小暴露面 |
| MIG-DEC-010 | Bootstrap 3 已停止维护且有 CVE，怎么处理 | ASKED | 用 3.4.1 并加规则规避；改用 Bootstrap 5 | 改用 Bootstrap 5.3.8 和 Bootstrap Icons 1.13.1，去掉 jQuery。外观和 class 名都会变，页面结构、文案和 URL 照旧（MIG-RULE-016） |
| MIG-DEC-011 | GitHub Actions 是否保留 Ubuntu 上的测试（部署始终只在 Windows 本机） | ASKED | 只用 windows-latest；Windows 和 Ubuntu 双平台 | 只用 windows-latest，让 CI 和部署环境一致。不要求 Linux 兼容；路径仍然用 pathlib 拼接 |
| MIG-DEC-012 | 签名 Cookie 会话在退出后被盗也仍然有效，怎么修 | ASKED | 加会话版本号和绝对有效期；把它改为接受风险 | 用户在评审后要求“全部修复”，采用前者：`user.session_version` 在退出、改密码、停用时递增，加 8 小时绝对有效期（MIG-RULE-021） |
| MIG-DEC-013 | 用户名和分类名的等值匹配是否区分大小写 | ASKED | 不区分 ASCII 大小写（NOCASE）；区分大小写（SQLite 默认的 BINARY） | 用户在评审后要求“全部修复”，采用前者：和 MySQL 常见的 `_ci` 默认排序规则一致，并防止出现 `Admin`、`admin` 这样的重名账号。代价是非 ASCII 字母仍然区分大小写（COMP-022） |

## Compatibility

### Version Matrix

| Concern | Source | Target | Evidence | Conclusion |
|---|---|---|---|---|
| 语言运行时 | Java 8 | CPython 3.12.10，状态为 security，支持到 2028-10，后续版本只出源码 | Python devguide；python.org 上 3.12.10 和 3.12.15 的发布页 | 可用，但有已接受的风险（COMP-001） |
| Web 框架 | Servlet 3.1 + `@WebServlet` | Flask 3.1.3、Werkzeug 3.1.9 | PyPI；EXP-001、EXP-002 | 能按旧 URL 逐条注册路由，能按 opttype 分派 |
| 模板 | JSP + JSTL，EL 不转义 | Jinja2 3.1.6，`.html` 模板自动转义 | EXP-005 | 等价，而且修好了 XSS |
| WSGI 服务器 | Tomcat | waitress 3.0.2（纯 Python，支持 Windows，要求 Python 3.9 及以上），`max_request_body_size` 设为 6 MiB | waitress 文档；EXP-009、EXP-012 | 可用 |
| 数据库 | MySQL（版本未知） | SQLite 3.49.1（本机）：STRICT 表、WAL、`BEGIN IMMEDIATE`、`COLLATE NOCASE` | SQLite 文档；EXP-003、EXP-013 | 可用；要注意的地方见 COMP-002 至 COMP-006、COMP-022、COMP-023 |
| 数据访问 | JDBC 拼接 SQL | 标准库 `sqlite3`，用 `?` 传参，`isolation_level=None` 后由应用显式控制事务，不用 ORM | EXP-003、EXP-013 | 可用 |
| 密码 | 明文 | Werkzeug `generate_password_hash`，默认 `scrypt:32768:8:1` | Werkzeug 文档；EXP-004 | 可用；本机单次约 120 ms，哈希串 162 个字符 |
| CSRF | 没有 | 应用内实现：令牌存在会话里，用 `hmac.compare_digest` 比较；不引入 Flask-WTF | Flask 本身不带 CSRF 防护 | 可用（COMP-010） |
| 会话 | Tomcat HttpSession，空闲 30 分钟 | Flask 签名 Cookie 会话，加上 `user.session_version` 做服务端吊销；空闲 30 分钟、绝对 8 小时过期 | Flask 配置文档；EXP-006、EXP-011 | 等价，并修好了吊销问题（COMP-007、COMP-008、COMP-017） |
| 前端 | Bootstrap 3.3.7 + jQuery 1.12.4 | Bootstrap 5.3.8（MIT）+ Bootstrap Icons 1.13.1（MIT），不用 jQuery | npm registry | 可用；模板要重写（COMP-015） |
| 编码 | UTF-8 过滤器；Java 源码 GBK | 全部 UTF-8；进程设置 `PYTHONUTF8=1` | EXP-002、EXP-009 | 等价（COMP-025） |
| 测试 | 没有 | pytest 9.1.1 + Flask 测试客户端；与服务器层有关的用例用真实 waitress 跑 | EXP-001、EXP-012 | 可用 |
| 依赖锁 | jar 在仓库外 | pip-tools 7.6.2 生成带哈希的锁，有 cp312 的 win_amd64 轮子 | EXP-008 | 可用 |
| CI | 没有 | GitHub Actions：只用 windows-latest，`setup-python` 固定为 3.12.10，在 `master` 上触发 | actions/python-versions 的 manifest；EXP-010 | 可用（COMP-016） |
| 许可证 | 内置 Bootstrap 3（MIT）、CKEditor | Flask 系列和 click：BSD-3-Clause；waitress：ZPL 2.1；Bootstrap 和 Bootstrap Icons：MIT；pytest：MIT | PyPI 和 npm 上的元数据 | 全部是宽松许可证；分发时附上许可证文本 |

### Findings

| Finding ID | Related IDs | Finding | Evidence | Impact | Mitigation | Status |
|---|---|---|---|---|---|---|
| COMP-001 | MIG-DEC-009 | 3.12 已进入 security 阶段，3.12.10 之后的版本（3.12.11～3.12.15）只出源码，没有 Windows 安装包 | python.org 上 3.12.10 和 3.12.15 的发布页 | 本机运行时缺少这几个版本的安全修复 | 默认只监听 127.0.0.1；在部署说明里写明这个风险；以后升级 Python 不在本次范围内 | ACCEPTED_RISK |
| COMP-002 | LEGACY-058、MIG-RULE-012 | SQLite 的外键默认关闭，每个连接都要单独开启 | SQLite foreignkeys 文档；EXP-003 | 忘记开启的话，外键约束形同虚设 | 统一的建连函数里执行 PRAGMA，并加测试 | RESOLVED |
| COMP-003 | LEGACY-026、LEGACY-028、MIG-RULE-018 | STRICT 表会把能无损转换的文本（如 `'5.00'`）收成整数 5，只拒绝像 `'abc'` 这样转不了的文本 | EXP-003 | 数据库挡不住格式不对但能转换的输入 | 校验放在应用层（MIG-RULE-018），数据库再用 CHECK 兜底 | RESOLVED |
| COMP-004 | LEGACY-016、LEGACY-065 | SQLite 的 LIKE 只对 ASCII 不区分大小写；原库的排序规则未知（如果是 `utf8mb4_0900_ai_ci`，还会忽略重音） | SQLite 表达式文档；EXP-003 | 带重音的拉丁字母、西里尔字母等的大小写匹配，可能和原库不同 | 在 LEGACY-016 中把目标行为定为“ASCII 不区分大小写”；书名以中文为主，影响很小 | RESOLVED |
| COMP-005 | LEGACY-016 | 改成参数化以后，用户输入的 `%` 和 `_` 仍然是通配符 | EXP-003 | 和旧系统行为一致 | 保留，不加 ESCAPE | RESOLVED |
| COMP-006 | LEGACY-058、MIG-RULE-012 | Windows 上没关闭的 SQLite 连接会锁住数据库文件，导致删不掉（原型第一次运行时报了 WinError 32） | EXP-003、EXP-013 | 备份、测试清理、重新初始化都会失败 | 请求结束时关闭连接；EXP-013 证实在 WAL 模式下关闭后能正常删除 | RESOLVED |
| COMP-007 | LEGACY-057、LEGACY-070、MIG-DEC-012 | Flask 默认的会话是签名 Cookie。登录后会签发新值，所以无法做会话固定。但服务端本身没法吊销某个 Cookie，而每次请求又会续期，被盗的 Cookie 可以一直用下去 | Flask 配置文档；EXP-006 | 如果不修，退出、改密码、停用之后，旧 Cookie 仍然有效 | `user.session_version` 在退出、改密码、停用时递增，每次请求都核对；另加 8 小时绝对有效期（MIG-RULE-021） | RESOLVED |
| COMP-008 | LEGACY-010、LEGACY-063 | Tomcat 默认空闲 30 分钟；Flask 的 permanent 会话在默认的 `SESSION_REFRESH_EACH_REQUEST` 下每次请求都会续期 | Flask 配置文档；EXP-006 | 没有绝对上限 | 设为 permanent，有效期 30 分钟；绝对上限按 MIG-RULE-021 由应用检查 | RESOLVED |
| COMP-009 | LEGACY-049 | scrypt 每次哈希约 120 ms | EXP-004 | 登录、注册、改密码各慢约 0.1 秒 | 可以接受；口令列用 TEXT 类型 | RESOLVED |
| COMP-010 | LEGACY-051 | Flask 本身没有 CSRF 防护 | Flask 文档 | 需要自己实现 | 应用内实现令牌，用测试覆盖（MIG-RULE-004） | RESOLVED |
| COMP-011 | LEGACY-054、LEGACY-027 | 超过 `MAX_CONTENT_LENGTH` 时 Werkzeug 直接返回 413；`secure_filename` 会删掉中文字符 | Flask 配置文档；Werkzeug 文档；EXP-007 | 中文文件名会变成空串 | 不用客户端文件名，由服务器生成。413 统一处理：5～6 MiB 之间用应用的错误页，超过 6 MiB 由 waitress 直接拒绝（MIG-RULE-009） | RESOLVED |
| COMP-012 | GAP-002 | 种子封面 `b6.jpg` 和 `b8.jpg` 的内容其实是 PNG | EXP-007、EXP-012 | 按扩展名设置 Content-Type 会设错 | 按文件头判断类型 | RESOLVED |
| COMP-013 | MIG-RULE-014 | 用 pip-tools 生成带哈希的锁，在本机全新的虚拟环境里用 `--require-hashes` 完整安装成功 | EXP-008 | windows-latest 上的安装还没跑过 | 由 CI 验证，这是 FEASIBILITY 的前提之一 | RESOLVED |
| COMP-014 | MIG-DEC-010、LEGACY-037 | Bootstrap 3 已于 2019-07-24 停止维护，3.4.1 仍受 CVE-2024-6484 和 CVE-2024-6485 影响（有争议）；Bootstrap 5.3 没有查到已知公告 | Bootstrap 3.4 文档；HeroDevs；Ubuntu USN-7556-1；GitLab 公告库 | 用 3.x 会留着已停止维护的依赖 | 改用 Bootstrap 5.3.8 | RESOLVED |
| COMP-015 | MIG-DEC-010、MIG-RULE-016 | Bootstrap 5 去掉了 jQuery 和 glyphicons，class 名、导航栏、轮播图、侧栏的写法都变了 | Bootstrap 5 文档；npm registry | 所有模板都要按 Bootstrap 5 重写 | 图标改用 Bootstrap Icons；保留结构和文案的页面测试（MIG-RULE-016） | RESOLVED |
| COMP-016 | MIG-RULE-013、MIG-DEC-011 | `setup-python` 有 3.12.10 的 win32 x64 构建；3.12.11 以后的 3.12 版本都没有 Windows 构建 | actions/python-versions 的 manifest；EXP-010 | CI 只能固定在 3.12.10，和本机一致 | windows-latest 固定用 3.12.10 | RESOLVED |
| COMP-017 | LEGACY-032、LEGACY-026、LEGACY-005 | 签名 Cookie 有大小上限。如果把新增书籍第一步的草稿也放进 Cookie，简介写到 1000 字时 Set-Cookie 就有 5742 字节，超过 4093，会被浏览器悄悄丢掉 | EXP-011 | CSRF 令牌和登录状态会跟着丢 | 草稿改存 `addbook_draft` 表；会话只存身份、版本、登录时间、令牌和长度有上限的查询条件；最坏情况实测 1238 字节 | RESOLVED |
| COMP-018 | LEGACY-063 | Werkzeug 按 UTF-8 解码查询参数，中文分类名“散文”能正确解码 | EXP-002 | 无 | 无需处理 | RESOLVED |
| COMP-019 | GAP-002 | 封面图是第三方出版物的封面，版权归原出版方 | `BookShop/WebContent/img/` | 迁移只是在同一个公开仓库里沿用这些图片，没有扩大分发范围 | 只用作演示数据，在数据说明里写明来源 | RESOLVED |
| COMP-020 | LEGACY-058、MIG-RULE-012 | SQLite 同一时刻只允许一个写入者，waitress 是多线程的 | SQLite 文档；EXP-013 | 并发写入时可能报 database is locked | WAL；busy timeout 5 秒；写事务尽量短。20 个线程并发实测没有出现锁错误 | RESOLVED |
| COMP-021 | LEGACY-054、MIG-RULE-009 | waitress 的 `max_request_body_size` 默认是 1 GiB，而且会先把请求体收完再交给应用，只靠 Flask 的上限挡不住大请求 | EXP-012 | 如果不改，任何能连上端口的客户端都能让服务器接收接近 1 GiB 的数据 | 设为 6 MiB。实测声明 100 MiB 的请求 1 ms 内就被拒绝，分块上传在 6 MiB 处被截断 | RESOLVED |
| COMP-022 | LEGACY-065、MIG-DEC-013 | SQLite 的 `COLLATE NOCASE` 只折叠 ASCII 字母，`Äb` 和 `äb` 被当作不同的用户名 | EXP-013 | 对非 ASCII 字母，和 MySQL 的 `_ci` 排序规则不同 | 接受；用户名以中文和 ASCII 为主 | RESOLVED |
| COMP-023 | LEGACY-040、LEGACY-058、MIG-RULE-012 | Python 3.12 `sqlite3` 默认的 `isolation_level` 是 `"DEFERRED"`，在 INSERT、UPDATE、DELETE 之前才隐式开事务。所以“先查后写”时，查询不在事务里，查和写之间有竞态；延迟事务升级成写事务时，还可能遇到 busy timeout 也解决不了的 SQLITE_BUSY。另外，3.12 新增的 `autocommit` 属性是文档推荐的事务控制方式 | Python 3.12 `sqlite3` 文档；EXP-013 | 会超卖，或出现随机的锁错误 | 用实测过的写法：`isolation_level=None`（不再隐式开事务），写操作一律显式 `BEGIN IMMEDIATE`，校验和写入放在同一个事务里。如果改用 `autocommit=True` 加显式 BEGIN，效果相同，但要重跑 EXP-013 | RESOLVED |
| COMP-024 | LEGACY-027、MIG-RULE-012 | 新增书籍要同时写封面文件和数据库，两者没法放进同一个事务 | 设计分析 | 可能留下孤立的文件，或者书指向不存在的文件 | 先写文件再开事务，事务失败就删除文件；只有进程在两步之间崩溃时，才可能留下孤立文件，这种文件不会被任何书引用，可以接受 | RESOLVED |
| COMP-025 | MIG-RULE-022 | 本机 PATH 上的 `python` 是 3.11.3（SQLite 3.40.1），3.12.10 只能用 `py -3.12` 调用；Windows 控制台默认不是 UTF-8 | 本机探测 | 如果用错解释器或编码，测试和运行结果会不一致，中文输出也可能出错 | 一律用虚拟环境里的解释器，设置 `PYTHONUTF8=1`（MIG-RULE-022） | RESOLVED |
| COMP-026 | LEGACY-047、MIG-RULE-011 | Bootstrap Icons 1.13.1 的 `font/bootstrap-icons.css` 在 `@font-face` 里用 `url("./fonts/bootstrap-icons.woff2?...")` 和 `.woff` 引用字体，只检查页面里的 `src` 和 `href` 查不到 | bootstrap-icons@1.13.1 发布包里的 `font/bootstrap-icons.css` | 字体缺失会再次让图标显示不出来，正是 LEGACY-047 那种缺陷 | 静态资源测试递归解析本地 CSS 里的 `url()`（MIG-RULE-011） | RESOLVED |
| COMP-027 | GAP-002、MIG-RULE-015 | 用命令行参数传管理员口令，口令会留在 shell 历史和进程列表里 | 设计分析 | 口令泄露 | 只允许用环境变量或在终端里交互输入 | RESOLVED |

### Experiments

实验脚本放在 `migration-plans/bookshop/experiments/`，运行方式见那里的 `README.md`。它们只是可行性原型，不是实现代码；按 MIG-RULE-023，实施时要改写成正式的 TEST。

| Experiment ID | Question | Method | Pass criteria | Result | Status |
|---|---|---|---|---|---|
| EXP-001 | 固定版本的依赖能否装到本机的 Python 3.12.10 上 | 新建虚拟环境，安装 Flask 3.1.3、Werkzeug 3.1.9、Jinja2 3.1.6、waitress 3.0.2、pytest 9.1.1、pip-tools 7.6.2 | 安装成功，导入后版本一致 | 安装成功；连带安装了 MarkupSafe 3.0.4、itsdangerous 2.2.0、click 8.5.0、blinker 1.9.0 | PASSED |
| EXP-002 | 旧 URL、opttype 分派、“查询后 302 到 JSP”的流程，以及中文 GET 参数 | `experiments/proto.py`：用 Flask 测试客户端请求 `/BookShop/jsp/book.action?opttype=queryBytag&tname=` 加百分号编码的“散文”，跟随跳转到 `buy.jsp`；再测缺少 opttype、未定义的 opttype、方法不对 | 302 到 `buy.jsp`，页面里有“清欢”；缺少或未定义的 opttype 返回 400；查询类 URL 用 POST 返回 405 | 5 项全部通过 | PASSED |
| EXP-003 | SQLite 的约束、事务、书目查询、LIKE、软删除和成交价 | `experiments/proto.py`，16 项断言：<br>• 外键：未开 PRAGMA 时不生效，开了以后拒绝不存在的分类；<br>• 约束：用户名唯一、role 只能是 1 或 2、STRICT 拒绝 `'abc'`、STRICT 会把 `'5.00'` 转成 5；<br>• 购买：库存 1 时第一次成功、第二次被拒且库存不为负，改价后成交价不变；<br>• 书目：同名书分开列出，排序为销量降序、同销量按 bid 升序；<br>• LIKE：ASCII 不区分大小写，能匹配中文子串，`%` 仍是通配符；<br>• 下架的书不出现，账目按成交价求和 | 16 项全部通过 | 第一次运行有 4 项失败：测试脚本以为 STRICT 会拒绝 `'5.00'`，结果它被转成 5 写了进去，多出的这一行又让后面 3 项计数断言出错。修正脚本后 16 项全部通过。由此发现了 COMP-003 和 COMP-006 | PASSED |
| EXP-004 | Werkzeug 默认的密码哈希 | `experiments/proto.py`：对 `generate_password_hash` 和 `check_password_hash` 计时并检查 | 方法为 `scrypt:32768:8:1`，正确和错误口令都判断对，单次低于 1000 ms | 3 项全部通过，单次约 120 ms | PASSED |
| EXP-005 | 模板自动转义 | `experiments/proto.py`：书名设为 `<script>alert(1)</script>`，渲染列表页 | 输出 `&lt;script&gt;`，没有原样的标签 | 通过 | PASSED |
| EXP-006 | 会话 Cookie 的属性、登录后换新值、退出 | `experiments/proto.py`：登录前先拿到一个会话 Cookie，再登录、检查 Set-Cookie、然后退出（原型里的退出路径只是示意，以 MIG-RULE-001 为准） | 登录后 Cookie 值变了；带 HttpOnly 和 SameSite=Lax；有 Expires；退出后会话里没有 uid | 4 项全部通过 | PASSED |
| EXP-007 | 上传限制和封面输出 | `experiments/proto.py`：测 6 MB 文件、伪装的 `.jpg`、大写 `.PNG`；请求 10 张种子封面；测路径穿越和不存在的文件 | 超限返回 413；伪装文件被拒；`.PNG` 被接受；10 张封面都返回 200，b6 和 b8 识别为 `image/png`；`../` 和不存在的文件返回 404 | 6 项全部通过 | PASSED |
| EXP-008 | 带哈希的锁能否复现安装 | 用 pip-compile 生成带哈希的锁（`experiments/requirements.txt`）；在全新的虚拟环境里用 `--require-hashes` 安装；用 `pip download --require-hashes` 分别下载 win_amd64 和 manylinux2014_x86_64 的 cp312、cp314 轮子 | Windows 上完整安装成功，轮子哈希能通过校验 | 都通过：锁文件含 8 个包；click 8.5.0 已不再依赖 colorama，锁是完整的。Linux 部分在 MIG-DEC-011 之后不再作要求 | PASSED |
| EXP-009 | waitress 能否在 Windows 上服务旧 URL | `experiments/serve_probe.py`：在本机用 waitress 3.0.2 起服务，用真实 HTTP 请求 `/BookShop/login.jsp` 和 `/BookShop/uploadServlet.do` | 前者返回 200、内容是 UTF-8 中文；后者返回 404 | 2 项全部通过 | PASSED |
| EXP-010 | CI 能否固定使用 Python 3.12.10 | 读取 actions/python-versions 的 versions-manifest.json | 有 win32 x64 的构建 | 有。3.12.11～3.12.15 都没有 Windows 构建，所以只能固定在 3.12.10 | PASSED |
| EXP-011 | 会话 Cookie 在最坏情况下会不会超过浏览器上限 | `experiments/cookie_size.py`：用 Flask 真实的会话序列化，填入随机汉字（几乎无法压缩），分别测目标设计和“草稿放进 Cookie”的对照组 | 目标设计的 Set-Cookie 不超过 3000 字节 | 目标设计最坏 1238 字节。对照组：简介 0、200、500、1000 字时分别为 2126、2863、3973、5742 字节，1000 字时已超过 4093 | PASSED |
| EXP-012 | 在真实的 waitress 上，请求体上限、413、302 和封面类型是否如预期 | `experiments/waitress_limits.py`：waitress 上限设 6 MiB、Flask 设 5 MiB；发 5.5 MiB 的 multipart、声明 100 MiB 只发 1 KiB、不带长度的分块上传；再请求 book.action 和 b6.jpg | 5.5 MiB 由应用返回 413；声明过大的请求不等收完就被 413 拒绝；分块上传超过 6 MiB 时返回 413；Location 是相对路径 `buy.jsp`；b6 为 `image/png` | 5 项全部通过：声明 100 MiB 的请求 1 ms 内被拒，分块上传在发出 6144 KiB 时被截断 | PASSED |
| EXP-013 | SQLite 写事务、并发、NOCASE 和 Windows 上的文件清理 | `experiments/sqlite_tx.py`：WAL、`isolation_level=None`、busy timeout 5 秒；20 个线程同时抢购库存 5 的书；10 个线程同时用大小写各异的同一用户名注册；测 NOCASE 的唯一约束和等值查询；最后删除库文件 | 恰好成交 5 单、没有锁错误、库存为 0；注册只成功 1 个；NOCASE 拒绝只差大小写的名字，等值查询不区分大小写，`Äb` 和 `äb` 被当作不同；所有文件都能删除 | 7 项全部通过 | PASSED |

### Sources

| Source | URL or repository evidence | Version | Accessed |
|---|---|---|---|
| Python 各版本状态 | https://devguide.python.org/versions/ | 3.12：security，支持到 2028-10 | 2026-10-10 |
| Python 3.12.10 发布页 | https://www.python.org/downloads/release/python-31210/ | 3.12.10 | 2026-10-10 |
| Python 3.12.15 发布页（只有源码） | https://www.python.org/downloads/release/python-31215/ | 3.12.15 | 2026-10-10 |
| SQLite 表达式（LIKE） | https://www.sqlite.org/lang_expr.html | 当前文档 | 2026-10-10 |
| SQLite 外键 | https://www.sqlite.org/foreignkeys.html | 当前文档 | 2026-10-10 |
| Werkzeug utils（密码哈希、secure_filename） | https://werkzeug.palletsprojects.com/en/stable/utils/ | 3.1.x | 2026-10-10 |
| Flask 配置 | https://flask.palletsprojects.com/en/stable/config/ | 3.1.x | 2026-10-10 |
| waitress 文档 | https://docs.pylonsproject.org/projects/waitress/en/stable/ | 3.0.2 | 2026-10-10 |
| Bootstrap 3.4 入门（停止维护声明） | https://getbootstrap.com/docs/3.4/getting-started/ | 3.4.1 | 2026-10-10 |
| Bootstrap 3.4.1 的 bower.json（jQuery 范围） | https://raw.githubusercontent.com/twbs/bootstrap/v3.4.1/bower.json | 3.4.1 | 2026-10-10 |
| CVE-2024-6484（HeroDevs） | https://herodevs.com/vulnerability-directory/cve-2024-6484 | Bootstrap 3.2.0～3.4.1 | 2026-10-10 |
| Ubuntu USN-7556-1 | https://ubuntu.com/security/notices/USN-7556-1 | libjs-bootstrap 3.4.1 | 2026-10-10 |
| GitLab 公告 CVE-2024-6531（已撤回） | https://advisories.gitlab.com/pkg/nuget/bootstrap/CVE-2024-6531/ | Bootstrap 4.x | 2026-10-10 |
| Python 3.12 `sqlite3` 文档（事务控制） | https://docs.python.org/3.12/library/sqlite3.html | 3.12 | 2026-10-10 |
| Bootstrap Icons 1.13.1 的字体 CSS | https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.css | 1.13.1 | 2026-10-10 |
| npm registry：bootstrap、bootstrap-icons | `npm view bootstrap`、`npm view bootstrap-icons` | 5.3.8 MIT；1.13.1 和 1.13.2，均为 MIT | 2026-10-10 |
| PyPI 版本查询 | `pip index versions`：flask、werkzeug、jinja2、waitress、pytest、pip-tools 等 | 见 Version Matrix | 2026-10-10 |
| actions/python-versions 的 manifest | https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json | 3.12.10～3.12.15 | 2026-10-10 |
| 可行性实验脚本 | `migration-plans/bookshop/experiments/` | EXP-002～EXP-013 | 2026-10-10 |
| 旧系统代码和基线 | `migration-plans/bookshop/legacy-inventory.md`、`migration-plans/bookshop/legacy-baseline.md`、`BookShop/src/`、`BookShop/WebContent/` | git `425edd4` | 2026-10-10 |
| 复原数据库 | `BookShop/db/seed.sql`、`migration-plans/bookshop/legacy-db-reconstruction.md` | 未提交的工作区版本 | 2026-10-10 |
| 迁移评审 | migration-review（strategy 模式）的 15 条意见，只报告在会话里，没有写成文件 | 2026-10-10 | 2026-10-10 |
