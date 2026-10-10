# Spec Delta: bookshop-platform

## Purpose

新书店的运行平台：URL 前缀和首页、字符编码、`*.action?opttype=` 分派、请求检查顺序、错误页与提示机制、CSRF、输出转义、SQL 参数化、静态资源、页面结构、配置与启动、日志、请求体上限。

## ADDED Requirements

### Requirement: REQ-PLATFORM-001 — 上下文路径与首页

系统 SHALL 把所有页面挂在 `/BookShop` 前缀下。`GET /BookShop/` 和 `GET /BookShop/index.jsp` SHALL 返回首页，首页内容包括：导航栏“网上书店 / 主页 / 购买 / 个人”，其中“购买”指向 `jsp/book.action?opttype=queryAllbook`，“个人”指向 `jsp/my.action?opttype=initMypage`；两张轮播图 `img/1.jpg`（“最新上架”）和 `img/2.jpg`（“销量最高”），按钮都指向购买页。登录后，导航栏 SHALL 多一个“退出”按钮（REQ-ACCOUNT-005）。

Traceability: `LEGACY-001`、`LEGACY-006`、`MIG-RULE-001`、`MIG-RULE-016`; disposition: `PRESERVE`（LEGACY-001）、`CHANGE`（LEGACY-006）。

#### Scenario: 打开站点根路径

- **WHEN** 未登录用户请求 `GET /BookShop/`
- **THEN** 返回 200，页面里有“网上书店”“最新上架”“销量最高”，以及指向 `jsp/book.action?opttype=queryAllbook` 的链接；没有“退出”按钮

#### Scenario: 登录后打开首页

- **WHEN** 已登录的会员请求 `GET /BookShop/index.jsp`
- **THEN** 导航栏里有“退出”按钮，它是一个 POST 到 `/BookShop/logout.action`、带 CSRF 令牌的表单

### Requirement: REQ-PLATFORM-002 — UTF-8 编码

系统 SHALL 按 UTF-8 解码请求体和查询参数，所有 HTML 响应 SHALL 声明并使用 `charset=utf-8`。

Traceability: `LEGACY-002`、`LEGACY-063`; disposition: `PRESERVE`（LEGACY-002）、`CHANGE`（LEGACY-063）。

#### Scenario: 中文查询参数

- **WHEN** 已登录用户请求 `GET /BookShop/jsp/book.action?opttype=queryBytag&tname=%E6%95%A3%E6%96%87`，然后跟随跳转
- **THEN** 系统把参数解码为“散文”，购买页列出“散文”分类下的书，响应头 `Content-Type` 含 `charset=utf-8`

### Requirement: REQ-PLATFORM-003 — opttype 分派与方法限制

`/BookShop/login.action`、`/BookShop/jsp/book.action`、`/BookShop/jsp/my.action`、`/BookShop/jsp/admin.action` SHALL 按 `opttype` 参数分派。查询类 opttype SHALL 只接受 GET，修改类 opttype SHALL 只接受 POST，方法不对时 SHALL 返回 405。`opttype` 缺失或不在该 URL 的分派表里时，SHALL 返回 400 错误页。分派表如下：

- `login.action`：`addusers`、`checkUsers`，都是 POST；
- `book.action`：`queryAllbook`、`queryByname`、`queryBytag`、`bookDetail` 是 GET，`buybook` 是 POST；
- `my.action`：`initMypage`、`queryMyorder` 是 GET，`updatePwd` 是 POST；
- `admin.action`：`queryAllcustomers`、`queryCustomers`、`queryAllbooks`、`queryBooks`、`showBooks`、`showAllmoney` 是 GET，`deleteCustomers`、`addBooks`、`addBooksimg`、`editBooks`、`deleteBooks` 是 POST。

Traceability: `LEGACY-005`、`LEGACY-039`、`MIG-RULE-001`; disposition: `CHANGE`（LEGACY-005）、`BUG_NOT_PRESERVED`（LEGACY-039）。

#### Scenario: 缺少 opttype

- **WHEN** 已登录用户请求 `GET /BookShop/jsp/book.action`
- **THEN** 返回 400 错误页，而不是旧系统的 500

#### Scenario: 未定义的 opttype

- **WHEN** 已登录用户请求 `GET /BookShop/jsp/book.action?opttype=nope`
- **THEN** 返回 400 错误页，而不是旧系统的空 200

#### Scenario: 查询类 opttype 用了 POST

