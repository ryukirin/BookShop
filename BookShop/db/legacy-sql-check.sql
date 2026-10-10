-- 用旧代码里的原始 SQL 回放一遍主要流程，检查复原库能否支撑旧系统。
-- 前提：新建的库，刚执行完 schema.sql 和 seed.sql。脚本里的 uid、bid 依赖这时的显式 ID 和自增值，只能跑一次。
-- 运行：mysql -uroot -p --force -t -n --default-character-set=utf8mb4 book < legacy-sql-check.sql
-- 语句按 DAO 原文抄录，只把拼接的参数换成示例值；两个删除方法用 setString 传参，这里写成带引号的字面量。
-- 预期会报错的语句已在注释中标出。
-- 会改数据：跑完之后库里多出测试会员、测试书和订单。

USE `book`;

SELECT '== 0 旧代码在 MySQL 8.0 默认 sql_mode 下：书目查询报 ERROR 1055 ==' AS step;
SET SESSION sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
-- CustomerDao.queryAllbook（预期 ERROR 1055）
select bname, url, cont, price, IFNULL(count(orders.bid),0) as num,book.bid
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid
group by bname, tname
order by num DESC;

-- 以下按 my.ini 的设置执行
SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

SELECT '== 1 注册：LoginServlet#addusers ==' AS step;
-- AdminDao.checkUserByUname：查不到才允许注册
select uid,uname,role from book.user where uname = '张三';
-- AdminDao.addCustomers
INSERT INTO book.user (uname,upwd,role) VALUES ('张三','abc123','1');
select uid,uname,role
from book.user
where uname = '张三';
INSERT INTO book.customer (uid) VALUES ('2');

SELECT '== 2 登录：LoginServlet#checkUsers（会员 role 1，管理员 role 2） ==' AS step;
select uid,uname,role
from book.user
where uname = '张三';
select upwd from user where uid='2';
select role from book.user where uid = '2';
select uid,uname,role
from book.user
where uname = 'admin';
select upwd from user where uid='1';
select role from book.user where uid = '1';

SELECT '== 3 个人页：MyDao.findUsername / findUserrole ==' AS step;
select uname from user where uid='2';
select role from user where uid='2';

SELECT '== 4 书目：CustomerDao ==' AS step;
-- queryAlltag
select tname from tag;
-- queryAllbook
select bname, url, cont, price, IFNULL(count(orders.bid),0) as num,book.bid
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid
group by bname, tname
order by num DESC;
-- queryByName('六便士')
select bname, url, cont, price, IFNULL(count(orders.bid),0) as num,book.bid
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid and bname like '%六便士%'
group by bname, tname
order by num DESC;
-- queryByTag('散文')
select bname, url, cont, price, IFNULL(count(orders.bid),0) as num, book.bid
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid and tname = '散文'
group by bname, tname
order by num DESC;
-- showBook('9')
select bname, tname, publishers, cont, stock, price, url, IFNULL(count(orders.bid),0) as num, book.bid
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid and book.bid = '9'
group by bname, tname;

SELECT '== 5 购买：MyDao.buyBook，会员 2 买 bid 9 两次、bid 1 一次 ==' AS step;
-- AdminDao.queryaBookByid 取库存，Java 端 Integer.parseInt 后减 1
select bid, bname, tname, publishers, cont, stock, price
from book.tag ,book.book
where book.tid = tag.tid and book.bid = '9';
update book set stock='99' where bid='9';
INSERT INTO `book`.`orders` (`bid`, `uid`) VALUES ('9', '2');
update book set stock='98' where bid='9';
INSERT INTO `book`.`orders` (`bid`, `uid`) VALUES ('9', '2');
update book set stock='99' where bid='1';
INSERT INTO `book`.`orders` (`bid`, `uid`) VALUES ('1', '2');

SELECT '== 6 我的订单：MyDao.queryAllmyorder ==' AS step;
select bname,uname,price
from book.orders,book.book,book.user
where orders.uid = '2' and orders.uid = user.uid and
book.bid = orders.bid;

