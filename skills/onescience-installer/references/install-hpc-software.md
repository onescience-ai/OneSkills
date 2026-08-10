# 工作流 - 安装 HPC 软件

每次 `install_intent=hpc_software` 的安装任务都先读取本工作流。读取本文件前，`SKILL.md` 中的运行站点门禁必须已经通过；若 `run_site` 或远程 SSH 信息缺失，先执行 `runsite-handoff.md`。

## 前置条件

- 已完成 discover 阶段的意图识别与软件匹配
- `onescience.json` 中的 `run_site` 和 `ssh`（remote 模式）已就绪
- 已从 `assets/hpc_software_profiles.json` 匹配到目标软件的 profile

## 步骤

### 1. 加载软件 profile

重新读取 `assets/hpc_software_profiles.json`，确认目标软件已匹配。若存在多个候选或匹配失败，只向用户确认目标软件名。

### 2. 确认安装目录

- 默认安装目录：`profile.install.default_install_dir`（如 `~/hpc_software/gromacs`）
- 向用户确认或允许用户指定自定义路径
- 若目标路径已存在且包含有效安装（存在 `bin/` 子目录且二进制文件可执行），询问用户：
  - **跳过安装**：直接进入验证步骤
  - **覆盖安装**：清空目录后重新下载解压
  - **更换路径**：指定新的安装目录

### 3. 确认 run_site 与渲染通道

从 `onescience.json` 获取：
- `run_site`：`local` 或 `remote`
- `remote` 时获取 `ssh` 信息（`host/hostname`、`port`、`user`、`identity_file`）

根据 `run_site` 选择 `install_flow.md` 中的对应模板：
- `remote` → `§20`（下载 remote）、`§22`（解压 remote）、`§24`（验证 remote）
- `local` → `§21`（下载 local）、`§23`（解压 local）、`§25`（验证 local）

### 4. precheck（环境预检）

安装前检查远端服务器环境：

1. **wget 可用性检查**：
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} "command -v wget >/dev/null 2>&1 && echo wget:available || echo wget:not_found"
   ```
2. **磁盘空间检查**（目标分区可用空间 > 10GB）：
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} "df -h \$(dirname {install_dir}) 2>/dev/null || df -h ~"
   ```
3. **必要 module 检查**（若 profile 定义了 `required_modules`）：
   ```bash
   ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "command -v module >/dev/null 2>&1 && module avail 2>&1 | grep -E \"{required_modules_pattern}\" || echo module:not_found"'
   ```

若 wget 不可用，阻塞安装并提示用户。若磁盘不足，警告用户。若 module 不可用，警告但不阻塞（可在验证阶段再检测）。

### 5. 执行下载

渲染 `install_flow.md` 中对应 run_site 的下载模板：

- 占位符填充：
  - `{install_dir}`：用户确认的安装目录
  - `{download_url}`：`profile.download.url`
  - `{ssh_options}`、`{ssh_port}`、`{ssh_identity}`、`{ssh_user}`、`{ssh_server}`：从 `onescience.json` 获取

下载完成后：
- 确认 `{install_dir}` 下存在 `.tar.gz` 文件
- 从输出中提取下载得到的文件名作为 `{archive_file}`

### 6. 执行解压

渲染 `install_flow.md` 中对应 run_site 的解压模板：

- 占位符填充：
  - `{install_dir}`：同下载目录
  - `{archive_file}`：上一步提取的文件名

解压完成后验证目录结构：
- 检查 `{install_dir}/bin/` 是否存在
- 检查 `{install_dir}/lib64/` 或 `{install_dir}/lib/` 是否存在

### 7. 执行验证

渲染 `install_flow.md` 中对应 run_site 的验证模板：

- 占位符填充：
  - `{verify_command}`：`profile.verify.command`
  - `{install_dir}`：安装目录

验证通过标准：命令输出符合 `profile.verify.pass_criteria` 的描述。

### 8. 环境配置提示

安装验证通过后，向用户输出环境配置指引，例如：

```bash
# 请将以下内容添加到 ~/.bashrc 中以持久化环境配置：
export PATH={install_dir}/bin:$PATH
export LD_LIBRARY_PATH={install_dir}/lib64:$LD_LIBRARY_PATH
```

> **注意**：installer 不自动修改用户的 `~/.bashrc`。仅输出配置提示，由用户自行决定是否持久化。

### 9. 可选冒烟测试

若 profile 定义了 `test_example`，询问用户是否运行冒烟测试：

- 冒烟测试命令来自 `profile.test_example.commands`
- 测试在已配置环境变量的 shell 中执行
- 测试结果仅作为参考，不影响安装成功判定

### 10. 返回结果

安装完成后返回安装摘要：
- 软件名与版本
- 安装路径
- 验证结果
- 环境配置命令
- 上游 handoff 信息（若有）

## 路由判定

| 状态 | 操作 |
|------|------|
| 缺少 `run_site` 或 SSH 信息 | 读取 `runsite-handoff.md` |
| 软件已安装（目录存在且二进制可执行） | 询问跳过/覆盖/更换路径 |
| wget 不可用 | 阻塞安装，提示用户 |
| 磁盘空间不足（< 1GB） | 阻塞安装，警告用户 |
| module 不可用 | 警告但不阻塞 |

## 输出契约

阶段汇报和最终输出至少包含：

- `software_name`：软件 display_name
- `software_version`：安装版本
- `install_dir`：安装目录
- `download_state`：success / failed / skipped
- `extract_state`：success / failed / skipped
- `verify_state`：success / failed
- `install_state`：success / failed / partial
- `next_action`：后续建议
