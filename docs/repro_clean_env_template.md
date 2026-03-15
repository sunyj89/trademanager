# TradeManager 干净环境实机验证模板

> 用途：在新的机器/容器完成端到端验证时，直接复制本模板填写并回传，作为最终验收记录。

## 基本信息
- 验证人：
- 验证日期：
- 操作系统：
- Python 版本：
- 网络环境说明（是否需要代理）：

## 执行命令与结果
> 建议严格按顺序执行，并记录每一步“通过/失败 + 错误摘要”。

1. 克隆与进入目录
   - `git clone <repo_url>`
   - `cd trademanager`
   - 结果：

2. 一键准备
   - `bash scripts/dev_bootstrap.sh`
   - 结果：

3. 启动服务
   - `source .venv/bin/activate`
   - `uvicorn app.main:app --reload`
   - 结果：

4. 健康检查
   - `curl -s http://127.0.0.1:8000/health`
   - 预期：`{"status":"ok"}`
   - 结果：

5. 页面与文档检查
   - `http://127.0.0.1:8000/`
   - `http://127.0.0.1:8000/docs`
   - 结果：

6. 开发检查
   - `bash scripts/dev_check.sh`
   - 结果：

## 问题与处理
- 问题 1：
  - 现象：
  - 原因：
  - 处理：

## 最终结论
- 是否通过端到端可复现验证：是 / 否
- 若否，剩余阻塞项：
- 建议下一步：
