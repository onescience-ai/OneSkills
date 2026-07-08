# SCNet Skill 详细文档

通过自然语言交互管理 SCNet 超算平台，包括缓存管理、区域切换、账户查询、作业管理和文件管理。

---

## 功能概览

| 功能类别 | 支持操作 |
| --- | --- |
| 缓存管理 | 自动初始化、自动刷新、手动刷新 |
| 区域切换 | 在已开通区域之间切换 |
| 用户信息 | 查询账户信息、余额、机时、作业统计 |
| 作业管理 | 查询、提交、删除作业，查看队列与集群信息 |
| 文件管理 | 列表、上传、下载、创建、删除、重命名、复制、移动 |

---

## 依赖安装

本 Skill 需要 Python 3.7+ 环境。

> Windows 下请优先使用 `python`，不要依赖 `python3`，因为它可能指向无效重定向器，导致脚本没有输出。

### 必需依赖

```bash
python -m pip install aiohttp
```

### 可选：使用虚拟环境

```bash
python -m venv ~/.scnet-chat-venv
source ~/.scnet-chat-venv/bin/activate
pip install aiohttp
python scripts/scnet.py "查询作业"
```

### 依赖说明

| 包名 | 版本要求 | 用途 |
| --- | --- | --- |
| `aiohttp` | >= 3.7.0 | 异步 HTTP 客户端，用于并发查询 API |

安装 `aiohttp` 后可以明显缩短缓存初始化和账户查询时间；未安装时程序仍可运行，但会退回同步模式，速度较慢。

---

## 配置方式

首次使用前需要配置 `~/.scnet-chat.env`：

```bash
SCNET_ACCESS_KEY=your_access_key_here
SCNET_SECRET_KEY=your_secret_key_here
SCNET_USER=your_username_here

# 可选
SCNET_LOGIN_URL=https://api.scnet.cn
SCNET_AC_URL=https://www.scnet.cn
```

### 获取凭证

1. 登录 SCNet 平台：<https://www.scnet.cn/ui/console/index.html#/personal/auth-manage>
2. 进入“个人中心 → 访问控制”
3. 创建访问密钥，获取 Access Key 和 Secret Key

---

## 推荐调用方式

优先使用跨平台包装脚本：

### macOS / Linux

```bash
./scripts/run "自然语言命令"
```

### Windows

```bash
./scripts/run.bat "自然语言命令"
```

如果需要，也可以直接调用：

```bash
python scripts/scnet.py "自然语言命令"
```

---

## 自然语言使用指南

### 1. 缓存管理

| 意图 | 示例 | 说明 |
| --- | --- | --- |
| 刷新缓存 | `刷新缓存`、`初始化缓存`、`更新缓存` | 手动刷新 token 和缓存数据 |

缓存会在以下情况自动处理：

- 首次使用时自动初始化
- 缓存过期时自动刷新
- 缓存损坏时尝试自动重建

### 2. 区域切换

| 意图 | 示例 |
| --- | --- |
| 切换区域 | `切换到昆山`、`切换到山东`、`切换到西安` |

当前代码中支持的常见区域别名包括：

- 华东一区【昆山】
- 东北一区【哈尔滨】
- 华东三区【乌镇】
- 西北一区【西安】
- 华北一区【雄衡】
- 华东四区【山东】
- 西南一区【四川】
- 华南一区【广东】
- 核心节点【分区一】
- 核心节点【分区二】
- 华中三区【武汉】

### 3. 用户信息查询

| 意图 | 示例 | 说明 |
| --- | --- | --- |
| 查询用户信息 | `查询用户`、`账户信息`、`我的信息`、`余额` | 查看完整账户信息 |
| 作业统计 | `作业统计`、`统计信息`、`作业状态统计` | 统计实时作业状态分布 |
| 机时查询 | `机时`、`剩余机时`、`已用机时` | 查看机时使用情况 |

### 4. 作业管理

#### 4.1 查询作业

| 意图 | 示例 | 说明 |
| --- | --- | --- |
| 通用作业查询 | `查询作业` | 未明确指定时，同时查询实时作业和历史作业 |
| 实时作业 | `查看运行中的作业`、`实时作业` | 仅查询实时作业 |
| 历史作业 | `历史作业`、`查询历史作业` | 仅查询历史作业 |
| 状态筛选 | `查询运行中的作业`、`查询历史作业，状态为失败` | 支持运行、排队、完成、失败、取消、超时等状态 |
| 队列筛选 | `查询队列 debug 的作业` | 按队列过滤 |
| 名称筛选 | `查询作业名称 test` | 支持模糊匹配 |
| 分页查询 | `查询作业 第2页 每页20条`、`查询历史作业，每页5条，显示第二页` | 支持中文页码和中文数字 |
| 用户筛选 | `查询用户 zhangsan 的作业` | 按用户过滤 |
| 区域筛选 | `查询区域ID 12345 的作业` | 按区域过滤 |
| 时间范围 | `历史作业 开始时间 2024-01-01 00:00:00 结束时间 2024-01-31 23:59:59` | 指定时间范围 |
| 最近 N 天 | `历史作业 最近7天`、`查询最近三天的历史作业` | 支持中文数字 |
| 作业详情 | `作业详情 12345` | 查询指定作业详情 |

