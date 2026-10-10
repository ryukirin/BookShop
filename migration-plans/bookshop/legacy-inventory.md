# Legacy Inventory

旧系统：`BookShop/`（Java Servlet/JSP 网上书店，课程设计项目）。本文件只记录事实，不做迁移决策；保留什么、怎么迁移由 migration-strategy.md 决定。

## Migration Readiness

READINESS: BLOCKED

本文件在 2026-10-10 共盘点了三次。第二次时仓库多了 `BookShop/db/`，里面是数据库的复原材料，还没有提交。第三次时，复原说明 `migration-plans/bookshop/legacy-db-reconstruction.md` 经过复核，更正了第一版中的 8 处问题（见它的“复核记录”）；多项可信度降为“推定”或“占位”，四个 SQL/ini 文件只改了注释，原库材料没有新增。复原是根据旧代码、作者上一个项目和封面图推定的，不是原库的材料，复原说明自己也写明“复原不等于补齐”。要不要拿它当旧库的基准，是迁移决策。所以 GAP-001 和 GAP-002 仍然是阻塞项，范围限于复原也确定不了的部分。

| Material | Status | Evidence | Blocking |
|---|---|---|---|
| Source code complete | PARTIAL | 4 个在用 Servlet、4 个 DAO、`SQLHelper`、2 个过滤器和 19 个 JSP 都在仓库中。`UploadServlet`、`DownloadServlet`、`UsersSrevlet` 整个文件被注释掉，但 `web.xml` 仍映射前两个。`download.jsp`、`upload.jsp`、`wirte.jsp`、`useredit.jsp` 是另一个项目（课程/博客/作业）的残留页面。见 INV-010、INV-023 | NO |
| Build and dependency definition | PARTIAL | 没有 Maven/Gradle/Ant 构建文件，只有 Eclipse 工程配置。`BookShop/.classpath` 用本机绝对路径（`<redacted-local-path>`）引用 jar，`WebContent/WEB-INF/lib` 不存在，`.gitignore` 排除了 `*.jar`。除 JSTL 外，各库版本可从 jar 文件名读出。见 INV-001、Dependencies | NO |
| Database schema (DDL) | PARTIAL | 仓库和 git 历史里都没有 BookShop 的原始 DDL（历史里只有作者上一个项目 StudentSystem 的表设计说明）。新增的复原文件 `BookShop/db/schema.sql` 有 5 张表，文件末尾有 4 个推定的外键，可以跳过。每一列的依据和可信度（确定/较高/推定/占位）写在 `legacy-db-reconstruction.md` 里；复核之后，能确定的只剩列名、`uid`/`bid`/`oid` 是自增列、`orders` 没有 `price` 列这几项，其余都是推定或占位。该文档说，在 MySQL 8.0.36 上用复原库回放 DAO 原文 SQL，没有出现列不存在或列名歧义的错误；本次盘点没有复跑。复原仍定不下来的：有没有外键、`price` 的实际类型、各列长度、`uname` 是否唯一。见 INV-017、INV-035、GAP-001 | YES |
| Database data or seed data | PARTIAL | 原始数据仍然缺失。新增的复原文件 `BookShop/db/seed.sql` 有 3 个分类（小说、散文、诗歌，按书的体裁推测）、1 个管理员（`admin`，口令是占位值）和 10 本书。书名和出版社从封面读出，其中几家出版社是推定的；价格、库存、简介是占位值；bid 沿用封面编号，没有 10。会员和订单历史无法恢复，没有包含。见 INV-037、GAP-002 | YES |
| Runtime configuration | PARTIAL | 应用这边，连接串、账号、口令仍硬编码在 `SQLHelper` 里（INV-018）。数据库服务器这边，新增了复原环境的配置文件 `BookShop/db/my.ini`：端口 3310、`utf8mb4`/`utf8mb4_0900_ai_ci`、去掉 `ONLY_FULL_GROUP_BY` 的 `sql_mode`（保留 `STRICT_TRANS_TABLES`）、`mysql_native_password`。按复原说明，这是让旧 SQL 能跑起来的环境设置，不是对原服务器的推断：版本 8.0.x 和 `sql_mode` 都标为占位，字符集只推得出“要支持中文”。原来的服务器配置仍然未知，这部分并入 GAP-001。Tomcat 没有 `server.xml`/`context.xml`，按容器默认值运行。见 INV-036 | NO |
| External services | PRESENT | 不依赖支付、邮件等后端服务。前端从 CDN 加载 jQuery 1.12.4（`ajax.googleapis.com`），IE9 以下还会加载 html5shiv/respond（`oss.maxcdn.com`）。见 INV-029 | NO |
| Static assets and media | PARTIAL | 自有 CSS、轮播图、默认头像、书籍封面和内置 Bootstrap 3.3.7 都在。页面引用的部分文件缺失：`bootstrap/docs/js/*`、`jsp/offcanvas.js`、`bootstrap/assets/*`、`css/changepwd.css`，`bootstrap/docs/dist/fonts` 也缺少 woff/woff2/ttf。运行期上传的封面写入部署目录，不在仓库中。见 INV-025～INV-028、LEGACY-047 | NO |
| Legacy system runnable | NO | 数据库这边可以按复原材料搭起来（见 `legacy-db-reconstruction.md` 的“使用方法”），但仍然需要 JDK 8、Tomcat 8.5/9.0 和 5 个仓库外的 jar。本机没有安装 Java、Tomcat、MySQL 或 Docker。本次盘点没有运行旧系统，所以基线仍然全部为 STATIC | NO |
| Existing tests or documentation | PARTIAL | 旧系统本身没有测试，`README.md` 只有 9 行。新增的 `BookShop/db/legacy-sql-check.sql` 把 DAO 原文 SQL 代入示例参数，按业务流程回放，但只能验证复原库能不能执行这些 SQL，不覆盖 Java 层。见 INV-038 | NO |

