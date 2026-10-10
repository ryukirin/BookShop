-- BookShop 目标表结构（GAP-001、REQ-DATA-001、DEC-007、MIG-RULE-018）。
-- 按旧代码的列名重建，补上约束；不建只写不读的 customer 表（LEGACY-073）。
-- 金额一律存整数分（MIG-RULE-007）。建库后由 initdb 设置 journal_mode=WAL、user_version=1。

CREATE TABLE user (
  uid             INTEGER PRIMARY KEY AUTOINCREMENT,
  uname           TEXT    NOT NULL COLLATE NOCASE UNIQUE CHECK (length(uname) BETWEEN 1 AND 20),
  upwd            TEXT    NOT NULL CHECK (length(upwd) BETWEEN 1 AND 255),
  role            INTEGER NOT NULL CHECK (role IN (1, 2)),
  active          INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
  session_version INTEGER NOT NULL DEFAULT 0 CHECK (session_version >= 0)
) STRICT;

CREATE TABLE tag (
  tid   INTEGER PRIMARY KEY,
  tname TEXT    NOT NULL COLLATE NOCASE UNIQUE CHECK (length(tname) BETWEEN 1 AND 20)
) STRICT;

CREATE TABLE book (
  bid         INTEGER PRIMARY KEY AUTOINCREMENT,
  bname       TEXT    NOT NULL CHECK (length(bname) BETWEEN 1 AND 100),
  publishers  TEXT    NOT NULL CHECK (length(publishers) BETWEEN 1 AND 100),
  stock       INTEGER NOT NULL CHECK (stock BETWEEN 0 AND 999999),
  price_cents INTEGER NOT NULL CHECK (price_cents BETWEEN 0 AND 9999999),
  tid         INTEGER NOT NULL REFERENCES tag (tid),
  url         TEXT    NOT NULL CHECK (length(url) BETWEEN 5 AND 69),
  cont        TEXT    NOT NULL CHECK (length(cont) BETWEEN 1 AND 4000),
  on_sale     INTEGER NOT NULL DEFAULT 1 CHECK (on_sale IN (0, 1))
) STRICT;

CREATE TABLE orders (
  oid              INTEGER PRIMARY KEY AUTOINCREMENT,
  bid              INTEGER NOT NULL REFERENCES book (bid),
  uid              INTEGER NOT NULL REFERENCES user (uid),
  unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents BETWEEN 0 AND 9999999)
) STRICT;

CREATE INDEX orders_bid ON orders (bid);
CREATE INDEX orders_uid ON orders (uid);

-- 新增书籍第一步的服务端草稿，每个管理员一行（LEGACY-026、LEGACY-071）。
CREATE TABLE addbook_draft (
  uid         INTEGER PRIMARY KEY REFERENCES user (uid),
  bname       TEXT    NOT NULL CHECK (length(bname) BETWEEN 1 AND 100),
  publishers  TEXT    NOT NULL CHECK (length(publishers) BETWEEN 1 AND 100),
  stock       INTEGER NOT NULL CHECK (stock BETWEEN 0 AND 999999),
  price_cents INTEGER NOT NULL CHECK (price_cents BETWEEN 0 AND 9999999),
  tid         INTEGER NOT NULL REFERENCES tag (tid),
  cont        TEXT    NOT NULL CHECK (length(cont) BETWEEN 1 AND 4000)
) STRICT;
