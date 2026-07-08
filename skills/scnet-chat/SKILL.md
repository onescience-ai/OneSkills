---
name: scnet-chat
description: 通过自然语言交互管理 SCNet Chat 超算平台。用户需要查询/管理 SCNet 超算平台资源，包括查询作业、提交作业、管理文件、查看账户信息、切换区域等。触发关键词：scnet、超算、作业、作业管理、文件管理、账户、余额、查询余额、机时、集群、队列、上传、下载、重命名、区域切换、昆山、山东、西安等。
metadata:
  openclaw:
    requires:
      env:
        - SCNET_ACCESS_KEY
        - SCNET_SECRET_KEY
        - SCNET_USER
      bins:
        - python3
        - python
license: MIT
clawhub:
  slug: scnet-chat
  repo: https://github.com/wiltonMotta/scnet-chat
  autoEnable: true
  version: 2.1.0
---

# SCNet Chat 技能

通过自然语言交互管理 SCNet 超算平台资源。

## When to Run

- 用户提到 SCNet、超算、作业管理、文件管理等关键词
- 用户需要查询作业（未指定实时/历史时同时查询两者）、提交作业、删除作业
- 用户需要上传/下载/管理远程文件
- 用户需要查看账户信息、余额、机时、作业统计（统计实时作业）
- 用户需要切换计算区域（昆山、山东、西安等）

## Workflow

1. **确定用户意图**：识别用户是想查询作业、管理文件、查看账户信息还是切换区域
2. **检查配置**：确保 `~/.scnet-chat.env` 文件存在且包含必要的环境变量
3. **执行命令**（根据操作系统选择正确的启动脚本）：
   - **macOS/Linux**: `./scripts/run "自然语言命令"`
   - **Windows**: `./scripts/run.bat "自然语言命令"`
4. **返回结果**：将执行结果格式化后返回给用户

> **说明**：`scripts/run` 和 `scripts/run.bat` 是跨平台包装脚本，会自动检测并使用正确的 Python 解释器（macOS/Linux 优先使用 `python3`，Windows 优先使用 `python`）。

### 常用命令示例

**macOS/Linux:**
```bash
# 查询作业
# 作业管理 - 查询（基础）
# ⚠️ 注意：实时作业列表和历史作业列表是全区域聚合查询，一次调用返回所有区域的作业
# 💡 重要：如果未明确指定"实时"或"历史"，默认同时查询实时作业和历史作业
./scripts/run "查询作业"                      # 未明确指定 → 同时查询实时作业+历史作业
./scripts/run "查看运行中的作业"              # 明确指定实时 → 仅查询实时作业
./scripts/run "实时作业"                      # 明确指定实时 → 仅查询实时作业
./scripts/run "历史作业"                      # 明确指定历史 → 仅查询历史作业
./scripts/run "作业详情 12345"                # 查询特定作业详情（需指定区域）

# 作业管理 - 查询（高级筛选）
./scripts/run "查询作业 第2页 每页20条"
./scripts/run "查询队列 debug 的作业 所有字段"
./scripts/run "查询用户 zhangsan 的作业"
./scripts/run "查询组作业"
./scripts/run "查询区域ID 12345 的作业"       # 筛选特定区域的作业

# 作业管理 - 历史作业查询（高级用法）
./scripts/run "历史作业 开始时间 2024-01-01 00:00:00 结束时间 2024-01-31 23:59:59"
./scripts/run "历史作业 最近7天"
./scripts/run "查询最近三天的历史作业"                    # 中文数字支持
./scripts/run "查询从2026-04-01到2026-04-03的历史作业"   # 简写日期范围
./scripts/run "查询历史作业，每页5条，显示第二页"         # 中文页码
./scripts/run "查询历史作业，状态为失败"                  # 中文状态筛选
./scripts/run "查询历史作业，队列为comp，每页10条"

# 作业管理 - 实时作业查询（高级用法）
# 💡 含"历史作业"关键词 → 仅查历史；含"实时"/"运行中" → 仅查实时；否则同时查两者
./scripts/run "查询作业 开始时间 2024-01-01 00:00:00 结束时间 2024-01-31 23:59:59"
./scripts/run "查询最近3天的作业"
./scripts/run "查询运行中的作业，每页5条"
./scripts/run "查询作业，状态为排队，显示第2页"

# 提交作业
./scripts/run "提交作业 sleep 900" # 简单命令
./scripts/run "提交作业 sleep 900 --queue comp --ppn 2 --wall-time 12:00:00 --job-name production-run1" # 位置命令 + 显式参数格式（推荐）

#提交作业帮助
./scripts/run "如何提交作业"
./scripts/run "提交作业帮助"
./scripts/run "作业有哪些参数"

# 删除作业
./scripts/run "删除作业 12345"

# 作业管理 - 队列和集群
./scripts/run "查询队列"
./scripts/run "集群信息"

# 文件管理 - 列表和上传下载
./scripts/run "文件列表"
./scripts/run "查看文件 /public/home/user"
./scripts/run "上传文件 ./data 到 /public/home/user/"
./scripts/run "下载文件 /public/home/user/data 到 ./"

# 文件管理 - 创建和删除
./scripts/run "创建目录 /public/home/user/workspace"
./scripts/run "创建文件 /public/home/user/data"
./scripts/run "删除文件 /public/home/user/data"

# 文件管理 - 复制移动和重命名
./scripts/run "复制文件 /src/data 到 /dst/"
./scripts/run "移动文件 /src/data 到 /dst/"
./scripts/run "重命名 /old/data 为 data1"
./scripts/run "检查文件 /public/home/user/file"

# 账户信息
./scripts/run "查询余额"
./scripts/run "查询用户"
./scripts/run "作业统计"                      # 按作业状态统计实时作业数量（非历史作业）
./scripts/run "机时"

# 区域切换
./scripts/run "切换到山东"
./scripts/run "切换到西安"

# 缓存管理
./scripts/run "刷新缓存"

# 帮助
./scripts/run "帮助"
```

