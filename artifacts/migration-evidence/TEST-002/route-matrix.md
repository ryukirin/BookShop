# TEST-002 活动路由冻结矩阵

证据边界：源修订 `eff378ba25960fd5c16d621a5940378504b7c1b1`；`BookShop/src/controller/` 中四个活动 `@WebServlet`、`BookShop/WebContent/` 的活动 JSP 与 `migration-plans/java-bookshop-to-python/legacy-baseline.md` 的 LEGACY-001～055、GOLD-001～020。旧容器和数据库无法运行，本表是已批准静态目标预言机，不是旧系统动态抓包结果。所有地址以 `/BookShop` 为前缀；未列出的 `opttype` 和缺少 `opttype` 返回 400，不存在的路径返回 404；参数缺失返回 400，不存在的资源 ID 返回 404，内部故障返回 500 中文通用提示、堆栈仅入脱敏日志。

| 路径 | `opttype`／页面 | 必需参数 | 目标状态、Location／正文与副作用 | GOLD／批次 |
|---|---|---|---|---|
| `/BookShop/health` | — | — | 200 `ok`，无业务写入 | TEST-001／BATCH-001 |
| `/BookShop/index.jsp`、`login.jsp`、`register.jsp` | 页面 | — | 200；原静态页面文案与导航，业务页面于对应批次接入 | LEGACY-003／BATCH-003～004 |
| `/BookShop/login.action` | `addusers` | `inputUname,inputPassword,checkPassword` | GOLD-001～004：重复名／密码不一致 200 原文提示、零写入；数据库故障 500 全回滚；成功 302 `/BookShop/login.jsp`，角色 1 用户＋客户原子创建且只存哈希 | BATCH-003 |
| 同上 | `checkUsers` | `inputName,inputPassword` | GOLD-005～007：角色 1 成功 302 `/BookShop/index.jsp`；角色 2 成功 302 `/BookShop/jsp/admin.action?opttype=queryAllcustomers`；错误凭据 200 原文提示；缺参 400；成功轮换服务端 Session 并设 `uid,role` | BATCH-003 |
| `/BookShop/jsp/my.action` | `initMypage` | 登录 Session | GOLD-008：302 `/BookShop/jsp/my.jsp`，Session 写入 `uname,role` 显示值 | BATCH-003 |
| 同上 | `queryMyorder` | 登录 Session | GOLD-009：302 `/BookShop/jsp/myorder.jsp`，仅本人订单按 `oid ASC` 写入 `molist` | BATCH-005 |
| 同上 | `updatePwd` | `oldpwd,newpwd,anewpwd`＋Session＋POST/CSRF | GOLD-010～013：成功／旧密码错／新密码不一致为 200 修改页及原文提示；缺参 400；失败密码不变；旧 GET 不写入 | BATCH-003 |
| `/BookShop/jsp/book.action` | `queryAllbook` | — | 302 `/BookShop/jsp/buy.jsp`；按 `bid` 分行、各自销量降序，查询结果写入 Session | GOLD-014／BATCH-004 |
| 同上 | `queryByname` | `bname`（允许空串） | 302 `buy.jsp`；参数化包含搜索、`!%_` 字面转义，同名书分行，Session 覆盖 | GOLD-015／BATCH-004 |
| 同上 | `queryBytag` | `tname`（允许空串） | 302 `buy.jsp`；精确名称覆盖全部同名 `tid`，书籍按 `bid` 分行，Session 覆盖 | GOLD-015／019／BATCH-004 |
| 同上 | `bookDetail` | `bid` | 302 `/BookShop/jsp/bookdetails.jsp`，详情与同一 `bid` 一致；不存在 ID 为 404 | GOLD-014／BATCH-004 |
| 同上 | `buybook` | `bid`＋登录 Session＋POST/CSRF | 成功 302 `/BookShop/jsp/my.action?opttype=queryMyorder`；库存扣减、单订单、变更日志同事务；旧 GET 不写入 | LEGACY-011／BATCH-005 |
| `/BookShop/jsp/admin.action` | `queryAllcustomers`、`queryCustomers` | 后者 `uname`；角色 2 Session | 302 `/BookShop/jsp/admin.jsp`；普通会员不可访问；精确用户名搜索，结果写 Session | LEGACY-015／BATCH-006 |
| 同上 | `deleteCustomers` | `uid`＋角色 2＋POST/CSRF | GOLD-017：有单 409 中文提示、账目零变；GOLD-018：无单 302 `admin.action?opttype=queryAllcustomers`，客户→用户原子删除；旧 GET 不写入 | BATCH-006 |
| 同上 | `queryAllbooks`、`queryBooks` | 后者 `bname`；角色 2 Session | 302 `/BookShop/jsp/bookadmin.jsp`；逐 `bid ASC`，重复书字段和管理链接不交叉 | GOLD-016／BATCH-006 |
| 同上 | `addBooks` | `bname,publishers,stock,price,tname,cont`＋角色 2＋POST/CSRF | 六字段进入 Session 草稿，302 `/BookShop/jsp/addnext.jsp`（携原字段）；旧 GET 不写入 | LEGACY-018／BATCH-006 |
| 同上 | `addBooksimg` | 单文件＋草稿＋角色 2＋POST/CSRF | GOLD-020：重复标签选最大 `tid`；文件及书籍／日志提交协议通过后 302 `admin.action?opttype=queryAllbooks`；失败无部分可见写入 | BATCH-006 |
| 同上 | `showBooks` | `bid`＋角色 2 | 302 `/BookShop/jsp/editbook.jsp`，Session 保存同一 `bid` 的书籍；不存在 ID 为 404 | LEGACY-020／BATCH-006 |
| 同上 | `editBooks` | `bid,publishers,stock,price`＋角色 2＋POST/CSRF | 302 `admin.action?opttype=queryAllbooks`；仅三字段更新且原子提交；旧 GET 不写入 | LEGACY-020／BATCH-006 |
| 同上 | `deleteBooks` | `bid`＋角色 2＋POST/CSRF | 302 `admin.action?opttype=queryAllbooks`；订单→书籍原子删除；旧 GET 不写入 | LEGACY-021／BATCH-006 |
| 同上 | `showAllmoney` | 角色 2 Session | 302 `/BookShop/jsp/oderadmin.jsp`；订单按 `oid ASC`，整数分累加并显示两位小数 | LEGACY-022／BATCH-006 |
| `/BookShop/jsp/*.jsp` | `buy,bookdetails,my,myorder,changepwd,admin,bookadmin,add,addnext,editbook,oderadmin,showpic` | 页面／图片各自参数 | 200 页面或受控图片；未登录／越权按安全契约拒绝；`showpic.jsp?img=...` 不接受任意路径 | LEGACY-023～026／BATCH-003～006 |
| `/BookShop/uploadServlet.do`、`downloadServlet.do`、`jsp/user.action`、`jsp/useredit.jsp` | 排除 | — | 404；无可达活动实现，不复活注释或孤立功能 | LEGACY-046／047 |