SELECT '== 7 账目统计：AdminDao.queryAllorder（Java 端再用 float 累加 price） ==' AS step;
select oid,bname,uname,price
from book.orders,book.book,book.user
where orders.uid = user.uid and book.bid = orders.bid;

SELECT '== 8 后台书目：AdminDao.queryAllbook / queryBookByname / queryBookByid ==' AS step;
select book.bid, bname, tname, publishers, cont, stock, price, IFNULL(count(orders.bid),0) as num
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid
group by bname, tname
order by book.bid ASC;
select book.bid, bname, tname, publishers, cont, stock, price, IFNULL(count(orders.bid),0) as num
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid and bname like '%的%'
group by bname, tname
order by book.bid ASC;
select bid, bname, tname, publishers, cont, stock, price
from book.tag ,book.book
where book.tid = tag.tid and book.bid = '9';

SELECT '== 9 新增书籍：AdminDao.queryTagByTname + addBook ==' AS step;
select tid from tag where tname = '小说';
INSERT INTO `book`.`book` (`bname`, `publishers`, `stock`, `price`, `tid`, `url`, `cont`) VALUES ('Python入门', '测试出版社', '10', '25.5', '1', '1700000000000cover.jpg', '测试简介');
-- 分类不存在时 queryTagByTname 返回 null，拼进 SQL 成了字符串 'null'（预期 ERROR 1366，书没有插入）
select tid from tag where tname = '不存在的分类';
INSERT INTO `book`.`book` (`bname`, `publishers`, `stock`, `price`, `tid`, `url`, `cont`) VALUES ('孤儿书', '测试出版社', '10', '25.5', 'null', '1700000000001cover.jpg', '测试简介');

SELECT '== 10 编辑书籍：AdminDao.updateBook（bid 12） ==' AS step;
update book set stock='8' where bid='12';
update book set publishers='改后出版社' where bid='12';
update book set price='19.9' where bid='12';
select bid, bname, tname, publishers, cont, stock, price
from book.tag ,book.book
where book.tid = tag.tid and book.bid = '12';

SELECT '== 11 搜索不区分大小写（utf8mb4_0900_ai_ci）：queryByName(python) ==' AS step;
select bname, url, cont, price, IFNULL(count(orders.bid),0) as num,book.bid
from book.tag, book.orders right outer join book.book
on orders.bid = book.bid
where book.tid = tag.tid and bname like '%python%'
group by bname, tname
order by num DESC;

SELECT '== 12 修改密码：MyDao.updatePwd ==' AS step;
UPDATE user SET upwd='new456' where uid='2';
select upwd from user where uid='2';

SELECT '== 13 会员管理：AdminDao.queryCustomer / queryUserByUname ==' AS step;
select uid,uname,role
from book.user
where role = '1';
select uid,uname,role
from book.user
where role = '1' and uname = '张三';

SELECT '== 14 删除有订单的会员：AdminDao.deleteCustomerById(2)（第二句预期 ERROR 1451） ==' AS step;
delete from customer where uid='2';
delete from user where  uid='2';
-- 结果：customer 行没了，user 行还在，会员列表里仍然有他，也还能登录
select uid,uname,role from book.user where role = '1';
select count(*) as customer_rows_for_uid2 from customer where uid = 2;
-- 再走一遍登录（口令已在第 12 步改成 new456）：三条查询都能查到，登录仍然成功
select uid,uname,role
from book.user
where uname = '张三';
select upwd from user where uid='2';
select role from book.user where uid = '2';

SELECT '== 15 删除没有订单的会员：注册李四后删除 ==' AS step;
INSERT INTO book.user (uname,upwd,role) VALUES ('李四','abc123','1');
INSERT INTO book.customer (uid) VALUES ('3');
delete from customer where uid='3';
delete from user where  uid='3';
select uid,uname,role from book.user where role = '1';

SELECT '== 16 删除书籍：AdminDao.deleteBookById(9)，先删订单再删书 ==' AS step;
delete from orders where bid='9';
delete from book where bid='9';
select oid,bname,uname,price
from book.orders,book.book,book.user
where orders.uid = user.uid and book.bid = orders.bid;
