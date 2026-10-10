# Spec Delta: bookshop-admin-members

## Purpose

管理端会员管理：会员列表（管理员登录后的落地页）、会员搜索、停用会员。

## ADDED Requirements

### Requirement: REQ-MEMBER-001 — 会员列表

`admin.action?opttype=queryAllcustomers` SHALL 把查询条件保存到会话里，然后 302 到 `admin.jsp`。`admin.jsp` SHALL 列出所有 role 为 1 且未停用的用户，按 uid 升序，表格列为“会员id”“会员名”“操作”。操作列的“删除”SHALL 是 POST 到 `admin.action?opttype=deleteCustomers` 的表单按钮，带 `uid` 和 CSRF 令牌。侧栏 SHALL 依次为“会员管理”“书籍管理”“账目统计”。

Traceability: `LEGACY-022`; disposition: `CHANGE`。

#### Scenario: 管理员登录后的落地页

- **WHEN** 已有会员 `zhangsan`、`lisi`，其中 `lisi` 已停用，管理员登录
- **THEN** 跳到 `admin.jsp`，表格里只有 `zhangsan`，不含管理员自己

### Requirement: REQ-MEMBER-002 — 会员搜索

`admin.action?opttype=queryCustomers&uname=<名>` SHALL 在 role 为 1 且未停用的用户中，按 ASCII 不区分大小写的等值比较查找，然后 302 到 `admin.jsp` 显示结果。搜索词超过 20 字时 SHALL 返回 400。

Traceability: `LEGACY-023`、`LEGACY-065`、`MIG-RULE-018`; disposition: `CHANGE`。

#### Scenario: 大小写不同

- **WHEN** 管理员搜索 `ZHANGSAN`
- **THEN** `admin.jsp` 显示 `zhangsan`

#### Scenario: 搜索已停用的会员

- **WHEN** 管理员搜索已停用的 `lisi`
- **THEN** 结果为空

### Requirement: REQ-MEMBER-003 — 停用会员

`POST admin.action?opttype=deleteCustomers` SHALL 带 `uid` 和有效 CSRF 令牌。

- **目标必须是未停用的会员**：目标不存在、已停用或 role 不是 1（包括管理员自己）时返回 404，`uid` 不是正整数时返回 400；
- **成功时的处理**：在一个写事务里把 `active` 设为 0、递增该用户的会话版本号，然后 302 到 `admin.action?opttype=queryAllcustomers`；
- **停用后**：该用户的订单 SHALL 保留并继续计入账目，用户名 SHALL 仍被占用；该用户已有的会话 SHALL 在下一次请求时失效。

Traceability: `LEGACY-030`、`LEGACY-044`、`MIG-RULE-008`、`MIG-RULE-021`; disposition: `CHANGE`（LEGACY-030）、`BUG_NOT_PRESERVED`（LEGACY-044）。

#### Scenario: 停用有订单的会员

- **WHEN** 会员 `zhangsan` 有 2 个订单，管理员停用他
- **THEN** 302 回会员列表，列表里没有 `zhangsan`；账目统计仍含这 2 个订单；`zhangsan` 登录时得到 `username or password error!`

#### Scenario: 停用后原会话失效

- **WHEN** `zhangsan` 在浏览器里保持登录，管理员停用他
- **THEN** `zhangsan` 下一次请求 `jsp/my.action?opttype=initMypage` 时被 302 到登录页

#### Scenario: 停用管理员自己

- **WHEN** 管理员提交自己的 uid
- **THEN** 返回 404，管理员账号不受影响
