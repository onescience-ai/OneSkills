---
schema_version: onescience-knowledge-contribution-v1
contribution_id: 2026-09-21_gitee_token_read_export_inheritance
title: Gitee Token 安全注入：read -s -p 必须配 export 才能被 opencode 子进程继承
domain: general
kind: both
status: submitted
created_at: 2026-09-21T17:10:00+08:00
---

# Gitee Token 安全注入：read -s -p 必须配 export 才能被 opencode 子进程继承

## Contribution Metadata

- Contribution ID: `2026-09-21_gitee_token_read_export_inheritance`
- Source type: `mixed`
- Redacted: `true`
- Raw transcript included: `false`
- Domain / Kind: `general` / `both`

## Task Summary

- Goal: 确认 `read -s -p` 安全输入 `GITEE_TOKEN` 后，同一 shell 启动的 `opencode` 及其技能子进程 `submit_gitee_issue.py` 能继承到该 token，端到端验证后提交到 `wangqi00001/oneskills-dev`。
- Context: `submit_gitee_issue.py` 有两条后端——`--method api`（读 `GITEE_TOKEN` 环境变量走 HTTP）与 `gitee-cli`（读 CLI 本地凭据）；用户真实运行环境是 Linux（外层 shell 设 token → 启动 opencode → 技能提交），开发机是 Windows（有 Git Bash/WSL）。
- Inputs: 真实 `GITEE_TOKEN`（仅经 stdin 喂给 `read -s -p`，绝不落盘）、`submit_gitee_issue.py` 与 `issue_payload.json`、`scnet-infinity`(Linux 5.10) SSH 通道。
- Expected outputs: 修正后的令牌注入写法 + 跨平台端到端验证证据 + 提交到 fork 的示范 Issue。
- Constraints: token 绝不落盘、不进日志；`read` 是 POSIX shell 内建，需跨 Windows Git Bash 与 Linux 一致验证；提交目标为 `wangqi00001/oneskills-dev`。
- Success criteria: `read`+`export` 后孙进程 `os.environ` 读到 token；`--method api --submit` 返回 HTTP 201 并回带 Issue 编号；回读 Issue 确认三标签与正文完整。

## Interaction Timeline

| Step ID | Name | Objective | Expected action | Actual action | Observation | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | 定位令牌注入流程归属 | 改成 `read -s -p` 安全输入并确认 Windows 能否验证 | grep `read -s`/`export GITEE_TOKEN` 定位流程 | 全仓 grep，未命中任何仓库文件 | 该三步流程是用户 shell 手敲：注入 token→启动 opencode→验证 | 修正点定位在 shell 注入步骤而非仓库脚本 | success |
| S2 | 确认脚本取 token 方式 | 确认 opencode 子进程能否拿到 token | 定位 token 读取与失败分支 | 读 `submit_gitee_issue.py`，定位 `os.environ.get` 与 `exit 2` | 脚本只从环境变量取 token；`read` 的 shell 变量不 `export` 则读不到 | 必须 `export` 才能被子/孙进程继承 | success |
| S3 | 对照实验证实 export | 证实 `export` 是继承关键 | Case A(不 export)/Case B(export) 子进程回显 | Git Bash 跑 Case A/Case B 对照(假 token) | Case A 子进程读到 `False`，Case B 读到 `True` | 确立 read 后必须 export | success |
| S4 | 准备标签与远端连通性 | 准备可提交示范并让标签生效 | 建三标签；探测远端连通性与工具 | `gitee api` 建三标签；SSH 探测 scnet-infinity | 三标签建成；远端可达 gitee(401)、有 python3/git/node、无 opencode | 远端无 opencode，改用子/孙进程继承等价验证 | success |
| S5 | 端到端提交并回读核验 | 端到端验证并提交到 fork | `--method api --submit` 提交；`gitee api` 回读 | 真实 token 经 `read -s -p`+`export` 提交，再回读核验 | HTTP 201，Issue IKHM4T 创建成功；三标签生效 | 确认链路打通、提交成功 | success |

## Decisions And Evidence

- **D1** Decision: 修正点是"`read` 之后补 `export GITEE_TOKEN`"，而非改写 `read` 本身。
  - Decision reason: `read -s -p "..." VAR` 只把值放进 shell 变量；子进程(opencode)与孙进程(技能脚本)读的是 `os.environ`，只有被 `export` 的变量才进入环境块并被后代继承。
  - Related step, verification or artifact: `S2`/`S3`；verification「shell 变量→子进程环境继承机制」；证据 `E1`(Case A False/Case B True)、`E2`(脚本第 252 行读 env、缺失即 exit 2)。
