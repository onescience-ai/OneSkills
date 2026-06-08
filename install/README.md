# OneSkills Installer

本目录提供 `OneSkills` 面向不同智能体的统一安装入口。

注意这里的“安装器”是指把本仓库 skills 安装到你的项目目录里：

- 本地安装器：`install/install_oneskills.py`
- 远程环境安装 skill：`skills/onescience-installer`

两者不要混淆：

- 前者解决“怎么把 OneSkills 装进 Codex / Claude / Trae / OpenCode 项目”
- 后者解决“怎么在远程硬件环境安装 OneScience 运行依赖”

正式安装内容包括：

- `skills/`
- 共享 `references/`
- 对应 agent 的 `integrations/` 适配说明
- `codex`：默认下载 OneScience 源码快照到 `<namespace_root>/onescience/`（供 `onescience-coder` 等读取），可用 `--skip-onescience-source` 跳过；默认下载 SCnet MCP 工具到 `<project>/.codex/oneskills/mcp-tools/scnet-mcp-server.exe`，可用 `--skip-mcp-tools` 跳过
- `runtime` 档位下的项目根运行资产：`onescience.json`、`tpl.slurm`（其中 `onescience.json` 默认来自 `skills/onescience-workflow/assets/onescience.default.json`）
- manifest 如声明 `bridge`，则额外补齐用户级 bridge skills，保证安装后可被对应 agent 发现

安装后的统一入口约定：

- “使用 / 启动 / 打开 / 进入 onescience”与“使用 / 启动 / 打开 / 进入 oneskills”默认进入 `onescience-workflow`。
- 明确点名 `onescience-coder`、`onescience-runtime`、`onescience-installer` 等具体 skill 时，优先使用对应 skill。

## 支持的目标

- `codex`
- `claude`
- `trae`
- `opencode`
- `generic`

## 推荐用法

注意：`install/install_oneskills.py` 需要用户本地已有 Python。Codex 面向普通用户的首选安装方式不依赖 Python，请使用仓库中的 `.codex/INSTALL.md`（含一行提示安装、SCnet MCP 与 OneScience 源码快照步骤）。

安装到指定项目：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project
```

`codex` 默认会下载 MCP 工具二进制：

```text
https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe
```

落盘位置示例：

```text
/path/to/project/.codex/oneskills/mcp-tools/scnet-mcp-server.exe
```

若只需 skills 与文档、不要 MCP 二进制：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --skip-mcp-tools
```

若不要 OneScience 源码快照：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --skip-onescience-source
```

指定 OneScience 源码 zip：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --onescience-source-url https://gitee.com/onescience-ai/onescience/releases/download/0.3.0/onescience-0.3.0.zip
```

按运行档位安装：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --profile runtime
```

开发期使用软链接：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --mode symlink
```

卸载：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --uninstall
```

## 跨平台说明

- `macOS / Linux`：`copy` 与 `symlink` 都可正常使用
- `Windows`：推荐使用默认 `copy` 模式
- 如果在 `Windows` 上显式传入 `--mode symlink`，安装器会自动降级为 `copy`

## 说明

- `--project` 支持相对路径和绝对路径
- `generic` 模式适合其他支持技能目录约定的智能体
- 可先用 `--dry-run` 查看将写入哪些路径
- 可用 `--list-agents` 查看当前 manifest 注册的目标 agent
- `--profile basic` 是默认档位，适合只安装技能本体
- `--profile runtime` 适合准备实际提交远程任务的项目

维护约定：

- `install/contract.json` 声明安装状态版本、bridge marker、legacy marker 与 bridge/template 共享契约
- `install/manifests/<agent>.json` 只声明 `namespace_root`、`integration_sources` 与可选 `bridge`
- `install/profile_targets.json` 声明各个 install profile 额外写入的项目根资产
- `install/templates/bridge_skill.md.tpl` 声明用户级 bridge skill 的文本模板
- `skills/`、共享 `references/`、`integrations/` 的实际落盘路径由安装器统一从 `namespace_root` 推导

## FAQ

### 1. 会安装到哪里？

安装器会根据 `--agent` 自动选择技能目录：

- `codex` → `.codex/oneskills/skills/`
- `claude` → `.claude/oneskills/skills/`
- `trae` → `.trae/oneskills/skills/`
- `opencode` → `.opencode/skills/`（与 OpenCode 默认发现路径一致；同时默认下载 `onescience/` 到 `.opencode/onescience/`，并生成 `.opencode/opencode.jsonc.snippet`）

如果使用 `generic`，则由 `--skills-dir` 明确指定。

安装完成后，用户可优先查看安装目录下的 `VERSION` 文件确认当前 skills 版本。
共享参考资料会与 namespaced skills 同级安装，例如 `.<agent>/oneskills/references/`；OpenCode 默认则为 `.opencode/references/`。
集成说明会放在 namespaced 根目录下的 `integrations/`；OpenCode 默认则为 `.opencode/integrations/`。
如目标 agent 的 manifest 声明了 `bridge`，安装器会同时在对应用户级 skills 根目录写入一层 bridge skill。
当前仓库内默认启用该能力的是 `codex`，会写入 `~/.codex/skills/onescience-*`。

### 2. 重复安装怎么办？

如果目标路径已存在，安装器会提示冲突。

这时可选择：

- 先用 `--uninstall` 卸载
- 或使用 `--force` 直接覆盖

### 3. `--profile runtime` 会安装什么？

更推荐直接使用：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --profile runtime
```