| Gap ID | Missing material | Why it is needed (evidence) | Impact if unresolved | Ways to unblock |
|---|---|---|---|---|
| GAP-001 | MySQL 库 `book` 的原始表结构（DDL）和服务器设置。已有一份按代码推定的复原（`BookShop/db/schema.sql`、`BookShop/db/my.ini`），但还有几项定不下来：有没有外键、是否开启 strict 模式、`price` 的实际类型、各列长度和唯一约束（包括 `bname` 是否唯一）、服务器版本和字符集，以及原服务器是怎样让分组查询跑起来的（复原说明列了三种解释：手动关掉 `ONLY_FULL_GROUP_BY`、服务器是 5.6 或更早、`bname` 唯一且非空） | 所有持久化都靠拼接的 SQL，例如 `BookShop/src/Service/AdminDao.java:AdminDao.queryAllbook`、`AdminDao.addCustomers`、`BookShop/src/Service/MyDao.java:MyDao.buyBook`、`BookShop/src/Service/CustomerDao.java:CustomerDao.queryAllbook`。唯一的直接依据就是这些 SQL。作者上一个项目 StudentSystem（git `d5dadef`，2019-10）只能间接参考：它的 README（`774ebae:README.md`）和它自己的 SQL 对不上（README 写 `USERS`、`TBRELA`，SQL 用的是 `user`、`tbrelation`，还多一张 `notes` 表）；改成 BookShop（`b7a282c`，2020-09）时，`Tag`、`Users` 的字段由 `id` 改成了 `tid`、`uid`；StudentDao 里有 10 处作者注释“不一定对”。复原说明复核后，已把这些都降为间接参考，并撤回了 `sql_mode` 的旁证 | 在定下来“复原结构算不算旧库基准”之前，设计目标数据模型、对照旧行为都没有依据。外键和 strict 模式有四种组合，LEGACY-044 和 LEGACY-055 的旧行为各不相同（复原文档已实测列出）；`price` 的类型会影响 LEGACY-045 | 找到原库，或请作者确认，然后重跑 migration-inventory；或者在 migration-strategy 中决定以复原结构为旧库基准，接受其中的“推定”和“占位”项，并为外键、strict 模式各选一种假设 |
| GAP-002 | 原始数据库数据：原来的分类名、管理员账号、书目明细（价格、库存、简介），以及会员和订单历史。已有一份推定的种子数据 `BookShop/db/seed.sql` | 界面上无法创建分类和管理员（`BookShop/src/Service/AdminDao.java:AdminDao.queryTagByTname`、`BookShop/src/controller/LoginServlet.java:LoginServlet.doGet#addusers`）。封面图 `BookShop/WebContent/img/b*.jpg` 在仓库里，对应的 `book` 行却不在。种子里的书名和出版社大多来自封面（b4 的中文书名和出版社、b5 和 b7 的出版社是推定的）；分类名是按体裁推测的；价格、库存、管理员口令是占位值，简介整段也是占位文字。会员和订单历史无法恢复 | 不做决定，目标系统的初始数据和数据迁移范围就定不下来；种子里的推测值如果被当成原值，会被写进目标系统的验收数据 | 提供原数据，然后重跑 migration-inventory；或者在 migration-strategy 中决定采用 `seed.sql` 作为初始数据（并标明哪些是占位值），放弃会员和订单历史 |