非敏感查询可同时接受 GET 和 POST；注册、购买、密码修改、管理写入只允许 POST 且须 CSRF。LEGACY-001 的未登录保护保留 302，并固定 Location 为绝对上下文路径 `/BookShop/login.jsp`；普通已登录会员访问管理操作为授权拒绝。未知路由的 404 不复活被排除功能。

Session 字段冻结：登录为 `uid,role`；顾客全部／搜索／分类为 `tlist,blist`，详情为 `sblist`；个人中心为 `uname,role`，本人订单为 `molist`；管理会员列表／搜索为 `clist`，书籍列表／搜索为 `blist`，编辑回显为 `eblist`，账目为 `olist,sum`；两步新增草稿为 `bname,publishers,stock,price,tname,cont`，图片逻辑标识为 `url`。这些业务字段仅在服务端存储，Cookie 不承载它们。后续并发测试必须按事务提交顺序核对最近查询覆盖和退出后不可复活。

具体页面文案、数据与 Session 逐分支预言机以 GOLD-001～020 和 TEST-003～019 的细分用例为准；LEGACY-001～055 的处置与 TEST 落点逐条沿用已批准 `legacy-baseline.md` 和 `test-plan.md`，本冻结不改写任何批准决定。本表不授权实际切换或导入历史数据。
