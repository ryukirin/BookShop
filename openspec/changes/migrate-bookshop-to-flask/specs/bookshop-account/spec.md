# Spec Delta: bookshop-account

## Purpose

账号与会话：注册、登录、会话有效性与吊销、管理端授权、退出、个人页、修改密码。会员身份只由 `user.role` 决定。

## ADDED Requirements

### Requirement: REQ-ACCOUNT-001 — 注册

`register.jsp` SHALL 提供 `inputUname`、`inputPassword`、`checkPassword` 三个字段，POST 到 `login.action?opttype=addusers`。系统 SHALL 按下面的顺序处理注册：

1. 用户名不足 1 字或超过 20 字、口令不足 1 字或超过 64 字时，返回 `alert('please check user name or password!')` 并跳回 `register.jsp`；
2. 用户名已被占用时，返回 `alert('please change uer name!')` 并跳回 `register.jsp`。按 ASCII 不区分大小写的等值比较，已停用会员的用户名也算占用；
3. 两次口令不一致时，返回 `alert('please check password!')` 并跳回；
4. 其余情况下，插入 role 为 1、`active` 为 1 的用户，口令只存 scrypt 哈希，然后 302 到 `login.jsp`；其他数据库写入失败时返回 `alert('fail,try again!')`。

查重和插入 SHALL 在同一个写事务里完成，并发注册同一个用户名时只有一个成功，其余按第 2 步提示。注册后 SHALL NOT 自动登录。系统 MUST NOT 写入任何 `customer` 表，会员身份只由 role 为 1 决定。

Traceability: `LEGACY-007`、`LEGACY-049`、`LEGACY-065`、`LEGACY-073`、`MIG-RULE-006`、`MIG-RULE-018`、`MIG-RULE-020`; disposition: `CHANGE`（LEGACY-007、LEGACY-065、LEGACY-073）、`SECURITY_FIX_REQUIRED`（LEGACY-049）。

#### Scenario: 注册成功

- **WHEN** 访客提交用户名 `zhangsan`、两次口令都是 `abc123`，并带有效令牌
- **THEN** 302 到 `login.jsp`；库里新增 role 为 1 的 `zhangsan`，`upwd` 以 `scrypt:` 开头且不等于 `abc123`

#### Scenario: 用户名只差大小写

- **WHEN** `zhangsan` 已存在，访客以 `ZhangSan` 注册
- **THEN** 返回 `alert('please change uer name!')`，跳回 `register.jsp`，用户数不变

#### Scenario: 用户名和两次口令都有问题

- **WHEN** `zhangsan` 已存在，访客以 `zhangsan` 注册，两次口令不一致
- **THEN** 提示的是 `please change uer name!`，即先检查用户名

#### Scenario: 用户名过长

- **WHEN** 访客以 21 个字的用户名注册
- **THEN** 返回 `alert('please check user name or password!')`，没有插入用户

#### Scenario: 并发注册同名

- **WHEN** 10 个请求同时以大小写各异的同一个用户名注册
- **THEN** 恰好 1 个得到 302，其余 9 个得到 `please change uer name!`

### Requirement: REQ-ACCOUNT-002 — 登录

`login.jsp` SHALL 提供 `inputName`、`inputPassword` 两个字段和“注册”按钮（跳到 `register.jsp`），表单 POST 到 `login.action?opttype=checkUsers`。系统 SHALL 按 ASCII 不区分大小写的等值比较查找用户名，再校验口令哈希。

- **登录成功**：系统 SHALL 清空原会话，重新签发会话，写入 `uid`、当前会话版本号、登录时间和新的 CSRF 令牌。然后按数据库里的 role 跳转：role 为 1 时 302 到 `index.jsp`，role 为 2 时 302 到 `jsp/admin.action?opttype=queryAllcustomers`。
- **登录失败**：用户不存在、口令错误或账号已停用时，系统 SHALL 统一返回 `alert('username or password error!')` 并跳回 `login.jsp`。

