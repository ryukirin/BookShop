# 旧数据库复原（GAP-001、GAP-002）

原库 `book` 的 DDL、服务器设置和数据都找不回来了。本文根据旧代码、作者上一个项目和封面图复原出一套能支撑旧系统运行的数据库，并逐项写明依据和可信度。它是推定的重建，不是原始材料。要不要把它当作旧库的基准，属于迁移决策。

复原产物在 `BookShop/db/`：

| 文件 | 内容 |
|---|---|
| `schema.sql` | 5 张表和 4 个外键（外键单独放在文件末尾，可以跳过） |
| `seed.sql` | 3 个分类、1 个管理员、10 本书 |
| `my.ini` | 端口、字符集、`sql_mode`、认证插件 |
| `legacy-sql-check.sql` | 把 DAO 里的原始 SQL 代入示例参数，按注册、登录、浏览、购买、后台增删改、账目统计的顺序回放 |

**实测结果**：在 MySQL 8.0.36 上加载 `schema.sql` 和 `seed.sql` 之后，`legacy-sql-check.sql` 里的语句全部按预期执行，只在三处报错，都在预期之内：8.0 默认 `sql_mode` 下书目查询报 1055；新增书籍时分类不存在报 1366；删除有订单的会员报 1451。没有出现列不存在或列名歧义的错误。

这只能说明复原结构和旧代码的 SQL 相容，不能证明原库就是这个样子：凡是能让这些 SQL 跑通的结构，都会得到同样的结果。Java 端没有运行（本机没有 JDK 和 Tomcat），涉及 JDBC 驱动行为的结论都标为“未实测”。

可信度分四档：

- **确定**：代码只允许这一种结构。
- **较高**：有直接旁证。
- **推定**：有间接依据，原库可能不同。
- **占位**：没有依据，为了能跑而选的值。

## 依据来源

1. **DAO 里的 SQL**：`BookShop/src/Service/*.java`。这是唯一的直接依据，能确定列名、哪些列自增，以及“哪些列名不能在多张表里重复”。
2. **作者的上一个项目 StudentSystem**（git 历史 `d5dadef`，2019-10）。BookShop（`b7a282c`，2020-09）是从它改出来的，但改动不少：
   - 两边的 `SQLHelper` 只有库名不同（`student` 和 `book`），配置的服务器地址都是 `localhost:3310`。地址相同、时间相隔将近一年，不能说明当时服务器的版本和设置一样。
   - 实体也改过：`Tag` 的字段从 `id` 改成了 `tid`，`Users` 的字段从 `id` 改成了 `uid`。
   - 历史 README（`git show 774ebae:README.md`）列出了一套带类型和约束的表设计，但它和 StudentSystem 自己的 SQL 对不上。比如 README 写的是 `USERS(USERID, UNAME, PWD)`、`TBRELA`、`COMMENTS`、`EVAL`，SQL 用的是 `user(uid, uname, pwd)`、`tbrelation`、`comment`、`evaluation`。SQL 里还有一张 `notes` 表，README 里根本没有。所以这份 README 只是设计稿，从中看出的建表习惯（主键 INT、名称和密码 VARCHAR(20)、长文本 VARCHAR(4000)、引用列标 FK）只能作为间接参考。
   - 作者在 StudentDao 的 10 条查询后面注释了“不一定对”。
3. **封面图**：`BookShop/WebContent/img/b*.jpg`，可以读出书名和出版社。
4. **实测**：在临时目录里运行便携版 MySQL 8.0.36，只用于验证，没有在本机安装。

## 服务器设置

| 项目 | 复原值 | 依据 | 可信度 |
|---|---|---|---|
| 端口、库名、账号 | 3310，`book`，root / 123456 | `SQLHelper.url`、`SQLHelper.user` | 确定 |
| 版本 | MySQL 8.0.x | 原版本不知道。驱动 Connector/J 8.0.11 支持 MySQL 5.6、5.7、8.0。选 8.0.x 只是为了搭复原环境，理由见“认证插件”一行 | 占位 |
| 字符集、排序规则 | `utf8mb4` / `utf8mb4_0900_ai_ci` | 连接串没有指定 `characterEncoding`，按驱动文档，连接字符集跟随服务器默认字符集（未实测）。中文要能正常存取，服务器默认字符集就得支持中文，`utf8`、`utf8mb4`、`gbk` 都满足；选 `utf8mb4` 是因为它是 8.0 的默认值。书名搜索不区分大小写（LEGACY-016）这一点，只要是 `_ci` 排序规则都成立，在 `utf8mb4_0900_ai_ci` 下已实测 | 推定（只推得出“支持中文”） |
| `sql_mode` | 8.0 默认值去掉 `ONLY_FULL_GROUP_BY` | 书目查询按 `(bname, tname)` 分组，又选了不在分组键里的列，8.0 默认设置下报 ERROR 1055（已实测）。原服务器是怎么让这些查询跑起来的不知道，至少有三种可能（见表下） | 占位 |
| strict 模式 | 保留 `STRICT_TRANS_TABLES` | 没有依据，沿用 8.0 默认值。它会影响 LEGACY-055 的结果，见“未定项” | 占位 |
| 认证插件 | `mysql_native_password` | 这是复原环境的要求，不是对原服务器的推断。驱动是 8.0.11，连接串有 `useSSL=false`，但没有 `allowPublicKeyRetrieval=true`，连 8.0 默认的 `caching_sha2_password` 账号会报 “Public Key Retrieval is not allowed”（未实测）。8.4 默认禁用、9.x 已移除这个插件，所以复原环境用 8.0.x。如果原库是 5.6 或 5.7，这个插件本来就是默认值 | 推定，未实测 |

