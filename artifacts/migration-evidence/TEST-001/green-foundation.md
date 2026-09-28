# TEST-001 BATCH-001 运行证据

日期：2026-09-28。使用 Python 3.11.3 新建的独立虚拟环境；以固定下载 wheel 的真实 SHA-256、`--no-index --require-hashes` 安装，未修改全局解释器。

验证范围：固定 Python／SQLite／Flask／gevent 版本，外置配置正反例，中文 400／404／500，日志不包含测试秘密／异常正文，真实 gevent 回环健康、服务 PID、停止文件优雅退出、只读 PID 探活、残留 PID 恢复和日志轮转。请求关联 ID 在响应与 JSON 日志一致。

Windows 脚本实测：临时环境配置、固定端口 8000、`scripts/start.ps1 -Background` 隐藏启动 → 健康 200 `ok` → `scripts/stop.ps1` 优雅停止，PID 文件清除。异常退出演练仅对刚创建且命令行身份已核对的测试进程强制中断：残留 PID 存在；重新启动健康通过；恢复诊断日志存在；随后优雅停止。没有操作其他用户进程或业务库。

曾发现并修复 Windows `os.kill(pid,0)` 误用；被中断运行不计为通过。当前 Windows 分支仅用 `OpenProcess`／`GetExitCodeProcess` 查询，关闭查询句柄；Unix 分支才使用信号 0。依据：[Python os.kill](https://docs.python.org/3.11/library/os.html#os.kill)、[Microsoft GetExitCodeProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getexitcodeprocess)。

完整基础子集的最终退出码与数量见同批 `TEST-020/green-foundation.md`。仍未实施任何业务流程或切换。