Traceability: `LEGACY-008`、`LEGACY-057`、`LEGACY-065`、`LEGACY-070`、`MIG-RULE-004`、`MIG-RULE-021`; disposition: `CHANGE`（LEGACY-008、LEGACY-065、LEGACY-070）、`SECURITY_FIX_REQUIRED`（LEGACY-057）。

#### Scenario: 会员登录

- **WHEN** 会员 `zhangsan` 打开 `login.jsp` 后，用正确口令登录
- **THEN** 302 到 `index.jsp`，响应里的会话 Cookie 和登录前不同

#### Scenario: 管理员登录

- **WHEN** 管理员 `admin` 用正确口令登录
- **THEN** 302 到 `jsp/admin.action?opttype=queryAllcustomers`

#### Scenario: 用户名大小写不同

- **WHEN** 会员 `zhangsan` 以 `ZHANGSAN` 和正确口令登录
- **THEN** 登录成功

#### Scenario: 已停用的会员

- **WHEN** 已停用的会员用正确口令登录
- **THEN** 返回 `alert('username or password error!')`，没有建立登录会话

### Requirement: REQ-ACCOUNT-003 — 会话有效性与吊销

会话里 SHALL 只保存这些内容：`uid`、会话版本号、登录时间、CSRF 令牌，以及页面查询条件。页面查询条件指三个列表页（`buy.jsp`、`admin.jsp`、`bookadmin.jsp`）的查询条件，加上最近查看的详情 bid 和最近编辑的 bid（LEGACY-032）。在最大输入下，会话 Cookie 不超过 3000 字节。

每个请求，系统 SHALL 从数据库读取当前用户。遇到以下任一情况，系统 SHALL 清空会话、按未登录处理，访问 `/BookShop/jsp/*` 时 302 到 `/BookShop/login.jsp`：

- 用户不存在；
- `active` 为 0；
- 会话版本号和数据库里的不一致；
- 登录已超过 8 小时；
- 空闲超过 30 分钟。

会话 Cookie SHALL 设为 HttpOnly 和 SameSite=Lax。

Traceability: `LEGACY-003`、`LEGACY-010`、`LEGACY-057`、`LEGACY-063`、`MIG-RULE-003`、`MIG-RULE-021`; disposition: `CHANGE`（LEGACY-003、LEGACY-010、LEGACY-063）、`SECURITY_FIX_REQUIRED`（LEGACY-057）。

#### Scenario: 未登录访问受保护页面

- **WHEN** 未登录用户请求 `GET /BookShop/jsp/my.jsp`
- **THEN** 302 到 `/BookShop/login.jsp`

#### Scenario: 退出后重放旧 Cookie

- **WHEN** 会员先复制下登录后的会话 Cookie，然后退出，再用这个 Cookie 请求 `jsp/my.action?opttype=initMypage`
- **THEN** 302 到 `/BookShop/login.jsp`

#### Scenario: 超过绝对有效期

- **WHEN** 会话里的登录时间早于当前时间 8 小时以上
- **THEN** 下一次请求 `/BookShop/jsp/*` 时 302 到登录页

#### Scenario: Cookie 在最大输入下的大小

- **WHEN** 管理员在三个列表页都用长度达上限的随机汉字搜索
- **THEN** 响应里 `Set-Cookie` 的长度不超过 3000 字节

### Requirement: REQ-ACCOUNT-004 — 管理端授权

管理端 URL（`jsp/admin.action`、`jsp/admin.jsp`、`jsp/bookadmin.jsp`、`jsp/add.jsp`、`jsp/addnext.jsp`、`jsp/editbook.jsp`、`jsp/oderadmin.jsp`）SHALL 只对数据库里当前 role 为 2 的有效用户开放，其他已登录用户 SHALL 得到 403。授权 MUST 以数据库为准，MUST NOT 读取会话里保存的角色或显示名。管理员 SHALL 仍然可以使用会员端页面。

Traceability: `LEGACY-050`、`LEGACY-011`、`MIG-RULE-003`; disposition: `SECURITY_FIX_REQUIRED`（LEGACY-050）、`CHANGE`（LEGACY-011）。