**Windows:**
```bash
# 查询作业
# 作业管理 - 查询（基础）
# ⚠️ 注意：实时作业列表和历史作业列表是全区域聚合查询，一次调用返回所有区域的作业
# 💡 重要：如果未明确指定"实时"或"历史"，默认同时查询实时作业和历史作业
./scripts/run.bat "查询作业"                      # 未明确指定 → 同时查询实时作业+历史作业
./scripts/run.bat "查看运行中的作业"              # 明确指定实时 → 仅查询实时作业
./scripts/run.bat "实时作业"                      # 明确指定实时 → 仅查询实时作业
./scripts/run.bat "历史作业"                      # 明确指定历史 → 仅查询历史作业
./scripts/run.bat "作业详情 12345"                # 查询特定作业详情（需指定区域）

# 作业管理 - 查询（高级筛选）
./scripts/run.bat "查询作业 第2页 每页20条"
./scripts/run.bat "查询队列 debug 的作业 所有字段"
./scripts/run.bat "查询用户 zhangsan 的作业"
./scripts/run.bat "查询组作业"
./scripts/run.bat "查询区域ID 12345 的作业"       # 筛选特定区域的作业

# 作业管理 - 历史作业查询（高级用法）
./scripts/run.bat "历史作业 开始时间 2024-01-01 00:00:00 结束时间 2024-01-31 23:59:59"
./scripts/run.bat "历史作业 最近7天"
./scripts/run.bat "查询最近三天的历史作业"                    # 中文数字支持
./scripts/run.bat "查询从2026-04-01到2026-04-03的历史作业"   # 简写日期范围
./scripts/run.bat "查询历史作业，每页5条，显示第二页"         # 中文页码
./scripts/run.bat "查询历史作业，状态为失败"                  # 中文状态筛选
./scripts/run.bat "查询历史作业，队列为comp，每页10条"

# 作业管理 - 实时作业查询（高级用法）
# 💡 含"历史作业"关键词 → 仅查历史；含"实时"/"运行中" → 仅查实时；否则同时查两者
./scripts/run.bat "查询作业 开始时间 2024-01-01 00:00:00 结束时间 2024-01-31 23:59:59"
./scripts/run.bat "查询最近3天的作业"
./scripts/run.bat "查询运行中的作业，每页5条"
./scripts/run.bat "查询作业，状态为排队，显示第2页"

# 提交作业
./scripts/run.bat "提交作业 sleep 900" # 简单命令
./scripts/run.bat "提交作业 sleep 900 --queue comp --wall-time 00:30:00" # Windows 下推荐使用位置命令 + 显式参数格式

#提交作业帮助
./scripts/run.bat "如何提交作业"
./scripts/run.bat "提交作业帮助"
./scripts/run.bat "作业有哪些参数"

# 删除作业
./scripts/run.bat "删除作业 12345"

# 作业管理 - 队列和集群
./scripts/run.bat "查询队列"
./scripts/run.bat "集群信息"

# 文件管理 - 列表和上传下载
./scripts/run.bat "文件列表"
./scripts/run.bat "查看文件 /public/home/user"
./scripts/run.bat "上传文件 ./data 到 /public/home/user/"
./scripts/run.bat "下载文件 /public/home/user/data 到 ./"

# 文件管理 - 创建和删除
./scripts/run.bat "创建目录 /public/home/user/workspace"
./scripts/run.bat "创建文件 /public/home/user/data"
./scripts/run.bat "删除文件 /public/home/user/data"

# 文件管理 - 复制移动和重命名
./scripts/run.bat "复制文件 /src/data 到 /dst/"
./scripts/run.bat "移动文件 /src/data 到 /dst/"
./scripts/run.bat "重命名 /old/data 为 data1"
./scripts/run.bat "检查文件 /public/home/user/file"

# 账户信息
./scripts/run.bat "查询余额"
./scripts/run.bat "查询用户"
./scripts/run.bat "作业统计"                      # 按作业状态统计实时作业数量（非历史作业）
./scripts/run.bat "机时"

# 区域切换
./scripts/run.bat "切换到山东"
./scripts/run.bat "切换到西安"

# 缓存管理
./scripts/run.bat "刷新缓存"

# 帮助
./scripts/run.bat "帮助"
```