#### 4.2 查询规则说明

- **未明确指定“实时”或“历史”时**：默认同时查询实时作业和历史作业。
- **包含“历史作业”关键词时**：仅查询历史作业。
- **包含“实时作业”或“运行中的作业”关键词时**：仅查询实时作业。

#### 4.3 AC 聚合作业接口说明

实时作业列表和历史作业列表都走 AC 聚合接口，返回的是**所有区域的聚合结果**，不需要逐个区域遍历。

- 实时作业接口：`POST /v3/jobs/active-job`
- 历史作业接口：`POST /v3/jobs/history-job`
- Token 来源：缓存中的 `clusterName = ac`
- 服务域名：`https://www.scnet.cn`

这意味着：

| 查询类型 | Token 来源 | 查询范围 | 是否需要遍历区域 |
| --- | --- | --- | --- |
| 实时作业列表 | AC | 全区域聚合 | 否 |
| 历史作业列表 | AC | 全区域聚合 | 否 |
| 作业详情 | 当前区域 | 单区域 | 否 |
| 队列查询 | 当前区域 | 单区域 | 否 |
| 集群信息 | 当前区域 | 单区域 | 否 |

#### 4.4 作业状态参考

| 中文状态 | API 代码 | 英文别名 |
| --- | --- | --- |
| 运行 | `statR` | `running` |
| 排队 | `statQ` | `queue` / `queued` |
| 完成 | `statC` | `completed` |
| 失败 | `statD` | `failed` |
| 取消 | `statDE` | `cancelled` |
| 超时 | `statT` | `timeout` |
| 退出 | `statE` | `exit` |
| 挂起 | `statS` | `suspend` |
| 保留 | `statH` | `hold` |
| 等待 | `statW` | `wait` |
| 节点异常 | `statN` | `nodefail` |
| 重新运行 | `statRQ` | `rerun` |

#### 4.5 提交作业

| 意图 | 示例 | 说明 |
| --- | --- | --- |
| 提交作业帮助 | `如何提交作业`、`提交作业帮助`、`作业有哪些参数` | 显示帮助信息 |
| 简单提交 | `提交作业 sleep 900` | 提交简单命令 |
| 显式参数提交 | `提交作业 --cmd "sleep 100" --queue debug` | 直接指定参数 |
| 指定区域提交 | `在昆山提交作业 hostname`、`在山东提交作业 sleep 60` | 自动切换区域并提交 |

Windows 下推荐使用“位置命令 + 显式参数”格式：

```bash
提交作业 bash run.sh --queue comp --work-dir /public/home/user/work --ppn 4 --wall-time 12:00:00 --job-name production-run
```

注意：

- 不要优先使用 `--cmd "bash run.sh"` 这种形式来提交真实软件任务。
- 不要使用“启动命令”“命令行内容”等中文标签。
- 一旦涉及 `work-dir`、队列、核数、作业名等参数，优先使用显式参数格式。

支持的常用参数：

| 参数 | 说明 | 示例 |
| --- | --- | --- |
| `--cmd` | 执行命令 | `sleep 100` |
| `--queue` | 队列名称 | `comp`、`debug` |
| `--nnode` | 节点数 | `1`、`2` |
| `--work-dir` | 工作目录 | `/public/home/user/work` |
| `--job-name` | 作业名称 | `my-job-001` |
| `--wall-time` | 最大运行时间 | `01:00:00` |
| `--nproc` | 总核心数 | `4`、`8` |
| `--ppn` | 每节点核心数 | `4`、`8` |
| `--ngpu` | 每节点 GPU 数 | `1`、`2` |
| `--ndcu` | 每节点 DCU 数 | `1`、`2` |
| `--job-mem` | 每节点内存 | `16GB`、`32GB` |
| `--exclusive` | 是否独占节点 | `1` |
| `--std-out` | 标准输出路径 | `/path/out.%j` |
| `--std-err` | 标准错误路径 | `/path/err.%j` |

#### 4.6 删除作业

| 意图 | 示例 |
| --- | --- |
| 删除作业 | `删除作业 12345`、`取消作业 12345`、`终止作业 12345` |

#### 4.7 队列和集群信息

