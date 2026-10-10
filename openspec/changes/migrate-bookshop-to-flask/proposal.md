# Migration Proposal

## Planning Pack

- Planning-pack path: `migration-plans/bookshop/`
- 依据文件：`legacy-inventory.md`（GAP-001、GAP-002）、`legacy-baseline.md`（LEGACY-001～LEGACY-073）、`migration-strategy.md`（FEASIBILITY: FEASIBLE_WITH_CONDITIONS），以及可行性实验脚本 `experiments/`。
- 本 change 只引用规划包里的 ID，不改动规划包本身。

## Purpose

把旧的 Java Servlet/JSP 网上书店（`BookShop/`）迁移到 Python + Flask，在 Windows 本机单进程运行。在用功能按行为等价迁移，并保留旧 URL；基线中的缺陷和安全问题按策略的 Behaviour Policy 修复。原数据库已经丢失，目标库按旧代码重建，初始化时导入演示数据（GAP-001、GAP-002）。

## Scope

- **迁移范围**：会员端和管理端的全部在用功能（MIG-DEC-002），按 Behaviour Policy 处理；未列出的 LEGACY 默认 PRESERVE。
- **修复范围**：修复 LEGACY-039～LEGACY-062 中的缺陷和安全问题；为安全修复新增退出登录、CSRF、管理端角色校验和会话吊销（MIG-DEC-012）。
- **软删除**：删书改为下架，删会员改为停用（MIG-DEC-007）。
- **数据**：按 GAP-001 新建 SQLite 表结构；按 GAP-002 提供初始化命令和演示数据。
- **工程**：配置外置、哈希锁定依赖、Windows 启停与初始化说明，以及在 `master` 分支触发的 GitHub Actions（windows-latest）测试（MIG-DEC-011）。
- **上一轮迁移产物**：工作区里已删除的上一轮迁移产物不复用，删除随本次迁移一并提交。
- **不做的事**：去掉的条目（LEGACY-009、LEGACY-036、LEGACY-061、LEGACY-067、LEGACY-068）以及策略 Out of Scope 中列出的内容。

## Target Stack and Constraints

- **技术栈**：Python 3.12.10、Flask 3.1.3、Werkzeug 3.1.9、Jinja2 3.1.6、waitress 3.0.2、SQLite（标准库 `sqlite3`）、Bootstrap 5.3.8、Bootstrap Icons 1.13.1、pytest 9.1.1、pip-tools 7.6.2（MIG-DEC-001、MIG-DEC-010）。
- **部署与 CI**：只在 Windows 上，部署和 CI 都是（MIG-DEC-004、MIG-DEC-011）；默认只监听 127.0.0.1；一律通过 `py -3.12` 创建的虚拟环境运行，并设置 `PYTHONUTF8=1`（MIG-RULE-022）。
- **兼容**：保留旧 URL、页面结构和文案（MIG-RULE-001、MIG-RULE-016）；各类请求的检查顺序和新增提示文案按 MIG-RULE-019、MIG-RULE-020。
- **安全**：SQL 参数化、密码哈希、CSRF、转义、上传限制、会话吊销，分别见 MIG-RULE-002 至 MIG-RULE-006、MIG-RULE-009、MIG-RULE-021。
- **数据**：金额用整数分（MIG-RULE-007）；软删除（MIG-RULE-008）；输入上限（MIG-RULE-018）；连接和事务（MIG-RULE-012）；种子数据里的占位值不得当作旧系统事实（MIG-RULE-015）。
- **实验转测试**：EXP-002～EXP-013 的检查项都要转成正式 TEST（MIG-RULE-023）。

## Capabilities

| Capability | Spec path | Legacy IDs |
|---|---|---|
| 平台与路由：URL 前缀、编码、opttype 分派、检查顺序、错误页、CSRF、转义、SQL 参数化、静态资源、页面结构、配置、日志、请求体上限 | `specs/bookshop-platform/spec.md` | LEGACY-001、LEGACY-002、LEGACY-004、LEGACY-005、LEGACY-006、LEGACY-033、LEGACY-034、LEGACY-035、LEGACY-037、LEGACY-038、LEGACY-039、LEGACY-047、LEGACY-048、LEGACY-051、LEGACY-052、LEGACY-054、LEGACY-056、LEGACY-060、LEGACY-062、LEGACY-063 |
| 账号与会话：注册、登录、会话有效性、管理端授权、退出、个人页、修改密码 | `specs/bookshop-account/spec.md` | LEGACY-003、LEGACY-006、LEGACY-007、LEGACY-008、LEGACY-010、LEGACY-011、LEGACY-012、LEGACY-049、LEGACY-050、LEGACY-057、LEGACY-063、LEGACY-065、LEGACY-070、LEGACY-073 |
| 书目与封面：书目列表、购买页、分类筛选、书名搜索、详情、直接打开列表页、封面输出 | `specs/bookshop-catalogue/spec.md` | LEGACY-004、LEGACY-013、LEGACY-014、LEGACY-015、LEGACY-016、LEGACY-017、LEGACY-018、LEGACY-032、LEGACY-046、LEGACY-053、LEGACY-065、LEGACY-069 |
| 购买与订单：购买、订单记录、我的订单 | `specs/bookshop-orders/spec.md` | LEGACY-019、LEGACY-020、LEGACY-021、LEGACY-040、LEGACY-041、LEGACY-042 |
| 会员管理：会员列表、搜索、停用 | `specs/bookshop-admin-members/spec.md` | LEGACY-022、LEGACY-023、LEGACY-030、LEGACY-044、LEGACY-065 |
| 书籍管理：书籍列表、搜索、两步新增、修改、下架 | `specs/bookshop-admin-books/spec.md` | LEGACY-024、LEGACY-025、LEGACY-026、LEGACY-027、LEGACY-028、LEGACY-029、LEGACY-043、LEGACY-046、LEGACY-054、LEGACY-055、LEGACY-071、LEGACY-072 |
| 账目统计 | `specs/bookshop-admin-revenue/spec.md` | LEGACY-031、LEGACY-042、LEGACY-045 |
| 数据存储：表结构、连接与事务、初始化与演示数据、金额、输入上限 | `specs/bookshop-data/spec.md` | LEGACY-045、LEGACY-058、LEGACY-059、LEGACY-064、LEGACY-065、LEGACY-066 |

## Major Decisions and Accepted Risks

- **策略决策**：MIG-DEC-001 至 MIG-DEC-013 都由用户确认过，本 change 不重新讨论。
- **已接受的风险**：COMP-001，即本机 Python 3.12.10 拿不到 3.12.11 以后的安全补丁（MIG-DEC-009）。缓解措施是默认只监听 127.0.0.1。
- **成立的前提**（FEASIBILITY 的前提）：
  - windows-latest 上的安装和全量测试要在实施时跑通（COMP-013、COMP-016）；
  - 种子里的占位值不得作为旧系统事实（MIG-RULE-015）。
- **无法和旧系统运行对照**：旧系统无法运行（GAP-001、GAP-002），对照测试以 `legacy-baseline.md` 的静态描述为准，不做运行期的黄金样本比对。
- **设计里的技术决策**：放在 design.md 的 DEC-###，都在策略的规则范围之内。超出策略的决定会回到用户确认，不会直接写进设计。