- **WHEN** 已登录用户用 POST（带有效 CSRF 令牌）请求 `/BookShop/jsp/book.action?opttype=queryAllbook`
- **THEN** 返回 405

#### Scenario: 修改类 opttype 用了 GET

- **WHEN** 已登录的会员请求 `GET /BookShop/jsp/book.action?opttype=buybook&bid=1`
- **THEN** 返回 405，库存和订单都不变

### Requirement: REQ-PLATFORM-004 — 请求检查顺序

系统 SHALL 按 MIG-RULE-019 的顺序检查每个请求，先命中的为准：路径未注册 404 → 请求体超过 6 MiB 时 413（waitress）→ `/jsp/*` 没有有效会话时 302 到 `/BookShop/login.jsp` → 管理端 URL 而当前用户不是管理员时 403 → opttype 缺失或未知 400 → 方法不对 405 → 请求体超过 5 MiB 时 413（应用）→ CSRF 令牌无效 400 → 查询参数或 ID 不合规 400 → 资源不存在、已下架或已停用 404 → 业务校验失败时返回 alert 提示。`/BookShop/login.action` 和 `/BookShop/logout.action` SHALL 跳过“有效会话”和“管理员”两步检查。

Traceability: `LEGACY-005`、`LEGACY-039`、`MIG-RULE-019`; disposition: `CHANGE`。

#### Scenario: 未登录访问已移除的页面

- **WHEN** 未登录用户请求 `GET /BookShop/jsp/upload.jsp`
- **THEN** 返回 404，而不是 302 到登录页

#### Scenario: 会员用 GET 请求修改类的管理操作

- **WHEN** 已登录的会员请求 `GET /BookShop/jsp/admin.action?opttype=deleteBooks&bid=1`
- **THEN** 返回 403

#### Scenario: 会员请求未知的管理 opttype

- **WHEN** 已登录的会员请求 `GET /BookShop/jsp/admin.action?opttype=nope`
- **THEN** 返回 403

#### Scenario: 未登录又不带令牌的 POST

- **WHEN** 未登录用户不带 CSRF 令牌 POST 到 `/BookShop/jsp/book.action?opttype=buybook&bid=1`
- **THEN** 返回 302，跳到 `/BookShop/login.jsp`

### Requirement: REQ-PLATFORM-005 — 错误页与数据库异常

系统 SHALL 用应用自己的错误页呈现 400、403、404、405、413、500，页面里要有状态码和简短的中文说明。超过 6 MiB 的请求由 waitress 直接返回 413 纯文本，是唯一的例外。数据库访问出错时，系统 SHALL 记录日志并返回 500 错误页，MUST NOT 悄悄显示空列表或空白页。

Traceability: `LEGACY-033`、`LEGACY-034`; disposition: `CHANGE`。

#### Scenario: 数据库不可用时打开书目

- **WHEN** 数据库文件不可读，已登录用户请求书目
- **THEN** 返回 500 错误页，日志里有一条带异常类型和请求路径的错误记录

#### Scenario: 不存在的路径

- **WHEN** 任何人请求 `GET /BookShop/nope.jsp`
- **THEN** 返回 404 错误页，页面里有“404”

### Requirement: REQ-PLATFORM-006 — alert 提示机制

业务校验失败时，系统 SHALL 按旧系统的方式返回 HTTP 200，响应体形如 `<script>alert('<文案>'); window.location='<目标>' </script>`。旧系统已有的英文文案 MUST 原样保留：`please change uer name!`、`please check password!`、`fail,try again!`、`username or password error!`、`success!`、`password error!`、`check new password!`。新增场景的文案按 MIG-RULE-020，具体见各能力的需求。

Traceability: `LEGACY-034`、`MIG-RULE-020`; disposition: `CHANGE`。

#### Scenario: 旧文案原样保留

- **WHEN** 用户用错误的口令登录
- **THEN** 返回 200，响应体含 `alert('username or password error!')` 和 `window.location='login.jsp'`

### Requirement: REQ-PLATFORM-007 — CSRF 令牌

每个修改数据的请求（包括登录、注册、退出和所有 POST 的 opttype）MUST 带上与会话中一致的 CSRF 令牌，表单字段名为 `csrf_token`，比较用常量时间。令牌缺失、不一致，或者请求没有会话时，系统 SHALL 返回 400，MUST NOT 修改任何数据。所有表单页面 SHALL 渲染当前会话的令牌。