会额外把下面两个运行资产放到项目根目录：

- `onescience.json`
- `tpl.slurm`

适合需要远程运行提交的项目；如果只是本地使用技能做分析或代码生成，可以不加这个参数。

当前默认导出的这套项目根运行资产中：

- `onescience.json` 用于声明目标 backend、任务资源与脚本入口（安装时从 `skills/onescience-workflow/assets/onescience.default.json` 拷贝到项目根；与 workflow 运行时自动初始化行为一致）
- `tpl.slurm` 是项目根默认导出的 slurm 模板入口

但是否真的支持某条执行链路，不应只看是否安装了这两个文件，还要看：

- `skills/onescience-runtime/assets/backend_specs.json` 中该 backend 的 `support_matrix`
- 当前 host 的 readiness / precheck 结果

当前共享边界是：

- `slurm_dcu`：runtime=`stable` / installer=`supported`
- `slurm_gpu`：runtime=`stable` / installer=`supported`
- `slurm_gpu_multinode_torchrun`：runtime=`stable` / installer=`supported`
- `slurm_cpu`：runtime=`stable` / installer=`unsupported_for_now`

如果未来需要支持其他硬件后端，建议在项目内按契约扩展 backend registry、source template 与 readiness 语义，而不是直接把这套 DCU 根模板改造成“伪通用模板”。

### 4. `--uninstall` 会删除什么？

安装器会删除它自己安装过的内容，包括：

- 对应 agent 的技能目录下本次安装的 `OneSkills` 条目
- 与技能同级的共享 `references/`
- 对应的集成说明文件
- 如有安装，则删除本次安装的运行资产
- 安装记录文件 `.oneskills/install-state/<agent>.json`
- 若该 agent 声明了 `bridge`，且当前机器上已没有其他项目注册该 bridge，则同时删除对应用户级 bridge 文件与 bridge state

安装记录当前只保留最小状态：

- `schema_version`
- `agent`
- `mode`
- `profile`
- `targets`（本次安装写入的相对路径列表；含 `codex` 时可能还有 `onescience` 源码目录等）
- 可选 `mcp_tools`（`codex` 且未 `--skip-mcp-tools` 时记录 MCP 二进制路径与下载 URL）

它不会删除未被安装器记录的其他用户文件。

### 5. 它和 `onescience-installer` 是什么关系？

没有直接替代关系，它们属于两条不同链路：

- `install/install_oneskills.py`：把 skills 和可选运行资产安装到本地项目
- `skills/onescience-installer`：读取完整硬件画像，在远程环境安装 `OneScience`

如果你现在是在维护本仓库的安装入口、manifest 或 agent 适配，优先看本目录。
如果你现在是在维护远程 DCU 环境安装流程，优先看 `skills/onescience-installer/SKILL.md`、`skills/onescience-installer/references/install_rules.md` 与 `skills/onescience-installer/references/install_flow.md`。

### 6. OpenCode 如何配置 skills.paths？

OpenCode 默认会自动扫描 `.opencode/skills/*/SKILL.md`。因此使用默认 OpenCode 安装布局时，通常**不必**修改 `opencode.jsonc`。

安装器仍会写入配置片段，供非默认布局或项目级显式配置时使用：

```text
<project>/.opencode/opencode.jsonc.snippet
```

若需要显式声明，可将片段中的 `skills.paths` 合并进项目或全局 `opencode.jsonc`：

```jsonc
{
  "skills": {
    "paths": [".opencode/skills"]
  }
}
```

全局安装示例：

```bash
python3 install/install_oneskills.py --agent opencode --project ~
```

若希望安装到持久化 vendor 目录：

```bash
python3 install/install_oneskills.py --agent opencode --project /path/to/project \
  --namespace-root vendor/oneskills/2026.05.15
```

此时 `skills.paths` 应改为 `vendor/oneskills/2026.05.15/skills`，且通常需要写入 `opencode.jsonc`。

### 7. Claude / Codex 插件模式怎么安装？

如果你希望按插件方式安装 Claude Code，或按 Codex 原生 skills 发现方式安装，请看：

- `docs/user-guides/claude_codex_plugin_install.md`
- `.codex/INSTALL.md`

MCP 配置示例在：

- `onescience-plugin/config-examples/claude.mcp.example.json`
- `onescience-plugin/config-examples/codex.mcp.example.json`