## Coverage

- Revision: git `425edd4`（分支 master）。`BookShop/` 下的原有文件没有改动，最近一次修改它们的提交是 `b7a282c`。新增的 `BookShop/db/` 和 `migration-plans/` 还没有提交。这是第三次盘点，原有 ID 不变。第二次盘点新增了 INV-035～INV-039 和 LEGACY-073，第三次没有新增 ID，只按复核后的复原说明更新了描述。
- Scanned paths:
  - `BookShop/src/**`（Java 源码是 GBK 编码，按 GBK 读取）。
  - `BookShop/WebContent/*.jsp`、`BookShop/WebContent/jsp/*.jsp`、`BookShop/WebContent/WEB-INF/web.xml`、`BookShop/WebContent/META-INF/MANIFEST.MF`、`BookShop/WebContent/css/*`、`BookShop/WebContent/img/*`（看了清单和文件格式）。
  - `BookShop/.classpath`、`BookShop/.project`、`BookShop/.settings/*`、`README.md`、`.gitignore`。
  - `BookShop/db/*` 的 4 个文件和 `migration-plans/bookshop/legacy-db-reconstruction.md`。
  - git 全部历史的文件名（查找 SQL/DDL/数据文件）；提交 `d5dadef`（StudentSystem，只核对了 `SQLHelper`、`Entity/Tag.java`、`Entity/Users.java`、`Service/*.java` 里的表名、`StudentDao.queryAllblog` 和“不一定对”注释的数量）；`774ebae:README.md`；`d5dadef` 和 `b7a282c` 的提交日期。
- Excluded or inaccessible paths:
  - `BookShop/WebContent/bootstrap/**`：内置的 Bootstrap 3.3.7 源码仓库，共 375 个文件，只核对了版本和页面引用到的路径。
  - `BookShop/WebContent/jsp/ckeditor/**`：内置的 CKEditor 4，只核对了版本和引用情况。
  - 工作区中已删除、但仍在 HEAD 提交里的上一轮迁移产物：`bookshop_app/`、`tests/`、`artifacts/`、`.github/`、`scripts/`、`docs/` 等。它们不是旧系统材料。
  - `openspec/`、`.claude/`。
  - 复原说明里 MySQL 8.0.36 的实测结果：本机没有 MySQL，没有复跑，按文档转述。
  - 无法访问：`.classpath` 引用的本机 jar（`<redacted-local-path>`）、原来的 MySQL 数据库实例、Tomcat 运行配置。

## System Summary

旧系统是一个部署在 Tomcat、上下文路径为 `/BookShop` 的 Java 8 Servlet/JSP 网上书店，数据存在 MySQL 库 `book`（`localhost:3310`）。