Traceability: `LEGACY-051`、`LEGACY-070`、`MIG-RULE-004`; disposition: `SECURITY_FIX_REQUIRED`。

#### Scenario: 令牌错误

- **WHEN** 已登录的管理员 POST 到 `/BookShop/jsp/admin.action?opttype=deleteBooks`，`bid=1`，但 `csrf_token` 是错的
- **THEN** 返回 400，书 1 仍然在架

#### Scenario: 不先打开登录页就直接登录

- **WHEN** 一个没有会话的客户端直接 POST 到 `/BookShop/login.action?opttype=checkUsers`，带着正确的用户名和口令
- **THEN** 返回 400，没有建立登录会话

### Requirement: REQ-PLATFORM-008 — 输出转义

所有模板 SHALL 开启自动转义。来自数据库或请求的数据，包括书名、简介、出版社、分类名、会员名和封面文件名，MUST 以转义后的形式输出；模板 MUST NOT 对这些数据使用 `safe` 过滤器或 `Markup`。

Traceability: `LEGACY-052`、`MIG-RULE-005`; disposition: `SECURITY_FIX_REQUIRED`。

#### Scenario: 书名里含脚本

- **WHEN** 库里有一本书名为 `<script>alert(1)</script>` 的在架书，会员打开购买页
- **THEN** 页面里出现 `&lt;script&gt;alert(1)&lt;/script&gt;`，没有原样的 `<script>alert(1)</script>`

#### Scenario: 会员名里含脚本

- **WHEN** 一个用户名为 `<b>x</b>` 的会员已注册，管理员打开会员列表
- **THEN** 页面里出现 `&lt;b&gt;x&lt;/b&gt;`

### Requirement: REQ-PLATFORM-009 — SQL 参数化

所有 SQL MUST 用 `?` 占位符传参，MUST NOT 用字符串拼接、格式化或 f-string 把请求数据拼进 SQL。注入载荷 SHALL 只被当作普通字面值。

Traceability: `LEGACY-048`、`MIG-RULE-002`; disposition: `SECURITY_FIX_REQUIRED`。

#### Scenario: 登录名里含注入载荷

- **WHEN** 用户用 `' OR '1'='1` 作为用户名、任意口令登录
- **THEN** 返回 `alert('username or password error!')`，没有建立登录会话

#### Scenario: 搜索词里含注入载荷

- **WHEN** 会员用 `x' UNION SELECT upwd FROM user --` 搜索书名
- **THEN** 302 到购买页，购买页列表为空，页面里没有任何口令哈希

### Requirement: REQ-PLATFORM-010 — 静态资源本地化

系统 SHALL 从本地提供 Bootstrap 5.3.8 和 Bootstrap Icons 1.13.1（附许可证），以及 `css/` 下的自有样式和 `img/` 下的轮播图、默认头像。页面 MUST NOT 引用任何外部 URL，也 MUST NOT 加载 jQuery。页面里 `src`、`href` 引用的每个本地资源，以及本地 CSS 里 `url()` 引用的每个资源（包括字体），SHALL 返回 200。

Traceability: `LEGACY-037`、`LEGACY-047`、`MIG-RULE-011`; disposition: `CHANGE`（LEGACY-037）、`BUG_NOT_PRESERVED`（LEGACY-047）。

#### Scenario: 页面引用的资源都能取到

- **WHEN** 测试依次渲染所有页面，收集 `src`、`href`，再递归解析本地 CSS 中的 `url()`
- **THEN** 所有引用都是本站路径，每个都返回 200；`bootstrap-icons.woff2` 也在其中

### Requirement: REQ-PLATFORM-011 — 页面结构与文案

所有页面 SHALL 用 Bootstrap 5 重做样式，但保留旧页面的结构和中文文案：导航栏项、侧栏项、表格列名、表单字段名和占位提示、按钮文字、链接目标。各页面的品牌名、标题和侧栏项 SHALL 与旧页面一致。具体包括：会员端品牌“网上书店”链接首页；管理端品牌“网上书店管理站”没有链接；`add.jsp`、`addnext.jsp`、`editbook.jsp` 导航栏里没有绑定动作的搜索框保留。模板 MUST NOT 含残缺的标签或任何本机路径。

Traceability: `LEGACY-035`、`LEGACY-062`、`MIG-RULE-016`; disposition: `PRESERVE`（LEGACY-035）、`BUG_NOT_PRESERVED`（LEGACY-062）。

#### Scenario: 书籍编辑页的侧栏