| 意图 | 示例 |
| --- | --- |
| 查询队列 | `查询队列`、`可用队列`、`队列列表` |
| 集群信息 | `集群信息`、`调度器信息` |

### 5. 文件管理

#### 5.1 文件列表

| 意图 | 示例 |
| --- | --- |
| 查看文件列表 | `文件列表`、`查看文件`、`ls /public/home/user` |

#### 5.2 上传和下载

| 意图 | 示例 |
| --- | --- |
| 上传文件 | `上传文件 ./data 到 /public/home/user/` |
| 下载文件 | `下载文件 /public/home/user/data 到 ./` |

#### 5.3 文件操作

| 意图 | 示例 |
| --- | --- |
| 创建目录 | `创建目录 /public/home/user/newdir`、`mkdir /work/test` |
| 创建文件 | `创建文件 /public/home/user/test.txt`、`touch file` |
| 删除文件 | `删除文件 /public/home/user/test.txt`、`rm /work/old.txt` |
| 重命名 | `重命名 /old/name.txt 为 newname.txt` |
| 复制文件 | `复制文件 /src/file.txt 到 /dst/` |
| 移动文件 | `移动文件 /src/file.txt 到 /dst/` |
| 检查文件 | `检查文件 /public/home/user/file.txt` |

---

## 常用示例

### 查询作业

```bash
./scripts/run "查询作业"
./scripts/run "查看运行中的作业"
./scripts/run "历史作业"
./scripts/run "查询历史作业，状态为失败"
./scripts/run "查询最近三天的历史作业"
./scripts/run "查询作业 第2页 每页20条"
./scripts/run "作业详情 12345"
```

### 提交和删除作业

```bash
./scripts/run "提交作业 sleep 900"
./scripts/run "提交作业 sleep 900 --queue comp --ppn 2 --wall-time 12:00:00 --job-name production-run1"
./scripts/run "如何提交作业"
./scripts/run "删除作业 12345"
```

### 文件管理

```bash
./scripts/run "文件列表"
./scripts/run "查看文件 /public/home/user"
./scripts/run "上传文件 ./data 到 /public/home/user/"
./scripts/run "下载文件 /public/home/user/data 到 ./"
./scripts/run "复制文件 /src/data 到 /dst/"
./scripts/run "移动文件 /src/data 到 /dst/"
./scripts/run "重命名 /old/data 为 data1"
```

### 账户与区域

```bash
./scripts/run "查询余额"
./scripts/run "查询用户"
./scripts/run "作业统计"
./scripts/run "机时"
./scripts/run "切换到山东"
./scripts/run "刷新缓存"
./scripts/run "帮助"
```

---

## 结构说明

本项目采用统一入口架构：

- `scripts/scnet.py`：推荐入口，负责自然语言意图识别和命令路由
- `scripts/job.py`：作业查询、提交、删除、队列、集群信息
- `scripts/file.py`：文件列表、上传下载、创建删除、复制移动、重命名
- `scripts/user.py`：账户信息、余额、机时、作业统计
- `scripts/cache.py`：认证、缓存初始化、缓存刷新、区域切换

设计原则：

- 所有日常使用优先通过 `scripts/scnet.py` 或 `scripts/run*` 入口完成
- 底层脚本主要服务于内部实现和调试，不保证长期兼容
- 文档优先描述自然语言用法，而不是底层参数细节

---

## 底层脚本示例（仅调试用）

### 作业管理

```bash
python scripts/job.py
python scripts/job.py --history
python scripts/job.py --job-id 12345
python scripts/job.py --submit --cmd "sleep 100" --queue debug
python scripts/job.py --delete --job-id 12345
python scripts/job.py --queues
python scripts/job.py --cluster-info
```

### 文件管理

```bash
python scripts/file.py --list /public/home/user
python scripts/file.py --upload ./data /public/home/user/
python scripts/file.py --download /public/home/user/data ./
python scripts/file.py --mkdir /public/home/user/workspace
python scripts/file.py --touch /public/home/user/hello.txt
python scripts/file.py --delete /public/home/user/old.txt
python scripts/file.py --rename /old/data data1
python scripts/file.py --copy /src/data /dst/
python scripts/file.py --move /src/data /dst/
```

### 用户信息

```bash
python scripts/user.py
```

---

## 注意事项

1. 首次使用前必须先配置 `~/.scnet-chat.env`。
2. 建议安装 `aiohttp` 以获得更好的性能。
3. 缓存会自动初始化和刷新，但也可以手动执行“刷新缓存”。
4. 大文件上传下载可能耗时较长。
5. 切换区域后，后续操作默认针对新区域执行。
6. 建议将配置文件权限限制为仅当前用户可读，例如：`chmod 600 ~/.scnet-chat.env`。
