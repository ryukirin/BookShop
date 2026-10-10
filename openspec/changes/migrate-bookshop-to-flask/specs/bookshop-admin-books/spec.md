# Spec Delta: bookshop-admin-books

## Purpose

管理端书籍管理：书籍列表、搜索、两步新增（含封面上传）、修改、下架。

## ADDED Requirements

### Requirement: REQ-BOOK-001 — 书籍列表

`admin.action?opttype=queryAllbooks` SHALL 把查询条件保存到会话里，然后 302 到 `bookadmin.jsp`。`bookadmin.jsp` SHALL 列出所有在架的书，按 bid 分组、按 bid 升序。

- **表格列**：“书籍id”“书名”“简介”“出版社”“分类”“库存”“售价”“销量”“操作”；售价显示两位小数；
- **操作列**：“修改”是链接 `admin.action?opttype=showBooks&bid=<bid>`；“删除”是 POST 到 `admin.action?opttype=deleteBooks` 的表单按钮；
- **表格上方**：有“添加”链接，指向 `add.jsp`。

Traceability: `LEGACY-024`、`LEGACY-046`; disposition: `CHANGE`（LEGACY-024）、`BUG_NOT_PRESERVED`（LEGACY-046）。

#### Scenario: 列表内容

- **WHEN** 管理员打开书籍管理
- **THEN** 列出 10 本演示书，按 bid 升序（1～9、11），每行都有售价、销量和“修改”“删除”

### Requirement: REQ-BOOK-002 — 书籍搜索

`admin.action?opttype=queryBooks&bname=<词>` SHALL 用和 REQ-CATALOG-004 相同的 LIKE 规则匹配，然后 302 到 `bookadmin.jsp`，返回内容同 REQ-BOOK-001。搜索词超过 100 字时 SHALL 返回 400。

Traceability: `LEGACY-025`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 搜索林清玄的书

- **WHEN** 管理员搜索“玄”
- **THEN** 结果只有书 8“玄想”

### Requirement: REQ-BOOK-003 — 新增书籍第一步

`add.jsp` SHALL 提供以下字段：书名 `bname`、出版社 `publishers`、分类 `tid`（下拉框，只列已有分类）、简介 `cont`、库存 `stock`、售价 `price`。表单 POST 到 `admin.action?opttype=addBooks`，带 CSRF 令牌。

系统 SHALL 按 MIG-RULE-018 校验：书名、出版社各 1～100 字，简介 1～4000 字，库存为 0～999999 的整数，售价为 0～99999.99 且最多两位小数，分类必须存在。

- **校验不通过**：返回 `alert('please check book info!')` 并跳回 `add.jsp`；
- **校验通过**：把字段保存为当前管理员的服务端草稿（每个管理员一份，新的覆盖旧的），然后 302 到 `addnext.jsp`。跳转 URL MUST NOT 带字段值，会话 MUST NOT 保存这些字段。

Traceability: `LEGACY-026`、`LEGACY-055`、`LEGACY-059`、`LEGACY-071`、`MIG-RULE-018`、`MIG-RULE-020`; disposition: `CHANGE`（LEGACY-026、LEGACY-071）、`BUG_NOT_PRESERVED`（LEGACY-055、LEGACY-059）。

#### Scenario: 第一步通过

- **WHEN** 管理员填写合规的字段，简介 4000 字，分类选“小说”
- **THEN** 302 到 `addnext.jsp`，`Location` 里没有查询参数；会话 Cookie 不超过 3000 字节

#### Scenario: 售价有三位小数

- **WHEN** 管理员把售价填为 `25.555`
- **THEN** 返回 `alert('please check book info!')`，跳回 `add.jsp`，没有保存草稿

#### Scenario: 伪造不存在的分类

- **WHEN** 管理员绕过下拉框提交 `tid=99`
- **THEN** 返回 `alert('please check book info!')`

### Requirement: REQ-BOOK-004 — 新增书籍第二步（上传封面）

`addnext.jsp` SHALL 提供文件字段 `file` 和客户端预览，表单以 multipart 方式 POST 到 `admin.action?opttype=addBooksimg`，带 CSRF 令牌。系统 SHALL 按下面的规则处理：

