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
- `runtime` 档位下的项目根运行资产：`onescience.json`、`tpl.slurm`
- `codex` 下额外补齐用户级 bridge skills，保证安装后可被当前 Codex 发现

安装后的统一入口约定：

- “使用 / 启动 / 打开 / 进入 onescience”与“使用 / 启动 / 打开 / 进入 oneskills”默认进入 `onescience-workflow`。
- 明确点名 `onescience-coder`、`onescience-runtime`、`onescience-debug` 等具体 skill 时，优先使用对应 skill。

## 支持的目标

- `codex`
- `claude`
- `trae`
- `opencode`
- `generic`

## 推荐用法

安装到指定项目：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project
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
- `--with-runtime-assets` 仍可使用，但只是兼容旧命令的别名

## FAQ

### 1. 会安装到哪里？

安装器会根据 `--agent` 自动选择技能目录：

- `codex` → `.codex/oneskills/skills/`
- `claude` → `.claude/oneskills/skills/`
- `trae` → `.trae/oneskills/skills/`
- `opencode` → `.opencode/oneskills/skills/`

如果使用 `generic`，则由 `--skills-dir` 明确指定。

安装完成后，用户可优先查看安装目录下的 `VERSION` 文件确认当前 skills 版本。
共享参考资料会与 namespaced skills 同级安装，例如 `.<agent>/oneskills/references/`。
集成说明会放在 `.<agent>/oneskills/integrations/`，保持与仓库内相同的相对路径结构。
其中 `codex` 会同时在 `~/.codex/skills/onescience-*` 写入一层 bridge skill，让用户在当前项目中安装后即可直接使用。

### 2. 重复安装怎么办？

如果目标路径已存在，安装器会提示冲突。

这时可选择：

- 先用 `--uninstall` 卸载
- 或使用 `--force` 直接覆盖

### 3. `--with-runtime-assets` 会安装什么？

更推荐直接使用：

```bash
python3 install/install_oneskills.py --agent codex --project /path/to/project --profile runtime
```

`--with-runtime-assets` 仍然有效，但只是 `--profile runtime` 的兼容别名。

会额外把下面两个运行资产放到项目根目录：

- `onescience.json`
- `tpl.slurm`

适合需要远程运行提交的项目；如果只是本地使用技能做分析或代码生成，可以不加这个参数。

当前默认导出的这套项目根运行资产中：

- `onescience.json` 用于声明目标 backend、任务资源与脚本入口
- `tpl.slurm` 仍是 `slurm_dcu` 兼容路径的根模板

但是否真的支持某条执行链路，不应只看是否安装了这两个文件，还要看：

- `skills/onescience-runtime/assets/backend_specs.json` 中该 backend 的 `support_matrix`
- 当前 host 的 readiness / precheck 结果

当前共享边界是：

- `slurm_dcu`：runtime=`stable` / installer=`supported` / debug=`supported`
- `slurm_gpu`：runtime=`stable` / installer=`unsupported_for_now` / debug=`supported`
- `slurm_cpu`：runtime=`planned` / installer=`unsupported_for_now` / debug=`planned_backend`

如果未来需要支持其他硬件后端，建议在项目内按契约扩展 backend registry、source template 与 readiness 语义，而不是直接把这套 DCU 根模板改造成“伪通用模板”。

### 4. `--uninstall` 会删除什么？

安装器会删除它自己安装过的内容，包括：

- 对应 agent 的技能目录下本次安装的 `OneSkills` 条目
- 与技能同级的共享 `references/`
- 对应的集成说明文件
- 如有安装，则删除本次安装的运行资产
- 安装记录文件 `.oneskills/install-state/<agent>.json`
- 若当前机器上已没有其他项目注册 `codex` bridge，则同时删除 `~/.codex/skills/onescience-*` bridge 和 `~/.codex/.oneskills/bridge-state.json`

它不会删除未被安装器记录的其他用户文件。

### 5. 它和 `onescience-installer` 是什么关系？

没有直接替代关系，它们属于两条不同链路：

- `install/install_oneskills.py`：把 skills 和可选运行资产安装到本地项目
- `skills/onescience-installer`：读取完整硬件画像，在远程环境安装 `OneScience`

如果你现在是在维护本仓库的安装入口、manifest 或 agent 适配，优先看本目录。
如果你现在是在维护远程 DCU 环境安装流程，优先看 `skills/onescience-installer/SKILL.md` 与 `skills/onescience-installer/references/install_flow.md`。

### 6. Claude / Codex 插件模式怎么安装？

如果你希望按插件方式安装 Claude Code，或按 Codex 原生 skills 发现方式安装，请看：

- `docs/user-guides/claude_codex_plugin_install.md`
- `.codex/INSTALL.md`

MCP 配置示例在：

- `onescience-plugin/config-examples/claude.mcp.example.json`
- `onescience-plugin/config-examples/codex.mcp.example.json`
