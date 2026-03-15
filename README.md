# TradeManager

基于《客户管理系统建设方案 V1》分期建设的 CRM 后端实现（持续迭代中）。

## 当前范围
### 一期模块
- 线索管理（Leads）
- 客户主档（Customers）
- 联系人管理（Contacts）
- 代理商管理（Agents）
- 跟进管理（Follow-ups）
- 商机管理（Opportunities）

### 二期闭环
- 合同管理（Contracts）
- 回款管理（Payments）

### 本轮新增能力
- 线索转化动作：`POST /leads/{id}/convert`（已增加重复转化拦截）
- 商机赢单动作：`POST /opportunities/{id}/mark-won`（已增加重复赢单拦截）
- 经营汇总接口：`GET /reports/profit-summary`
- 销售漏斗汇总接口：`GET /reports/pipeline-summary`

## 快速启动
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

接口文档：`http://127.0.0.1:8000/docs`


## 本轮补强
- 合同创建新增客户与商机归属一致性校验
- 回款创建新增取消合同状态拦截
- 新增客户价值汇总接口：`GET /reports/customer-value-summary`

- 代理佣金汇总接口：`GET /reports/agent-commission-summary`

- 商机丢单动作：`POST /opportunities/{id}/mark-lost`
- 合同状态流转动作：`POST /contracts/{id}/status`
- 回款进度报表：`GET /reports/collection-progress-summary`

- 回款新增超额校验（累计回款不得超过合同额）
- 合同完成新增全额回款前置校验
- 合同状态汇总报表：`GET /reports/contract-status-summary`


## 快速查看页面效果（MVP）
- 启动后访问：`http://127.0.0.1:8000/`
- 页面展示：核心经营 KPI、销售漏斗、最近客户与最近商机


## 当前页面能力（连续推进版）
- 多模块标签页：总览、客户、线索、商机、合同、回款、报表
- 支持在线操作：新增客户/线索/商机/合同/回款
- 支持关键动作：线索转化、商机赢单/丢单、合同状态流转
- 操作后自动刷新看板与列表


- 已补齐页面模块：代理商、联系人、跟进（含创建与列表）
- 页面已覆盖关键动作：线索转化、商机赢单/丢单、合同状态流转


## 本地演示辅助接口
- `POST /demo/seed`：快速注入一批演示数据
- `POST /demo/reset`：清空系统数据

- `POST /demo/bootstrap`：一键重置并注入演示数据


## 一键本地启动准备
- 运行：`bash scripts/dev_bootstrap.sh`
- 作用：创建虚拟环境、安装依赖、可选注入 demo 数据（默认开启）
- 完成后启动：`source .venv/bin/activate && uvicorn app.main:app --reload`

## 开发检查
- 运行：`bash scripts/dev_check.sh`

## 项目检查清单
- 见 `docs/checklist.md`


## 项目推进汇报约定
- 每次任务完成后，固定输出：已完成 / 进行中 / 下一步 / 项目总进度（百分比）。
- 详细清单维护在：`docs/checklist.md`。


## 启动失败排查（dev_bootstrap）
- 若依赖安装失败：优先检查网络/代理配置（如 `pip config list`、代理环境变量）。
- 若提示缺少 `curl`：安装后重试，或设置 `SEED_DEMO=0` 跳过自动注入。
- 若应用启动超时：查看 `/tmp/trademanager_uvicorn.log`。
- 若提示缺少 `uvicorn`：确认依赖已安装，或用 `python -m uvicorn app.main:app --reload` 启动。


## 常见问题（FAQ）
- 见：`docs/faq.md`。


## 可复现验证手册
- 见：`docs/repro_check.md`。


## 可复现验证执行记录
- 当前环境预演记录：`docs/repro_report.md`。


## 干净环境验收模板
- 见：`docs/repro_clean_env_template.md`。


## 当前阶段完成度
- 按项目可控范围口径：**100%**。
- 详细状态与验收口径见：`docs/checklist.md`、`docs/repro_report.md`。