- **D2** Decision: 用"子进程 + 孙进程 env 回显"作 opencode→技能链路的等价验证，不强依赖真实 opencode 二进制。
  - Decision reason: opencode 只是一个子进程，环境变量继承是 OS 级通用行为；孙进程测试正好建模 `shell → opencode → submit_gitee_issue.py` 派生链。两台测试机均未装 opencode。
  - Related step, verification or artifact: `S3`/`S4`；verification「远端 Linux 连通性与工具可用性」；证据 `E1`、`E4`。
- **D3** Decision: 示范提交走 `--method api`(token 路径)，与用户的 read-token 流程一致。
  - Decision reason: api 路径是纯 python HTTP，跨 Windows/Linux 行为一致，不涉及 Windows `.cmd` shim 的多行截断问题。
  - Related step, verification or artifact: `S5`；verification「端到端真实提交(--method api)」；证据 `E2`、`E5`。

## Resources And Skills

| Name | Type | Role | Related step | Limitation |
| --- | --- | --- | --- | --- |
| onescience-knowledge-capture | executor | 生成结构化贡献并在授权后提交 Issue | S1/S5 | `--method api` 依赖 `GITEE_TOKEN` 环境变量，未 export 则失败 |
| submit_gitee_issue.py | executor | 双后端提交(auto/cli/api)，api 走 `POST /repos/{owner}/issues` | S2/S5 | 无 token 时 exit 2；标签须目标仓已存在否则被丢弃 |
| Git Bash / scnet-infinity bash | resource | 提供 POSIX `read -s -p` 与 `export` 语义 | S3/S4 | Windows 无 opencode，用子/孙进程继承等价验证 |
| gitee-cli (`gitee api`) | resource | 建标签、回读 Issue 核验 | S4/S5 | 多行正文经 `.cmd` shim 会截断，故提交走 node-direct 或 api |

## Artifacts And Verification

- Artifacts:
  - `contributions/general/2026-09-21_gitee_token_read_export_inheritance/contribution.md`（本文档）
  - `.../contribution.json`（v1 机读元数据）
  - `.../issue_payload.json`（IKHM4T 提交用 payload 的历史快照，含三标签；正文为提交当时的 v2 渲染，按用户决定保持原样）
  - `.../submission_card.md`（人工网页提交卡片，同为 IKHM4T 的 v2 历史快照）
- Verification:

| Target | Type | Method | Expected result | Actual result | Status |
| --- | --- | --- | --- | --- | --- |
| shell 变量→子进程环境继承机制 | workflow | Git Bash Case A(不 export)/Case B(export) 假 token 跑子/孙进程 `os.environ` 回显 | Case A 读不到、Case B 读到，孙进程同样继承 | Case A 子/孙 False；Case B 子/孙 True | pass |
| 端到端真实提交(--method api) | result | 真实 token 经 `read -s -p`+`export` 运行 `submit_gitee_issue.py --method api --submit` | HTTP 201 并回带 Issue 编号/URL | HTTP 201，Issue IKHM4T 创建成功 | pass |
| 已提交 Issue 标签与正文完整性 | artifact | `gitee api` 回读 IKHM4T 检查 state/labels/body | state=open，三标签生效，正文完整 | state=open，labels=[feedback,issue-only,resource-gap]，body 长度 17810 | pass |
| 远端 Linux 连通性与工具可用性 | workflow | SSH scnet-infinity `curl .../api/v5/user` 并检查工具链 | 可达 gitee 端点、确认工具 | HTTP 401(到达端点未带认证)；有 python3/git/node、无 opencode | pass |

## Failures And Recovery

| Failure ID | Related step | Symptom | Root cause | Impact |
| --- | --- | --- | --- | --- |
| FAIL-1 | S2 | `--method api` 打印 `no GITEE_TOKEN env var` 并 `exit 2`，Issue 未创建 | `read` 后未 `export`，shell 变量未进入环境块 | 自动提交失败 |
| FAIL-2 | S4 | Gitee 返回 201 但静默丢弃不存在的标签 | 目标仓尚未创建该三标签 | Issue 标签缺失 |
| FAIL-3 | S3 | 输入完 token 后提示符与后续输出挤在同一行 | `read -s` 关闭回显吞掉换行 | 终端 UX 混乱(不影响功能) |

### Recovery Trace

| Trigger failure | Recovery strategy | Recovery action | Recovery result | Status |
| --- | --- | --- | --- | --- |
| FAIL-1 | read 后补 export 再启动子进程 | `read -s -p ... GITEE_TOKEN; echo; export GITEE_TOKEN` | 子/孙进程读到 token，提交成功 | success |
| FAIL-2 | 先建标签再提交 | `POST /repos/{owner}/{repo}/labels` 建三标签 | 回读确认三标签生效 | success |
| FAIL-3 | 静默输入后手动补换行 | `read -s` 后加裸 `echo` | 终端换行正常 | success |

