# Spec Delta: bookshop-orders

## Purpose

会员购买与订单：一键购买、订单记录内容、我的订单。

## ADDED Requirements

### Requirement: REQ-ORDER-001 — 购买

`POST book.action?opttype=buybook` SHALL 带 `bid` 和有效 CSRF 令牌，每次固定买 1 本。系统 SHALL 在同一个 `BEGIN IMMEDIATE` 事务里依次完成：确认书存在且在架、确认库存大于 0、库存减 1、插入订单（`bid`、当前用户 `uid`、成交价 `unit_price_cents` 等于此刻售价）。

- **成功**：302 到 `my.action?opttype=queryMyorder`；
- **库存为 0**：返回 `alert('out of stock!')` 并跳到 `book.action?opttype=bookDetail&bid=<bid>`，库存和订单都不变；
- **书不存在或已下架**：返回 404；
- **bid 不是正整数**：返回 400。

并发购买 MUST NOT 超卖，库存 MUST NOT 为负。管理员也 SHALL 可以购买。

Traceability: `LEGACY-019`、`LEGACY-040`、`LEGACY-041`、`LEGACY-042`、`MIG-RULE-012`; disposition: `CHANGE`（LEGACY-019）、`BUG_NOT_PRESERVED`（LEGACY-040、LEGACY-041、LEGACY-042）。

#### Scenario: 购买成功

- **WHEN** 会员购买库存为 100 的书 9
- **THEN** 302 到 `my.action?opttype=queryMyorder`；书 9 的库存变为 99；新订单的成交价等于书 9 当时的售价

#### Scenario: 库存为 0

- **WHEN** 会员购买库存为 0 的书
- **THEN** 返回 `alert('out of stock!')`，跳到该书详情；库存仍为 0，没有新订单

#### Scenario: 并发购买最后几本

- **WHEN** 库存为 5 的书同时收到 20 个购买请求
- **THEN** 恰好 5 个请求得到 302，15 个得到 `out of stock!`，库存为 0，订单数为 5，没有 500

#### Scenario: 购买已下架的书

- **WHEN** 会员购买已下架的书 2
- **THEN** 返回 404，库存和订单不变

### Requirement: REQ-ORDER-002 — 订单记录内容

每个订单 SHALL 记录 `oid`（自增）、`bid`、`uid` 和成交价 `unit_price_cents`，SHALL NOT 记录下单时间和数量。之后修改售价 MUST NOT 改变已有订单的成交价。

Traceability: `LEGACY-020`、`LEGACY-042`、`MIG-RULE-007`; disposition: `CHANGE`（LEGACY-020）、`BUG_NOT_PRESERVED`（LEGACY-042）。

#### Scenario: 改价不影响历史订单

- **WHEN** 会员以 39.80 买了书 9，管理员随后把书 9 改价为 99.00
- **THEN** 这笔订单的成交价仍是 39.80

### Requirement: REQ-ORDER-003 — 我的订单

`my.action?opttype=queryMyorder` SHALL 302 到 `myorder.jsp`。`myorder.jsp` SHALL 列出当前用户的全部订单，按 oid 升序，表格列为“用户名”“书名”“订单金额”。订单金额 SHALL 是成交价，显示两位小数，不显示订单号和合计。已下架的书的订单 SHALL 照常显示。

Traceability: `LEGACY-021`、`LEGACY-042`、`MIG-RULE-007`; disposition: `CHANGE`（LEGACY-021）、`BUG_NOT_PRESERVED`（LEGACY-042）。

#### Scenario: 订单含已下架的书

- **WHEN** 会员先后买了书 9 和书 1，书 1 随后被下架
- **THEN** `myorder.jsp` 依次列出书 9 和书 1 两行，金额都是各自的成交价
