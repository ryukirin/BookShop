# 第三方组件声明

BookShop Flask 迁移版使用了下列第三方组件。版本以 `requirements.txt`、`requirements-test.txt` 和 `bookshop_web/static/VENDOR.md` 为准。再分发时，必须保留各组件的许可证原文。Python 包的许可证原文随 wheel 一起安装；前端库的许可证原文放在 `bookshop_web/static/*/LICENSE`。

## 运行期（`requirements.txt`）

| 组件 | 版本 | 许可证 |
|---|---|---|
| Flask | 3.1.3 | BSD-3-Clause |
| Werkzeug | 3.1.9 | BSD-3-Clause |
| Jinja2 | 3.1.6 | BSD-3-Clause |
| MarkupSafe | 3.0.4 | BSD-3-Clause |
| itsdangerous | 2.2.0 | BSD-3-Clause |
| click | 8.5.0 | BSD-3-Clause |
| blinker | 1.9.0 | MIT |
| waitress | 3.0.2 | ZPL-2.1 |

## 前端（`bookshop_web/static/`）

| 组件 | 版本 | 许可证 |
|---|---|---|
| Bootstrap | 5.3.8 | MIT |
| Bootstrap Icons | 1.13.1 | MIT |

## 仅测试用（`requirements-test.txt`）

| 组件 | 版本 | 许可证 |
|---|---|---|
| pytest | 9.1.1 | MIT |
| pluggy | 1.6.0 | MIT |
| iniconfig | 2.3.1 | MIT |
| packaging | 26.3 | Apache-2.0 或 BSD-2-Clause |
| Pygments | 2.21.0 | BSD-2-Clause |
| colorama | 0.4.6 | BSD-3-Clause |

## 演示数据

`bookshop_web/static/img/`（轮播图、默认头像）和演示书籍的封面，都来自旧系统仓库 `BookShop/WebContent/img/`。封面图版权属于各原出版方，这里只作演示数据使用（COMP-019）。