书目查询能在原服务器上执行，至少有三种解释，代码里都找不到能区分它们的证据：

1. 服务器是 5.7 或 8.0，手动去掉了 `ONLY_FULL_GROUP_BY`。复原采用的是这一种。
2. 服务器是 5.6 或更早。那时 `ONLY_FULL_GROUP_BY` 不在默认 `sql_mode` 里，不用改配置。
3. `book.bname` 有唯一约束，而且不允许为空。这样即使开着 `ONLY_FULL_GROUP_BY`，查询也能执行，已实测成立。代价是同名书无法新增。

## 表结构

DAO 插入时只给出部分列，所以每张表都不能有“不允许为空、又没有默认值”的其他列。这条结论只在 strict 模式下成立；非 strict 模式下，缺少的列会被填成隐式默认值，只产生警告。

### user

| 列 | 复原定义 | 依据 | 可信度 |
|---|---|---|---|
| uid | `INT AUTO_INCREMENT` 主键 | 注册时不写 uid，插入后再按用户名查回 uid（`AdminDao.addCustomers`），所以它是自增列，这一点确定。用 INT 是推定（MySQL 也允许 BIGINT、甚至 FLOAT 自增） | 自增确定，类型推定 |
| uname | `VARCHAR(20) NOT NULL`，不加唯一约束 | 列名确定。长度参考 StudentSystem README 里的 `USERS.UNAME`，属于间接参考。用户名不重复是由代码 `checkUserByUname` 保证的，库里有没有唯一约束不知道 | 推定 |
| upwd | `VARCHAR(20) NOT NULL` | 长度参考 README 的 `USERS.PWD`，间接参考。密码明文存储（LEGACY-049） | 推定 |
| role | `INT NOT NULL` | 代码按字符串 `"1"` / `"2"` 比较，整数和字符串类型都行。不能是 `TINYINT(1)`：Connector/J 默认把它读成 Boolean，`toString()` 会得到 `"true"`（未实测） | 推定 |

### customer

| 列 | 复原定义 | 依据 | 可信度 |
|---|---|---|---|
| uid | `INT` 主键，外键指向 `user.uid` | 代码只写 uid。删除会员时先删 `customer` 再删 `user`：这个顺序和外键相容，但没有外键时也可能这么写，不能证明有外键 | 推定 |

实体 `Customer` 的 cid、cname 和实体 `Admin` 都没有被任何 SQL 用到，所以没有建 `admin` 表。

### tag

| 列 | 复原定义 | 依据 | 可信度 |
|---|---|---|---|
| tid | `INT` 主键，自增 | 列名确定。它和 `book.tid` 做等值连接，两边类型应该一致，但具体类型不知道。代码不往这张表插数据，加自增只是为了方便维护 | 列名确定，类型推定，自增占位 |
| tname | `VARCHAR(20) NOT NULL`，不加唯一约束 | 列名确定。长度参考 README 的 `TAG.TNAME`，间接参考。`queryTagByTname` 遇到重名分类时取最后一行，库里有没有唯一约束不知道 | 推定 |

### book

