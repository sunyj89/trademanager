# TradeManager 常见问题排查（FAQ）

## 1) `pip install -e .[dev]` 失败
**现象**
- 安装依赖时报网络、代理、超时或无法解析包版本。

**排查建议**
- 检查代理与 pip 配置：
  - `pip config list`
  - `env | grep -i proxy`
- 若公司网络限制外网，请切换可用网络或配置可用镜像源。

## 2) `dev_bootstrap.sh` 提示缺少 `curl`
**现象**
- 脚本提示 `SEED_DEMO=1 需要 curl`。

**排查建议**
- 安装 `curl` 后重试。
- 或临时跳过 demo 注入：`SEED_DEMO=0 bash scripts/dev_bootstrap.sh`。

## 3) `dev_bootstrap.sh` 提示缺少 `uvicorn`
**现象**
- 脚本提示未找到 `uvicorn`。

**排查建议**
- 先确认虚拟环境已激活，且依赖安装成功。
- 可直接使用模块启动验证：
  - `python -m uvicorn app.main:app --reload`

## 4) 应用启动超时
**现象**
- 脚本等待健康检查超时。

**排查建议**
- 查看日志：`/tmp/trademanager_uvicorn.log`。
- 常见原因：端口占用、依赖缺失、导入错误。

## 5) `pytest -q` 失败并提示缺少 `fastapi`
**现象**
- `ModuleNotFoundError: No module named 'fastapi'`。

**排查建议**
- 说明开发依赖未安装成功；先修复依赖安装问题后再执行测试。
- 建议先执行：
  - `python -m pip install --upgrade pip`
  - `pip install -e .[dev]`

## 6) 如何快速校验本地是否可运行？
建议最小链路：
1. `bash scripts/dev_bootstrap.sh`
2. `source .venv/bin/activate`
3. `uvicorn app.main:app --reload`
4. 访问：`http://127.0.0.1:8000/health` 与 `http://127.0.0.1:8000/docs`