#### Scenario: 会员访问管理端

- **WHEN** 已登录的会员请求 `GET /BookShop/jsp/admin.action?opttype=queryAllcustomers`
- **THEN** 返回 403

#### Scenario: 管理员先访问个人页再访问管理端

- **WHEN** 管理员先打开 `jsp/my.action?opttype=initMypage`，再打开 `jsp/admin.action?opttype=showAllmoney`
- **THEN** 两次都成功：前者 302 到个人页，后者 302 到账目页

### Requirement: REQ-ACCOUNT-005 — 退出登录

系统 SHALL 提供 `POST /BookShop/logout.action`，要求有效 CSRF 令牌。成功时递增当前用户的会话版本号、清空会话，302 到 `/BookShop/login.jsp`。用 GET 访问 SHALL 返回 405。登录后，首页以及会员端、管理端所有页面的导航栏 SHALL 显示“退出”按钮。退出 SHALL 让该用户在所有设备上的会话一起失效。

Traceability: `LEGACY-006`、`LEGACY-010`、`LEGACY-057`、`MIG-RULE-001`、`MIG-RULE-021`; disposition: `CHANGE`（LEGACY-006、LEGACY-010）、`SECURITY_FIX_REQUIRED`（LEGACY-057）。

#### Scenario: 退出

- **WHEN** 已登录的会员在购买页点“退出”
- **THEN** 302 到 `/BookShop/login.jsp`，之后访问 `jsp/my.jsp` 时被 302 到登录页

#### Scenario: 用 GET 退出

- **WHEN** 已登录用户请求 `GET /BookShop/logout.action`
- **THEN** 返回 405，会话仍然有效

### Requirement: REQ-ACCOUNT-006 — 个人页

`my.action?opttype=initMypage` SHALL 302 到 `my.jsp`。`my.jsp` SHALL 显示默认头像 `img/default.jpg`、当前用户名和角色名（role 为 1 显示“会员”，role 为 2 显示“管理员”），侧栏依次为“个人信息”“修改密码”“我的订单”。用户名和角色名 SHALL 每次都从数据库读取，会话里不保存。

Traceability: `LEGACY-011`; disposition: `CHANGE`。

#### Scenario: 会员的个人页

- **WHEN** 会员 `zhangsan` 请求 `jsp/my.action?opttype=initMypage`，并跟随跳转
- **THEN** `my.jsp` 显示 `zhangsan` 和“会员”

### Requirement: REQ-ACCOUNT-007 — 修改密码

`changepwd.jsp` SHALL 提供 `oldpwd`、`newpwd`、`anewpwd` 三个字段，POST 到 `my.action?opttype=updatePwd`。系统 SHALL 按下面的规则处理：

- 两次新口令一致、新口令为 1～64 字、旧口令正确：用 scrypt 哈希保存新口令，递增会话版本号，让当前会话换上新版本号后保持登录，返回 `alert('success!')`；
- 否则旧口令错误：返回 `alert('password error!')`；
- 否则：返回 `alert('check new password!')`。

三种情况都跳回 `changepwd.jsp`。

Traceability: `LEGACY-012`、`LEGACY-049`、`MIG-RULE-006`、`MIG-RULE-021`; disposition: `CHANGE`（LEGACY-012）、`SECURITY_FIX_REQUIRED`（LEGACY-049）。

#### Scenario: 修改成功后其他会话失效

- **WHEN** 会员在浏览器 A 和 B 都已登录，在 A 中成功修改了密码
- **THEN** A 收到 `alert('success!')` 并保持登录；B 下一次请求 `/BookShop/jsp/*` 时被 302 到登录页；新口令可以登录，旧口令不行

#### Scenario: 旧口令错误

- **WHEN** 会员输入错误的旧口令，两次新口令一致
- **THEN** 返回 `alert('password error!')`，口令不变

#### Scenario: 两次新口令不一致

- **WHEN** 会员输入正确的旧口令，两次新口令不一致
- **THEN** 返回 `alert('check new password!')`
