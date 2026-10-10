# Spec Delta: bookshop-catalogue

## Purpose

会员端书目：书目列表、购买页、按分类筛选、按书名搜索、书籍详情、直接打开列表页，以及封面输出。

## ADDED Requirements

### Requirement: REQ-CATALOG-001 — 书目列表

`book.action?opttype=queryAllbook` SHALL 把查询条件保存到会话里，然后 302 到 `buy.jsp`。`buy.jsp` SHALL 按保存的条件渲染：

- **分类侧栏**：所有分类名，按 tid 升序；
- **书目列表**：所有在架的书，按 bid 分组，同名同分类的书分开列出；销量等于该书的订单数；按销量降序，销量相同时按 bid 升序；
- 下架的书和没有对应分类的书都不出现。

Traceability: `LEGACY-013`、`LEGACY-032`、`LEGACY-046`; disposition: `CHANGE`（LEGACY-013、LEGACY-032）、`BUG_NOT_PRESERVED`（LEGACY-046）。

#### Scenario: 按销量排序

- **WHEN** 在架书 9 有 2 个订单、书 1 有 1 个订单，其余没有订单，会员打开书目
- **THEN** `buy.jsp` 依次列出书 9、书 1，其余按 bid 升序排在后面

#### Scenario: 同名同分类的书分开列出

- **WHEN** 库里有两本在架的“清欢”，同属“散文”，bid 不同
- **THEN** 列表中出现两个“清欢”条目，各自链接到自己的 bid

#### Scenario: 下架的书不出现

- **WHEN** 书 2 已下架
- **THEN** 书目、筛选和搜索结果里都没有书 2

### Requirement: REQ-CATALOG-002 — 购买页内容

`buy.jsp` SHALL 为每本书显示封面（`showpic.jsp?img=<url>`）、书名、简介和“查看详情”链接（`book.action?opttype=bookDetail&bid=<bid>`），SHALL NOT 显示价格。右侧栏 SHALL 列出所有分类，每项链接到 `book.action?opttype=queryBytag&tname=<分类名>`。导航栏的搜索表单 SHALL 以 GET 提交 `opttype=queryByname` 和 `bname`。

Traceability: `LEGACY-014`; disposition: `PRESERVE`。

#### Scenario: 购买页元素

- **WHEN** 会员打开书目
- **THEN** 每个条目都有 `showpic.jsp?img=` 图片、书名、简介和“查看详情”链接；侧栏有“小说”“散文”“诗歌”；搜索表单的 method 是 GET

### Requirement: REQ-CATALOG-003 — 按分类筛选

`book.action?opttype=queryBytag&tname=<分类名>` SHALL 用按 ASCII 不区分大小写的等值比较筛选分类，返回内容和排序同 REQ-CATALOG-001。`tname` 超过 20 字时 SHALL 返回 400；分类不存在时 SHALL 显示空列表。

Traceability: `LEGACY-015`、`LEGACY-065`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 筛选散文

- **WHEN** 会员筛选“散文”
- **THEN** 列表只有书 6、7、8

#### Scenario: 分类参数过长

- **WHEN** 会员筛选一个 21 字的分类名
- **THEN** 返回 400

### Requirement: REQ-CATALOG-004 — 按书名搜索

`book.action?opttype=queryByname&bname=<词>` SHALL 用 `LIKE '%<词>%'` 匹配书名，返回内容和排序同 REQ-CATALOG-001。

- 大小写：对 ASCII 字母不区分大小写，对其他字符区分；
- 通配符：输入中的 `%`、`_` 仍按通配符处理；
- 空词：返回全部在架书；
- 长度：搜索词超过 100 字时返回 400。

Traceability: `LEGACY-016`、`LEGACY-065`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 中文子串

- **WHEN** 会员搜索“六便士”
- **THEN** 列表只有书 9

#### Scenario: ASCII 大小写

- **WHEN** 库里有在架书“Python入门”，会员搜索 `python`
- **THEN** 这本书在结果里

#### Scenario: 通配符

- **WHEN** 会员搜索 `%`
- **THEN** 返回全部在架书

### Requirement: REQ-CATALOG-005 — 书籍详情

`book.action?opttype=bookDetail&bid=<bid>` SHALL 把 bid 存进会话，然后 302 到 `bookdetails.jsp`（跳转地址不带查询参数）。该页面 SHALL 显示封面，以及“书名”“出版商”“价格”“库存”“简介”“销量”，还有一个“立即购买”按钮。按钮是 POST 到 `book.action?opttype=buybook` 的表单，带 `bid` 和 CSRF 令牌。