## Output Format

- 作业查询结果按区域分组显示
- **未明确指定实时/历史时**：同时返回实时作业列表和历史作业列表
- **作业统计**：按作业状态（运行中、排队、完成等）统计**实时作业**数量
- 账户信息以表格形式展示
- 文件操作结果简洁明了
- 错误信息包含具体原因
- 根据用户当前操作给出3个下一步操作的预测问题

## 提交作业格式约束（Windows 重点）

- Windows 下提交作业时，优先使用“位置命令 + 显式参数”格式：`提交作业 bash run.sh --queue {queue} --work-dir {workdir} --ppn {ppn} --wall-time {wall_time} --job-name {job_name}`。
- `--ppn` 与 `--nproc` 对应平台 `GAP_PPN` / `GAP_NPROC`，是二选一资源参数；单节点软件任务优先只传 `--ppn`，软件内部并行数由各软件 skill 自己写入输入文件或运行脚本。
- Windows/OpenClaw 下软件任务不要优先使用 `--cmd "bash run.sh"`；该形式在平台模板二次注入时可能触发引号不闭合。保留 `--cmd` 仅用于兼容简单命令或人工调试。
- 启动命令只能出现在 `提交作业` 后、第一组显式参数前，例如 `bash run.sh`；`--queue`、`--work-dir`、`--ppn`、`--wall-time`、`--job-name` 等必须作为 scnet-chat 参数单独传递，不能拼进启动命令。
- 不要使用 `启动命令`、`命令行内容` 等中文标签；这些标签在某些路径下可能被原样写入生成脚本，导致 `command not found`。
- 若只是简单测试命令，可使用简洁格式：`提交作业 sleep 900`。
- 一旦涉及 `workdir`、队列、核数、作业名等参数，改用 `提交作业 <启动命令> --queue ... --work-dir ... --ppn ...` 形式，不要混用自然语言长句。

## 网络容错规则

scnet-chat 依赖远程 API，网络不稳定时可能出现超时或连接失败。执行命令时必须遵守以下规则：

1. **超时识别**：以下情况视为网络故障：
   - 命令执行超时（> 30 秒无响应）
   - SSL 握手超时（`handshake operation timed out`）
   - 读取超时（`read operation timed out`）
   - 连接拒绝或 DNS 解析失败

2. **重试策略**：遇到网络故障时，按以下策略重试：
   - 第 1 次：等待 5 秒后重试
   - 第 2 次：等待 15 秒后重试
   - 第 3 次：等待 30 秒后重试
   - 3 次重试均失败：停止并报告错误，让用户决定下一步

3. **重试时的提示**：每次重试前告知用户"网络超时，正在重试（第 N/3 次）..."

4. **禁止行为**：
   - 不要在未重试的情况下直接报错
   - 不要无限重试
   - 不要在重试间不做任何等待

## 配置说明

首次使用需要在 `~/.scnet-chat.env` 配置：

```bash
SCNET_ACCESS_KEY=your_access_key
SCNET_SECRET_KEY=your_secret_key
SCNET_USER=your_username
```

获取凭证：https://www.scnet.cn/ui/console/index.html#/personal/auth-manage

## 依赖安装

```bash
pip install aiohttp
```