- 结构：4 个 Servlet 按 `opttype` 参数分派操作，调用 4 个 DAO。DAO 通过 `SQLHelper` 用字符串拼接的 JDBC SQL 访问数据库。结果放进 HttpSession 后 302 跳转到 JSP，页面用 JSTL 和 EL 渲染，UI 基于 Bootstrap 3。
- 角色：会员（role `1`）和管理员（role `2`）。`/jsp/*` 只检查是否登录，不检查角色。
- 会员功能：注册、登录、按销量浏览书目、按书名搜索、按分类筛选、查看详情、一键购买一本（不支付、不选数量）、查看自己的订单、修改密码、查看个人信息。
- 管理员功能：会员列表/搜索/删除；书籍列表/搜索/两步新增（第二步上传封面）/修改（只能改出版社、库存、售价）/删除；全部订单与总金额统计。
- 没有退出登录，没有自动化测试，没有构建脚本。原数据库丢失，`BookShop/db/` 里是推定的复原。

## Inventory

| ID | Area | Component or concern | Evidence | Notes |
|---|---|---|---|---|
| INV-001 | 构建 | Eclipse Dynamic Web Project，没有 Maven/Gradle/Ant；Java 源码/目标 1.8；Servlet facet 3.1；输出到 `build/classes` | `BookShop/.settings/org.eclipse.jdt.core.prefs:compiler.source`、`BookShop/.settings/org.eclipse.wst.common.project.facet.core.xml:jst.web`、`BookShop/.classpath:output` | jar 用本机绝对路径引用（`<redacted-local-path>`），离开作者机器无法构建；`.gitignore:*.jar` 排除了所有 jar |
| INV-002 | 运行容器 | Apache Tomcat。classpath 同时声明了 Tomcat v8.5 和 v9.0 运行时，`servlet-api.jar` 取自 Tomcat 8.5.41 | `BookShop/.classpath:org.eclipse.jst.server.tomcat.runtimeTarget` | 实际部署用哪个版本未知（LEGACY-063） |
| INV-003 | 部署描述 | `web.xml`：2 个过滤器、2 个 servlet 映射（`/uploadServlet.do`、`/downloadServlet.do`）；没有 welcome-file、error-page、session-config、security-constraint | `BookShop/WebContent/WEB-INF/web.xml:web-app` | 根元素没有 `version` 属性；其余 Servlet 用 `@WebServlet` 注解注册 |
| INV-004 | 部署配置 | 上下文路径 `BookShop`；`/WebContent` 部署为站点根，`/src` 编译到 `/WEB-INF/classes` | `BookShop/.settings/org.eclipse.wst.common.component:context-root` | |
| INV-005 | 过滤器 | `SetCharacterEncodingFilter`，映射 `/*`，把请求编码设为 UTF-8 | `BookShop/src/filter/SetCharacterEncodingFilter.java:SetCharacterEncodingFilter.doFilter` | 每次请求都强制设置（`ignore` 默认 true） |
| INV-006 | 认证过滤器 | `MyFilter`，映射 `/jsp/*`：session 中没有 `uid` 就 302 到 `../login.jsp` | `BookShop/src/filter/MyFilter.java:MyFilter.doFilter` | 不检查角色；每次请求都在 stdout 打印 `doFilter()` |
| INV-007 | 控制器 | `LoginServlet`，`/login.action`，处理 `addusers`（注册）和 `checkUsers`（登录） | `BookShop/src/controller/LoginServlet.java:LoginServlet.doGet` | doPost 转给 doGet；有一个未使用的实例字段 `session` |
| INV-008 | 控制器 | `BookServlet`，`/jsp/book.action`，处理 `queryAllbook`、`queryByname`、`queryBytag`、`bookDetail`、`buybook` | `BookShop/src/controller/BookServlet.java:BookServlet.doGet` | |
| INV-009 | 控制器 | `MyServlet`，`/jsp/my.action`，处理 `initMypage`、`queryMyorder`、`updatePwd` | `BookShop/src/controller/MyServlet.java:MyServlet.doGet` | |
| INV-010 | 控制器 | `AdminServlet`，`/jsp/admin.action`，处理 11 个 opttype：`queryAllcustomers`、`queryCustomers`、`deleteCustomers`、`queryAllbooks`、`queryBooks`、`addBooks`、`addBooksimg`、`showBooks`、`editBooks`、`deleteBooks`、`showAllmoney` | `BookShop/src/controller/AdminServlet.java:AdminServlet.doGet` | 封面上传也在这里（INV-024） |
| INV-011 | 失效控制器 | `UploadServlet`、`DownloadServlet`、`UsersSrevlet` 整个文件被注释，内容是作业上传下载和博客功能 | `BookShop/src/controller/UploadServlet.java`、`BookShop/src/controller/DownloadServlet.java`、`BookShop/src/controller/UsersSrevlet.java` | 被注释的代码调用的 `MyDao.queryMygbook`、`addMyhomework` 并不存在 |
| INV-012 | 数据访问 | `SQLHelper`：每次调用都用 `DriverManager` 新建连接；提供 `executeQueryList`、`executeQuery`（未被使用）、`executeUpdate`、`executeUpdateByParams`；捕获所有异常后只打印堆栈 | `BookShop/src/dbutil/SQLHelper.java:SQLHelper` | 连接存在静态字段 `conn` 中，多线程共享；没有连接池，也没有事务 |
| INV-013 | DAO | `SystemDao`：`checkUsers`、`checkPwd`、`checkRoles` | `BookShop/src/Service/SystemDao.java:SystemDao` | 拼接 SQL |
| INV-014 | DAO | `AdminDao`：用户/会员查询、注册、会员删除、分类查找、书籍增删改查、订单查询、金额汇总 | `BookShop/src/Service/AdminDao.java:AdminDao` | 只有两个删除方法用参数化语句 |
| INV-015 | DAO | `CustomerDao`：分类列表、书目（按销量排序）、详情、按名搜索、按分类筛选 | `BookShop/src/Service/CustomerDao.java:CustomerDao` | 拼接 SQL |
| INV-016 | DAO | `MyDao`：`findUsername`、`findUserrole`、`queryAllmyorder`、`updatePwd`、`buyBook` | `BookShop/src/Service/MyDao.java:MyDao` | 拼接 SQL |
| INV-017 | 持久化 | MySQL 库 `book`。从 SQL 推断出的列：`user(uid, uname, upwd, role)`、`customer(uid)`、`book(bid, bname, publishers, stock, price, tid, url, cont)`、`tag(tid, tname)`、`orders(oid, bid, uid)` | `BookShop/src/Service/AdminDao.java:AdminDao.addCustomers`、`AdminDao.addBook`、`AdminDao.queryAllorder`、`BookShop/src/Service/MyDao.java:MyDao.buyBook` | `uid`、`bid`、`oid` 在插入时省略，推断为自增。`AdminDao.queryAllorder` 中 `price` 不带表名也不报歧义，推断 `orders` 没有 `price` 列。`customer` 只写不读（LEGACY-073）。原始类型和约束未知（GAP-001），推定的复原见 INV-035 |
| INV-018 | 配置 | 硬编码连接：驱动 `com.mysql.cj.jdbc.Driver`，URL `jdbc:mysql://localhost:3310/book?useSSL=false&serverTimezone=Asia/Shanghai`，账号 root，密码明文写在源码里。还有一段被注释的 Oracle 连接配置（同样带明文凭据） | `BookShop/src/dbutil/SQLHelper.java:SQLHelper.url`、`SQLHelper.user` | 没有环境变量或外置配置 |
| INV-019 | 实体 | `Users`、`Book`、`Order`、`Tag` 在用；`Admin`、`Customer` 已定义但没有任何引用 | `BookShop/src/Entity/Users.java:Users`、`BookShop/src/Entity/Admin.java:Admin`、`BookShop/src/Entity/Customer.java:Customer` | 所有字段都是 `String`，包括价格、库存、销量 |
| INV-020 | 视图（公开） | `index.jsp`（首页轮播）、`login.jsp`、`register.jsp` | `BookShop/WebContent/index.jsp`、`BookShop/WebContent/login.jsp`、`BookShop/WebContent/register.jsp` | 不在 `/jsp/*` 下，不需要登录 |
| INV-021 | 视图（会员） | `jsp/buy.jsp`、`jsp/bookdetails.jsp`、`jsp/my.jsp`、`jsp/myorder.jsp`、`jsp/changepwd.jsp` | `BookShop/WebContent/jsp/buy.jsp`、`BookShop/WebContent/jsp/myorder.jsp` | JSTL `c:forEach` 读取 session 中的列表 |
| INV-022 | 视图（管理员） | `jsp/admin.jsp`、`jsp/bookadmin.jsp`、`jsp/add.jsp`、`jsp/addnext.jsp`、`jsp/editbook.jsp`、`jsp/oderadmin.jsp` | `BookShop/WebContent/jsp/admin.jsp`、`BookShop/WebContent/jsp/oderadmin.jsp` | `add.jsp`、`editbook.jsp` 导航栏的搜索框没有绑定任何动作 |
| INV-023 | 残留页面 | `jsp/download.jsp`、`jsp/upload.jsp`、`jsp/wirte.jsp` 的内容整体包在 HTML 注释里；`jsp/useredit.jsp` 提交 `opttype=update`，但没有对应处理 | `BookShop/WebContent/jsp/useredit.jsp:form frm1`、`BookShop/WebContent/jsp/upload.jsp` | 内容属于另一个项目（课程、博客、作业，角色是学生/老师/管理员） |
| INV-024 | 图片端点与存储 | `jsp/showpic.jsp?img=` 读取 `<站点根>/img/<img>` 并输出字节流；封面上传用 commons-fileupload 写进部署目录的 `/img` | `BookShop/WebContent/jsp/showpic.jsp:scriptlet`、`BookShop/src/controller/AdminServlet.java:AdminServlet.doGet#addBooksimg` | 路径用 Windows 反斜杠拼接；上传的文件不在仓库中 |
| INV-025 | 静态资源（自有） | CSS：`carousel.css`、`dashboard.css`、`offcanvas.css`、`signin.css`、`theme.css`、`wirte.css` | `BookShop/WebContent/css/` | `theme.css`、`wirte.css` 没有被在用页面引用 |
| INV-026 | 静态媒体 | `img/1.jpg`、`img/2.jpg`（轮播），`img/default.jpg`（默认头像），`img/b1.jpg`～`b9.jpg` 和 `b11.jpg`（书籍封面，共 10 张） | `BookShop/WebContent/img/` | 封面和书籍的对应关系原本存在数据库的 `book.url` 列里，不在仓库中（GAP-002）。`b6.jpg`、`b8.jpg` 的扩展名是 `.jpg`，内容其实是 PNG |
| INV-027 | 前端库 | 内置完整的 Bootstrap 3.3.7 源码仓库（含 `dist/`、`docs/`、`less/`、Grunt 构建等 375 个文件）。根目录页面用 `bootstrap/dist`，`/jsp/` 下的页面用 `bootstrap/docs/dist` | `BookShop/WebContent/bootstrap/package.json:version` | `docs/dist/fonts` 只有 eot/svg，没有 woff/woff2/ttf |
| INV-028 | 前端库（未用） | 内置 CKEditor 4（版权年份 2019），包括带 `.php` 文件的 samples 目录 | `BookShop/WebContent/jsp/ckeditor/ckeditor.js:header` | 只被已注释的 `wirte.jsp` 引用；位于 `/jsp/` 下，访问也需要登录 |
| INV-029 | 外部依赖 | 从 CDN `ajax.googleapis.com` 加载 jQuery 1.12.4。本地兜底文件 `bootstrap/docs/assets/js/vendor/jquery.min.js` 存在，但 `/jsp/` 下部分页面的兜底路径指向站点外。IE9 以下会加载 `oss.maxcdn.com` 的 html5shiv/respond | `BookShop/WebContent/jsp/buy.jsp:script jquery`、`BookShop/WebContent/index.jsp:script jquery` | 离线环境下，`/jsp/` 页面的 Bootstrap JS 交互不可用 |
| INV-030 | 认证与会话 | session 属性 `uid`、`role`（`1`=会员、`2`=管理员）；登录不更换 session ID；没有退出登录；超时用容器默认值 | `BookShop/src/controller/LoginServlet.java:LoginServlet.doGet#checkUsers` | 管理功能不做角色校验（LEGACY-050） |
| INV-031 | 页面数据传递 | 查询结果写进 HttpSession，再 302 跳转到 JSP 渲染（`clist`、`blist`、`tlist`、`sblist`、`eblist`、`molist`、`olist`、`sum`、`uname`、`role`） | `BookShop/src/controller/AdminServlet.java:AdminServlet.doGet`、`BookShop/src/controller/BookServlet.java:BookServlet.doGet` | 新增书籍的第一步还把表单字段放进 session |
| INV-032 | 日志 | 只有 `System.out.println`（包括完整 SQL）和 `printStackTrace` | `BookShop/src/Service/SystemDao.java:SystemDao.checkUsers`、`BookShop/src/Service/AdminDao.java:AdminDao.addBook` | 没有日志框架 |
| INV-033 | 源码编码 | Java 源码是 GBK（注释和中文字面量，例如 `MyDao.findUserrole` 里的“会员”“管理员”），JSP 是 UTF-8。Eclipse 只给 `login.jsp`、`register.jsp` 声明了 UTF-8 | `BookShop/.settings/org.eclipse.core.resources.prefs`、`BookShop/src/Service/MyDao.java:MyDao.findUserrole` | 用 UTF-8 编译 Java 源码会把中文字面量弄乱 |
| INV-034 | 测试 | 旧系统没有任何自动化测试 | `BookShop/`（全目录） | |
| INV-035 | 复原材料 | 推定的表结构：`user(uid INT 自增, uname VARCHAR(20), upwd VARCHAR(20), role INT)`、`customer(uid INT 主键)`、`tag(tid INT 自增, tname VARCHAR(20))`、`book(bid INT 自增, bname/publishers VARCHAR(100), stock INT, price DECIMAL(10,2), tid INT, url VARCHAR(255), cont VARCHAR(4000))`、`orders(oid INT 自增, bid INT, uid INT)`，所有列都是 NOT NULL；文件末尾有 4 个外键（RESTRICT） | `BookShop/db/schema.sql` | 不是原始 DDL。能确定的只有列名、`uid`/`bid`/`oid` 是自增列、`orders` 没有 `price` 列；列类型、长度、NOT NULL、`tag.tid` 自增和 4 个外键都是推定或占位（其中 `book.tid`、`orders.uid` 两个外键是占位）。`CREATE DATABASE` 没有 `IF NOT EXISTS`，库已存在时会报错停止 |
| INV-036 | 复原材料 | 复原环境的 MySQL 设置：端口 3310、`utf8mb4`/`utf8mb4_0900_ai_ci`、去掉 `ONLY_FULL_GROUP_BY` 的 `sql_mode`（保留 `STRICT_TRANS_TABLES`）、`default_authentication_plugin=mysql_native_password` | `BookShop/db/my.ini:mysqld` | 不是原来的配置，也不是对原服务器的推断，只是让旧 SQL 能跑的环境设置。只适用于 MySQL 8.0.x（8.4 默认禁用、9.x 已移除 `mysql_native_password`） |
| INV-037 | 复原材料 | 推定的种子数据：3 个分类、1 个管理员、10 本书（显式指定 bid 1～9 和 11） | `BookShop/db/seed.sql` | 价格、库存、简介和口令是占位值；没有会员和订单 |
| INV-038 | 复原材料 | SQL 回放脚本：把 DAO 原文 SQL 代入示例参数，覆盖注册、登录、个人页、书目、购买、订单、后台增删改、统计、删除会员和书籍；其中有 3 条预期报错（1055、1366、1451） | `BookShop/db/legacy-sql-check.sql` | 会写入测试数据，只验证 SQL 层；脚本里的 uid、bid 依赖种子的显式 ID 和自增值 |
| INV-039 | 复原材料 | 复原说明：逐项写明依据，按“确定/较高/推定/占位”分档；列出外键和 strict 模式四种组合的实测结果，以及使用方法 | `migration-plans/bookshop/legacy-db-reconstruction.md` | 文档自己的结论是：复原不等于补齐 GAP-001、GAP-002。末尾的“复核记录”列出了对第一版的 8 处更正（旁证降级、撤回 `sql_mode` 旁证、改正 `stock` 和自增类型的推理等） |

