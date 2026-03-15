# TradeManager 可复现验证清单（Reproducibility Runbook）

> 目标：在一台“干净环境”机器上，按统一步骤验证项目可从零启动并完成基础功能检查。

## 环境前置
- Python 3.10+
- 可用网络（用于安装依赖）
- `curl` 可用（若使用 `SEED_DEMO=1` 自动注入）

## 标准验证步骤
1. 获取代码并进入目录
   - `git clone <repo_url>`
   - `cd trademanager`
2. 执行一键准备
   - `bash scripts/dev_bootstrap.sh`
3. 启动服务
   - `source .venv/bin/activate`
   - `uvicorn app.main:app --reload`
4. 验证基础接口
   - `curl -s http://127.0.0.1:8000/health`
   - 预期：`{"status":"ok"}`
5. 验证页面与文档
   - 打开 `http://127.0.0.1:8000/`
   - 打开 `http://127.0.0.1:8000/docs`
6. 运行开发检查（可选）
   - `bash scripts/dev_check.sh`

## 验证结果记录模板
- 验证机器：
- Python 版本：
- 操作系统：
- 是否完整通过：是 / 否
- 失败步骤：
- 错误摘要：
- 处理方式：

## 常见失败定位
- 依赖安装问题：见 `docs/faq.md` 第 1、5 条
- 启动脚本报错：见 `docs/faq.md` 第 2、3、4 条