- **没有第一步的草稿**：返回 `alert('please fill in book info first!')` 并跳到 `add.jsp`；
- **没选文件，或文件头不是 PNG/JPEG**（扩展名不区分大小写，不看文件名）：返回 `alert('please upload a png or jpg image!')` 并跳回 `addnext.jsp`；
- **请求体超限**：返回 413（REQ-PLATFORM-014）；
- **校验通过**：
  1. 用服务器生成的文件名（32 位十六进制加 `.png` 或 `.jpg`）把文件写进数据目录的 `covers/`；
  2. 在同一个写事务里插入书籍（在架，`url` 为该文件名）并删除草稿，然后 302 到 `admin.action?opttype=queryAllbooks`；
  3. 事务失败时，删除刚写入的文件。

客户端提供的文件名 MUST NOT 用于存储。

Traceability: `LEGACY-027`、`LEGACY-054`、`LEGACY-072`、`MIG-RULE-009`、`MIG-RULE-012`、`MIG-RULE-020`; disposition: `CHANGE`（LEGACY-027）、`SECURITY_FIX_REQUIRED`（LEGACY-054）、`BUG_NOT_PRESERVED`（LEGACY-072）。

#### Scenario: 上传 PNG 完成新增

- **WHEN** 管理员完成第一步后，上传名为 `封面.PNG` 的真实 PNG
- **THEN** 302 到书籍管理；新书在列表里；`covers/` 下多了一个 32 位十六进制命名的 `.png` 文件；草稿被删除

#### Scenario: 伪装成 jpg 的非图片

- **WHEN** 管理员上传内容以 `GIF89a` 开头、名为 `a.jpg` 的文件
- **THEN** 返回 `alert('please upload a png or jpg image!')`，没有新书，`covers/` 下没有新文件

#### Scenario: 没有草稿

- **WHEN** 管理员没做第一步，直接提交第二步
- **THEN** 返回 `alert('please fill in book info first!')`

#### Scenario: 事务失败时清理文件

- **WHEN** 文件已写入，但插入书籍的事务失败
- **THEN** 刚写入的文件被删除，页面返回 500 错误页

### Requirement: REQ-BOOK-005 — 修改书籍

`admin.action?opttype=showBooks&bid=<bid>` SHALL 把 bid 存进会话，然后 302 到 `editbook.jsp`（跳转地址不带查询参数）。表单 SHALL 显示只读的书籍id，以及可编辑的出版社、库存、售价；书名、简介、分类和封面不能改。表单 POST 到 `admin.action?opttype=editBooks`，带 CSRF 令牌。

- **校验**：规则同 REQ-BOOK-003 中的对应字段；不通过时返回 `alert('please check book info!')` 并跳到 `admin.action?opttype=showBooks&bid=<bid>`；
- **保存**：三项修改在同一个写事务里完成，然后 302 到 `admin.action?opttype=queryAllbooks`；
- **异常**：书不存在或已下架时返回 404，bid 不是正整数时返回 400。

Traceability: `LEGACY-028`、`MIG-RULE-012`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 修改售价

- **WHEN** 管理员把书 9 的售价改为 `45.00`
- **THEN** 302 到书籍管理，书 9 显示 45.00；已有订单的成交价不变

#### Scenario: 库存为负数

- **WHEN** 管理员把库存填为 `-1`
- **THEN** 返回 `alert('please check book info!')`，书 9 不变

### Requirement: REQ-BOOK-006 — 下架书籍

`POST admin.action?opttype=deleteBooks` SHALL 带 `bid` 和有效 CSRF 令牌。

- **成功**：把书设为下架，302 到 `admin.action?opttype=queryAllbooks`；
- **下架之后**：这本书 SHALL 从所有书目、搜索和详情中消失，也不能再购买；订单、账目和封面文件 SHALL 保留；
- **异常**：书不存在或已下架时返回 404。

Traceability: `LEGACY-029`、`LEGACY-043`、`MIG-RULE-008`; disposition: `CHANGE`（LEGACY-029）、`BUG_NOT_PRESERVED`（LEGACY-043）。

#### Scenario: 下架卖过的书

- **WHEN** 书 1 有 1 个订单，管理员把它下架
- **THEN** 书目和书籍管理里都没有书 1；账目统计和会员的“我的订单”里仍有这笔订单；`covers/b1.jpg` 仍在

#### Scenario: 重复下架

- **WHEN** 管理员再次下架书 1
- **THEN** 返回 404
