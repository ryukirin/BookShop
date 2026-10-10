# Spec Delta: bookshop-admin-revenue

## Purpose

管理端账目统计：列出订单并给出总金额。

## ADDED Requirements

### Requirement: REQ-REVENUE-001 — 账目统计

`admin.action?opttype=showAllmoney` SHALL 302 到 `oderadmin.jsp`。`oderadmin.jsp` SHALL 列出全部订单，包括已下架书籍的订单和已停用会员的订单，按 oid 升序，表格列为“订单id”“用户名”“书名”“订单金额”。金额 SHALL 是成交价。

最后一行 SHALL 显示“总金额：<合计>元”。合计 SHALL 用整数分精确求和，显示两位小数，MUST NOT 出现二进制浮点误差。

Traceability: `LEGACY-031`、`LEGACY-042`、`LEGACY-045`、`MIG-RULE-007`; disposition: `CHANGE`（LEGACY-031）、`BUG_NOT_PRESERVED`（LEGACY-042、LEGACY-045）。

#### Scenario: 精确合计

- **WHEN** 有三笔订单，成交价分别为 0.10、0.20、39.80
- **THEN** 最后一行是“总金额：40.10元”

#### Scenario: 软删除不影响账目

- **WHEN** 一笔订单对应的书已下架，另一笔对应的会员已停用
- **THEN** 两笔都在列表里，并计入合计

#### Scenario: 改价不影响账目

- **WHEN** 管理员在订单产生之后修改了售价
- **THEN** 列表和合计仍按成交价计算