| 列 | 复原定义 | 依据 | 可信度 |
|---|---|---|---|
| bid | `INT AUTO_INCREMENT` 主键 | 插入时省略，所以是自增列。类型同 `user.uid` | 自增确定，类型推定 |
| 列顺序 | bid, bname, publishers, stock, price, tid, url, cont | 照抄 `addBook` 的 INSERT 列清单。原表的列顺序不知道，也不影响功能 | 占位 |
| bname, publishers | `VARCHAR(100) NOT NULL` | 长度不知道，取了宽松的值 | 占位 |
| stock | `INT NOT NULL` | `MyDao.buyBook` 用 `Integer.parseInt` 读库存，带小数位的类型会抛异常（DECIMAL(10,2) 读出 `"5.00"`，FLOAT 读出 `"5.0"`）。剩下的整数类型、DECIMAL(n,0) 和字符串类型都可以 | “不带小数位”较高，INT 推定 |
| price | `DECIMAL(10,2) NOT NULL` | 只知道它要能被 `Float.parseFloat` 解析，FLOAT、DOUBLE、VARCHAR 也都能跑 | 占位 |
| tid | `INT NOT NULL`，外键指向 `tag.tid` | 列名确定。外键只是参考 README“引用列标 FK”的写法加的，没有代码证据 | 列推定，外键占位 |
| url | `VARCHAR(255) NOT NULL` | 后台上传的文件名是 13 位毫秒时间戳加客户端文件名，取宽松长度 | 占位 |
| cont | `VARCHAR(4000) NOT NULL` | 长度参考 README 的 `CONT VARCHAR(4000)`，间接参考 | 推定 |

所有列都设为 NOT NULL，因为 DAO 对每一列都调用 `toString()`，任何一列是 NULL 都会让整页报 500（LEGACY-059）。这能说明实际数据里没有 NULL，但不能说明列定义就是 NOT NULL。

### orders

| 列 | 复原定义 | 依据 | 可信度 |
|---|---|---|---|
| oid | `INT AUTO_INCREMENT` 主键 | 插入时省略 | 自增确定，类型推定 |
| bid | `INT NOT NULL`，外键指向 `book.bid` | `deleteBookById` 先删订单再删书。这个顺序和外键相容，但不能证明有外键 | 推定 |
| uid | `INT NOT NULL`，外键指向 `user.uid` | 没有代码证据；`deleteCustomerById` 不删订单，反而更像没有外键 | 外键占位 |
| 没有 price 列 | | `queryAllorder` 里 `price` 不带表名，也没有报列名歧义 | 确定 |

### 跨表的列名约束

几条查询里的列不带表名，所以这些列名不能在相关的表里重复出现。比如：

- `queryaBookByid` 的 `bid` 不带表名，所以 `tag` 不能有 `bid` 列；
- `CustomerDao.queryAllbook` 的 `url`、`cont` 不带表名，所以 `orders` 和 `tag` 不能有同名列；
- `queryAllorder` 的 `oid` 不带表名，所以 `book` 和 `user` 不能有 `oid` 列。

复原结构满足所有这些约束，实测没有出现歧义报错。

## 未定项对旧系统行为的影响（实测）

外键和 strict 模式是两个独立的未知数。下表是四种组合在两个场景里的实测结果（只在 SQL 层实测；页面表现是按 Servlet 代码推出来的）。

旧代码捕获了所有 SQL 异常。写操作失败时返回 0，Servlet 不跳转，页面是空白的 200（LEGACY-033）。

| 组合 | 新增书籍时分类不存在（LEGACY-055） | 删除有订单的会员（LEGACY-044） |
|---|---|---|
| 有外键 + strict（复原采用） | ERROR 1366，书没有插入，页面空白 | `customer` 行被删掉，删除 `user` 时报 ERROR 1451，页面空白。会员仍在会员列表里，也还能登录 |
| 无外键 + strict | ERROR 1366，书没有插入，页面空白 | 删除成功，跳回会员列表。订单变成孤儿行，从账目统计里消失 |
| 无外键 + 非 strict | `tid` 被写成 0，书插入了，跳回书目列表，但在所有列表里都看不到它（baseline 原来描述的就是这种情况） | 同上 |
| 有外键 + 非 strict | ERROR 1452，书没有插入，页面空白 | 和第一行相同 |

如果 `sql_mode` 保留 8.0 默认值，购买页、后台书目页和书籍详情页全部是空列表。原因是查询报 1055，`SQLHelper` 把异常吞掉了，返回空结果。

## 种子数据

| bid | 封面 | 书名 | 出版社 | 怎么得到的 | 分类 |
|---|---|---|---|---|---|
| 1 | b1.jpg | 你一生的故事 | 译林出版社 | 封面 | 小说 |
| 2 | b2.jpg | 盛夏的方程式 | 南海出版公司 | 封面 | 小说 |
| 3 | b3.jpg | 诗经译注（修订本） | 中华书局 | 封面 | 诗歌 |
| 4 | b4.jpg | 鲍勃·迪伦诗歌集（1961-2012） | 广西师范大学出版社 | 封面只有英文书名 *The Lyrics 1961–2012*（八册套装）和“新民说”标识，中文书名和出版社是按这个品牌推定的 | 诗歌 |
| 5 | b5.jpg | 刺猬的优雅 | 南海出版公司 | 书名来自封面。封面没有印出版社，按这个封面版本推定 | 小说 |
| 6 | b6.jpg | 清欢 | 河北教育出版社 | 封面（“林清玄经典散文”系列） | 散文 |
| 7 | b7.jpg | 林泉 | 河北教育出版社 | 封面。出版社字样太小，按同系列推定 | 散文 |
| 8 | b8.jpg | 玄想 | 河北教育出版社 | 封面 | 散文 |
| 9 | b9.jpg | 月亮和六便士 | 晨光出版社 | 封面（“云南出版集团｜晨光出版社”，字较小） | 小说 |
| 11 | b11.jpg | 小王子 | 天津人民出版社 | 封面 | 小说 |

