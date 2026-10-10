-- BookShop 旧系统数据库 `book` 的复原表结构（MySQL 8.0）
--
-- 原库已经丢失。本文件是根据旧代码里的 SQL 复原的，不是原始 DDL。
-- 每一列的依据和可信度见 migration-plans/bookshop/legacy-db-reconstruction.md。
-- 服务器设置（端口、字符集、sql_mode、认证插件）见同目录的 my.ini。
--
-- 外键单独放在文件末尾。要模拟“原库没有外键”的情况，跳过最后一段即可。
-- 库 `book` 已存在时 CREATE DATABASE 会报错，避免误覆盖现有数据。

CREATE DATABASE `book` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `book`;

-- 账号表。注册写 role 1（会员），管理员 role 2 只能直接在库里建。口令明文存储。
CREATE TABLE `user` (
  `uid`   INT         NOT NULL AUTO_INCREMENT,
  `uname` VARCHAR(20) NOT NULL,
  `upwd`  VARCHAR(20) NOT NULL,
  `role`  INT         NOT NULL COMMENT '1=会员，2=管理员',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB;

-- 会员表。代码只写入 uid，注册时和 user 行一起插入。
CREATE TABLE `customer` (
  `uid` INT NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB;

-- 分类表。界面上没有新增入口，只能直接在库里维护。
CREATE TABLE `tag` (
  `tid`   INT         NOT NULL AUTO_INCREMENT,
  `tname` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`tid`)
) ENGINE=InnoDB;

-- 书籍表。列顺序照抄 AdminDao.addBook 的 INSERT 列清单，原表顺序不知道。
-- url 只存文件名，文件在部署目录 img/ 下；后台上传的文件名是“13 位毫秒时间戳 + 原文件名”。
CREATE TABLE `book` (
  `bid`        INT           NOT NULL AUTO_INCREMENT,
  `bname`      VARCHAR(100)  NOT NULL,
  `publishers` VARCHAR(100)  NOT NULL,
  `stock`      INT           NOT NULL,
  `price`      DECIMAL(10,2) NOT NULL,
  `tid`        INT           NOT NULL,
  `url`        VARCHAR(255)  NOT NULL,
  `cont`       VARCHAR(4000) NOT NULL,
  PRIMARY KEY (`bid`)
) ENGINE=InnoDB;

-- 订单表。一行代表买 1 本，不记录成交价和时间；金额总是取 book 的当前售价。
CREATE TABLE `orders` (
  `oid` INT NOT NULL AUTO_INCREMENT,
  `bid` INT NOT NULL,
  `uid` INT NOT NULL,
  PRIMARY KEY (`oid`)
) ENGINE=InnoDB;

-- 外键（均为默认的 RESTRICT）。原库有没有外键不知道：
-- customer.uid、orders.bid 的删除顺序和外键相容（推定），book.tid、orders.uid 没有代码证据（占位）。
-- 有外键时：删除有订单的会员，customer 行删掉了，user 行删不掉（LEGACY-044）；
-- 新增书籍时分类不存在，插入失败。
ALTER TABLE `customer` ADD CONSTRAINT `fk_customer_user` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`);
ALTER TABLE `book`     ADD CONSTRAINT `fk_book_tag`      FOREIGN KEY (`tid`) REFERENCES `tag`  (`tid`);
ALTER TABLE `orders`   ADD CONSTRAINT `fk_orders_book`   FOREIGN KEY (`bid`) REFERENCES `book` (`bid`);
ALTER TABLE `orders`   ADD CONSTRAINT `fk_orders_user`   FOREIGN KEY (`uid`) REFERENCES `user` (`uid`);