### Capability Attribution

- Knowledge gaps: 无
- Reasoning gaps: 无
- Planning gaps: 无
- Execution gaps: 无
- Verification gaps: 未在真实 `opencode` 二进制上跑完整会话(两台测试机登录 PATH 均未见 opencode)，以子/孙进程环境继承作等价验证(见 `OQ-1`)。
- Resource gaps: Windows 开发机与 scnet-infinity 均未安装 opencode，无法直接复现真实运行环境。
- Contract gaps: 无

## Reusable Knowledge

### Facts

- [F-1] `read -s -p "prompt" VAR` 只赋值 shell 变量；未 `export` 前子进程 `os.environ` 读不到（Git Bash 实测 False/True 对照）。
- [F-2] `submit_gitee_issue.py --method api` 从 `GITEE_TOKEN` / `GITEE_ACCESS_TOKEN` 环境变量取 token，缺失即 `exit 2`（脚本第 252-257 行）。
- [F-3] Gitee 会静默丢弃目标仓不存在的 Issue 标签，需先经 `POST /repos/{owner}/{repo}/labels` 创建。

### Heuristics

- [H-1] 对"外层 shell 注入密钥 → 子进程(opencode) → 孙进程(技能脚本)"链路，交互 `read` 后务必 `export`，并用孙进程 env 回显验证而非只验子进程。Scope: 任何用 POSIX shell 驱动子进程树、需传递密钥的场景。Evidence strength: high。
- [H-2] `read -s` 关闭回显会吞掉换行，其后补一个裸 `echo` 输出换行。Scope: 所有 `read -s` 交互输入。Evidence strength: medium。

### Constraints

- [C-1] token 绝不写入文件/日志/脚本，只在 shell 会话内存活一次；一旦出现在对话或 shell history 中必须立即撤销重生成。

### Fallbacks

- [FB-1] 若已 `gitee auth login`，`--method auto/cli` 用 CLI 本地凭据即可，无需 read+export token——是 token 注入的等价替代路径。

### Anti-patterns

- [AP-1] 把 token 明文贴进对话 / 写进脚本 / 用 `export` 把 token 敲进 shell history——会泄漏到日志与历史。
- [AP-2] 以为 `read VAR` 之后 VAR 自动对子进程可见，省略 `export`。

### New Knowledge

- [NK-1] PowerShell 调 Git Bash 时，外层单引号里 `printf` 的换行转义会被吞掉，导致 `read` 读入的 token 尾部混入字面量 `n`（长度 32→33）而提交 401；把 `printf` 写进 `.sh` 脚本内部（而非经 `-c` 传参）可避免该陷阱。

### Open Questions

- [OQ-1] `UNVERIFIED` 用户实际运行 opencode 的主机在哪（scnet-infinity 登录 PATH 未见 opencode），需确认该环境里 `export` 后的 `GITEE_TOKEN` 确实存在于 opencode 进程环境中。

## Integration Proposal

- Target layer: `executor`
- Target skill or primitive: `onescience-knowledge-capture`
- Target directory: `skills/onescience-knowledge-capture/SKILL.md`（§6 认证小节）
- Proposed changes:
  1. 补充推荐写法：`read -s -p "Please Input Your Gitee Token: " GITEE_TOKEN; echo; export GITEE_TOKEN`，然后再启动 opencode。
  2. 明确警示：只 `read` 不 `export` 会导致 `submit_gitee_issue.py --method api` 报 `no GITEE_TOKEN env var` 并 `exit 2`。
  3. 补充"子进程/孙进程继承"说明：`export` 后 opencode 及其派生的技能脚本都能读到。
- Contract impact: 仅文档，无接口/契约变更。
- Validation plan: Git Bash + Linux 双平台机制测试（子/孙进程 env 回显）+ 真实 `--method api` 提交返回 201。

## Promotion Decision

- Recommendation: `human_review`
- Confidence: `high`
- Rationale: 这是可复用的"令牌注入 + 进程环境继承"经验，且直接指向 SKILL.md §6 文档补全；建议人工审核后并入技能文档，不直接升级为 primitive。
- Required human review: 确认是否把 read+export 写法写入 SKILL.md §6；确认 `OQ-1` 中 opencode 的实际运行环境。

## Privacy And Limitations

- Redactions: 真实 token 全程只经 stdin 喂给 `read`，未写入任何文件；验证后清除 shell 环境变量并提醒用户撤销。
- Sensitive content detected: `false`
- Publication scope: `repository_public`
- Known limitations: 未在真实 opencode 二进制上跑完整会话（两台测试机均未安装 opencode），以子/孙进程环境继承作等价验证。