- **bid**：沿用封面文件的编号，方便对照。仓库里没有 b10.jpg，原因不明，bid 10 留空。
- **分类**：小说、散文、诗歌三类是按书的体裁推测的，原分类名不知道。
- **简介**：作者、译者、丛书名来自封面；国籍标注（如“[日]”）和体裁说明（如“长篇小说”）是补写的。整段都是占位文字。
- **价格、库存**：占位值，不是原值。
- **管理员账号**：`admin` / `123456` 是占位值。注册功能只能创建会员，管理员只能直接在库里建。
- **不包含的内容**：会员和订单历史无法恢复，所以没有种子数据。这两类数据可以在界面上通过注册和购买产生。
- **封面文件格式**：`b6.jpg`、`b8.jpg` 的内容其实是 PNG。`showpic.jsp` 原样输出字节，浏览器能识别。

种子里的推测值和占位值不是原值。如果原样写进目标系统，它们会进入验收数据。

## 使用方法

1. 安装 MySQL 8.0.x，套用 `BookShop/db/my.ini`。`default_authentication_plugin` 要在初始化数据目录之前加上。
2. 把 root 改成旧代码用的口令：`ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';`
3. 依次执行 `mysql -uroot -p < schema.sql` 和 `mysql -uroot -p < seed.sql`。
4. （可选）`mysql -uroot -p --force -t -n book < legacy-sql-check.sql`。这一步会写入测试数据，而且脚本里的 uid、bid 依赖刚加载完种子时的值，所以只能在新建的库上跑一次。要再跑，先删库，再从第 3 步开始。要模拟“原库没有外键”，执行 `schema.sql` 时跳过末尾的 `ALTER TABLE` 语句。

## 两个缺口仍未关闭

复原不等于补齐。要不要拿它当旧库的基准，在 migration-strategy 中决定。复原也确定不了的部分如下。

**GAP-001**：

- 有没有外键、是否开启 strict 模式：两者的组合决定 LEGACY-044、055 的旧行为；
- `price` 的实际类型；
- 各列长度和唯一约束（包括 `bname` 是否唯一）；
- MySQL 版本和字符集；
- 原服务器是怎样让分组查询跑起来的（三种可能见“服务器设置”）：决定 LEGACY-046 能否原样执行。

**GAP-002**：

- 原来的分类名、价格、库存、简介和管理员账号；
- 会员和订单历史已经无法恢复。

这些只有找到原库或作者本人才能确认。

## 复核记录

2026-10-10 复核，更正了第一版中的以下问题：

- 第一版说 `Tag.java` 和 StudentSystem 的“完全一样”、`SQLHelper`“一模一样”。实际上 `Tag`、`Users` 的字段都改过名，`SQLHelper` 的库名也不同。
- 第一版把 StudentSystem README 当作类型和长度的直接依据，并把 `tag` 标为“较高”。README 和 StudentSystem 自己的 SQL 对不上，现在改为间接参考，`tag` 降为“推定”。
- 第一版用 `StudentDao.queryAllblog` 推定原服务器关掉了 `ONLY_FULL_GROUP_BY`，并说这条查询“无论设什么键都过不了”。这个说法不对：只要 `tbrelation` 只以 `bid` 为键，它就能通过；作者还在旁边注释了“不一定对”。这条旁证已撤掉，`sql_mode` 降为“占位”，另列出三种可能的解释。
- 第一版用“INSERT 写法像 MySQL Workbench 生成的”来推定版本和列顺序。这一点没有核实，已删除。版本降为“占位”。
- “只有整数列能自增”有误，已改为“自增确定，类型推定”。`stock` 的依据只能排除带小数位的类型，已改正。
- “不能有其他非空列”只在 strict 模式下成立，已补上前提。`book.tid`、`orders.uid` 的外键没有代码证据，降为“占位”。
- 第一版说四种组合下页面表现都一样，这不准确。三种组合是空白页，“无外键 + 非 strict”会跳回书目列表。已改正。
- 第一版说简介只写了封面信息，实际上国籍和体裁是补写的，已改正。