- bid 不是正整数：返回 400；
- 书不存在或已下架：返回 404；
- 价格：显示两位小数。

Traceability: `LEGACY-017`、`MIG-RULE-007`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 打开详情

- **WHEN** 会员打开书 9 的详情
- **THEN** 页面显示“月亮和六便士”、出版商、两位小数的价格、库存、简介、销量和“立即购买”按钮

#### Scenario: 已下架的书

- **WHEN** 会员打开已下架的书 2 的详情
- **THEN** 返回 404

#### Scenario: 非法 bid

- **WHEN** 会员请求 `bookDetail&bid=abc`
- **THEN** 返回 400

### Requirement: REQ-CATALOG-006 — 直接打开列表页

直接请求结果页的 JSP URL 时，系统 SHALL 按会话里保存的最近一次查询条件重新查询，显示最新数据，会话 MUST NOT 保存查询结果。各页面的规则如下：

- `jsp/buy.jsp`、`jsp/admin.jsp`、`jsp/bookadmin.jsp`：用各自保存的列表条件；从没查询过时显示空列表；
- `jsp/bookdetails.jsp`、`jsp/editbook.jsp`：用保存的最近查看或最近编辑的 bid；从没查看过时显示没有内容的页面；那本书已不存在或已下架时返回 404；
- `jsp/myorder.jsp`、`jsp/oderadmin.jsp`：没有查询条件，总是显示当前用户或全部订单的最新数据。

Traceability: `LEGACY-032`; disposition: `CHANGE`。

#### Scenario: 条件不变，数据刷新

- **WHEN** 会员搜索“清欢”后，管理员把其中一本下架，会员再直接打开 `jsp/buy.jsp`
- **THEN** 列表按“清欢”重新查询，已下架的那本不再出现

#### Scenario: 从没查询过

- **WHEN** 刚登录的会员直接打开 `jsp/buy.jsp`
- **THEN** 返回 200，书目列表为空

#### Scenario: 直接打开详情页

- **WHEN** 会员看过书 9 的详情后，直接打开 `jsp/bookdetails.jsp`
- **THEN** 页面显示书 9 的最新信息；如果书 9 已被下架，则返回 404

### Requirement: REQ-CATALOG-007 — 封面输出

`jsp/showpic.jsp?img=<文件名>` SHALL 只对已登录用户开放，只在数据目录的 `covers/` 下查找。文件名 MUST 符合白名单 `^[A-Za-z0-9_-]{1,64}\.(jpg|jpeg|png)$`（扩展名不区分大小写）。系统 SHALL 按文件头设置 `Content-Type` 为 `image/png` 或 `image/jpeg`。文件名不合规、路径越界、文件不存在或文件头不是 PNG/JPEG 时，SHALL 返回 404。

Traceability: `LEGACY-018`、`LEGACY-053`、`LEGACY-069`、`MIG-RULE-009`; disposition: `CHANGE`（LEGACY-018、LEGACY-069）、`SECURITY_FIX_REQUIRED`（LEGACY-053）。

#### Scenario: 内容是 PNG 的 jpg 文件

- **WHEN** 会员请求 `showpic.jsp?img=b6.jpg`
- **THEN** 返回 200，`Content-Type` 为 `image/png`

#### Scenario: 路径穿越

- **WHEN** 会员请求 `showpic.jsp?img=../bookshop.db`
- **THEN** 返回 404

#### Scenario: 不存在的封面

- **WHEN** 会员请求 `showpic.jsp?img=nope.jpg`
- **THEN** 返回 404，而不是旧系统的 500

### Requirement: REQ-CATALOG-008 — 公开的图片路径

`/BookShop/img/<文件名>` SHALL 不需要登录，按同样的白名单校验文件名，依次在静态图片（`1.jpg`、`2.jpg`、`default.jpg`）和数据目录的 `covers/` 下查找，Content-Type 按文件头设置。不符合白名单或找不到时 SHALL 返回 404。

Traceability: `LEGACY-004`、`MIG-RULE-009`; disposition: `CHANGE`。

#### Scenario: 未登录取封面

- **WHEN** 未登录用户请求 `GET /BookShop/img/b1.jpg`
- **THEN** 返回 200，`Content-Type` 为 `image/jpeg`

#### Scenario: 上传的封面同样公开

- **WHEN** 管理员上传封面后，未登录用户请求 `/BookShop/img/<服务器生成的文件名>`
- **THEN** 返回 200