## Dependencies

| Dependency | Version | Evidence | Risk |
|---|---|---|---|
| JDK | 1.8 | `BookShop/.settings/org.eclipse.jdt.core.prefs:compiler.compliance` | 本机未安装 |
| Servlet API | 3.1（取自 Tomcat 8.5.41 的 `servlet-api.jar`） | `BookShop/.classpath:servlet-api.jar`、`BookShop/.settings/org.eclipse.wst.common.project.facet.core.xml:jst.web` | `javax.servlet` 命名空间 |
| Apache Tomcat | 8.5（`servlet-api.jar` 取自 8.5.41），另声明了 9.0 运行时 | `BookShop/.classpath:org.eclipse.jst.server.tomcat.runtimeTarget` | Tomcat 8.5 已于 2024-03 停止支持 |
| MySQL Connector/J | 8.0.11 | `BookShop/.classpath:mysql-connector-java-8.0.11.jar` | jar 不在仓库；版本较旧，有已知 CVE |
| Apache Commons FileUpload | 1.4 | `BookShop/.classpath:commons-fileupload-1.4.jar` | jar 不在仓库；1.4 受 CVE-2023-24998（上传 DoS）影响，1.5 修复 |
| Apache Commons IO | 2.6 | `BookShop/.classpath:commons-io-2.6.jar` | jar 不在仓库；作为 FileUpload 的运行期依赖；2.6 受 CVE-2021-29425 影响 |
| JSTL（`jstl.jar` 和 `standard.jar`） | 未知 | `BookShop/.classpath:jstl.jar`、`BookShop/WebContent/index.jsp:taglib` | jar 不在仓库（`WEB-INF/lib` 不存在）；taglib URI 是 `http://java.sun.com/jsp/jstl/core` |
| MySQL Server | 原版本未知（端口 3310）；驱动 8.0.11 支持 5.6、5.7、8.0；复原环境用 8.0.x（占位） | `BookShop/src/dbutil/SQLHelper.java:SQLHelper.url`、`BookShop/db/my.ini` | 版本和 `sql_mode` 都是推定的（GAP-001）；复原依赖的 `mysql_native_password` 在 8.4 默认禁用、9.x 已移除 |
| Bootstrap | 3.3.7 | `BookShop/WebContent/bootstrap/package.json:version` | 已停止维护；有 XSS 类 CVE（CVE-2018-14040、CVE-2018-14041、CVE-2018-14042、CVE-2019-8331） |
| jQuery | 1.12.4 | `BookShop/WebContent/bootstrap/docs/assets/js/vendor/jquery.min.js:header` | 有已知 CVE（CVE-2015-9251、CVE-2019-11358、CVE-2020-11022、CVE-2020-11023）；主要从 CDN 加载 |
| holder.js | 未核对 | `BookShop/WebContent/bootstrap/docs/assets/js/vendor/holder.min.js` | 只用于占位图，`/jsp/` 下的引用路径缺失 |
| CKEditor | 4.x（2019） | `BookShop/WebContent/jsp/ckeditor/ckeditor.js:header` | 未被使用 |