- **WHEN** 管理员打开 `editbook.jsp`
- **THEN** 侧栏依次是“会员管理”“书籍管理”“账目统计”三个链接，HTML 能被严格解析，没有残缺标签

#### Scenario: 管理端品牌名

- **WHEN** 管理员打开 `admin.jsp`
- **THEN** 导航栏品牌文字是“网上书店管理站”，它不是链接

### Requirement: REQ-PLATFORM-012 — 配置、启动与运行环境

系统 SHALL 从 `BOOKSHOP_` 开头的环境变量读取配置，包括 `BOOKSHOP_DATA_DIR`、`BOOKSHOP_SECRET_KEY`、`BOOKSHOP_HOST`（默认 `127.0.0.1`）和 `BOOKSHOP_PORT`（默认 `8080`）。以下情况系统 SHALL 拒绝启动并给出说明：

- 数据目录缺失或不可写；
- 密钥缺失、短于 32 字节，或者用的是仓库里的示例值；
- 解释器不是 Python 3.12.10。

服务 SHALL 由 waitress 单进程提供，`max_request_body_size` 为 6 MiB。启停脚本 SHALL 使用虚拟环境里的解释器，并设置 `PYTHONUTF8=1`。路径一律用 pathlib 拼接。仓库 MUST NOT 含真实密钥或本机路径。

Traceability: `LEGACY-056`、`LEGACY-060`、`MIG-RULE-010`、`MIG-RULE-013`、`MIG-RULE-022`; disposition: `SECURITY_FIX_REQUIRED`（LEGACY-056）、`BUG_NOT_PRESERVED`（LEGACY-060）。

#### Scenario: 密钥是示例值

- **WHEN** `BOOKSHOP_SECRET_KEY` 等于示例配置里的占位值，此时启动服务
- **THEN** 进程以非零退出码结束，输出说明“密钥不合规”，没有监听任何端口

#### Scenario: 默认监听地址

- **WHEN** 没有设置 `BOOKSHOP_HOST`，按说明启动服务
- **THEN** 服务只监听 `127.0.0.1:8080`

### Requirement: REQ-PLATFORM-013 — 日志

系统 SHALL 用 Python logging 记录运行日志，写到标准输出和数据目录下的日志文件。日志 MUST NOT 含密码、SQL 参数、表单值和会话内容。出错时 SHALL 只记录异常类型、请求方法和路径。

Traceability: `LEGACY-038`、`MIG-RULE-017`; disposition: `CHANGE`。

#### Scenario: 登录和注册不泄露口令

- **WHEN** 用户注册并登录，口令是 `Secret#123`，然后触发一次 500
- **THEN** 捕获到的全部日志里都没有 `Secret#123`，也没有任何 SQL 语句文本

### Requirement: REQ-PLATFORM-014 — 请求体上限

应用层 SHALL 把请求体限制在 5 MiB，超过时返回应用的 413 错误页。waitress 层 SHALL 把请求体限制在 6 MiB，超过时直接返回 413，MUST NOT 先收完请求体。

Traceability: `LEGACY-054`、`MIG-RULE-009`; disposition: `SECURITY_FIX_REQUIRED`。

#### Scenario: 5.5 MiB 的上传

- **WHEN** 管理员通过真实的 waitress 上传 5.5 MiB 的文件
- **THEN** 返回 413，响应体是应用的错误页，没有新增书籍

#### Scenario: 声明超大的请求

- **WHEN** 客户端向真实的 waitress 发送 `Content-Length: 104857600` 的 POST，只发 1 KiB 就停下
- **THEN** waitress 在请求体收完之前就返回 413

### Requirement: REQ-PLATFORM-015 — 未迁移的路径

旧系统里的残留页面和失效映射 SHALL 返回 404，包括 `jsp/download.jsp`、`jsp/upload.jsp`、`jsp/wirte.jsp`、`jsp/useredit.jsp`、`jsp/ckeditor/` 下的任何路径、`/BookShop/uploadServlet.do` 和 `/BookShop/downloadServlet.do`。这些行为按策略去掉（LEGACY-036、LEGACY-061、LEGACY-067、LEGACY-068），本需求只规定它们的 URL 在目标系统中的响应。

Traceability: `MIG-RULE-019`; disposition: `CHANGE`（对应的 LEGACY 条目处置为 REMOVE）。

#### Scenario: 旧的上传映射

- **WHEN** 任何人请求 `GET /BookShop/uploadServlet.do`
- **THEN** 返回 404
