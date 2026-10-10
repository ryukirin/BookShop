# Spec Delta: bookshop-data

## Purpose

数据存储：SQLite 表结构与约束、连接与事务、初始化命令与演示数据、金额存储、输入长度与取值范围。

## ADDED Requirements

### Requirement: REQ-DATA-001 — 表结构与约束

数据库 SHALL 是数据目录下的单个 SQLite 文件，日志模式为 WAL，所有表都是 STRICT 表。表 SHALL 如下：

- `user(uid, uname, upwd, role, active, session_version)`；
- `tag(tid, tname)`；
- `book(bid, bname, publishers, stock, price_cents, tid, url, cont, on_sale)`；
- `orders(oid, bid, uid, unit_price_cents)`；
- `addbook_draft`：每个管理员一行。

约束 SHALL 包括：

- 主键；
- 外键：`book.tid` 指向 `tag`，`orders.bid` 指向 `book`，`orders.uid` 指向 `user`，草稿指向 `user`；
- 所有业务列都是 NOT NULL；
- `role IN (1, 2)`；
- `uname` 和 `tname` 用 `COLLATE NOCASE UNIQUE`；
- 库存和金额不能为负；
- MIG-RULE-018 的长度和取值范围，用 CHECK 落实。

系统 MUST NOT 创建 `customer` 表。

Traceability: `LEGACY-064`、`LEGACY-065`、`MIG-RULE-012`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 只差大小写的用户名

- **WHEN** 直接向 `user` 表插入 `Admin`，而库里已有 `admin`
- **THEN** 违反唯一约束，插入失败

#### Scenario: 引用不存在的分类

- **WHEN** 直接插入一本 `tid=99` 的书
- **THEN** 违反外键约束，插入失败

#### Scenario: 非数字的库存

- **WHEN** 直接把库存写为文本 `abc`
- **THEN** STRICT 表拒绝写入

### Requirement: REQ-DATA-002 — 连接与事务

系统 SHALL 为每个请求单独开一个连接，参数为 `isolation_level=None`，连接后执行 `PRAGMA foreign_keys = ON` 和 `PRAGMA busy_timeout = 5000`，请求结束时 MUST 关闭连接。写操作 SHALL 用 `BEGIN IMMEDIATE ... COMMIT`，异常时 ROLLBACK。依赖数据库状态的校验和写入 SHALL 放在同一个事务里。

Traceability: `LEGACY-058`、`MIG-RULE-012`; disposition: `BUG_NOT_PRESERVED`。

#### Scenario: 每个连接都开外键

- **WHEN** 测试在一个请求里查询 `PRAGMA foreign_keys`
- **THEN** 结果为 1

#### Scenario: 请求结束后能删除数据库

- **WHEN** 完成一组请求后，测试删除数据目录里的数据库文件和 `-wal`、`-shm` 文件
- **THEN** 都能删除，没有被锁住的文件

### Requirement: REQ-DATA-003 — 初始化命令与演示数据

系统 SHALL 提供初始化命令 `python -m bookshop_web init-db`，在数据目录下建库，并导入以下演示数据：

- 3 个分类：小说（tid 1）、散文（tid 2）、诗歌（tid 3）；
- 10 本书：bid 1～9 和 11，书名、出版社、价格、库存、简介、分类取自 `BookShop/db/seed.sql`；
- 封面：`b1.jpg`～`b9.jpg`、`b11.jpg` 按原名复制到 `covers/`；
- 管理员：`admin`，role 为 2。

口令规则：

- 管理员口令 SHALL 只从环境变量 `BOOKSHOP_ADMIN_PASSWORD` 读取，或者在终端里交互输入（不回显）；
- 初始化命令 MUST NOT 接受口令参数；
- 口令为空、等于 `123456` 或长度不在 1～64 字时，SHALL 拒绝初始化。

其他：

- 数据库已存在时，SHALL 拒绝覆盖并退出；
- 演示数据的说明 SHALL 写明价格、库存、简介和分类归属都是占位值；
- 不导入会员和订单。

Traceability: `LEGACY-066`、`MIG-RULE-015`; disposition: `CHANGE`。

#### Scenario: 初始化成功

- **WHEN** 在空的数据目录下设置合规的 `BOOKSHOP_ADMIN_PASSWORD` 并执行 `init-db`
- **THEN** 库里有 3 个分类、10 本书、1 个管理员，没有会员和订单；`covers/` 下有 10 个文件

#### Scenario: 口令是 123456

- **WHEN** `BOOKSHOP_ADMIN_PASSWORD=123456`，执行 `init-db`
- **THEN** 命令以非零退出码结束，没有创建数据库

#### Scenario: 已有数据库

- **WHEN** 数据目录里已有数据库，执行 `init-db`
- **THEN** 命令以非零退出码结束，原数据库保持不变

#### Scenario: 用参数传口令

- **WHEN** 执行 `init-db --password x`
- **THEN** 命令报“未知参数”，以非零退出码结束

### Requirement: REQ-DATA-004 — 金额存储与显示

售价和成交价 SHALL 以整数分存储，计算只用整数或 Decimal，页面上 SHALL 显示为两位小数（例如 `39.80`）。输入的售价 SHALL 按十进制解析，最多两位小数。

Traceability: `LEGACY-045`、`MIG-RULE-007`; disposition: `BUG_NOT_PRESERVED`。

#### Scenario: 售价的往返

- **WHEN** 管理员把售价设为 `0.1`，然后打开详情页
- **THEN** 库里存 10，页面显示 `0.10`

### Requirement: REQ-DATA-005 — 输入长度与取值范围

系统 SHALL 在应用层按 MIG-RULE-018 校验所有输入，数据库再用 CHECK 兜底。

- 表单字段不合规时，按各能力规定的 alert 提示；
- 查询参数或 ID 参数不合规时，返回 400；
- 任何输入都 MUST NOT 让数据库出现 NULL，也 MUST NOT 引起整数溢出或 500。

Traceability: `LEGACY-059`、`MIG-RULE-018`; disposition: `BUG_NOT_PRESERVED`。

#### Scenario: 超大整数

- **WHEN** 管理员把库存填为 `99999999999999999999`
- **THEN** 返回 `alert('please check book info!')`，而不是 500

#### Scenario: 超大 bid

- **WHEN** 会员请求 `bookDetail&bid=99999999999999999999`
- **THEN** 返回 400
