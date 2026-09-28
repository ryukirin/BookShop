# TEST-002 BATCH-001 子集证据

日期：2026-09-28。`FoundationRouteTests` 共 5 项通过：健康与上下文边界、四个活动 Servlet 的全部 21 个 opttype 与目标登记精确相等、缺失／未知操作 400、未知页面 404、内部异常 500 与中文脱敏正文。

命令（干净虚拟环境）：`python -m unittest tests.test_runtime tests.test_routes.FoundationRouteTests tests.test_delivery.FoundationDeliveryTests`；设置 `BOOKSHOP_VERIFY_ENV=1`，组合运行 18 项、退出码 0。

旧 Java 源码包含混合编码，静态检查只逐字节提取 ASCII 的注解／case，不重写源码。`git diff --exit-code -- BookShop` 退出码 0。

身份、目录、购买、管理全量业务分支仍待各批次转绿；本文件只证明 BATCH-001 子集，不能代替全量 TEST-002。
