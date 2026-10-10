# 第三方前端资源（DEC-011）

下面的文件都从 npm registry 的发布包中原样取出，没有任何修改。取出前，先用 npm 给出的 `dist.integrity` 校验了整个发布包。TEST-043 会重新计算每个文件的 sha512，并与本表比对。

| 文件（相对 `bookshop_web/static/`） | sha512 | 来源 |
|---|---|---|
| `bootstrap/css/bootstrap.min.css` | `sha512-2bBQCjcnw658Lho4nlXJcc6WkV/UxpE/sAokbXPxQNGqmNdQrWqtw26Ns9kFF/yG792pKR1Sx8/Y1Lf1XN4GKA==` | bootstrap@5.3.8，`dist/css/bootstrap.min.css` |
| `bootstrap/js/bootstrap.bundle.min.js` | `sha512-HvOjJrdwNpDbkGJIG2ZNqDlVqMo77qbs4Me4cah0HoDrfhrbA+8SBlZn1KrvAQw7cILLPFJvdwIgphzQmMm+Pw==` | bootstrap@5.3.8，`dist/js/bootstrap.bundle.min.js` |
| `bootstrap-icons/bootstrap-icons.min.css` | `sha512-t7Few9xlddEmgd3oKZQahkNI4dS6l80+eGEzFQiqtyVYdvcSG2D3Iub77R20BdotfRPA9caaRkg1tyaJiPmO0g==` | bootstrap-icons@1.13.1，`font/bootstrap-icons.min.css` |
| `bootstrap-icons/fonts/bootstrap-icons.woff2` | `sha512-12eBTRRLMRJU3l0kjUoc0ndyCQFmh8EbOneRZC2Q/yZ8EdAAH7MENeN2eVmioA1AduG8b608eljP2wDlx3xEzg==` | bootstrap-icons@1.13.1，`font/fonts/bootstrap-icons.woff2` |
| `bootstrap-icons/fonts/bootstrap-icons.woff` | `sha512-yyPIwHNm3QG75/vgKa5oODBUTTDuXODB7pRHmMWJ4BQRNZaiPLb2ReQUCILPAms1CAVr7uoVmWAv1l9NFOPWBw==` | bootstrap-icons@1.13.1，`font/fonts/bootstrap-icons.woff` |

## 发布包校验值

| 发布包 | npm `dist.integrity` |
|---|---|
| bootstrap@5.3.8 | `sha512-HP1SZDqaLDPwsNiqRqi5NcP0SSXciX2s9E+RyqJIIqGo+vJeN5AJVM98CXmW/Wux0nQ5L7jeWUdplCEf0Ee+tg==` |
| bootstrap-icons@1.13.1 | `sha512-ijombt4v6bv5CLeXvRWKy7CuM3TRTuPEuGaGKvTV5cz65rQSY8RQ2JcHt6b90cBBAC7s8fsf2EkQDldzCoXUjw==` |

## 许可证

两个包都是 MIT 许可证，原文分别是 `bootstrap/LICENSE` 和 `bootstrap-icons/LICENSE`。

## 升级

1. 用 `npm pack <包>@<版本>` 下载发布包，核对 `npm view <包>@<版本> dist.integrity`；
2. 取出上表中的文件，覆盖原文件；
3. 更新本表，并跑一遍全量测试。

## 其他图片

`img/1.jpg`、`img/2.jpg`、`img/default.jpg` 是旧系统 `BookShop/WebContent/img/` 里的轮播图和默认头像，原样复制过来。
