# StudentSystem
课程管理系统（JavaEE课程设计）
## 功能
  1.是学生登录该网站可以查看所有课程，所有博客，可以上交作业，写博客，可以更改自己的密码，也可以查看自己的课程和博客。
  2.是教师登录该网站可以查看到自己上的课程，自己的博客，也可以开课。
  3.是管理员登录该网站可以对该网站用户等进行管理。
## 数据存储
Mysql
### 表结构
ADMIN(ANO，ANAME)

BLOG(BID,BNAME,CONT,USERID)

CLA (CLA)

COMMENTS(COID,CONT,USERID,BID)

COURSE(CNO,CNAME	,PROTABLE,CONT,OUTLINE,CLA,TNO)

EVAL(EID,STARS,USERID,BID)

HOMEWORK(HID,HNAME,GBOOK,CID)

RLOE(RID,RNAME)

SC(SNO,CNO,SCORE)

STUDENT(SNO,SNAME)

STUDENTHOMEWORK(STID,BOOK,SNO,HID)

TAG(TID,TNAME)

TAGSTAT(TID	,STAT)

TBRELA(BID,TID,USERID)

TEACHER(TNO,TNAME)

USERROLE(USERID,RID)

USERS(USERID,UNAME,PWD)

表1 ADMIN表

| ADMIN  |             |          |          |
| :----: | :---------: | :------: | :------: |
| 数据名 |    类型     |   约束   |   备注   |
|  ANO   |     INT     |    PK    | 管理员号 |
| ANAME  | VARCHAR(20) | NOT NULL | 管理员名 |

 

表2 BLOG表

|  BLOG  |             |          |          |
| :----: | :---------: | :------: | :------: |
| 数据名 |    类型     |   约束   |   备注   |
|  BID   |     INT     |    PK    |  博客号  |
| BNAME  | VARCHAR(20) | NOT NULL |  博客名  |
|  CONT  |    LONG     | NOT NULL | 博客内容 |
| USERID |     INT     |    FK    | 创建者号 |

 

表3 CLA表

|  CLA   |             |      |        |
| :----: | :---------: | :--: | :----: |
| 数据名 |    类型     | 约束 |  备注  |
|  CLA   | VARCHAR(20) |  PK  | 分类名 |

 

表4 COMMENTS表

| COMMENTS |              |          |          |
| :------: | :----------: | :------: | :------: |
|  数据名  |     类型     |   约束   |   备注   |
|   COID   |     INT      |    PK    | 管理员号 |
|   CONT   | VARCHAR(200) | NOT NULL | 管理员名 |
|  USERID  |     INT      |    FK    | 发布者号 |
|   BID    |     INT      |    FK    |  博客号  |

 

表5 COURSE表

|  COURSE  |               |          |        |
| :------: | :-----------: | :------: | :----: |
|  数据名  |     类型      |   约束   |  备注  |
|   CNO    |      INT      |    PK    | 课程号 |
|  CNAME   |  VARCHAR(20)  | NOT NULL | 课程名 |
| PROTABLE | VARCHAR(4000) | NOT NULL | 进度表 |
|   CONT   | VARCHAR(4000) | NOT NULL |  简介  |
| OUTLINE  | VARCHAR(4000) | NOT NULL |  大纲  |
|   CLA    | VARCHAR(200)  |    FK    |  分类  |
|   TNO    |      INT      |    FK    | 教师号 |

 

表6 EVAL表

|  EVAL  |      |          |          |
| :----: | :--: | :------: | :------: |
| 数据名 | 类型 |   约束   |   备注   |
|  EID   | INT  |    PK    |  评价号  |
| STARS  | INT  | NOT NULL |   评价   |
| USERID | INT  |    FK    | 评价者号 |
|  BID   | INT  |    FK    |  博客号  |

 

表7 HOMEWORK表

| HOMEWORK |             |          |            |
| :------: | :---------: | :------: | :--------: |
|  数据名  |    类型     |   约束   |    备注    |
|   HID    |     INT     |    PK    |   作业号   |
|  HNAME   | VARCHAR(20) | NOT NULL |   作业名   |
|   CID    |     INT     |    FK    |   课程号   |
|  GBOOK   | VARCHAR(50) | NOT NULL | 实验指导书 |

 

表8 RLOE表

|  RLOE  |             |          |        |
| :----: | :---------: | :------: | :----: |
| 数据名 |    类型     |   约束   |  备注  |
|  RID   |     INT     |    PK    | 角色号 |
| RNAME  | VARCHAR(20) | NOT NULL | 角色名 |

 

表9 SC表

|   SC   |      |          |        |
| :----: | :--: | :------: | :----: |
| 数据名 | 类型 |   约束   |  备注  |
|  SNO   | INT  |  PK,FK   | 学生号 |
|  CNO   | INT  |  PK,FK   | 课程名 |
| SCORE  | INT  | NOT NULL |  成绩  |

 

表10 STUDENT表

| STUDENT |             |          |        |
| :-----: | :---------: | :------: | :----: |
| 数据名  |    类型     |   约束   |  备注  |
|   SNO   |     INT     |    PK    | 学生号 |
|  SNAME  | VARCHAR(20) | NOT NULL | 学生名 |

 

表11 STUDENTHOMEWORK表

| STUDENTHOMEWORK |             |          |            |
| :-------------: | :---------: | :------: | :--------: |
|     数据名      |    类型     |   约束   |    备注    |
|      STID       |     INT     |    PK    | 学生作业号 |
|      BOOK       | VARCHAR(20) | NOT NULL |    作业    |
|       SNO       |     INT     |    FK    |   学生号   |
|       HID       |     INT     |    FK    |   作业号   |

 

表12 TAG表

|  TAG   |             |          |        |
| :----: | :---------: | :------: | :----: |
| 数据名 |    类型     |   约束   |  备注  |
|  TID   |     INT     |    PK    | 标签号 |
| TNAME  | VARCHAR(20) | NOT NULL | 标签名 |

 

表13 TBRELA表

| TBRELA |      |       |        |
| :----: | :--: | :---: | :----: |
| 数据名 | 类型 | 约束  |  备注  |
|  BID   | INT  | PK,FK | 博客号 |
|  TID   | INT  | PK,FK | 标签号 |
| USERID | INT  |  FK   | 用户号 |

 

表14 TEACHER表

| TEACHER |             |          |        |
| :-----: | :---------: | :------: | :----: |
| 数据名  |    类型     |   约束   |  备注  |
|   TNO   |     INT     |    PK    | 教师号 |
|  TNAME  | VARCHAR(20) | NOT NULL | 教师名 |

 

表15 USERROLE表

| USERROLE |      |       |        |
| :------: | :--: | :---: | :----: |
|  数据名  | 类型 | 约束  |  备注  |
|  USERID  | INT  | PK,FK | 用户号 |
|   RID    | INT  | PK,FK | 角色号 |

 

表16 USERS表

| USERS  |             |          |        |
| :----: | :---------: | :------: | :----: |
| 数据名 |    类型     |   约束   |  备注  |
| USERID |     INT     |    PK    | 用户号 |
| UNAME  | VARCHAR(20) | NOT NULL | 用户名 |
|  PWD   | VARCHAR(20) | NOT NULL |  密码  |

 
## 感谢
本项目是半年前的项目，有一部分使用了第三方库来实现，老师也给予了我很多帮助，谢谢谢谢。
 
